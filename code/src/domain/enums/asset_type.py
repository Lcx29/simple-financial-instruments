#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcn29
@Software:  PyCharm
@File    :  asset_type.py
@Time    :  2025-08-03 16:44:07
@Desc    :  财产类型枚举
"""

from enum import Enum


class AssetType(Enum):
    """资产类型枚举"""
    STOCK = ("stock", "股票")
    FUND = ("fund", "基金")
    CONSERVATIVE_WEALTH_MANAGEMENT = ("conservative_wealth_management", "稳健理财")
    BANK_DEPOSIT = ("bank_deposit", "银行存款")
    CASH_EQUIVALENT = ("cash_equivalent", "现金等价物")
    PENSION_FUND = ("pension_fund", "养老金")
    CREDIT_CARD = ("credit_card", "信用卡")

    @property
    def en_name(self) -> str:
        """英文名称"""
        return self.value[0]

    @property
    def cn_name(self) -> str:
        """中文名称"""
        return self.value[1]

    @classmethod
    def convert_from_en_str(cls, asset_en_str: str) -> "AssetType":
        """将字符串财产类型转换为 AssetType 枚举
        
        Args:
            asset_en_str: 资产类型字符串
            
        Returns:
            AssetType: 对应的 AssetType 枚举
            
        Raises:
            ValueError: 当资产类型字符串无效时
        """
        for member in cls:
            if member.en_name == asset_en_str:
                return member
        raise ValueError(f"Invalid AssetType: {asset_en_str}")