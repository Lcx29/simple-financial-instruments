#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcn29
@Software:  PyCharm
@File    :  boc_hk_exchange_rate_service.py
@Time    :  2025-08-22
@Desc    :  中银香港汇率服务实现
"""

from decimal import Decimal
from typing import Dict

from domain.services.exchange_rate_service import ExchangeRateService, ExchangeRateError
from domain.enums.money_code import MoneyCode
from infrastructure.providers.boc_hk_provider import BocHkExchangeRateProvider


class BocHkExchangeRateService(ExchangeRateService):
    """中银香港汇率服务的具体实现。
    
    实现了ExchangeRateService接口，提供基于中银香港的汇率转换服务。
    支持人民币、美元、港币之间的相互转换。
    
    Attributes:
        _provider: 中银香港汇率数据提供者
        _exchange_rates: 缓存的汇率数据字典
    """
    
    def __init__(self, provider: BocHkExchangeRateProvider):
        """初始化中银香港汇率服务。
        
        Args:
            provider: 中银香港汇率数据提供者实例
        """
        self._provider = provider
        self._exchange_rates: Dict[str, Decimal] = {}
        self._load_exchange_rates()
    
    def _load_exchange_rates(self) -> None:
        """从提供者加载最新的汇率数据。
        
        获取并缓存所有支持的货币对汇率。
        
        Raises:
            ExchangeRateError: 当汇率数据加载失败时抛出异常
        """
        try:
            self._exchange_rates = self._provider.fetch_all_rates()
        except Exception as e:
            raise ExchangeRateError(f"Failed to load exchange rates: {str(e)}")
    
    def convert(self, from_currency: MoneyCode, to_currency: MoneyCode, 
               amount: Decimal) -> Decimal:
        """执行货币汇率转换。
        
        将指定金额从源货币转换为目标货币。
        
        Args:
            from_currency: 源货币类型
            to_currency: 目标货币类型
            amount: 需要转换的金额
            
        Returns:
            转换后的金额，四舍五入到小数点后2位
            
        Raises:
            ExchangeRateError: 当汇率转换失败时抛出异常
        """
        if from_currency == to_currency:
            return amount
        
        if not self.is_supported_currency_pair(from_currency, to_currency):
            raise ExchangeRateError(
                f"Unsupported currency pair", from_currency, to_currency
            )
        
        exchange_rate = self.get_exchange_rate(from_currency, to_currency)
        return round(amount * exchange_rate, 2)
    
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
        if from_currency == to_currency:
            return Decimal("1.0")
        
        rate_key = self._make_rate_key(from_currency, to_currency)
        if rate_key not in self._exchange_rates:
            raise ExchangeRateError(
                f"Exchange rate not found", from_currency, to_currency
            )
        
        rate = self._exchange_rates[rate_key]
        if rate <= 0:
            raise ExchangeRateError(
                f"Invalid exchange rate: {rate}", from_currency, to_currency
            )
        
        return rate
    
    def is_supported_currency_pair(self, from_currency: MoneyCode, 
                                  to_currency: MoneyCode) -> bool:
        """检查是否支持指定的货币对转换。
        
        Args:
            from_currency: 源货币类型
            to_currency: 目标货币类型
            
        Returns:
            True表示支持该货币对的转换，False表示不支持
        """
        if from_currency == to_currency:
            return True
        
        rate_key = self._make_rate_key(from_currency, to_currency)
        return rate_key in self._exchange_rates
    
    def refresh_rates(self) -> None:
        """刷新汇率数据。
        
        重新从数据提供者获取最新的汇率信息。
        
        Raises:
            ExchangeRateError: 当汇率数据刷新失败时抛出异常
        """
        self._load_exchange_rates()
    
    def _make_rate_key(self, from_currency: MoneyCode, 
                      to_currency: MoneyCode) -> str:
        """生成汇率字典的键名。
        
        Args:
            from_currency: 源货币类型
            to_currency: 目标货币类型
            
        Returns:
            汇率键名，格式为"源货币->目标货币"
        """
        return f"{from_currency.value}->{to_currency.value}"
    
    def get_available_currencies(self) -> list[MoneyCode]:
        """获取服务支持的所有货币类型。
        
        Returns:
            支持的货币类型列表
        """
        currencies = set()
        for rate_key in self._exchange_rates.keys():
            from_currency, to_currency = rate_key.split("->")
            currencies.add(MoneyCode(from_currency))
            currencies.add(MoneyCode(to_currency))
        return list(currencies)