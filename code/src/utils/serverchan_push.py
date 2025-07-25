#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcx29

@Software:  PyCharm

@File    :  serverchan_push.py

@Time    :  2025-07-25 10:26:36

@Desc    :  基与 ServerChan 的推送工具 (https://sct.ftqq.com/)
"""
from typing import Any
from loguru import logger
from serverchan_sdk import sc_send


class ServerChanPushParam:

    def __init__(self, title: str, content: str, options: dict[str, Any] = None):
        self._title = title
        self._content = content
        self._options = options

    @property
    def title(self) -> str:
        return self._title

    @property
    def content(self) -> str:
        return self._content

    @property
    def options(self) -> dict[str, Any]:
        return self._options


class ServerChanPush:

    def __init__(self, send_key: str):
        self._send_key = send_key

    def push(self, send_param: ServerChanPushParam) -> None:
        """
        发送推送消息
        :param send_param: 推送参数
        """

        try:
            response = sc_send(
                sendkey=self._send_key,
                title=send_param.title,
                desp=send_param.content,
                options={} if send_param.options is None else send_param.options
            )
            logger.info(f"server chan response is {response}")
            if response.get("code") != 0:
                raise ValueError(f"ServerChan push failed: {response.get('message', 'Unknown error')}")
            print(f"ServerChan push success: {response.get('message', 'No message')}")
        except Exception as exception:
            raise RuntimeError(f"ServerChan push failed: {str(exception)}") from exception


if __name__ == '__main__':
    push = ServerChanPush(send_key="SCT251954TODBC150trJRSiZOBE9kYzv5J")
    param = ServerChanPushParam(title="Test Title", content="This is a test content.")
    push.push(param)
