#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcn29
@Software:  PyCharm
@File    :  asset.py
@Time    :  2025-08-22
@Desc    :  资产领域模型
"""

from decimal import Decimal
from dataclasses import dataclass
from typing import Optional

from domain.enums.asset_type import AssetType
from domain.enums.money_code import MoneyCode


@dataclass
class Asset:
    """资产领域模型。
    
    代表用户的单个金融资产，包含资产的基本信息和业务操作。
    
    Attributes:
        name: 资产名称，如"招商银行"、"中信建投"等
        asset_type: 资产类型，如股票、基金、银行存款等
        currency: 资产货币类型，如人民币、美元、港币等
        current_balance: 当前账户余额
        previous_balance: 上月账户余额
    """
    
    name: str
    asset_type: AssetType
    currency: MoneyCode
    current_balance: Decimal
    previous_balance: Decimal
    
    def __post_init__(self):
        """数据类初始化后的验证。
        
        对资产的基本信息进行业务规则验证，确保数据的合法性。
        
        Raises:
            ValueError: 当资产名称为空或余额为负数时抛出异常
        """
        if not self.name or not self.name.strip():
            raise ValueError("Asset name cannot be empty")
        
        if self.current_balance < 0:
            raise ValueError("Current balance cannot be negative")
            
        if self.previous_balance < 0:
            raise ValueError("Previous balance cannot be negative")
    
    def calculate_profit_loss(self) -> Decimal:
        """计算资产的盈亏金额。
        
        通过当前余额减去上月余额来计算盈亏情况。
        
        Returns:
            盈亏金额，正数表示盈利，负数表示亏损，零表示持平
        """
        return self.current_balance - self.previous_balance
    
    def has_profit(self) -> bool:
        """判断资产是否盈利。
        
        Returns:
            True表示资产盈利，False表示亏损或持平
        """
        return self.calculate_profit_loss() > 0
    
    def has_loss(self) -> bool:
        """判断资产是否亏损。
        
        Returns:
            True表示资产亏损，False表示盈利或持平
        """
        return self.calculate_profit_loss() < 0
    
    def is_credit_card(self) -> bool:
        """判断是否为信用卡类型资产。
        
        信用卡资产在处理下月配置时有特殊逻辑。
        
        Returns:
            True表示是信用卡资产，False表示其他类型资产
        """
        return self.asset_type == AssetType.CREDIT_CARD
    
    def prepare_for_next_month(self) -> "Asset":
        """生成下月资产配置。
        
        根据资产类型生成下月的资产配置：
        - 信用卡：保持当前配置不变
        - 其他资产：将当前余额移至上月余额，当前余额清零
        
        Returns:
            下月的资产配置对象
        """
        if self.is_credit_card():
            # 信用卡不需要重建配置
            return Asset(
                name=self.name,
                asset_type=self.asset_type,
                currency=self.currency,
                current_balance=self.current_balance,
                previous_balance=self.previous_balance
            )
        
        # 其他资产将当前余额移到上月余额，当前余额置零
        return Asset(
            name=self.name,
            asset_type=self.asset_type,
            currency=self.currency,
            current_balance=Decimal("0.00"),
            previous_balance=self.current_balance
        )
    
    def __str__(self) -> str:
        return (f"Asset(name={self.name}, type={self.asset_type.cn_name}, "
                f"currency={self.currency.value}, balance={self.current_balance})")
    
    def __repr__(self) -> str:
        return self.__str__()