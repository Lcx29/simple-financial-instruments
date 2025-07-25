#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcx29

@Software:  PyCharm

@File    :  test_exchange_rate.py

@Time    :  2025-07-25 09:45:15

@Desc    :  基与 ExchangeRate-API 的汇率计算工具测试类
"""
import unittest

from institutions.exchangerate_api.exchange_rate import ExchangeRateApiExchangeRateHandler
from institutions.money_code import MoneyCode


class TestExchangeRateApiExchangeRateHandler(unittest.TestCase):

    def setUp(self):
        self.exchange_rate_handler = ExchangeRateApiExchangeRateHandler()

    def test_exchange_rate_transfer(self):
        exchange_rate = self.exchange_rate_handler.fetch_exchange_rate()
        self.assertIsNotNone(exchange_rate)
        print(exchange_rate)

        cal_num = 12.21

        print(f"CNY->USD: {exchange_rate.exchange_rate_transfer(MoneyCode.CNY, MoneyCode.USD, cal_num)}")
        print(f"CNY->HKD: {exchange_rate.exchange_rate_transfer(MoneyCode.CNY, MoneyCode.HKD, cal_num)}")

        print(f"HKD->CNY: {exchange_rate.exchange_rate_transfer(MoneyCode.HKD, MoneyCode.CNY, cal_num)}")
        print(f"HKD->USD: {exchange_rate.exchange_rate_transfer(MoneyCode.HKD, MoneyCode.USD, cal_num)}")

        print(f"USD->CNY: {exchange_rate.exchange_rate_transfer(MoneyCode.USD, MoneyCode.CNY, cal_num)}")
        print(f"USD->HKD: {exchange_rate.exchange_rate_transfer(MoneyCode.USD, MoneyCode.HKD, cal_num)}")
