#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcx29

@Software:  PyCharm

@File    :  http_client.py

@Time    :  2025-07-21 15:33:20

@Desc    :  基与 requests 封装的 HTTP 客户端
"""
from enum import Enum
from typing import Any, Dict

import requests
from requests import Timeout, HTTPError


class HttpResponseCode(Enum):
    SUCCESS = 200
    FAILED = 400
    UNKNOWN_ERROR = 500


class HttpResponse:

    def __init__(self, status_code: int, data: Any):
        self._status_code = status_code
        self._data = data

    def is_success(self) -> bool:
        return self._status_code == HttpResponseCode.SUCCESS.value

    @property
    def data(self) -> Any:
        return self._data

    @property
    def status_code(self) -> int:
        return self._status_code


class HttpClient:

    def get(self, url: str, params: Dict[str, Any] = None, **kwargs: Dict[str, Any]) -> HttpResponse:
        return self._request("get", url, params=params, **kwargs)

    def post(self, url: str, data: Dict[str, Any] = None, body: Dict[str, Any] = None,
             **kwargs: Dict[str, Any]) -> HttpResponse:
        return self._request("post", url, data=data, json=body, **kwargs)

    @staticmethod
    def _request(method, url, **kwargs) -> HttpResponse:
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return HttpResponse(HttpResponseCode.SUCCESS.value, response.content.decode("utf-8"))
        except ConnectionError as e:
            return HttpResponse(HttpResponseCode.FAILED.value, {"error: ": "Connection error: " + str(e)})
        except Timeout as e:
            return HttpResponse(HttpResponseCode.FAILED.value, {"error: ": "Timeout error: " + str(e)})
        except HTTPError as e:
            return HttpResponse(HttpResponseCode.FAILED.value, {"error: ": "HTTP error: " + str(e)})
        except Exception as e:
            return HttpResponse(HttpResponseCode.UNKNOWN_ERROR.value, {"error: ": "Unknown error: " + str(e)})
