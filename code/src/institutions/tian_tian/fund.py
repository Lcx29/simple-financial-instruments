#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcx29

@Software:  PyCharm

@File    :  fund.py

@Time    :  2025-07-23 11:30:04

@Desc    :  天天基金数据查询
"""
from typing import List

from bs4 import BeautifulSoup

from utils.http_client import HttpClient, HttpResponse


class TianTianFundParam:
    """
    天天基金参数类
    """

    def __init__(
        self,
        fund_code: str,
        start_date: str,
        end_date: str,
        data_type: str = "lsjz",
        page: int = 1,
        per: int = 20
    ):
        self._fund_code = fund_code
        self._start_date = start_date
        self._end_date = end_date
        self._data_type = data_type
        self._page = page
        self._per = per

    @property
    def fund_code(self) -> str:
        return self._fund_code

    @property
    def start_date(self) -> str:
        return self._start_date

    @property
    def end_date(self) -> str:
        return self._end_date

    @property
    def data_type(self) -> str:
        return self._data_type

    @property
    def page(self) -> int:
        return self._page

    @property
    def per(self) -> int:
        return self._per


class TianTianFundHandler:
    """
    天天基金处理类
    """

    def __init__(self, tian_tian_fund_param: TianTianFundParam):
        self._tian_tian_fund_param = tian_tian_fund_param

    def fetch_fund_data(self) -> List[dict[str, float]]:
        response = self.__request_fund_data_from_api()
        return self.__parse_response(response)

    def __request_fund_data_from_api(self) -> HttpResponse:
        """
        使用提供的参数从天天基金 API 获取基金数据
        :return: 包含基金数据的字典
        """

        url = (f"http://fund.eastmoney.com/f10/F10DataApi.aspx?"
               f"type={self._tian_tian_fund_param.data_type}"
               f"&code={self._tian_tian_fund_param.fund_code}"
               f"&sdate={self._tian_tian_fund_param.start_date}"
               f"&edate={self._tian_tian_fund_param.end_date}"
               f"&page={self._tian_tian_fund_param.page}"
               f"&per={self._tian_tian_fund_param.per}")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/92.0.4515.131 Safari/537.36'
        }

        http_client = HttpClient()
        return http_client.get(url, headers=headers)

    @staticmethod
    def __parse_response(http_response: HttpResponse) -> List[dict[str, float]]:
        if not http_response.is_success():
            print(
                f"Failed to fetch tian tian fund data, status code: {http_response.status_code}, response: {http_response.data}")
            raise Exception("Failed to fetch tian tian fund data")

        soup = BeautifulSoup(http_response.data, 'html.parser')
        table_rows = soup.find_all("tr")
        responses = []

        for row in table_rows[1:]:
            try:
                columns = row.find_all("td")
                if len(columns) < 2:
                    # Skip rows with insufficient data
                    continue

                date = columns[0].text.strip()
                net_asset_value = float(columns[1].text.strip())
                responses.append({
                    "date": date,
                    "net_asset_value": net_asset_value
                })
            except (IndexError, ValueError) as e:
                print(f"Error parsing row: {row}, {e}")
        return responses
