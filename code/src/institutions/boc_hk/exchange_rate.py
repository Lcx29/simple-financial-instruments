#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcn29

@Software:  PyCharm

@File    :  exchange_rate.py

@Time    :  2025-07-20 17:01:17

@Desc    :  基与 BOC HK 汇率计算工具
"""

from decimal import Decimal
from typing import List

import bs4
from bs4.element import Tag
from loguru import logger

from institutions.money_code import MoneyCode
from utils.http_client import HttpClient, HttpResponse


class BocHkExchangeRate:

    def __init__(self, exchange_rate_dict: dict[str, Decimal]):
        self._exchange_rate_dict = exchange_rate_dict

    def exchange_rate_transfer(self, from_code: MoneyCode, to_code: MoneyCode, amount: float) -> Decimal:
        dict_key = self.dict_key(from_code, to_code)
        current_exchange_rate = self._exchange_rate_dict[dict_key]

        if current_exchange_rate is None:
            logger.error(f"Exchange rate not found for {from_code.value} to {to_code.value}")
            raise ValueError(f"Exchange rate not found for {from_code.value} to {to_code.value}")

        if current_exchange_rate <= 0:
            logger.error(f"Exchange rate from {from_code.value} to {to_code.value} is less than 0")
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
        return f"BocHkExchangeRate ==> current exchange rate: {self._exchange_rate_dict})"


class BocHkExchangeRateHandler:

    def __init__(self):
        self.http_client = HttpClient()

    def fetch_exchange_rate(self) -> BocHkExchangeRate:

        hkd_base_rate_dict = self.__request_hkd_base_rate()
        usd_base_rate_dict = self.__request_usd_base_rate()
        merged_rate_dict = {**hkd_base_rate_dict, **usd_base_rate_dict}

        bock_exchange_rate = BocHkExchangeRate(merged_rate_dict)
        return bock_exchange_rate

    def __request_hkd_base_rate(self) -> dict[str, Decimal]:
        # 请求 BOC HK 和 HKD 相关的汇率数据 - 实时
        hkd_to_cny_real_time_rate = Decimal(self.__request_hkd_base_real_time_rate(MoneyCode.HKD, MoneyCode.CNY))
        cny_to_hkd_real_time_rate = Decimal(self.__request_hkd_base_real_time_rate(MoneyCode.CNY, MoneyCode.HKD))

        hkd_to_usd_real_time_rate = Decimal(self.__request_hkd_base_real_time_rate(MoneyCode.HKD, MoneyCode.USD))
        usd_to_hkd_real_time_rate = Decimal(self.__request_hkd_base_real_time_rate(MoneyCode.USD, MoneyCode.HKD))

        return {
            BocHkExchangeRate.dict_key(MoneyCode.HKD, MoneyCode.CNY): hkd_to_cny_real_time_rate,
            BocHkExchangeRate.dict_key(MoneyCode.CNY, MoneyCode.HKD): cny_to_hkd_real_time_rate,
            BocHkExchangeRate.dict_key(MoneyCode.HKD, MoneyCode.USD): hkd_to_usd_real_time_rate,
            BocHkExchangeRate.dict_key(MoneyCode.USD, MoneyCode.HKD): usd_to_hkd_real_time_rate
        }

    def __request_usd_base_rate(self) -> dict[str, Decimal]:

        # 请求 BOC HK 和 USD 相关的汇率数据 - 有延迟
        http_response = self.http_client.get(
            "https://www.bochk.com/whk/rates/exchangeRatesUSD/exchangeRatesUSD-input.action?lang=en")

        rate_tr_list = self.__parse_response(http_response)
        usd_cny_rate = self.__search_rate(rate_tr_list, 'USD/CNH')

        # 因为表格中都是以美元为角度, 卖出美元，买入人民币(卖出 1 美元可以买入多少人民币), 和卖出人民币, 买入美元(卖出 多少人民币可以买入 1 美元)
        # 所以人民币兑美元, 需要将卖出人民币做转换
        cny_to_usd_rate = Decimal("1") / Decimal(usd_cny_rate['buy'])

        return {
            BocHkExchangeRate.dict_key(MoneyCode.CNY, MoneyCode.USD): cny_to_usd_rate,
            BocHkExchangeRate.dict_key(MoneyCode.USD, MoneyCode.CNY): Decimal(usd_cny_rate['sell'])
        }

    def __request_hkd_base_real_time_rate(self, from_code: MoneyCode, to_code: MoneyCode) -> str:
        form_data = {
            "bean.rateType": 1,
            "bean.depCurrency": "RMB" if from_code == MoneyCode.CNY else from_code.value,
            "bean.withdrCurrency": "RMB" if to_code == MoneyCode.CNY else to_code.value
        }

        http_response = self.http_client.post(
            "https://www.bochk.com/whk/calculator/realTimeRate/realTimeRate-getRealTimeRate.action", data=form_data,
            body=None)

        if not http_response.is_success():
            print(
                f"Failed to fetch exchange rate data, status code: {http_response.status_code}, response: {http_response.data}")
            raise Exception("Failed to fetch exchange rate data")
        return str(http_response.data).replace("\"", "")

    def __request_hkd_base_delay_time_rate(self) -> dict[str, Decimal]:
        http_client = HttpClient()
        http_response = http_client.get(
            "https://www.bochk.com/whk/rates/exchangeRatesForCurrency/exchangeRatesForCurrency-input.action?lang=en")

        rate_tr_list = self.__parse_response(http_response)

        hkd_cny_rate = self.__search_rate(rate_tr_list, 'CNY')
        hkd_usd_rate = self.__search_rate(rate_tr_list, 'USD')

        # 因为表格中都是以其他货币为角度, 卖出多少其他货币，买入港币(卖出多少其他货币, 买入 1 港币), 和买入其他货币, 需要卖出多少港币(卖出多少港币可以买入 1 其他货币)
        # 所以港币转其他货币, 需要做一下转换

        hkd_to_cny_rate = Decimal("1") / Decimal(hkd_cny_rate['buy'])
        hkd_to_usd_rate = Decimal("1") / Decimal(hkd_usd_rate['buy'])

        return {
            BocHkExchangeRate.dict_key(MoneyCode.CNY, MoneyCode.HKD): Decimal(hkd_cny_rate['sell']),
            BocHkExchangeRate.dict_key(MoneyCode.HKD, MoneyCode.CNY): hkd_to_cny_rate,
            BocHkExchangeRate.dict_key(MoneyCode.USD, MoneyCode.HKD): Decimal(hkd_usd_rate['sell']),
            BocHkExchangeRate.dict_key(MoneyCode.HKD, MoneyCode.USD): hkd_to_usd_rate
        }

    @staticmethod
    def __parse_response(http_response: HttpResponse) -> List[Tag]:

        if not http_response.is_success():
            print(
                f"Failed to fetch exchange rate data, status code: {http_response.status_code}, response: {http_response.data}")
            raise Exception("Failed to fetch exchange rate data")

        beautiful_soup = bs4.BeautifulSoup(http_response.data, features='lxml')
        rate_tr_list = beautiful_soup.select("#form-div .import-data tr")

        if not rate_tr_list:
            return []
        return rate_tr_list

    @staticmethod
    def __search_rate(rate_tr_list: List[Tag], target_mark: str) -> dict[str, str]:

        for rate_tr in rate_tr_list:
            rate_tb_list = rate_tr.select("td")
            for rate_tb in rate_tb_list:
                tb_content = rate_tb.text.strip()
                if tb_content == target_mark:
                    return {
                        "sell": rate_tb_list[1].text.strip(),
                        "buy": rate_tb_list[2].text.strip()
                    }
        return {}
