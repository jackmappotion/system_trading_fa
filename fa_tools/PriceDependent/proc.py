import numpy as np
import pandas as pd


class FundamentalProc:
    def __init__(self, fundamental: pd.DataFrame) -> None:
        self.fundamental = fundamental

    @staticmethod
    def _filter(fundamental: pd.DataFrame, reprt_no: str) -> pd.DataFrame:
        filtered_fundamental = fundamental[fundamental["reprt_no"] == reprt_no].copy()
        return filtered_fundamental

    @staticmethod
    def _preproc(fundamental: pd.DataFrame) -> pd.DataFrame:
        fundamental = fundamental.pivot(index=["stock_code"], columns=["factor"], values=["amount"])
        fundamental.columns = fundamental.columns.get_level_values(1)
        fundamental = fundamental.replace(0, np.NaN)
        return fundamental

    @staticmethod
    def _proc(fundamental) -> pd.DataFrame:
        # current related
        fundamental["CBPS"] = (
            fundamental["current_assets"] - fundamental["current_liabilities"]
        ) / fundamental["shares"]

        fundamental["CPBR"] = fundamental["price"] / fundamental["CBPS"]

        fundamental["C_debt_ratio"] = (
            fundamental["current_liabilities"] / fundamental["current_assets"]
        )

        # Total Related

        fundamental["TBPS"] = (
            fundamental["total_assets"] - fundamental["total_liabilities"]
        ) / fundamental["shares"]

        fundamental["TPBR"] = fundamental["price"] / fundamental["TBPS"]

        fundamental["T_debt_ratio"] = fundamental["total_liabilities"] / fundamental["total_assets"]

        # Profit Related
        fundamental["operation_expense"] = (
            fundamental["raw_profit"] - fundamental["operation_profit"]
        )
        fundamental["operation_profit_ratio"] = (
            fundamental["operation_profit"] / fundamental["raw_profit"]
        )

        fundamental["total_expense"] = fundamental["raw_profit"] - fundamental["net_profit"]
        fundamental["net_profit_ratio"] = fundamental["net_profit"] / fundamental["raw_profit"]

        # Etcs
        fundamental["Liquidity"] = fundamental["current_assets"] / fundamental["total_assets"]
        return fundamental

    @staticmethod
    def _postproc(fundamental) -> pd.DataFrame:
        using_columns = [
            "CBPS",
            "CPBR",
            "C_debt_ratio",
            "TBPS",
            "TPBR",
            "T_debt_ratio",
            "operation_expense",
            "operation_profit_ratio",
            "total_expense",
            "net_profit_ratio",
            "Liquidity",
            "price",
            "net_profit",
        ]
        fundamental = fundamental.loc[:, using_columns]
        return fundamental

    def __call__(self, reprt_no: str) -> pd.DataFrame:
        fundamental = self._filter(self.fundamental, reprt_no)
        fundamental = self._preproc(fundamental)
        fundamental = self._proc(fundamental)
        fundamental = self._postproc(fundamental)
        return fundamental
