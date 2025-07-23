#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcx29

@Software:  PyCharm

@File    :  test_personal_finance.py

@Time    :  2025-07-23 17:19:11

@Desc    :  personal_finance 测试类
"""
import unittest
from institutions.cmb_china.personal_finance import PersonalFinanceHandler, PersonalFinanceParam


class TestPersonalFinanceHandler(unittest.TestCase):
    """
    招商银行私人理财处理测试类
    """

    def test_fetch_personal_finance_data(self):
        request_personal_finance_param = PersonalFinanceParam(
            product_code="109405A",
            product_name="定期宝: 招银理财嘉裕日开14月持有1号",
            initial_amount=1000.00,
            available_shares=968.77
        )
        test_personal_finance_handler = PersonalFinanceHandler(request_personal_finance_param)
        personal_finance_data = test_personal_finance_handler.fetch_personal_finance_data()
        self.assertIsNotNone(personal_finance_data)
        print(personal_finance_data)
