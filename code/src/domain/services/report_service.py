#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcn29
@Software:  PyCharm
@File    :  report_service.py
@Time    :  2025-08-22
@Desc    :  报表生成服务
"""

from decimal import Decimal
from typing import List, Dict, Any

from loguru import logger

from domain.models.portfolio import Portfolio, AssetTypeSummary
from domain.models.report import ProfitLossReport
from domain.enums.asset_type import AssetType
from domain.services.exchange_rate_service import ExchangeRateService


class ReportService:
    """报表生成服务"""
    
    def __init__(self, exchange_service: ExchangeRateService):
        self._exchange_service = exchange_service
    
    def format_profit_loss_report(self, report: ProfitLossReport) -> str:
        """格式化盈亏报表为可读文本
        
        Args:
            report: 盈亏报表
            
        Returns:
            str: 格式化后的报表文本
        """
        lines = []
        lines.append("=" * 60)
        lines.append(f"资产盈亏分析报表 - {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 60)
        
        for summary in report.asset_type_summaries:
            lines.append(f"\n【{summary.asset_type.cn_name}】")
            lines.append("-" * 40)
            
            for detail in summary.profit_loss_details:
                profit_loss_str = f"¥{detail.profit_loss_amount_rmb:,.2f}"
                if detail.profit_loss_amount_rmb > 0:
                    profit_loss_str = f"+{profit_loss_str}"
                
                lines.append(
                    f"  {detail.name:<20} "
                    f"{detail.money_code.value:<5} "
                    f"盈亏: {profit_loss_str}"
                )
            
            total_str = f"¥{summary.total_profit_loss_rmb:,.2f}"
            if summary.total_profit_loss_rmb > 0:
                total_str = f"+{total_str}"
            
            lines.append(f"  {'小计:':<26} {total_str}")
        
        lines.append("\n" + "=" * 60)
        total_str = f"¥{report.total_profit_loss_rmb:,.2f}"
        if report.total_profit_loss_rmb > 0:
            total_str = f"+{total_str}"
        
        lines.append(f"总计盈亏: {total_str}")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def export_report_to_dict(self, report: ProfitLossReport) -> Dict[str, Any]:
        """将报表导出为字典格式
        
        Args:
            report: 盈亏报表
            
        Returns:
            Dict[str, Any]: 字典格式的报表数据
        """
        export_data = {
            'generated_at': report.generated_at.isoformat(),
            'total_profit_loss_rmb': float(report.total_profit_loss_rmb),
            'summary': {
                'has_profit': report.has_profit(),
                'has_loss': report.has_loss(),
                'profitable_asset_types': [at.cn_name for at in report.get_profitable_asset_types()],
                'loss_asset_types': [at.cn_name for at in report.get_loss_asset_types()],
            },
            'asset_types': []
        }
        
        for summary in report.asset_type_summaries:
            asset_type_data = {
                'type_name': summary.asset_type.cn_name,
                'type_code': summary.asset_type.en_name,
                'total_profit_loss_rmb': float(summary.total_profit_loss_rmb),
                'details': []
            }
            
            for detail in summary.profit_loss_details:
                detail_data = {
                    'name': detail.name,
                    'currency': detail.money_code.value,
                    'last_month_balance': float(detail.last_month_balance),
                    'profit_loss_rmb': float(detail.profit_loss_amount_rmb)
                }
                asset_type_data['details'].append(detail_data)
            
            export_data['asset_types'].append(asset_type_data)
        
        return export_data
    
    def generate_portfolio_overview(self, portfolio: Portfolio) -> Dict[str, Any]:
        """生成投资组合概览
        
        Args:
            portfolio: 投资组合
            
        Returns:
            Dict[str, Any]: 概览数据
        """
        overview = {
            'total_assets': portfolio.size(),
            'asset_types_count': len(portfolio.get_asset_types()),
            'asset_types': []
        }
        
        grouped_assets = portfolio.group_by_asset_type()
        
        for asset_type, assets in grouped_assets.items():
            type_info = {
                'type_name': asset_type.cn_name,
                'type_code': asset_type.en_name,
                'count': len(assets),
                'assets': []
            }
            
            for asset in assets:
                asset_info = {
                    'name': asset.name,
                    'currency': asset.currency.value,
                    'current_balance': float(asset.current_balance),
                    'previous_balance': float(asset.previous_balance),
                    'profit_loss': float(asset.calculate_profit_loss())
                }
                type_info['assets'].append(asset_info)
            
            overview['asset_types'].append(type_info)
        
        return overview