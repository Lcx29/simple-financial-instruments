#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcn29
@Software:  PyCharm
@File    :  report.py
@Time    :  2025-08-22
@Desc    :  报表领域模型
"""

from decimal import Decimal
from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime

from domain.models.portfolio import ProfitLossInfo, AssetTypeSummary
from domain.enums.asset_type import AssetType


@dataclass
class ProfitLossReport:
    """盈亏分析报表。
    
    包含完整的投资组合盈亏分析结果，包括各资产类型的详细信息和汇总数据。
    
    Attributes:
        generated_at: 报表生成时间
        asset_type_summaries: 各资产类型的汇总信息列表
        total_profit_loss_rmb: 总盈亏金额（人民币）
    """
    
    generated_at: datetime
    asset_type_summaries: List[AssetTypeSummary]
    total_profit_loss_rmb: Decimal
    
    def get_summary_by_type(self, asset_type: AssetType) -> AssetTypeSummary:
        """根据资产类型获取汇总信息。
        
        Args:
            asset_type: 资产类型枚举
            
        Returns:
            对应资产类型的汇总信息
            
        Raises:
            ValueError: 当找不到指定资产类型的汇总信息时抛出异常
        """
        for summary in self.asset_type_summaries:
            if summary.asset_type == asset_type:
                return summary
        raise ValueError(f"No summary found for asset type: {asset_type}")
    
    def has_profit(self) -> bool:
        """判断整体投资组合是否盈利。
        
        Returns:
            True表示整体盈利，False表示亏损或持平
        """
        return self.total_profit_loss_rmb > 0
    
    def has_loss(self) -> bool:
        """判断整体投资组合是否亏损。
        
        Returns:
            True表示整体亏损，False表示盈利或持平
        """
        return self.total_profit_loss_rmb < 0
    
    def get_profitable_asset_types(self) -> List[AssetType]:
        """获取盈利的资产类型列表。
        
        Returns:
            盈利的资产类型列表
        """
        return [summary.asset_type for summary in self.asset_type_summaries 
                if summary.total_profit_loss_rmb > 0]
    
    def get_loss_asset_types(self) -> List[AssetType]:
        """获取亏损的资产类型列表。
        
        Returns:
            亏损的资产类型列表
        """
        return [summary.asset_type for summary in self.asset_type_summaries 
                if summary.total_profit_loss_rmb < 0]