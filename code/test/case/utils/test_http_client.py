#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcx29

@Software:  PyCharm

@File    :  test_http_client.py

@Time    :  2025-07-22 14:46:10

@Desc    :  utils.http_client 测试类
"""

import unittest

from utils.http_client import HttpClient


class TestHttpClient(unittest.TestCase):
    def setUp(self):
        self.client = HttpClient()

    def test_get_request(self):
        print("test get method")
        response = self.client.get("https://www.baidu.com")
        self.assertIsNotNone(response)
        print(response.data)

    def test_post_request(self):
        print("test post method")
        response = self.client.post("https://httpbin.org/post", data={"key": "value"})
        self.assertIsNotNone(response)
        print(response.data)
