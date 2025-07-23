#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcx29

@Software:  PyCharm

@File    :  test_http_client.py

@Time    :  2025-07-22 14:44:15

@Desc    :  institutions.bochk.exchange_rate 测试类
"""

import unittest

from institutions.bochk.exchange_rate import BocHkExchangeRateHandler, MoneyCode


class TestBocHkExchangeRateHandler(unittest.TestCase):

    def setUp(self):
        self.exchange_rate_handler = BocHkExchangeRateHandler()

    def test_exchange_rate_transfer(self):
        exchange_rate = self.exchange_rate_handler.fetch_exchange_rate()
        self.assertIsNotNone(exchange_rate)
        print(exchange_rate)

        cal_num = 41.64

        print(f"CNY->USD: {exchange_rate.exchange_rate_transfer(MoneyCode.CNY, MoneyCode.USD, cal_num)}")
        print(f"CNY->HKD: {exchange_rate.exchange_rate_transfer(MoneyCode.CNY, MoneyCode.HKD, cal_num)}")

        print(f"HKD->CNY: {exchange_rate.exchange_rate_transfer(MoneyCode.HKD, MoneyCode.CNY, cal_num)}")
        print(f"HKD->USD: {exchange_rate.exchange_rate_transfer(MoneyCode.HKD, MoneyCode.USD, cal_num)}")

        print(f"USD->CNY: {exchange_rate.exchange_rate_transfer(MoneyCode.USD, MoneyCode.CNY, cal_num)}")
        print(f"USD->HKD: {exchange_rate.exchange_rate_transfer(MoneyCode.USD, MoneyCode.HKD, cal_num)}")
