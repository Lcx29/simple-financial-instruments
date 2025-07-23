#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcx29

@Software:  PyCharm

@File    :  personal_finance.py

@Time    :  2025-07-23 17:12:42

@Desc    :  招商银行私人理财数据查询
"""
from datetime import datetime
from typing import List

import bs4

from utils.http_client import HttpClient, HttpResponse


class PersonalFinanceParam:
    """
    个人金融参数类
    """

    def __init__(self, product_code: str, product_name: str, initial_amount: float, available_shares: float):
        # 基金代码
        self._product_code = product_code
        # 名称
        self._product_name = product_name
        # 初始金额
        self._initial_amount = initial_amount
        # 可用份额
        self._available_shares = available_shares

    @property
    def product_code(self) -> str:
        """
        获取产品代码
        :return:  产品代码
        """
        return self._product_code

    @property
    def product_name(self) -> str:
        """
        获取产品名称
        :return:  产品代码
        """
        return self._product_name

    @property
    def initial_amount(self) -> float:
        """
        获取产品的初始金额
        :return:  产品的初始金额
        """
        return self._initial_amount

    @property
    def available_shares(self) -> float:
        """
        获取产品的可用份额
        :return:  产品的可用份额
        """
        return self._available_shares


class PersonalFinanceHandler:
    """
    招商银行个人金融处理类
    """

    # 常量定义
    URL_TEMPLATE = (f"https://www.cmbchina.com/cfweb/personal/saproductdetail.aspx"
                    f"?saacod=D07&funcod={{code}}"
                    f"&type=prodvalue"
                    f"&PageNo=1"
                    f"#toTarget")

    def __init__(self, personal_finance_param: PersonalFinanceParam, show_row_num: int = 3):
        self._personal_finance_param = personal_finance_param
        self._show_row_num = show_row_num

    def fetch_personal_finance_data(self) -> List[dict[str, float]]:
        """
        获取个人金融数据
        :return 包含金融数据的列表
        """
        response = self.__request_data_from_api()
        return self.__parse_response(response)

    def __request_data_from_api(self) -> HttpResponse:
        """
        向招商银行个人金融API发送请求
        """
        url = self.URL_TEMPLATE.format(code=self._personal_finance_param.product_code)
        return HttpClient().get(url)

    def __parse_response(self, http_response: HttpResponse) -> List[dict[str, float]]:
        """
        解析 HTTP 响应数据
        """
        if not http_response.is_success():
            raise RuntimeError(
                f"Failed to fetch personal finance data, status code: {http_response.status_code}, "
                f"error: {http_response.data}")

        # 使用 BeautifulSoup 解析 HTML
        soup = bs4.BeautifulSoup(http_response.data, 'lxml')

        # 今天日期从第二行开始, 只计算需要的天数的
        start_index = 2
        # 这里有个问题, 招商一页 10 条数据, 可能一页的条数不够, 先这样
        end_index = start_index + self._show_row_num

        results = []
        for i in range(start_index, end_index):
            row_selector = f'#cList .ProductTable tr:nth-child({i}) td'
            row_data = soup.select(row_selector)

            if len(row_data) < 5:  # 检查是否有足够的列
                break

            try:
                results.append({
                    "date": self.convert_date_format(row_data[4].text),
                    "net_asset_value": float(row_data[3].text.strip()),
                })
            except (ValueError, IndexError) as e:
                raise RuntimeError(f"Error parsing row {i}: {e}") from e

        return results

    @staticmethod
    def convert_date_format(date_str: str) -> str:
        """
        将日期从 yyyyMMdd 格式转换为 yyyy-MM-dd 格式
        :param date_str: 原始日期字符串
        :return 转换后的日期字符串
        """

        if not date_str:
            raise ValueError("Date string cannot be empty")

        # 去除字符串中的多余空白字符
        no_whitespace_data_str = date_str.strip()

        try:
            date_obj = datetime.strptime(no_whitespace_data_str, '%Y%m%d')
            return date_obj.strftime('%Y-%m-%d')
        except ValueError as e:
            raise RuntimeError(f"Invalid date format: {date_str}, {e}") from e
