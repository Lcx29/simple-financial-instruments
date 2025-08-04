#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcn29

@Software:  PyCharm

@File    :  asset_inventory.py

@Time    :  2025-08-02 16:49:57

@Desc    :  资产清单工具
"""
from decimal import Decimal
from typing import List, Any

from loguru import logger

from institutions.asset_type import AssetType
from institutions.boc_hk.exchange_rate import BocHkExchangeRateHandler, BocHkExchangeRate
from institutions.money_code import MoneyCode
from utils.file_parse import parse_yaml_file, write_yaml_file


class AssetInventory:
    """资产清单工具类"""

    def __init__(self,
                 boc_hk_exchange_rate: BocHkExchangeRate,
                 assert_inventory_config: dict[str, List[dict[str, Any]]]):
        self.boc_hk_exchange_rate = boc_hk_exchange_rate
        self.assert_inventory_config = assert_inventory_config

    def start_handle_asset_inventory(self) -> dict[str, List[dict[str, Any]]]:
        """开始处理资产清单
        Returns:
            dict[str, List[dict[str, Any]]]: 下月资产配置列表
        """

        cal_next_month_asset_config_dict = {}

        for asset_type_en_str in self.assert_inventory_config:
            asset_type = AssetType.covert_from_en_str(asset_type_en_str)
            if asset_type is None:
                logger.error("资产类型 {} 不存在", asset_type_en_str)
                continue
            logger.info("开始计算资产类型: {}", asset_type.cn_name)
            asset_profit_loss_situation_list = self.__calculate_this_month_asset_profit_loss_situation(asset_type,
                                                                                                       self.assert_inventory_config[
                                                                                                           asset_type_en_str])
            self.__calculate_this_month_total_asset_balance(asset_type, asset_profit_loss_situation_list)
            next_month_asset_config_list = self.__rebuild_next_month_asset_config(asset_type,
                                                                                  self.assert_inventory_config[
                                                                                      asset_type_en_str])
            cal_next_month_asset_config_dict[asset_type_en_str] = next_month_asset_config_list

        return cal_next_month_asset_config_dict

    def __calculate_this_month_asset_profit_loss_situation(self, assert_type: AssetType,
                                                           assert_config_list: List[dict[str, Any]]) -> List[
        dict[str, Any]]:
        """计算资产盈亏情况

        Args:
            assert_type: 资产类型枚举
            assert_config_list: 资产配置列表
        Returns:
            List[dict[str, Any]]: 资产盈亏情况
        """

        if not isinstance(assert_config_list, list):
            logger.error("{}资产清单配置文件格式错误", assert_type.cn_name)
            raise ValueError(f"{assert_type.cn_name}资产清单配置文件格式错误")
        if assert_config_list is None or len(assert_config_list) == 0:
            logger.info("当前没有{}资产", assert_type.cn_name)
            return None

        this_month_asset_profit_loss_situation_list = []

        for asset_config in assert_config_list:
            this_month_profit_loss_situation = Decimal(asset_config["current_account_balance"]) - Decimal(
                asset_config["last_month_account_balance"])
            this_month_profit_loss_situation_in_rmb = self.__convert_to_rmb_if_needed(this_month_profit_loss_situation,
                                                                                      asset_config["money_code"])

            this_month_asset_profit_loss_situation_list.append({
                "name": asset_config["name"],
                "money_code": asset_config["money_code"],
                "last_month_account_balance": asset_config["current_account_balance"],
                "this_month_profit_loss_situation_in_rmb": str(round(this_month_profit_loss_situation_in_rmb, 2))
            })

        logger.info("本月{}资产盈亏情况:\n{}", assert_type.cn_name, this_month_asset_profit_loss_situation_list)
        return this_month_asset_profit_loss_situation_list

    def __convert_to_rmb_if_needed(self, account_balance: Decimal, money_code: str) -> Decimal:
        """如果货币代码不是人民币，则将金额转为人民币

        Args:
            account_balance: 金额
            money_code: 货币代码
        Returns:
            Decimal: 如果货币代码是人民币，则返回原汇率，否则返回人民币汇率
        """
        money_code_enum = MoneyCode.covert_from_str(money_code)
        if MoneyCode.CNY == money_code_enum:
            return account_balance
        return self.boc_hk_exchange_rate.exchange_rate_transfer(money_code_enum, MoneyCode.CNY, float(account_balance))

    @staticmethod
    def __calculate_this_month_total_asset_balance(assert_type: AssetType,
                                                   this_month_profit_loss_status_list: List[dict[str, Any]]) -> str:
        """计算资产本月总的盈亏情况

        Args:
            assert_type: 资产类型枚举
            this_month_profit_loss_status_list: 本月资产盈亏情况列表
        Returns:
            Decimal: 列表中的资产的盈亏总余额
        """
        this_month_total_profit_loss_situation_in_rmb = Decimal("0.00")

        for profit_loss_status in this_month_profit_loss_status_list:
            this_month_profit_loss_situation_in_rmb = Decimal(
                str(profit_loss_status["this_month_profit_loss_situation_in_rmb"]))
            this_month_total_profit_loss_situation_in_rmb += this_month_profit_loss_situation_in_rmb

        this_month_total_profit_loss_situation_in_rmb_str = str(round(this_month_total_profit_loss_situation_in_rmb, 2))
        logger.info("本月{}总盈亏情况:{}", assert_type.cn_name, this_month_total_profit_loss_situation_in_rmb_str)
        return this_month_total_profit_loss_situation_in_rmb_str

    @staticmethod
    def __rebuild_next_month_asset_config(assert_type: AssetType, assert_config_list: List[dict[str, Any]]) -> List[
        dict[str, Any]]:
        """重建下月资产配置
        Args:
            assert_type: 资产类型枚举
            assert_config_list: 资产配置列表
        Returns:
            List[dict[str, Any]]: 下月资产配置列表
        """

        if AssetType.CREDIT_CARD == assert_type:
            logger.info("信用卡不需要重建下月配置")
            return assert_config_list

        next_month_asset_config_list = []

        for assert_config in assert_config_list:
            next_month_asset_config_list.append({
                "name": assert_config["name"],
                "money_code": assert_config["money_code"],
                "current_account_balance": float(0.00),
                "last_month_account_balance": assert_config["current_account_balance"]
            })
        return next_month_asset_config_list


if __name__ == '__main__':

    boc_hk_exchange_rate_handler = BocHkExchangeRateHandler()
    boc_hk_exchange_rate = boc_hk_exchange_rate_handler.fetch_exchange_rate()

    # 读取资产清单配置文件
    assert_inventory_config = parse_yaml_file("../../resources/asset_inventory.yaml")

    asset_inventory = AssetInventory(boc_hk_exchange_rate, assert_inventory_config)
    next_month_asset_config_dict = asset_inventory.start_handle_asset_inventory()
    logger.info("{}", next_month_asset_config_dict)

    write_yaml_file("../../resources/next_month_asset_inventory2.yaml", next_month_asset_config_dict)
