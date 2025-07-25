#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcx29

@Software:  PyCharm

@File    :  exchange_rate.py

@Time    :  2025-07-25 09:45:15

@Desc    :  基与 ExchangeRate-API 的汇率计算工具
"""
import json
from decimal import Decimal
from typing import List

from institutions.money_code import MoneyCode
from utils.http_client import HttpClient


class ExchangeRateApiExchangeRate:

    def __init__(self, exchange_rate_dict: dict[str, Decimal]):
        self._exchange_rate_dict = exchange_rate_dict

    def exchange_rate_transfer(self, from_code: MoneyCode, to_code: MoneyCode, amount: float) -> Decimal:
        dict_key = self.dict_key(from_code, to_code)
        current_exchange_rate = self._exchange_rate_dict[dict_key]
        if current_exchange_rate is None:
            raise ValueError(f"Exchange rate not found for {from_code.value} to {to_code.value}")
        if current_exchange_rate <= 0:
            raise ValueError(f"Invalid exchange rate: {current_exchange_rate} for {from_code.value} to {to_code.value}")
        return round(Decimal(str(amount)) * current_exchange_rate, 2)

    def add_new_rate(self, from_code: MoneyCode, to_code: MoneyCode, rate: str) -> None:
        dict_key = self.dict_key(from_code, to_code)
        self._exchange_rate_dict[dict_key] = Decimal(rate)

    @property
    def exchange_rate(self) -> dict[str, Decimal]:
        return self._exchange_rate_dict

    @staticmethod
    def dict_key(from_code: MoneyCode, to_code: MoneyCode) -> str:
        """生成字典键"""
        return f"{from_code.value}->{to_code.value}"

    def __str__(self):
        return f"ExchangeRateApiExchangeRate ==> current exchange rate: {self._exchange_rate_dict})"


class ExchangeRateApiExchangeRateHandler:
    REQUEST_URL = f"https://api.exchangerate-api.com/v4/latest/{{code}}"

    def __init__(self):
        self._http_client = HttpClient()

    def fetch_exchange_rate(self) -> ExchangeRateApiExchangeRate:
        hkd_base_rate_dict = self.__request_money_code_base_rate(MoneyCode.HKD, [MoneyCode.USD, MoneyCode.CNY])
        usd_base_rate_dict = self.__request_money_code_base_rate(MoneyCode.USD, [MoneyCode.HKD, MoneyCode.CNY])
        cny_base_rate_dict = self.__request_money_code_base_rate(MoneyCode.CNY, [MoneyCode.HKD, MoneyCode.USD])

        merged_rate_dict = {**hkd_base_rate_dict, **usd_base_rate_dict, **cny_base_rate_dict}
        exchange_rate_api_exchange_rate = ExchangeRateApiExchangeRate(merged_rate_dict)
        return exchange_rate_api_exchange_rate

    def __request_money_code_base_rate(self,
                                       base_money_code: MoneyCode,
                                       query_money_code: List[MoneyCode]) -> dict[str, Decimal]:
        request_url = self.REQUEST_URL.format(code=base_money_code.value)
        http_response = self._http_client.get(request_url)
        if not http_response.is_success():
            print(
                f"Failed to fetch exchange rate data, status code: {http_response.status_code}, response: {http_response.data}")
            raise Exception("Failed to fetch exchange rate data")

        rate_list_json = json.loads(http_response.data)["rates"]
        rate_dict = {}
        for money_code in query_money_code:
            rate_value = rate_list_json[money_code.value]
            if rate_value is None:
                print(f"Money code {money_code.value} not found in response data")
                continue
            rate_dict[ExchangeRateApiExchangeRate.dict_key(base_money_code, money_code)] = Decimal(
                str(rate_list_json[money_code.value]))
        return rate_dict
