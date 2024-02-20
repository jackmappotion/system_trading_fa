class FundamentalPreProc:
    def __init__(self, fundamental) -> None:
        self.fundamental = fundamental.copy()

    @staticmethod
    def _rename_account_nm(account_nm_series):
        account_rename_dict = {
            "당기순이익": "net_profit",
            "매출액": "raw_profit",
            "영업이익": "operation_profit",
            "자산총계": "total_assets",
            "부채총계": "total_liabilities",
            "비유동자산": "fixed_assets",
            "비유동부채": "fixed_liabilities",
            "유동자산": "current_assets",
            "유동부채": "current_liabilities",
        }
        renamed_series = account_nm_series.map(account_rename_dict)
        return renamed_series

    @staticmethod
    def _rename_columns(fundamental):
        column_rename_dict = {
            "thstrm_amount": "first",
            "frmtrm_amount": "second",
            "bfefrmtrm_amount": "third",
        }
        fundamental = fundamental.rename(columns=column_rename_dict)
        return fundamental

    @staticmethod
    def _slice_columns(fundamental):
        using_columns = [
            "reprt_date",
            "reprt_code",
            "reprt_year",
            "stock_code",
            "factor",
            "first",
            "second",
            "third",
        ]
        fundamental = fundamental.loc[:, using_columns]
        return fundamental

    @staticmethod
    def _filter_size(fundamental):
        fundamental.dropna(axis=0, inplace=True)
        fundamental_gb = fundamental.groupby("stock_code")

        stock_codes = fundamental_gb.size()[
            fundamental_gb.size() == len(set(fundamental["factor"]))
        ].index
        fundamental = fundamental[fundamental["stock_code"].isin(stock_codes)]
        return fundamental

    def __call__(self):
        fundamental = self.fundamental
        fundamental["stock_code"] = fundamental["stock_code"].apply(lambda x: str(x).zfill(6))
        fundamental["factor"] = self._rename_account_nm(fundamental["account_nm"])
        fundamental = self._rename_columns(fundamental)
        fundamental = self._slice_columns(fundamental)
        fundamental = self._filter_size(fundamental)
        return fundamental