import os
import pandas as pd
import pyodbc

from fds.datax._get_data._get_data import GetSDFData as fd
from fds.datax._sdfhelpers._find import FdsDataStoreLedger
from fds.datax.utils.helper_func import __valid_cache_name__
from fds.datax.utils.ipyexit import IpyExit


class FdsDataStore:
    def __init__(self, dir_path):
        self.dir_path = dir_path

    def __get_data__(
        self,
        cache_name: object,
        univ: object,
        mssql_dsn: object,
        currency: object,
        start_date: object,
        fname: object,
        df_type: object,
    ) -> object:
        """
        df_type is used to flag the import type.  Different queries are used for
        Step 1 depending on file import vs Ownership universe.  
        0: Ownership
        1: import. 
        """

        ed = pd.to_datetime("today").strftime("%Y-%m-%d")
        connection = pyodbc.connect("DSN={}".format(mssql_dsn))

        #####################################
        ## Step 1: Attach FDS Symbology
        #####################################

        print("Downloading FDS Symbology for Universe File...")
        fds_sym = fd.fds_symbology(
            univ_df=univ,
            mssql_dsn=mssql_dsn,
            id_type=df_type,
            ref_id="ref_id",
            ref_date="date",
        )

        print("\tFDS Symbology Downloaded.")
        ## Create Master Universe DataFrame
        sec_ref_univ = fds_sym.factset_entity_id.dropna().unique().tolist()
        prices_univ = fds_sym.fsym_primary_listing_id.dropna().unique().tolist()

        ## Export file to Feather

        print("\tSaving FDS Universe File as {}_univ.snappy\n".format(fname))

        fds_sym.reset_index(drop=True).to_parquet(fname + "_univ.snappy")

        ######################################
        ## Step 2: Grabbing Security Reference
        ######################################
        print("Downloading Security Reference Data for Universe File...")
        ref_data = fd.fds_sec_ref(entity_id_list=sec_ref_univ, mssql_dsn=mssql_dsn)

        id_map = dict(zip(fds_sym.factset_entity_id.tolist(), fds_sym.ref_id.tolist()))
        ref_data["ref_id"] = ref_data.factset_entity_id.map(id_map)
        ref_data = ref_data[
            [
                "ref_id",
                "factset_entity_id",
                "country",
                "region",
                "rbics_l1",
                "rbics_l2",
                "rbics_l3",
                "rbics_l4",
                "rbics_l1_id",
                "rbics_l2_id",
                "rbics_l3_id",
                "rbics_l4_id",
            ]
        ]

        print("\tSaving Universe Metadata File as {}_ref_data.snappy\n".format(fname))
        # feather.write_dataframe(ref_data,fname+'_ref_data.feather')

        ref_data.to_parquet(fname + "_ref_data.snappy")

        #####################################
        ## Step 3: Grab Pricings
        #####################################
        print(
            "Downloading Pricing for Universe File...\n \tThis can take a few minutes...\n\n"
        )
        prices = fd.fds_prices(
            regional_id_list=prices_univ,
            start_date=start_date,
            end_date=ed,
            currency=currency,
            adjtype=3,
            mssql_dsn=mssql_dsn,
        )
        id_map = dict(
            zip(fds_sym.fsym_primary_listing_id.tolist(), fds_sym.ref_id.tolist())
        )

        prices["ref_id"] = prices.fsym_id.map(id_map)

        corp_actions = prices.loc[prices.adj_factor_flag == 1][
            ["ref_id", "fsym_id", "price_date", "cum_split_factor", "cum_spin_factor"]
        ].copy()

        ########################################
        ## Step 5: Create Corporate Actions File
        ########################################

        print("\tSaving Universe Prices File as {}_corp_actions.snappy\n".format(fname))

        corp_actions.reset_index(drop=True).to_parquet(fname + "_corp_actions.snappy")
        del corp_actions

        prices["ref_id"] = prices.fsym_id.map(id_map)
        prices = prices.loc[
            :,
            ~prices.columns.isin(
                ["cum_split_factor", "cum_spin_factor", "adj_factor_flag"]
            ),
        ]

        print("\tSaving Universe Prices File as {}_prices.snappy\n\n".format(fname))

        prices.reset_index(drop=True).to_parquet(fname + "_prices.snappy")
        print("FDS Cache Created.")

    def build_universe(
        self, cache_name, mssql_dsn, etf_ticker, currency, start_date, end_date
    ):
        """
        This function requires the following inputs:
        
        -cache_name: Unique name to define the collection of cache files
        -mssql_dsn:  DSN name associated with the MSSQL Server where FDS data resides
        -currency: currency for pricing data to be return, if local currency is desired set
                   to "LOCAL"
        -etf_ticker: ETF-Region ticker used to retrieve information from FDS Ownership
        -start_date: YYYY-MM-DD date for the start of the universe pull (first available)
        -end_date: YYYY-MM-DD date for the end of the universe pull (most recent)
        
        The output of this function will be 4 files:
        
        -[cache_name]_univ.snappy: This file will contain a time series
        universe along with FDS symbology.  Fields include:
            -ref_id: FSYM-S designated by FactSet Ownership
            -date: data date
            -fsym_primary_equity_id: FactSet Security ID
			-fsym_primary_listing_id: FactSet Regional ID
			-factset_entity_id: FactSet Entity ID
        
        -[cache_name]_ref_data.snappy: This file will contain country and current
		     RBICS Classifications:
			 -country: country of domicile 
			 -L1-L6 ID and Name: RBICS sector classficiations        
        
        -[cache_name]_prices.snappy: This file will contain pricing information:
			-currency - Currency of the prices
			-market_value - Market Value of the security
			-one_day_tr - 1 day total return
			-price_close - Closing price
			-p_price_high - Intraday High
			-p_price_low - Intraday Low
			-p_price_open - Open price
			-p_volume - Daily Volume
			-p_shares_outstanding - Shares Outstanding
        
        
        
        -[cache_name]_corp_actions.snappy: This file will contain cumulative
		            adjustment factors. 
			-price_date: Change date of either factor
			-cum_split_factor - Cumulative split factor
			-cum_spin_factor: Cumulative spin-off factor
        
        """
        __valid_cache_name__(cache_name)

        dsn = mssql_dsn
        etf = etf_ticker.upper()
        sd = start_date
        ed = end_date
        fname = os.path.join(self.dir_path, "fdsDataStore", cache_name)

        #####################################
        ## Check for data directory
        #####################################
        if not os.path.exists(os.path.join(self.dir_path, "fdsDataStore")):
            print(
                "Creating for fdsDataStore directory to store files in {}.\n\n\n".format(
                    self.dir_path
                )
            )
            os.makedirs(os.path.join(self.dir_path, "fdsDataStore"))
        else:
            pass

            df = FdsDataStoreLedger(self.dir_path).avail_caches()

            if type(df) == type(None):
                pass
            elif cache_name in df.index.get_level_values(0).tolist():
                print(
                    """This cache name is already in use!
                         Please select a new name, use rebuild_cache to refresh,
                         or delete_cache to remove."""
                )
                raise IpyExit

        connection = pyodbc.connect("DSN={}".format(mssql_dsn))

        #####################################
        ## Step 1: Universe Creation
        #####################################

        print(
            "Downloading ETF Constituents for {t} from {s} to {e}".format(
                t=etf_ticker, s=start_date, e=end_date
            )
        )

        univ = fd.etf_universe(
            etf_ticker=etf_ticker,
            start_date=start_date,
            end_date=ed,
            mssql_dsn=mssql_dsn,
        )

        self.__get_data__(cache_name, univ, mssql_dsn, currency, sd, fname, 0)
        FdsDataStoreLedger(dir_path=self.dir_path).cache_ledger(
            cache_name,
            "FDS Ownership",
            mssql_dsn,
            currency,
            etf_ticker,
            start_date,
            end_date,
        )

        return True

    def load_universe(self, data, cache_name, mssql_dsn, currency, start_date):
        """
        This function requires the following inputs:
        
        -data:  a pandas dataframe containing a time series universe.
              file must include the following headers:
              ref_id:  ISIN, CUSIP, SEDOL, Ticker-Region, or Ticker-Exchange. 
                          (Check digits required)
              date:  date in a YYYY-MM-DD format
              
        -cache_name: Unique name to define the collection of cache files
        -mssql_dsn:  DSN name associated with the MSSQL Server where FDS data resides
        -currency: currency for pricing data to be return, if local currency is desired set
                   to "LOCAL"
        -start_date: YYYY-MM-DD date for the start of the universe pull (first available)
                
        The output of this function will be 4 files:
        
        -[cache_name]_univ.snappy: This file will contain a time series
        universe along with FDS symbology.  Fields include:
            -market_id: stored from the input dataframe. 
        
        
        
        -[cache_name]_ref_data.snappy:
        
        
        -[cache_name]_prices.snappy:
        
        
        
        -[cache_name]_corp_actions.snappy:
        
        """

        __valid_cache_name__(cache_name)
        if "date" not in data.columns:
            if "ref_id" not in data.columns:
                print(
                    """Dataframe must have columns labeled "date" and "ref_id".
    See docstring for more details"""
                )
            else:
                print(
                    """Dataframe must have columns labeled "date".
    See docstring for more details"""
                )
            raise IpyExit

        dsn = mssql_dsn
        sd = start_date
        fname = os.path.join(self.dir_path, "fdsDataStore", cache_name)

        #####################################
        ## Check for data directory
        #####################################
        if not os.path.exists("fdsDataStore"):
            print(
                "Creating for fdsDataStore directory to store files in {}\n\n\n.".format(
                    self.dir_path
                )
            )
            os.makedirs("fdsDataStore")
        else:
            pass

            df = FdsDataStoreLedger(self.dir_path).avail_caches()
            fname = os.path.join(self.dir_path, "fdsDataStore", cache_name)
            data.to_parquet(fname + "_imported.snappy")

            if type(df) == type(None):
                pass
            elif cache_name in df.index.get_level_values(0).tolist():
                print(
                    """This cache name is already in use!
                         Please select a new name, use rebuild_cache to refresh,
                         or delete_cache to remove."""
                )
                raise IpyExit

        connection = pyodbc.connect("DSN={}".format(mssql_dsn))

        #####################################
        ## Step 1: Universe Creation
        #####################################

        data["date"] = pd.to_datetime(data["date"], format="%Y-%m-%d")

        self.__get_data__(cache_name, data, mssql_dsn, currency, sd, fname, 1)
        FdsDataStoreLedger(self.dir_path).cache_ledger(
            cache_name, "Imported", mssql_dsn, currency, "", start_date, ""
        )

    def rebuild_cache(self, cache_name):
        df = FdsDataStoreLedger(self.dir_path).avail_caches()
        try:
            fname = os.path.join(self.dir_path, "fdsDataStore", cache_name)
            df = df.loc[cache_name]
        except:
            print("Cache Not Found. Check for available caches with avail_caches.")
            raise IpyExit
        if df["Source"] == "Imported":
            data = pd.read_parquet(fname + "_imported.snappy")
            self.__get_data__(
                cache_name,
                data,
                df["MSSQL DSN"],
                df["Currency"],
                df["Start Date"],
                fname,
                1,
            )
            FdsDataStoreLedger(self.dir_path).cache_ledger(
                cache_name,
                "Imported",
                df["MSSQL DSN"],
                df["Currency"],
                "",
                df["Start Date"],
                "",
            )
        else:
            data = pd.read_parquet(fname + "_univ.snappy").iloc[:, 0:4]
            self.__get_data__(
                cache_name,
                data,
                df["MSSQL DSN"],
                df["Currency"],
                df["Start Date"],
                fname,
                0,
            )
            FdsDataStoreLedger(self.dir_path).cache_ledger(
                cache_name,
                "FDS Ownership",
                df["MSSQL DSN"],
                df["Currency"],
                df["ETF Ticker"],
                df["Start Date"],
                df["End Date"],
            )

        print("Cache Rebuilt.")
        return True

