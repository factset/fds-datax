import os
import pandas as pd
import pkg_resources
import pyodbc

from fds.datax.utils.helper_func import __insert_values__
from fds.datax.utils.loadsql import get_sql_q as ls

cwd = os.getcwd()
path = '../sql_files/'
sql_path = pkg_resources.resource_filename(__name__, path)


class GetSDFData:
    """
The GetSDFData class is designed to streamline the retrieval of data from FactSet's Standard DataFeeds.  Each
attribute within the class is designed to retrieve a specific set of data items:

Main Features
--------------------

- Utilize FactSet's Ownership Database to access historical ETF holdings as a baseline universe.

- Retrieve all levels of FactSet's Entity centric symbology model to all instance access to any content set within
the Standard DataFeed ecosystem.

- Access baseline categorical information such as country of domicile, sector classifications, and other company
specific meta data.

- Fetch prices (OHLC), 1 day total returns, market cap, exchange rates, and corporate action adjustment ratios for a
universe.
    """

    @classmethod
    def etf_universe(cls, etf_ticker, start_date, end_date, mssql_dsn):
        """
Returns the constituents of an ETF from FDS Ownership in a pandas DataFrame.
ETF Ownership is available on a annual, semi-annual, quarterly, or monthly frequency
depending on the frequency of filings. Data will be resampled daily by forward filling the data set.


Parameters
-----------

   - etf_ticker: ETF ticker in a ticker-region format. For example,
                SPY-US.

   - start_date: earliest available report date in YYYY-MM-DD format

   - end_date: most recent available report date to be returned in YYYY-MM-DD format

   - mssql_dsn: the name of a DSN connection that has access to FDS Standard Datafeeds


Returns
-----------

A Pandas DataFrame containing:

    ref_id|fsym_primary_listing_id|fsym_primary_equity_id|date
        """
        connection = pyodbc.connect("DSN={}".format(mssql_dsn))

        q = ls(
            os.path.join(sql_path, "etf_universe.sql"), show=0, connection=mssql_dsn
        ).format(etf_ticker=etf_ticker, sd=start_date, ed=end_date)

        univ = pd.read_sql(q, connection, parse_dates={"date": {"format": "%Y-%m-%d"}})

        return univ

    @classmethod
    def fds_symbology(
        cls, univ_df, mssql_dsn, id_type="0", ref_id="ref_id", ref_date="date"
    ):
        """
fds_symbology
-----------

Returns FDS symbology at the -R, -S, and -E level.  For the -E will be returned in a PIT
manner based on the date in the input data frame.

Parameters
-----------

   - univ_df: the input dataframe containing at least a FDS or market ID
            (SEDOL, CUSIP, ISIN all with a check digit included)

   - mssql_dsn: DSN name for a connection to a MSSQL Server DB containing
                 FDS Standard DataFeeds content.

   - id_type: flagged designating if the input ID is a FDS ID or market
            1: Market ID (SEDOL, CUSIP, ISIN all must include a check digit)
            2: FDS Id

   - ref_id: This will identify the column name in the univ_df of the primary
            ID.

   - ref_date: This will identify the column name in the univ_df of the date field.

Returns
-----------

A Pandas DataFrame containing:

    ref_id | fsym_primary_listing_id | fsym_primary_equity_id | date | adj_holding | proper_name | factset_entity_id
        """

        connection = pyodbc.connect("DSN={}".format(mssql_dsn))

        id_list = __insert_values__(univ_df[ref_id].dropna().unique().tolist())
        if id_type == 1:
            query_file = ls(
                os.path.join(sql_path, "fds_symbology_df.sql"),
                show=0,
                connection=mssql_dsn,
            )

        else:
            query_file = ls(
                os.path.join(sql_path, "fds_symbology_own.sql"),
                show=0,
                connection=mssql_dsn,
            )

        q = query_file.format(insert_statements=id_list)

        fds_sym = pd.read_sql(
            q, connection, parse_dates=["entity_start_date", "entity_end_date"]
        )
        fds_sym["ref_id"] = fds_sym.ref_id.str.strip()
        fds_sym = univ_df.merge(fds_sym, how="inner", on=ref_id)

        fds_sym = fds_sym.loc[
            (fds_sym[ref_date] >= fds_sym.entity_start_date)
            & (
                (fds_sym[ref_date] < fds_sym.entity_end_date)
                | (fds_sym.entity_end_date.isnull())
            )
        ]
        fds_sym = fds_sym.iloc[:, :-2]
        return fds_sym

    @classmethod
    def fds_sec_ref(cls, entity_id_list, mssql_dsn):
        """
fds_sec_ref
-----------------

Returns country and RBICS sector levels 1-4 for a universe.

Parameters
-----------

   - entity_id_list:  A python list containing FactSet Entity IDs for the universe.**

   - mssql_dsn: DSN name for a connection to a MSSQL Server DB containing
                 FDS Standard DataFeeds content.

**To retrieve FactSet Entity IDs please use the fds_symbology function.

Returns
-----------

A Pandas DataFrame containing:

    factset_entity_id | entity_proper_name | country | region | rbics_l1_id | rbics_l1 |....| rbics_l4_id | rbics_l4

        """
        connection = pyodbc.connect("DSN={}".format(mssql_dsn))

        q = ls(
            os.path.join(sql_path, "fds_sec_ref.sql"), show=0, connection=mssql_dsn
        ).format(insert_statements=__insert_values__(entity_id_list))
        ref_data = pd.read_sql(q, connection)
        to_convert = [
            "country",
            "region",
            "rbics_l1",
            "rbics_l2",
            "rbics_l3",
            "rbics_l4",
        ]
        ref_data[to_convert] = ref_data[to_convert].astype("category")
        return ref_data

    @classmethod
    def fds_fx_rates(
        cls, currency_list, target_currency, start_date, end_date, mssql_dsn
    ):
        """
fds_fx_rates
-----------------

Returns daily exchange rates from a list of currency to a common target currency.

Parameters
-----------

    - currency_list:  A python list containing currency ISO-3

    - target_currency: Currency to be converted to (ISO-3)

    - start_date: earliest fx rate to be returned in YYYY-MM-DD format

    - end_date: most recent fx rate to be returned in YYYY-MM-DD format

Returns
-----------

A Pandas DataFrame containing:

    price_date | currency | currency_to | exch_rate_usd | exch_rate_per_usd_to | fx_rate

        """
        connection = pyodbc.connect("DSN={}".format(mssql_dsn))
        currency_list.append(target_currency)
        currency_list = "'" + "','".join(str(c) for c in currency_list) + "'"
        q = ls(
            os.path.join(sql_path, "fds_fx_rates.sql"), show=0, connection=mssql_dsn
        ).format(ids=currency_list, sd=start_date, ed=end_date)
        fx = pd.read_sql(q, connection, parse_dates=["price_date"])
        fx = pd.merge(
            fx,
            fx[fx.currency == target_currency],
            how="inner",
            left_on=["price_date"],
            right_on=["price_date"],
            suffixes=("", "_to"),
        )
        fx = fx[
            [
                "price_date",
                "currency",
                "currency_to",
                "exch_rate_usd",
                "exch_rate_per_usd_to",
            ]
        ]
        fx["fx_rate"] = fx["exch_rate_usd"] * fx["exch_rate_per_usd_to"]
        return fx

    @classmethod
    def fds_prices(
        cls, regional_id_list, start_date, end_date, currency, adjtype, mssql_dsn
    ):
        """
fds_prices
Returns daily pricing information for the specified universe.

Parameters
regional_id_list: A python list containing FactSet Entity IDs for the universe.**

start_date: The earliest date for which pricing will be retrieved. Format requires

    YYYY-MM-DD.
end_date: The earliest date for which pricing will be retrieved. Format requires

    YYYY-MM-DD.
currency: currency for pricing data to be return, if local currency is desired set

  to "LOCAL"
adjtype: Specifies the type of pricing to be returned:

 0:  Unadjusted values.
 1:  Split adjusted values.
 2:  Split and spin-off adjusted values.
 3:  All types.
mssql_dsn: DSN name for a connection to a MSSQL Server DB containing

        FDS Standard DataFeeds content.
**To retrieve FactSet Entity IDs please use the fds_symbology method.

Returns
A Pandas DataFrame containing:

ref_id | fsym_id | price_date | currency | one_day_total_return | volume | shares_outstanding | price_close |
price_high | price_low | price_open | market_value
        """

        connection = pyodbc.connect("DSN={}".format(mssql_dsn))

        q = ls(
            os.path.join(sql_path, "fds_prices.sql"), show=0, connection=mssql_dsn
        ).format(
            insert_statements=__insert_values__(regional_id_list),
            sd=start_date,
            ed=end_date,
        )
        out = []
        for chunk in pd.read_sql(
            q, connection, chunksize=10000, parse_dates=["price_date"]
        ):
            out.append(chunk)
        if len(out) > 1:
            prices = pd.concat(out)
        else:
            prices = pd.read_sql(q, connection, parse_dates=["price_date"])
        del out

        to_convert = ["currency"]
        prices[to_convert] = prices[to_convert].astype("category")
        ######################################
        # Handle FX rate conversions
        ######################################
        curr_list = prices.currency.unique().tolist()
        curr_list.append(currency)
        curr_list = list(set(curr_list))

        if currency.upper() == "LOCAL" or (
            len(curr_list) == 1 and curr_list[0] == currency.upper()
        ):
            pass
        else:

            # Get FX
            fx = cls.fds_fx_rates(curr_list, currency, start_date, end_date, mssql_dsn)
            filtered_fx = fx[fx.currency == currency].copy()

            fx = fx.merge(
                filtered_fx, how="inner", on=["price_date"], suffixes=("", "_target")
            )

            fx = fx[
                [
                    "price_date",
                    "currency",
                    "currency_to",
                    "exch_rate_usd",
                    "exch_rate_per_usd_to_target",
                ]
            ]
            fx["fx_rate"] = fx["exch_rate_usd"] * fx["exch_rate_per_usd_to_target"]
            fx = fx[["price_date", "currency", "currency_to", "fx_rate"]]

            prices = prices.merge(fx, how="left", on=["price_date", "currency"])
            prices.iloc[:, 5:20] = prices.iloc[:, 5:20].multiply(
                prices["fx_rate"], axis="index"
            )

            prices = prices.drop("currency", axis=1)

            prices.rename(columns={"currency_to": "currency"}, inplace=True)
        if adjtype == 0:
            # unadjusted data
            p_type = [
                # 'ref_id',
                "fsym_id",
                "price_date",
                "currency",
                "one_day_total_return",
                "unadj_price_close",
                "unadj_price_high",
                "unadj_price_low",
                "unadj_price_open",
                "unadj_volume",
                "unadj_shares_outstanding",
                "market_value",
            ]
        elif adjtype == 1:
            # split adjusted data
            p_type = [
                # 'ref_id',
                "fsym_id",
                "price_date",
                "currency",
                "one_day_total_return",
                "split_adj_volume",
                "split_adj_shares_outstanding",
                "split_adj_price_close",
                "split_adj_price_high",
                "split_adj_price_low",
                "split_adj_price_open",
                "market_value",
            ]

        elif adjtype == 2:
            # split and spin-off adjusted
            p_type = [
                # 'ref_id',
                "fsym_id",
                "price_date",
                "currency",
                "one_day_total_return",
                "split_adj_volume",
                "split_adj_shares_outstanding",
                "split_spin_adj_price_close",
                "split_spin_adj_price_high",
                "split_spin_adj_price_low",
                "split_spin_adj_price_open",
                "market_value",
            ]
        else:
            return prices
        prices = prices[p_type]
        prices.columns = [
            col.replace("unadj_", "")
            .replace("split_spin_adj_", "")
            .replace("split_adj_", "")
            for col in prices.columns
        ]
        prices.reset_index(inplace=True, drop=True)
        return prices

    @classmethod
    def fds_corp_actions(cls, regional_id_list, mssql_dsn):
        """
fds_corp_actions
-----------------

Returns cumulative adjustment factors for splits and spin-offs for a universe.

Parameters
-----------

    - regional_id_list:  A python list containing FactSet Entity IDs for the universe.

    - mssql_dsn: DSN name for a connection to a MSSQL Server DB containing
                 FDS Standard DataFeeds content.

**To retrieve FactSet Regional IDs please use the fds_symbology method.

Returns
-----------

A Pandas DataFrame containing:

    ref_id | fsym_id | price_date | cum_split_factor | cum_spin_factor

        """
        connection = pyodbc.connect("DSN={}".format(mssql_dsn))

        q = ls(
            os.path.join(sql_path, "fds_corp_actions.sql"), show=0, connection=mssql_dsn
        ).format(insert_statements=__insert_values__(regional_id_list))
        ca = pd.read_sql(q, connection)

        return ca
