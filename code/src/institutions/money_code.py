#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcx29

@Software:  PyCharm

@File    :  money_code.py

@Time    :  2025-07-25 10:09:51

@Desc    :  常用货币代码枚举类
"""
from enum import Enum


class MoneyCode(Enum):
    """货币代码"""
    USD = "USD"  # 美元
    HKD = "HKD"  # 港币
    CNY = "CNY"  # 人民币

    @staticmethod
    def covert_from_str(money_code_str: str) -> "MoneyCode":
        """将字符串货币代码转换为 MoneyCode 枚举

        Args:
            money_code_str: 货币代码字符串
        Returns:
            MoneyCode: 对应的 MoneyCode 枚举
        """
        try:
            return MoneyCode(money_code_str)
        except ValueError as e:
            raise ValueError(f"Invalid MoneyCode: {money_code_str}") from e
