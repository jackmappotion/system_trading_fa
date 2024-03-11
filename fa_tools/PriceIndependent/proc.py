import numpy as np
import pandas as pd
from typing import List, Tuple, Callable

from .utils import *


class FundamentalProc:
    def __init__(self, factor_df: pd.DataFrame, stock_code: str) -> None:
        self.factor_df = self._filter_factor_df(factor_df, stock_code)

    @staticmethod
    def _filter_factor_df(factor_df: pd.DataFrame, stock_code: str) -> pd.DataFrame:
        filtered_factor_df = factor_df[factor_df["stock_code"] == stock_code].copy()
        return filtered_factor_df

    @staticmethod
    def get_factor_dict(factor_df: pd.DataFrame, arg: str) -> pd.DataFrame:
        """
        arg : ['first','second','third']
        """
        _factor_df = factor_df[factor_df["variable"] == arg]
        factor_dict = _factor_df.set_index("factor")["value"].to_dict()
        return factor_dict

    @staticmethod
    def append_factors(factor_dict: dict) -> dict:
        factor_dict["ALR"] = get_alr(factor_dict)

        factor_dict["CDR"] = get_cdr(factor_dict)
        factor_dict["TDR"] = get_tdr(factor_dict)

        factor_dict["OPR"] = get_opr(factor_dict)
        factor_dict["NPR"] = get_npr(factor_dict)

        factor_dict["OER"] = get_oer(factor_dict)
        factor_dict["TER"] = get_ter(factor_dict)
        return factor_dict

    def __call__(self) -> pd.DataFrame:
        factor_df = self.factor_df

        first_factor_dict = self.get_factor_dict(factor_df, "first")
        first_factor_dict = self.append_factors(first_factor_dict)

        second_factor_dict = self.get_factor_dict(factor_df, "second")
        second_factor_dict = self.append_factors(second_factor_dict)

        third_factor_dict = self.get_factor_dict(factor_df, "third")
        third_factor_dict = self.append_factors(third_factor_dict)
        df = pd.DataFrame(
            [first_factor_dict, second_factor_dict, third_factor_dict],
            index=["first", "second", "third"],
        ).T
        return df


class FundamentalController:
    def __init__(self, factor_analysis_df: pd.DataFrame) -> None:
        self.factor_analysis_df = factor_analysis_df.copy()

    def _get_filtered_stocks(self, factor: str, condition: Callable):
        factor_analysis_df = self.factor_analysis_df

        _factor_analysis_df = factor_analysis_df[factor_analysis_df["factor"] == factor]
        _factor_analysis_gb = _factor_analysis_df.groupby("stock_code")

        result = _factor_analysis_gb.apply(condition)
        filtered_stocks = set(self._get_stocks_from_result(result))
        return filtered_stocks

    def get_filtered_stocks(self, factor_conditions: List[Tuple[str, Callable]]):
        filtered_stocks_list = list()
        for factor, condition in factor_conditions:
            filtered_stocks_list.append(self._get_filtered_stocks(factor, condition))
        return set.intersection(*filtered_stocks_list)

    @staticmethod
    def _get_stocks_from_result(result: pd.DataFrame) -> np.array:
        filtered_stocks = result[result == True].reset_index()["stock_code"].to_numpy()
        return filtered_stocks
