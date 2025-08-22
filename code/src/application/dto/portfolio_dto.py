#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcn29
@Software:  PyCharm
@File    :  portfolio_dto.py
@Time    :  2025-08-22
@Desc    :  投资组合数据传输对象
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from decimal import Decimal


@dataclass
class AssetDTO:
    """资产数据传输对象"""
    name: str
    asset_type: str
    currency: str
    current_balance: float
    previous_balance: float
    profit_loss: float


@dataclass
class PortfolioSummaryDTO:
    """投资组合概要数据传输对象"""
    total_assets: int
    asset_types_count: int
    asset_type_breakdown: Dict[str, int]


@dataclass
class ProfitLossDetailDTO:
    """盈亏详情数据传输对象"""
    name: str
    currency: str
    last_month_balance: float
    profit_loss_rmb: float


@dataclass
class AssetTypeSummaryDTO:
    """资产类型汇总数据传输对象"""
    type_name: str
    type_code: str
    total_profit_loss_rmb: float
    details: List[ProfitLossDetailDTO]


@dataclass
class ProfitLossReportDTO:
    """盈亏报表数据传输对象"""
    generated_at: str
    total_profit_loss_rmb: float
    has_profit: bool
    has_loss: bool
    profitable_asset_types: List[str]
    loss_asset_types: List[str]
    asset_type_summaries: List[AssetTypeSummaryDTO]


@dataclass
class AnalysisResultDTO:
    """分析结果数据传输对象"""
    success: bool
    portfolio_summary: Optional[PortfolioSummaryDTO]
    report_text: Optional[str]
    report_data: Optional[ProfitLossReportDTO]
    error: Optional[str]


@dataclass
class TemplateGenerationResultDTO:
    """模板生成结果数据传输对象"""
    success: bool
    template_data: Optional[Dict[str, List[Dict[str, Any]]]]
    statistics: Optional[PortfolioSummaryDTO]
    error: Optional[str]