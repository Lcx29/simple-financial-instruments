#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcn29
@Software:  PyCharm
@File    :  analyze_portfolio_use_case.py
@Time    :  2025-08-22
@Desc    :  分析投资组合用例
"""

from typing import Dict, Any

from loguru import logger

from domain.models.report import ProfitLossReport
from domain.services.asset_management_service import AssetManagementService
from domain.services.report_service import ReportService


class AnalyzePortfolioUseCase:
    """投资组合分析用例。
    
    负责协调资产管理服务和报表服务，执行完整的投资组合盈亏分析流程。
    这是应用层的核心用例，封装了分析投资组合的业务流程。
    
    Attributes:
        _asset_service: 资产管理服务，用于执行盈亏分析
        _report_service: 报表服务，用于格式化分析结果
    """
    
    def __init__(self, asset_service: AssetManagementService, 
                 report_service: ReportService):
        """初始化投资组合分析用例。
        
        Args:
            asset_service: 资产管理服务实例
            report_service: 报表服务实例
        """
        self._asset_service = asset_service
        self._report_service = report_service
    
    def execute(self, output_format: str = 'text') -> Dict[str, Any]:
        """执行投资组合分析业务流程。
        
        完整的分析流程包括：
        1. 执行投资组合盈亏分析
        2. 获取投资组合概要信息
        3. 根据指定格式生成分析结果
        4. 记录分析摘要日志
        
        Args:
            output_format: 输出格式，可选值：
                - 'text': 纯文本格式报表
                - 'dict': 字典格式数据
                - 'both': 同时包含文本和字典格式
                
        Returns:
            包含分析结果的字典，包含以下键：
            - success: 分析是否成功
            - portfolio_summary: 投资组合概要信息
            - report_text: 文本格式报表（当output_format包含'text'时）
            - report_data: 字典格式数据（当output_format包含'dict'时）
            - error: 错误信息（当分析失败时）
        """
        logger.info("Starting portfolio analysis...")
        
        try:
            # 1. 执行盈亏分析
            profit_loss_report = self._asset_service.analyze_profit_loss()
            
            # 2. 获取投资组合概要
            portfolio_summary = self._asset_service.get_portfolio_summary()
            
            # 3. 根据输出格式生成结果
            result = {
                'success': True,
                'portfolio_summary': portfolio_summary
            }
            
            if output_format in ['text', 'both']:
                result['report_text'] = self._report_service.format_profit_loss_report(profit_loss_report)
            
            if output_format in ['dict', 'both']:
                result['report_data'] = self._report_service.export_report_to_dict(profit_loss_report)
            
            # 4. 记录分析结果
            self.__log_analysis_summary(profit_loss_report)
            
            logger.info("Portfolio analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Portfolio analysis failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'portfolio_summary': None
            }

    @staticmethod
    def log_analysis_summary(report: ProfitLossReport) -> None:
        """记录投资组合分析的摘要信息。
        
        将分析结果的关键信息记录到日志中，便于跟踪和调试。
        
        Args:
            report: 盈亏分析报表对象
        """
        logger.info(f"Analysis completed with {len(report.asset_type_summaries)} asset types")
        logger.info(f"Total profit/loss: ¥{report.total_profit_loss_rmb:,.2f}")

        if report.has_profit():
            logger.info("Overall portfolio is profitable")
        elif report.has_loss():
            logger.info("Overall portfolio has losses")
        else:
            logger.info("Overall portfolio is break-even")

        # 记录各资产类型表现
        for summary in report.asset_type_summaries:
            status = "profitable" if summary.total_profit_loss_rmb > 0 else "loss" if summary.total_profit_loss_rmb < 0 else "break-even"
            logger.info(f"{summary.asset_type.cn_name}: ¥{summary.total_profit_loss_rmb:,.2f} ({status})")
