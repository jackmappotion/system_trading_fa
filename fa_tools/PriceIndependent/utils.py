"""
Mapping Tools
    - General Fundamental factor calcuating
"""

import pandas as pd
from functools import wraps


def except_return_zero(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ZeroDivisionError:
            return 0

    return wrapper


@except_return_zero
def get_alr(factor_dict: dict) -> float:
    """
    ALR : Asset Liquidity Ratio
    """
    asset_liquidity_ratio = factor_dict["current_assets"] / factor_dict["total_assets"]
    return asset_liquidity_ratio


@except_return_zero
def get_cdr(factor_dict: dict) -> float:
    """
    CAR : Current Debt Ratio
    """
    current_debt_ratio = factor_dict["current_liabilities"] / factor_dict["current_assets"]
    return current_debt_ratio


@except_return_zero
def get_tdr(factor_dict: dict) -> float:
    """
    TDR : Total Debt Ratio
    """
    total_debt_ratio = factor_dict["current_liabilities"] / factor_dict["current_assets"]
    return total_debt_ratio


@except_return_zero
def get_opr(factor_dict: dict) -> float:
    """
    OPR : Operation Profit Ratio
    """

    operation_profit_ratio = factor_dict["operation_profit"] / factor_dict["raw_profit"]
    return operation_profit_ratio


@except_return_zero
def get_npr(factor_dict: dict) -> float:
    """
    NPR : Net Profit Ratio
    """
    net_profit_ratio = factor_dict["net_profit"] / factor_dict["raw_profit"]
    return net_profit_ratio


@except_return_zero
def get_oer(factor_dict: dict) -> float:
    """
    OPR : Operation Expense Ratio
    """
    operation_expense = factor_dict["raw_profit"] - factor_dict["operation_profit"]
    operation_expense_ratio = operation_expense / factor_dict["raw_profit"]
    return operation_expense_ratio


@except_return_zero
def get_ter(factor_dict: dict) -> float:
    """
    TER : Total Expense Ratio
    """
    total_expense = factor_dict["raw_profit"] - factor_dict["net_profit"]
    total_expense_ratio = total_expense / factor_dict["raw_profit"]
    return total_expense_ratio
