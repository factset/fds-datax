import glob
import os
import pandas as pd

from fds.datax.utils.ipyexit import IpyExit


class FdsDataStoreLedger:
    def __init__(self, dir_path):
        self.dir_path = dir_path

    def __load_cache_details__(self):
        """
        This function will check for available FDS Caches within the
        existing working directory. The full list will be stored in a
        "fds_cache_details.txt" file within an fdsDataStore directory within
        the current working directory. 
        
        """

        cache = os.path.join(self.dir_path, "fdsDataStore", "fds_cache_details.txt")

        if len(glob.glob(cache, recursive=False)) == 0:
            return None
        else:
            caches = pd.read_csv(
                cache,
                sep="|",
                index_col="Cache Name",
                parse_dates=["Start Date", "End Date", "Last Update Date"],
            )
            return caches

    def avail_caches(self):
        """
        Determine if caches exist in the established working directory.
        """
        df = self.__load_cache_details__()

        if type(df) is not type(None):
            return df
        else:
            print(
                "No existing Data Cache Universes exist in this Data Store. Use the fds.datax.Universe.create() function to "
                "generate a new data cache universe."
            )

    def cache_ledger(
        self, cache_name, source, mssql_dsn, currency, etf_ticker, start_date, end_date
    ):
        """
        This function is used to:
        
        -Determine if the fdsDataStore directory exists in the current working dir.
        -Check if a fds_cache_details.txt file exists.
        -Create or update the fds_cache_details with latest information. 
        """

        cols = [
            "Cache Name",
            "Source",
            "Cache Location",
            "MSSQL DSN",
            "ETF Ticker",
            "Currency",
            "Start Date",
            "End Date",
            "Last Update Date",
        ]

        cache = os.path.join(self.dir_path, "fdsDataStore", "fds_cache_details.txt")

        if len(glob.glob(cache, recursive=False)) > 0:
            print("Cache Detail File Found.")
            # cache file exists create, read in cache
            df = pd.read_csv(
                cache,
                sep="|",
                index_col="Cache Name",
                parse_dates=["Start Date", "End Date", "Last Update Date"],
            )

        else:
            # no ledger, create new dataframe:
            print("Cache Detail Not File Found, Creating File.")
            df = pd.DataFrame(columns=cols)
            df.set_index("Cache Name", inplace=True)

        df.loc[cache_name] = [
            source,
            os.path.join(self.dir_path, "fdsDataStore"),
            mssql_dsn,
            etf_ticker,
            currency,
            start_date,
            end_date,
            pd.to_datetime("today"),
        ]
        df.to_csv(cache, sep="|")
        print("Cache Details Saved.")

    def delete_cache(self, cache_name):
        """
        Based on an input cache name, the related components are deleted and wiped from the fds_cache_details.txt file.
        """
        df = self.__load_cache_details__()
        try:
            df.drop(cache_name, inplace=True)
            if len(df) == 0:
                os.remove(
                    os.path.join(self.dir_path, "fdsDataStore", "fds_cache_details.txt")
                )
            else:
                df.to_csv(
                    os.path.join(
                        self.dir_path, "fdsDataStore", "fds_cache_details.txt"
                    ),
                    sep="|",
                )
        except:
            print("Cache Not Found. Check for available caches with avail_caches.")
            raise IpyExit
        filenames = [
            "_univ.snappy",
            "_ref_data.snappy",
            "_prices.snappy",
            "_corp_actions.snappy",
        ]

        for fn in filenames:
            os.remove(os.path.join(self.dir_path, "fdsDataStore", cache_name + fn))

        print("Cache Deleted.")
