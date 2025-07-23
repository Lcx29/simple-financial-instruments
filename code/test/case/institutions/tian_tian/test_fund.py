#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcx29

@Software:  PyCharm

@File    :  test_fund.py

@Time    :  2025-07-23 11:30:04

@Desc    :  天天基金数据查询测试类
"""
import unittest

from institutions.tian_tian.fund import TianTianFundHandler, TianTianFundParam


class TestTianTianFundHandler(unittest.TestCase):
    """
    天天基金处理测试类
    """

    def test_fetch_fund_data(self):
        request_tian_tian_fund_param = TianTianFundParam("018124", "2025-07-20", "2025-07-25")
        test_tian_tian_handler = TianTianFundHandler(request_tian_tian_fund_param)
        tian_tian_fund_data = test_tian_tian_handler.fetch_fund_data()
        self.assertIsNotNone(tian_tian_fund_data)
        print(tian_tian_fund_data)
