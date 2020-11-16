from fds.datax._sdfhelpers._create import FdsDataStore as hcreate
from fds.datax._sdfhelpers._find import FdsDataStoreLedger as hfind
from fds.datax._sdfhelpers._read import FdsReadCache as hread


class Universe:
    def __init__(self, dir_path):
        self.dir_path = dir_path

    def locate(self):
        """
       locate
    --------

The "fds.datax.universe.locate" module allows you to find a list of existing data cache files or delete an individual cache
from the default working directory.


     Returns
    -----------
A Pandas DataFrame containing metadata pertaining to each data cache that has been created. This data is a result of
the parameters that were the inputs within the “fds.sdf.create” module.

        Cache Name | Source | Cache Location | MSSQL DSN | ETF Ticker | Currency | Start Date | End Date | Last
        Update Date

     If no data cache files are found: "No existing Data Cache Universes exist in this Data Store. Use the
     fds.datax.universe.create() function to generate a new data cache universe." Will be returned

        """
        obj = hfind(dir_path=self.dir_path).avail_caches()

        return obj

    def delete(self, cache_name=""):
        """
       Delete
    --------

The "fds.datax.universe.delete" module allows you to delete an individual cache from the default working directory.
    Parameters
    -----------

        -cache_name (string) – A string parameter that will specify the cache name to be deleted.


    Returns
    -----------
    Returns a success message once the identified cache has been removed.
        """

        obj = hfind(dir_path=self.dir_path).delete_cache(cache_name=cache_name)
        return obj

    def create(
        self,
        option="generate",
        source="SDF",
        cache_name="",
        mssql_dsn="",
        etf_ticker="",
        currency="",
        start_date="",
        end_date="",
    ):
        """
    create

The "fds.universe.create" module allows you to generate a new universe cache, load a custom data frame, or rebuild an
existing universe cache from the default working directory.

    Parameters
    -----------
    - Option: "generate" or "load"

•	generate – generates a universe data file for a given ETF and time range.
•	load – load a custom data frame containing a universe to generate a new universe data file.


    - Source:
        -Default is 'SDF.'  This references to the ultimate source of the underlying data will be retrieved from a
        FactSet Standard DataFeed deployment.

        -Future support will be developed for API sourced content.

    "Generate" Parameters
    --------------------------
    This option requires the following inputs:
cache_name (string) – Unique name to define the collection of cache files

mssql_dsn (string) – DSN name for a connection to MSSQL Server DB containing FDS Standard DataFeeds content.

curreny (string) – currency for pricing data to be return, if local currency is desired set to “LOCAL”

etf_ticker (string) – ETF-regional identifier used to retrieve information from FDS Ownership data

start_date (date - YYYY-MM-DD) – date for the start of the universe pull (first available)

end_date (date - YYYY-MM-DD) – date for the end of the universe pull (most recent)

source (string) – This references to the ultimate source of the underlying data. ‘SDF’ represents the FactSet
Standard DataFeed. Future support will be developed for API sourced content.




    "load" Parameters
    --------------------------
    This option requires the following inputs:

data (pd.DataFrame) – A pandas DataFrame containing a timer series universe. File must include the following headers:
•	ref_id – such as ISIN, CUSIP, SEDOL, Ticker-region (AAPL-US) or Ticker-Exchange (AAPL-NAS)
•	date – date in a YYYY-MM-DD format

cache_name (string) – Unique name to define the collection of cache files

mssql_dsn (string) – DSN name for a connection to MSSQL Server DB containing FDS Standard DataFeeds content.

curreny (string) – currency for pricing data to be return, if local currency is desired set to “LOCAL”

start_date (date - YYYY-MM-DD) – date for the start of the universe pull (first available)


    Returns
    -----------

    Each option will return a status message. To access the content created, utilize "fds.universe.read"
        """
        if (option.lower() == "generate") & (source.lower() == "sdf"):
            obj = hcreate(dir_path=self.dir_path).build_universe(
                cache_name, mssql_dsn, etf_ticker, currency, start_date, end_date
            )
        elif (option.lower() == "load") & (source.lower() == "sdf"):
            obj = hcreate(dir_path=self.dir_path).load_universe(
                data, cache_name, mssql_dsn, currency, start_date
            )
        else:
            print("Select the option of Generate or Load!")
        return obj

    def rebuild(self, cache_name=""):
        """
    create

The `fds.universe.rebuild` module rebuilds an existing cache with the details contained in the fds details file.

    Parameter
    ------------------------------

cache_name (string) – A Universe cache name found in the available cache data store.

    Returns
    -----------

A string status message informing you that the universe was rebuilt. To access the content created,
utilize “fds.universe.read”
"""
        obj = hcreate(dir_path=self.dir_path).rebuild_cache(cache_name)
        return obj

    def read(self, cache_name, option="Universe", adj=1, show_details=1):
        """
    read
    ------

The `fds.universe.read` module will load data files specific to the universe and cache name that is specified.

    Parameters
    ----------------
    - cache_name: Universe cache name found in the available cache
    - option: "universe", "sec ref", "prices", or "corp actions"
        - Universe: load time series symbology information for a cache
        - Sec Ref: load security reference for a cache
        - Prices: load pricing data for a cache. Choose unadjusted, split, or split & spin-off.
        - Corp Actions: load corporate action factors for a cache

    "prices" Parameters
    -----------------------------
    When using the option "prices", you must also define the adjustments that should be applied to the data:
    -adj: The following adjustments are supported:
             0:  Unadjusted values.
             1:  Split adjusted values.
             2:  Split and spin-off adjusted values.
             3:  All types.

    Returns
    ------------

    "universe" Returns
    ---------------------------
    A Pandas DataFrame containing the cached universe and FDS symbology:

    ref_id | fsym_primary_listing_id | fsym_primary_equity_id | date  | proper_name | factset_entity_id


    "sec ref" Returns
    -------------------------
    A Pandas DataFrame containing security reference data:

    factset_entity_id | entity_proper_name | country | region | rbics_l1 | rbics_l2| rbics_l3| rbics_l4| rbics_l1_id
    |..|rbics_l4_id


    "corp actions" Returns
    --------------------------------
    A Pandas DataFrame containing cumulative adjustment factors for splits and spin-offs for a universe:

    ref_id | fsym_id | price_date | cum_split_factor | cum_spin_factor


    "prices" Returns
    ------------------------
    A Pandas DataFrame containing daily pricing information for the specified universe:

    ref_id | fsym_id| price_date | currency | one_day_total_return | volume | shares_outstanding | price_close |
    price_high | price_low | price_open | market_value

        """
        if option.lower() == "universe":
            obj = hread(dir_path=self.dir_path).load_sym(
                cache_name=cache_name, show_details=show_details
            )
        elif option.lower() == "sec ref":
            obj = hread(dir_path=self.dir_path).load_sec_ref(
                cache_name=cache_name, show_details=show_details
            )
        elif option.lower() == "prices":
            obj = hread(dir_path=self.dir_path).load_prices(
                cache_name=cache_name, adj=adj, show_details=show_details
            )
        elif option.lower() == "corp actions":
            obj = hread(dir_path=self.dir_path).load_corp_actions(
                cache_name=cache_name, show_details=show_details
            )
        else:
            print("Select the option of Generate, Load, or Rebuild")
        return obj

