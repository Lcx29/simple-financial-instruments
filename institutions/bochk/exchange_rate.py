#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :   lcn29

@Software:   PyCharm

@File    :   exchange_rate.py

@Time    :   2025-07-20 17:01:17

@Desc    : BOC HK 汇率计算工具
"""
import requests
import bs4
import lxml

def request_data_from_network(url):
    try:
        response = requests.Session().request(method= "get".upper(),url=url)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        print(f"Error occurred: {e}")
        return None


def hkd_base_currency():
    response = request_data_from_network( "https://www.bochk.com/whk/rates/exchangeRatesForCurrency/exchangeRatesForCurrency-input.action?lang=en")
    # 为了使用这个 需要安装 lxml 库
    soup = bs4.BeautifulSoup(response.text, features='lxml')

    tr_list = soup.select("#form-div .import-data tr")

    for tr in tr_list:
        if not tr:
            continue
        tb_list = tr.select("td")
        if not tb_list:
            continue
        for tb in tb_list:
            tb_content = tb.text.strip()
            if tb_content == "CNY":
                print(tb.text.strip())
                continue
            if tb_content == "USD":
                print(tb.text.strip())
                continue

def usd_base_currency():
    response = request_data_from_network( "https://www.bochk.com/whk/rates/exchangeRatesUSD/exchangeRatesUSD-input.action?lang=en")
    soup = bs4.BeautifulSoup(response.text, features='lxml')

    tr_list = soup.select("#form-div .import-data tr")

    for tr in tr_list:
        if not tr:
            continue
        tb_list = tr.select("td")
        if not tb_list:
            continue
        for tb in tb_list:
            tb_content = tb.text.strip()
            if tb_content == "USD/CNH":
                print(tb.text.strip())
                continue
            if tb_content == "USD/HKD":
                print(tb.text.strip())
                continue

if __name__ == '__main__':
    hkd_base_currency()
    #usd_base_currency()


