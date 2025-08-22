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
        
        # 标题部分
        title_line = "╔" + "═" * 98 + "╗"
        lines.append(title_line)
        title_text = f"║{'资产盈亏分析报表':^96}║"
        lines.append(title_text)
        date_text = f"║{report.generated_at.strftime('%Y年%m月%d日 %H:%M:%S'):^94}║"
        lines.append(date_text)
        lines.append("╠" + "═" * 98 + "╣")

        # 统计信息头部
        profit_count = len(report.get_profitable_asset_types())
        loss_count = len(report.get_loss_asset_types())
        total_types = len(report.asset_type_summaries)
        
        stats_text = f"║ 总资产类型: {total_types:2d} | 盈利类型: {profit_count:2d} | 亏损类型: {loss_count:2d} " + " " * 51 + "║"
        lines.append(stats_text)
        lines.append("╠" + "═" * 98 + "╣")

        # 各资产类型详情
        for i, summary in enumerate(report.asset_type_summaries):
            # 资产类型标题
            type_name = summary.asset_type.cn_name
            type_total = summary.total_profit_loss_rmb
            
            # 确定盈亏状态图标
            if type_total > 0:
                status_icon = "📈"
                color_symbol = "+"
            elif type_total < 0:
                status_icon = "📉"
                color_symbol = ""
            else:
                status_icon = "➖"
                color_symbol = " "
            
            type_header = f"║ {status_icon} {type_name:<15} " + " " * 78 + "║"
            lines.append(type_header)
            
            # 分隔线
            lines.append("║" + "─" * 98 + "║")
            
            # 表头
            header = f"║ {'资产名称':<20} {'币种':<6} {'上月余额':<15} {'本月余额':<15} {'盈亏金额':<15} {'状态':<8} ║"
            lines.append(header)
            lines.append("║" + "─" * 98 + "║")

            # 详细数据
            for detail in summary.profit_loss_details:
                profit_loss_amount = detail.profit_loss_amount_rmb
                
                # 格式化金额
                last_month_str = f"¥{detail.last_month_balance:,.2f}"
                current_month_str = f"¥{detail.current_month_balance:,.2f}"
                profit_loss_str = f"¥{abs(profit_loss_amount):,.2f}"
                
                # 状态显示
                if profit_loss_amount > 0:
                    status = "📈 盈利"
                    profit_loss_display = f"+{profit_loss_str}"
                elif profit_loss_amount < 0:
                    status = "📉 亏损"
                    profit_loss_display = f"-{profit_loss_str}"
                else:
                    status = "➖ 持平"
                    profit_loss_display = profit_loss_str

                data_line = (f"║ {detail.name:<20} "
                           f"{detail.money_code.value:<6} "
                           f"{last_month_str:<15} "
                           f"{current_month_str:<15} "
                           f"{profit_loss_display:<15} "
                           f"{status:<8} ║")
                lines.append(data_line)

            # 小计行
            lines.append("║" + "─" * 98 + "║")
            subtotal_str = f"¥{abs(type_total):,.2f}"
            if type_total > 0:
                subtotal_display = f"+{subtotal_str}"
                subtotal_status = "📈 盈利"
            elif type_total < 0:
                subtotal_display = f"-{subtotal_str}"
                subtotal_status = "📉 亏损"
            else:
                subtotal_display = subtotal_str
                subtotal_status = "➖ 持平"
                
            subtotal_line = (f"║ {'小计':<20} "
                           f"{'合计':<6} "
                           f"{'':<15} "
                           f"{'':<15} "
                           f"{subtotal_display:<15} "
                           f"{subtotal_status:<8} ║")
            lines.append(subtotal_line)
            
            # 如果不是最后一个类型，添加分隔
            if i < len(report.asset_type_summaries) - 1:
                lines.append("╠" + "═" * 98 + "╣")

        # 总计部分
        lines.append("╠" + "═" * 98 + "╣")
        
        total_amount = report.total_profit_loss_rmb
        total_str = f"¥{abs(total_amount):,.2f}"
        
        if total_amount > 0:
            total_display = f"+{total_str}"
            total_status = "🎉 整体盈利"
            total_icon = "📈"
        elif total_amount < 0:
            total_display = f"-{total_str}"
            total_status = "⚠️  整体亏损"
            total_icon = "📉"
        else:
            total_display = total_str
            total_status = "➖ 收支平衡"
            total_icon = "➖"

        # 计算盈利比例（如果有上月数据）
        profit_ratio_text = ""
        if hasattr(report, 'total_last_month_balance'):
            if report.total_last_month_balance > 0:
                ratio = (total_amount / report.total_last_month_balance) * 100
                profit_ratio_text = f" ({ratio:+.2f}%)"

        final_line = f"║ {total_icon} 总计盈亏: {total_display:<20} {total_status:<15}{profit_ratio_text:<30} ║"
        lines.append(final_line)
        lines.append("╚" + "═" * 98 + "╝")

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
                    'current_month_balance': float(detail.current_month_balance),
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

    def format_portfolio_overview(self, portfolio: Portfolio) -> str:
        """格式化投资组合概览为可读文本
        
        Args:
            portfolio: 投资组合
            
        Returns:
            str: 格式化后的概览文本
        """
        lines = []
        
        # 标题部分
        title_line = "╔" + "═" * 88 + "╗"
        lines.append(title_line)
        title_text = f"║{'投资组合概览':^84}║"
        lines.append(title_text)
        lines.append("╠" + "═" * 88 + "╣")

        # 统计信息
        total_assets = portfolio.size()
        asset_types_count = len(portfolio.get_asset_types())
        grouped_assets = portfolio.group_by_asset_type()
        
        # 计算货币分布
        currency_stats = {}
        total_current_value = Decimal('0')
        total_previous_value = Decimal('0')
        
        for asset in portfolio.assets:
            currency = asset.currency.value
            if currency not in currency_stats:
                currency_stats[currency] = {
                    'count': 0,
                    'current_value': Decimal('0'),
                    'previous_value': Decimal('0')
                }
            currency_stats[currency]['count'] += 1
            currency_stats[currency]['current_value'] += asset.current_balance
            currency_stats[currency]['previous_value'] += asset.previous_balance
            total_current_value += asset.current_balance
            total_previous_value += asset.previous_balance

        # 概要统计
        stats_line1 = f"║ 总资产数量: {total_assets:3d} | 资产类型: {asset_types_count:2d} | 涉及货币: {len(currency_stats):2d} 种" + " " * 40 + "║"
        lines.append(stats_line1)
        
        # 货币分布统计
        lines.append("╠" + "═" * 88 + "╣")
        lines.append("║ 💰 货币分布统计" + " " * 68 + "║")
        lines.append("║" + "─" * 88 + "║")
        
        currency_header = f"║ {'货币':<8} {'资产数量':<10} {'当前总值':<20} {'上月总值':<20} {'变化':<15} ║"
        lines.append(currency_header)
        lines.append("║" + "─" * 88 + "║")
        
        for currency, stats in sorted(currency_stats.items()):
            current_str = f"{stats['current_value']:,.2f}"
            previous_str = f"{stats['previous_value']:,.2f}"
            change = stats['current_value'] - stats['previous_value']
            
            if change > 0:
                change_str = f"+{change:,.2f} 📈"
            elif change < 0:
                change_str = f"{change:,.2f} 📉"
            else:
                change_str = "0.00 ➖"
                
            currency_line = (f"║ {currency:<8} "
                           f"{stats['count']:<10} "
                           f"{current_str:<20} "
                           f"{previous_str:<20} "
                           f"{change_str:<15} ║")
            lines.append(currency_line)

        # 各资产类型详情
        lines.append("╠" + "═" * 88 + "╣")
        lines.append("║ 📊 资产类型明细" + " " * 68 + "║")
        lines.append("╠" + "═" * 88 + "╣")

        for i, (asset_type, assets) in enumerate(grouped_assets.items()):
            # 资产类型标题
            type_name = asset_type.cn_name
            type_count = len(assets)
            
            # 计算该类型的统计数据
            type_current_total = sum(asset.current_balance for asset in assets)
            type_previous_total = sum(asset.previous_balance for asset in assets)
            type_profit_loss = sum(asset.calculate_profit_loss() for asset in assets)
            
            # 确定状态图标
            if type_profit_loss > 0:
                status_icon = "📈"
            elif type_profit_loss < 0:
                status_icon = "📉"
            else:
                status_icon = "➖"
            
            type_header = f"║ {status_icon} {type_name:<15} (共 {type_count} 项)" + " " * 60 + "║"
            lines.append(type_header)
            
            # 分隔线
            lines.append("║" + "─" * 88 + "║")
            
            # 表头
            detail_header = f"║ {'资产名称':<25} {'货币':<6} {'当前余额':<15} {'上月余额':<15} {'盈亏状态':<12} ║"
            lines.append(detail_header)
            lines.append("║" + "─" * 88 + "║")

            # 详细数据
            for asset in assets:
                current_str = f"{asset.current_balance:,.2f}"
                previous_str = f"{asset.previous_balance:,.2f}"
                profit_loss = asset.calculate_profit_loss()
                
                # 状态显示
                if profit_loss > 0:
                    status = f"+{profit_loss:,.2f} 📈"
                elif profit_loss < 0:
                    status = f"{profit_loss:,.2f} 📉"
                else:
                    status = "0.00 ➖"

                asset_line = (f"║ {asset.name:<25} "
                            f"{asset.currency.value:<6} "
                            f"{current_str:<15} "
                            f"{previous_str:<15} "
                            f"{status:<12} ║")
                lines.append(asset_line)

            # 类型小计
            lines.append("║" + "─" * 88 + "║")
            type_profit_loss_str = f"{type_profit_loss:,.2f}"
            if type_profit_loss > 0:
                type_status = f"+{type_profit_loss_str} 📈"
            elif type_profit_loss < 0:
                type_status = f"{type_profit_loss_str} 📉"
            else:
                type_status = "0.00 ➖"
                
            current_total_str = f"{type_current_total:,.2f}"
            previous_total_str = f"{type_previous_total:,.2f}"
            subtotal_line = (f"║ {'小计':<25} "
                           f"{'--':<6} "
                           f"{current_total_str:<15} "
                           f"{previous_total_str:<15} "
                           f"{type_status:<12} ║")
            lines.append(subtotal_line)
            
            # 如果不是最后一个类型，添加分隔
            if i < len(grouped_assets) - 1:
                lines.append("╠" + "═" * 88 + "╣")

        lines.append("╚" + "═" * 88 + "╝")
        
        return "\n".join(lines)
