import os
import pandas as pd

from fds.datax._sdfhelpers._find import FdsDataStoreLedger as ledger
from fds.datax.utils.ipyexit import IpyExit


def __load_file__(cn, dir_path, ft):
    """
    Generic function used to load a feather file from the defined working directory within the instance.
    cn - cache name
    ft - file type, one of the following:
            *_univ.snappy
            *_ref_data.snappy
            *_prices.snappy
            *_corp_actions.snappy
    """
    fname = os.path.join(dir_path, "fdsDataStore", cn + ft)
    return pd.read_parquet(fname)


class FdsReadCache:
    def __init__(self, dir_path):
        self.dir_path = dir_path

    def __cache_check__(self, cache_name, show_details):
        cwd = self.dir_path
        df = ledger(self.dir_path).avail_caches()
        try:
            df = df.loc[cache_name]
            if show_details == 1:
                print("Cache Details:")
                print(df)
                print("\n")
        except:
            print("Cache Not Found. Check for available caches with avail_caches.")
            raise IpyExit

    def load_sym(self, cache_name, show_details):
        self.__cache_check__(cache_name, show_details)
        return __load_file__(cache_name, self.dir_path, "_univ.snappy")

    def load_sec_ref(self, cache_name, show_details):
        self.__cache_check__(cache_name, show_details)
        return __load_file__(cache_name, self.dir_path, "_ref_data.snappy")

    def load_prices(self, cache_name, adj, show_details):
        self.__cache_check__(cache_name, show_details)

        if adj == 0:
            # unadjusted data
            p_type = [
                "ref_id",
                "fsym_id",
                "price_date",
                "currency",
                "market_value",
                "one_day_total_return",
                "unadj_price_close",
                "unadj_price_high",
                "unadj_price_low",
                "unadj_price_open",
                "unadj_volume",
                "unadj_shares_outstanding",
            ]
        elif adj == 1:
            # split adjusted data
            p_type = [
                "ref_id",
                "fsym_id",
                "price_date",
                "currency",
                "market_value",
                "one_day_total_return",
                "split_adj_volume",
                "split_adj_shares_outstanding",
                "split_adj_price_close",
                "split_adj_price_high",
                "split_adj_price_low",
                "split_adj_price_open",
            ]

        elif adj == 2:
            # split and spin-off adjusted
            p_type = [
                "ref_id",
                "fsym_id",
                "price_date",
                "currency",
                "market_value",
                "one_day_total_return",
                "split_adj_volume",
                "split_adj_shares_outstanding",
                "split_spin_adj_price_close",
                "split_spin_adj_price_high",
                "split_spin_adj_price_low",
                "split_spin_adj_price_open",
            ]
        else:
            print("Enter a 0, 1, or 2!  Returning all columns")

        prices = __load_file__(cache_name, self.dir_path, "_prices.snappy")
        prices = prices[p_type]
        prices.columns = [
            col.replace("unadj_", "")
            .replace("split_spin_adj_", "")
            .replace("split_adj_", "")
            for col in prices.columns
        ]
        return prices

    def load_corp_actions(self, cache_name, show_details):
        self.__cache_check__(cache_name, show_details)
        return __load_file__(cache_name, self.dir_path, "_corp_actions.snappy")
