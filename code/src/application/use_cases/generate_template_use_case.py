#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcn29
@Software:  PyCharm
@File    :  generate_template_use_case.py
@Time    :  2025-08-22
@Desc    :  生成下月模板用例
"""

from typing import Dict, List, Any

from loguru import logger

from domain.services.asset_management_service import AssetManagementService


class GenerateTemplateUseCase:
    """生成下月资产配置模板用例。
    
    负责协调资产管理服务，生成下月的资产配置模板。
    这是应用层的核心用例，封装了模板生成的业务流程。
    
    Attributes:
        _asset_service: 资产管理服务，用于执行模板生成
    """
    
    def __init__(self, asset_service: AssetManagementService):
        """初始化模板生成用例。
        
        Args:
            asset_service: 资产管理服务实例
        """
        self._asset_service = asset_service
    
    def execute(self) -> Dict[str, Any]:
        """执行下月模板生成业务流程。
        
        完整的生成流程包括：
        1. 调用资产管理服务生成下月模板数据
        2. 计算生成结果的统计信息
        3. 记录生成摘要日志
        
        Returns:
            包含生成结果的字典，包含以下键：
            - success: 生成是否成功
            - template_data: 下月模板的字典数据
            - statistics: 生成统计信息
            - error: 错误信息（当生成失败时）
        """
        logger.info("Starting next month template generation...")
        
        try:
            # 1. 生成下月模板数据
            next_month_data = self._asset_service.generate_next_month_template()
            
            # 2. 统计生成结果
            stats = self._calculate_template_stats(next_month_data)
            
            result = {
                'success': True,
                'template_data': next_month_data,
                'statistics': stats
            }
            
            # 3. 记录生成摘要
            self._log_generation_summary(stats)
            
            logger.info("Next month template generation completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Template generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'template_data': None,
                'statistics': None
            }
    
    def _calculate_template_stats(self, template_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """计算模板生成的统计信息。
        
        分析生成的模板数据，计算各种统计指标。
        
        Args:
            template_data: 生成的下月模板数据
            
        Returns:
            包含统计信息的字典，包含：
            - total_assets: 总资产数量
            - asset_types_count: 资产类型数量
            - asset_type_breakdown: 各资产类型的资产数量分布
        """
        total_assets = 0
        asset_types = len(template_data)
        asset_type_breakdown = {}
        
        for asset_type, assets in template_data.items():
            asset_count = len(assets)
            total_assets += asset_count
            asset_type_breakdown[asset_type] = asset_count
        
        return {
            'total_assets': total_assets,
            'asset_types_count': asset_types,
            'asset_type_breakdown': asset_type_breakdown
        }
    
    def _log_generation_summary(self, stats: Dict[str, Any]) -> None:
        """记录模板生成的摘要信息。
        
        将生成结果的关键统计信息记录到日志中。
        
        Args:
            stats: 生成统计信息字典
        """
        logger.info(f"Generated template for {stats['total_assets']} assets")
        logger.info(f"Covering {stats['asset_types_count']} asset types")
        
        for asset_type, count in stats['asset_type_breakdown'].items():
            logger.info(f"  {asset_type}: {count} assets")