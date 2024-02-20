import datetime as dt
import pandas as pd


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
    def _format_specific_amount(fundamental, amount_nm):
        def _filter_specific_amount(fundamental, amount_nm):
            col_except_amount = [col for col in fundamental.columns if col not in ["0", "1", "2"]]
            _fundamental_df = fundamental.loc[:, col_except_amount + [amount_nm]].rename(
                columns={amount_nm: "amount"}
            )
            return _fundamental_df

        _fundamental = _filter_specific_amount(fundamental, amount_nm)
        _fundamental["date"] = _fundamental["date"].apply(
            lambda x: x - dt.timedelta(days=365 * eval(amount_nm))
        )
        _fundamental["reprt_no"] = amount_nm
        return _fundamental

    @staticmethod
    def _rename_columns(fundamental):
        column_rename_dict = {
            "reprt_date": "date",
            "thstrm_amount": "0",
            "frmtrm_amount": "1",
            "bfefrmtrm_amount": "2",
        }
        fundamental = fundamental.rename(columns=column_rename_dict)
        return fundamental

    def __call__(self):
        fundamental = self.fundamental
        fundamental["stock_code"] = fundamental["stock_code"].apply(lambda x: str(x).zfill(6))
        fundamental["factor"] = self._rename_account_nm(fundamental["account_nm"])
        fundamental = self._rename_columns(fundamental)
        fundamental["date"] = pd.to_datetime(fundamental["date"])
        fundamental = pd.concat(
            [self._format_specific_amount(fundamental, str(idx)) for idx in range(3)], axis=0
        )
        fundamental.sort_values("date", inplace=True)
        return fundamental

class OhlcvPreProc:
    def __init__(self, ohlcv) -> None:
        self.ohlcv = ohlcv.copy()

    def get_ma_prices(self, window=32):
        ohlcv = self.ohlcv
        ohlcv = ohlcv.rename(columns={"Close": "price"})
        ohlcv.index.name = "date"

        ohlcv.index = pd.to_datetime(ohlcv.index)
        ohlcv.sort_index(inplace=True)
        price_ma = ohlcv.groupby("stock_code")["price"].rolling(window=window).mean()
        price_ma = price_ma.reset_index().dropna()
        price_ma.sort_values("date", inplace=True)
        return price_ma

class InfoPreproc:
    def __init__(self, info) -> None:
        self.info = info.copy()

    def get_shares(self):
        info = self.info
        info = info.rename(columns={"Code": "stock_code"})
        shares = info.set_index("stock_code")["Stocks"].rename("shares").reset_index()
        return shares


class FaPreProc:
    def __init__(self, fundamental, prices, shares) -> None:
        self.fundamental = fundamental
        self.prices = prices
        self.shares = shares

    @staticmethod
    def _melt_args_to_factor(fundamental):
        fundamental_price_b = fundamental.loc[
            :, ["date", "stock_code", "price", "shares", "reprt_no"]
        ].drop_duplicates()
        fundamental_price_b = fundamental_price_b.melt(
            id_vars=["date", "stock_code", "reprt_no"],
            value_vars=["price", "shares"],
            var_name="factor",
            value_name="amount",
        )
        return fundamental_price_b

    def __call__(self):
        fundamental_price = pd.merge_asof(
            left=self.fundamental,
            right=self.prices,
            by="stock_code",
            on="date",
            direction="nearest",
        )
        fundamental_price_shares = pd.merge(left=fundamental_price, right=self.shares, how="left")
        fundamental_price_shares = fundamental_price_shares.loc[
            :, ["date", "stock_code", "factor", "amount", "price", "shares", "reprt_no"]
        ]
        fundamental_price_shares.dropna(subset=["factor"], inplace=True)
        fundamental_price_a = fundamental_price_shares.loc[
            :, ["date", "stock_code", "factor", "amount", "reprt_no"]
        ]
        fundamental_price_b = self._melt_args_to_factor(fundamental_price_shares)
        fundamental = pd.concat([fundamental_price_a, fundamental_price_b], axis=0)
        return fundamental
