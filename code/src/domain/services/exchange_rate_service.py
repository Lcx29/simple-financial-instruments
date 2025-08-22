#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcn29
@Software:  PyCharm
@File    :  exchange_rate_service.py
@Time    :  2025-08-22
@Desc    :  汇率服务接口
"""

from abc import ABC, abstractmethod
from decimal import Decimal

from domain.enums.money_code import MoneyCode


class ExchangeRateService(ABC):
    """汇率服务接口。
    
    定义汇率转换相关操作的抽象接口，支持多种汇率数据源的实现。
    """
    
    @abstractmethod
    def convert(self, from_currency: MoneyCode, to_currency: MoneyCode, 
               amount: Decimal) -> Decimal:
        """执行货币汇率转换。
        
        将指定金额从源货币转换为目标货币。
        
        Args:
            from_currency: 源货币类型
            to_currency: 目标货币类型
            amount: 需要转换的金额
            
        Returns:
            转换后的金额
            
        Raises:
            ExchangeRateError: 当汇率转换失败时抛出异常
        """
        pass
    
    @abstractmethod
    def get_exchange_rate(self, from_currency: MoneyCode, 
                         to_currency: MoneyCode) -> Decimal:
        """获取两种货币之间的汇率。
        
        Args:
            from_currency: 源货币类型
            to_currency: 目标货币类型
            
        Returns:
            汇率值，表示1单位源货币等于多少目标货币
            
        Raises:
            ExchangeRateError: 当获取汇率失败时抛出异常
        """
        pass
    
    @abstractmethod
    def is_supported_currency_pair(self, from_currency: MoneyCode, 
                                  to_currency: MoneyCode) -> bool:
        """检查是否支持指定的货币对转换。
        
        Args:
            from_currency: 源货币类型
            to_currency: 目标货币类型
            
        Returns:
            True表示支持该货币对的转换，False表示不支持
        """
        pass


class ExchangeRateError(Exception):
    """汇率服务相关异常。
    
    用于表示汇率获取、转换等操作中发生的错误。
    
    Attributes:
        message: 错误消息
        from_currency: 源货币类型（可选）
        to_currency: 目标货币类型（可选）
    """
    
    def __init__(self, message: str, from_currency: MoneyCode = None, 
                 to_currency: MoneyCode = None):
        """初始化汇率异常。
        
        Args:
            message: 错误消息
            from_currency: 源货币类型，可选
            to_currency: 目标货币类型，可选
        """
        super().__init__(message)
        self.from_currency = from_currency
        self.to_currency = to_currency
        self.message = message
    
    def __str__(self) -> str:
        if self.from_currency and self.to_currency:
            return (f"ExchangeRateError: {self.message} "
                   f"({self.from_currency.value} -> {self.to_currency.value})")
        return f"ExchangeRateError: {self.message}"