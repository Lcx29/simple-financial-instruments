#!/usr/bin/env python

# -*- encoding: utf-8 -*-

"""
@Author  :  lcn29

@Software:  PyCharm

@File    :  http_client.py

@Time    :  2025-07-20 17:13:20

@Desc    :  一个 Http 客户端，用于向 BOC HK 汇率 API 发送请求并获取响应。
"""

import json
from typing import Optional, Dict, Any, Union
import requests


class HttpClient:
    """通用HTTP客户端封装"""

    def __init__(
        self,
        base_url: str = '',
        default_timeout: float = 10.0,
        default_headers: Optional[Dict[str, str]] = None
    ):
        """
        初始化HTTP客户端

        :param base_url: 基础API地址
        :param default_timeout: 默认超时时间(秒)
        :param default_headers: 默认请求头
        """
        self.base_url = base_url.rstrip('/')
        self.default_timeout = default_timeout
        self.default_headers = default_headers or {'Content-Type': 'application/json'}
        self.session = requests.Session()

    def _send_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Union[Dict[str, Any], bytes, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        发送HTTP请求核心方法

        :return: 包含状态码和响应数据的字典，出错时包含error信息
        """
        # 构造完整URL
        url = f"{self.base_url}/{endpoint.lstrip('/')}" if self.base_url else endpoint

        # 合并请求头
        merged_headers = {**self.default_headers, **(headers or {})}

        # 设置超时
        timeout = timeout or self.default_timeout

        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                params=params,
                data=data,
                json=json_data,
                headers=merged_headers,
                timeout=timeout,
                **kwargs
            )
            response.raise_for_status()

            # 尝试解析JSON响应，失败则返回文本
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = response.text

            return {
                'status_code': response.status_code,
                'data': response_data
            }

        except requests.RequestException as e:
            # 异常处理
            error_info = self.handle(e)
            # 包含原始异常信息，便于高级调试
            error_info['exception'] = repr(e)
            return error_info

    # 以下是常用HTTP方法封装
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        return self._send_request(
            'GET', endpoint, params=params, headers=headers, timeout=timeout, **kwargs
        )

    def post(
        self,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], bytes, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        return self._send_request(
            'POST', endpoint, data=data, json_data=json_data,
            headers=headers, timeout=timeout, **kwargs
        )

    def put(
        self,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], bytes, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        return self._send_request(
            'PUT', endpoint, data=data, json_data=json_data,
            headers=headers, timeout=timeout, **kwargs
        )

    def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        return self._send_request(
            'DELETE', endpoint, headers=headers, timeout=timeout, **kwargs
        )

    def close(self):
        """关闭会话连接池"""
        self.session.close()

    @staticmethod
    def handle(exception: requests.RequestException) -> Dict[str, Any]:
        """统一处理请求异常"""
        if isinstance(exception, requests.Timeout):
            return {'error': '请求超时', 'details': str(exception)}
        elif isinstance(exception, requests.ConnectionError):
            return {'error': '网络连接错误', 'details': str(exception)}
        elif isinstance(exception, requests.HTTPError):
            return {'error': 'HTTP协议错误', 'details': str(exception)}
        else:
            return {'error': '未知网络错误', 'details': str(exception)}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
