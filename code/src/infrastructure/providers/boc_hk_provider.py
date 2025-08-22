#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcn29
@Software:  PyCharm
@File    :  boc_hk_provider.py
@Time    :  2025-08-22
@Desc    :  中银香港汇率数据提供者
"""

from decimal import Decimal
from typing import List, Dict

import bs4
from bs4.element import Tag
from loguru import logger

from domain.enums.money_code import MoneyCode
from utils.http_client import HttpClient, HttpResponse


class BocHkExchangeRateProvider:
    """中银香港汇率数据提供者"""
    
    def __init__(self):
        self._http_client = HttpClient()
    
    def fetch_all_rates(self) -> Dict[str, Decimal]:
        """获取所有汇率"""
        hkd_base_rates = self._fetch_hkd_base_rates()
        usd_base_rates = self._fetch_usd_base_rates()
        
        all_rates = {**hkd_base_rates, **usd_base_rates}
        logger.info(f"Fetched {len(all_rates)} exchange rates from BOC HK")
        return all_rates
    
    def _fetch_hkd_base_rates(self) -> Dict[str, Decimal]:
        """获取以港币为基础的汇率"""
        rates = {}
        
        # 港币到人民币
        hkd_to_cny = self._fetch_real_time_rate(MoneyCode.HKD, MoneyCode.CNY)
        cny_to_hkd = self._fetch_real_time_rate(MoneyCode.CNY, MoneyCode.HKD)
        
        # 港币到美元
        hkd_to_usd = self._fetch_real_time_rate(MoneyCode.HKD, MoneyCode.USD)
        usd_to_hkd = self._fetch_real_time_rate(MoneyCode.USD, MoneyCode.HKD)
        
        rates.update({
            self._make_rate_key(MoneyCode.HKD, MoneyCode.CNY): Decimal(hkd_to_cny),
            self._make_rate_key(MoneyCode.CNY, MoneyCode.HKD): Decimal(cny_to_hkd),
            self._make_rate_key(MoneyCode.HKD, MoneyCode.USD): Decimal(hkd_to_usd),
            self._make_rate_key(MoneyCode.USD, MoneyCode.HKD): Decimal(usd_to_hkd),
        })
        
        return rates
    
    def _fetch_usd_base_rates(self) -> Dict[str, Decimal]:
        """获取以美元为基础的汇率"""
        url = "https://www.bochk.com/whk/rates/exchangeRatesUSD/exchangeRatesUSD-input.action?lang=en"
        response = self._http_client.get(url)
        
        rate_tr_list = self._parse_response(response)
        usd_cny_rate = self._search_rate(rate_tr_list, 'USD/CNH')
        
        if not usd_cny_rate:
            raise Exception("Failed to fetch USD/CNY exchange rate")
        
        # 美元到人民币的汇率
        usd_to_cny_rate = Decimal(usd_cny_rate['sell'])
        # 人民币到美元的汇率需要倒数
        cny_to_usd_rate = Decimal("1") / Decimal(usd_cny_rate['buy'])
        
        return {
            self._make_rate_key(MoneyCode.USD, MoneyCode.CNY): usd_to_cny_rate,
            self._make_rate_key(MoneyCode.CNY, MoneyCode.USD): cny_to_usd_rate,
        }
    
    def _fetch_real_time_rate(self, from_code: MoneyCode, to_code: MoneyCode) -> str:
        """获取实时汇率"""
        form_data = {
            "bean.rateType": 1,
            "bean.depCurrency": "RMB" if from_code == MoneyCode.CNY else from_code.value,
            "bean.withdrCurrency": "RMB" if to_code == MoneyCode.CNY else to_code.value
        }
        
        url = "https://www.bochk.com/whk/calculator/realTimeRate/realTimeRate-getRealTimeRate.action"
        response = self._http_client.post(url, data=form_data, body=None)
        
        if not response.is_success():
            raise Exception(
                f"Failed to fetch real-time rate for {from_code.value} to {to_code.value}: "
                f"status {response.status_code}"
            )
        
        return str(response.data).replace("\"", "")
    
    def _parse_response(self, response: HttpResponse) -> List[Tag]:
        """解析HTTP响应"""
        if not response.is_success():
            raise Exception(
                f"HTTP request failed: status {response.status_code}, "
                f"response: {response.data}"
            )
        
        soup = bs4.BeautifulSoup(response.data, features='lxml')
        rate_tr_list = soup.select("#form-div .import-data tr")
        
        return rate_tr_list or []
    
    def _search_rate(self, rate_tr_list: List[Tag], target_mark: str) -> Dict[str, str]:
        """在汇率表格中搜索特定汇率"""
        for rate_tr in rate_tr_list:
            rate_td_list = rate_tr.select("td")
            for rate_td in rate_td_list:
                td_content = rate_td.text.strip()
                if td_content == target_mark:
                    return {
                        "sell": rate_td_list[1].text.strip(),
                        "buy": rate_td_list[2].text.strip()
                    }
        return {}
    
    def _make_rate_key(self, from_code: MoneyCode, to_code: MoneyCode) -> str:
        """生成汇率键"""
        return f"{from_code.value}->{to_code.value}"