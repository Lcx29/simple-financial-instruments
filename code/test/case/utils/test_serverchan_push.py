#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcx29

@Software:  PyCharm

@File    :  test_serverchan_push.py

@Time    :  2025-07-25 10:51:57

@Desc    :  serverchan_push.py 测试类
"""

import unittest

from utils.serverchan_push import ServerChanPush, ServerChanPushParam


class TestServerChanPush(unittest.TestCase):

    def setUp(self):
        self.send_key = ""

    def test_serverchan_push(self):

        push_service = ServerChanPush(self.send_key)
        send_param = ServerChanPushParam(
            title="Test Push",
            content="This is a test message from the ServerChan push service.",
            options={"url": "https://example.com"}
        )

        try:
            push_service.push(send_param)
            print("ServerChan push test passed.")
        except Exception as e:
            self.fail(f"ServerChan push test failed: {e}")
