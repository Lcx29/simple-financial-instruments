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
