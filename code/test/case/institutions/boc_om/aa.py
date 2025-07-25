#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcx29

@Software:  PyCharm

@File    :  aa.py

@Time    :  2025-07-25 15:54:36

@Desc    :  TODO
"""
from utils.http_client import HttpClient
import certifi

if __name__ == '__main__':
    HttpClient = HttpClient()

    header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Referer": "https://www.bocommwm.com/BankCommSite/jylc/cn/zhexian.html?proCode=5811224061&&c_productcode=undefined",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": "https://www.bocommwm.com"
    }

    data = {
        "REQ_MESSAGE": "{\"REQ_HEAD\":{\"TRAN_PROCESS\":\"\",\"TRAN_ID\":\"\"},\"REQ_BODY\":{\"c_fundcode\":\"5811224061\",\"c_interestway\":\"0\",\"c_productcode\":\"undefined\",\"type\":\"month\"}}"
    }

    print(HttpClient.post(url="https://www.bocommwm.com/SITE/queryJylcBreakDetail.do", data=data, body=None,
                          headers=header, verify=certifi.where()))

    # print(HttpClient.post("https://www.bocommwm.com/SITE/queryJylcBreakDetail.do", data, headers=header))
