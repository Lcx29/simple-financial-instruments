#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcn29
@Software:  PyCharm
@File    :  asset_management_service.py
@Time    :  2025-08-22
@Desc    :  资产管理服务
"""

from decimal import Decimal
from typing import List, Dict, Any
from datetime import datetime

from loguru import logger

from domain.models.asset import Asset
from domain.models.portfolio import Portfolio, ProfitLossInfo, AssetTypeSummary
from domain.models.report import ProfitLossReport
from domain.enums.asset_type import AssetType
from domain.enums.money_code import MoneyCode
from domain.services.asset_repository import AssetRepository
from domain.services.exchange_rate_service import ExchangeRateService


class AssetManagementService:
    """资产管理核心业务服务。
    
    提供投资组合的盈亏分析、下月模板生成等核心业务功能。
    协调资产仓库和汇率服务，实现复杂的业务逻辑。
    
    Attributes:
        _repository: 资产数据仓库，用于数据的加载和保存
        _exchange_service: 汇率服务，用于货币转换计算
    """
    
    def __init__(self, repository: AssetRepository, 
                 exchange_service: ExchangeRateService):
        """初始化资产管理服务。
        
        Args:
            repository: 资产数据仓库实例
            exchange_service: 汇率服务实例
        """
        self._repository = repository
        self._exchange_service = exchange_service
    
    def analyze_profit_loss(self) -> ProfitLossReport:
        """分析投资组合的盈亏情况。
        
        执行完整的投资组合盈亏分析，包括：
        1. 加载当前投资组合数据
        2. 按资产类型分组计算盈亏
        3. 执行货币转换（统一为人民币）
        4. 生成详细的盈亏报表
        
        Returns:
            包含完整盈亏分析结果的报表对象
            
        Raises:
            RepositoryError: 当数据加载失败时
            ExchangeRateError: 当汇率转换失败时
        """
        portfolio = self._repository.load_portfolio()
        logger.info(f"Analyzing profit/loss for portfolio with {portfolio.size()} assets")
        
        asset_type_summaries = []
        total_profit_loss_rmb = Decimal("0.00")
        
        # 按资产类型分组处理
        grouped_assets = portfolio.group_by_asset_type()
        
        for asset_type, assets in grouped_assets.items():
            logger.info(f"Processing asset type: {asset_type.cn_name}")
            
            summary = self._analyze_asset_type_profit_loss(asset_type, assets)
            asset_type_summaries.append(summary)
            total_profit_loss_rmb += summary.total_profit_loss_rmb
            
            logger.info(f"{asset_type.cn_name} total profit/loss: ¥{summary.total_profit_loss_rmb}")
        
        report = ProfitLossReport(
            generated_at=datetime.now(),
            asset_type_summaries=asset_type_summaries,
            total_profit_loss_rmb=total_profit_loss_rmb
        )
        
        logger.info(f"Portfolio total profit/loss: ¥{total_profit_loss_rmb}")
        return report
    
    def generate_next_month_template(self) -> Dict[str, List[Dict[str, Any]]]:
        """生成下月资产配置模板。
        
        根据当前投资组合生成下月的资产配置模板：
        1. 调用仓库的save_next_month_portfolio方法生成模板文件
        2. 加载生成的模板以获取统计信息
        3. 返回统计信息供上层使用
        
        Returns:
            下月资产配置的字典数据，按资产类型组织
            
        Raises:
            RepositoryError: 当数据操作失败时
        """
        try:
            # 使用仓库的模板处理器生成下月模板（保持原始格式）
            self._repository.save_next_month_portfolio({})  # 传递空字典，实际不使用
            
            # 为了返回统计信息，我们需要生成一个简化的数据结构
            portfolio = self._repository.load_portfolio()
            next_month_portfolio = portfolio.prepare_next_month_portfolio()
            
            # 转换为字典格式以供统计
            next_month_data = {}
            grouped_assets = next_month_portfolio.group_by_asset_type()
            
            for asset_type, assets in grouped_assets.items():
                asset_list = []
                for asset in assets:
                    asset_data = {
                        'name': asset.name,
                        'money_code': asset.currency.value,
                        'current_account_balance': float(asset.current_balance),
                        'last_month_account_balance': float(asset.previous_balance)
                    }
                    asset_list.append(asset_data)
                
                next_month_data[asset_type.en_name] = asset_list
            
            logger.info(f"Generated next month template with {len(next_month_data)} asset types")
            return next_month_data
            
        except Exception as e:
            logger.error(f"Failed to generate next month template: {e}")
            raise
    
    def _analyze_asset_type_profit_loss(self, asset_type: AssetType, 
                                       assets: List[Asset]) -> AssetTypeSummary:
        """分析特定资产类型的盈亏情况。
        
        对指定资产类型下的所有资产进行盈亏分析，包括货币转换。
        
        Args:
            asset_type: 要分析的资产类型
            assets: 该类型下的资产列表
            
        Returns:
            该资产类型的汇总盈亏信息
        """
        if not assets:
            logger.info(f"No assets found for type: {asset_type.cn_name}")
            return AssetTypeSummary(
                asset_type=asset_type,
                total_profit_loss_rmb=Decimal("0.00"),
                profit_loss_details=[]
            )
        
        profit_loss_details = []
        total_profit_loss_rmb = Decimal("0.00")
        
        for asset in assets:
            # 计算盈亏
            profit_loss_amount = asset.calculate_profit_loss()
            
            # 转换为人民币
            profit_loss_rmb = self._convert_to_rmb_if_needed(
                profit_loss_amount, asset.currency
            )
            
            detail = ProfitLossInfo(
                name=asset.name,
                money_code=asset.currency,
                last_month_balance=asset.previous_balance,
                profit_loss_amount_rmb=profit_loss_rmb
            )
            
            profit_loss_details.append(detail)
            total_profit_loss_rmb += profit_loss_rmb
        
        return AssetTypeSummary(
            asset_type=asset_type,
            total_profit_loss_rmb=total_profit_loss_rmb,
            profit_loss_details=profit_loss_details
        )
    
    def _convert_to_rmb_if_needed(self, amount: Decimal, currency: MoneyCode) -> Decimal:
        """如果需要，将金额转换为人民币。
        
        如果金额已经是人民币，则直接返回；否则通过汇率服务进行转换。
        
        Args:
            amount: 要转换的金额
            currency: 金额的货币类型
            
        Returns:
            转换后的人民币金额
        """
        if currency == MoneyCode.CNY:
            return amount
        
        try:
            return self._exchange_service.convert(currency, MoneyCode.CNY, amount)
        except Exception as e:
            logger.warning(f"Failed to convert {currency.value} to CNY: {e}")
            # 如果转换失败，返回原金额（可能需要根据业务需求调整）
            return amount
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """获取投资组合的概要统计信息。
        
        提供投资组合的基本统计数据，用于快速了解组合构成。
        
        Returns:
            包含统计信息的字典，包括总资产数、资产类型数等
            
        Raises:
            RepositoryError: 当数据加载失败时
        """
        portfolio = self._repository.load_portfolio()
        
        summary = {
            'total_assets': portfolio.size(),
            'asset_types': len(portfolio.get_asset_types()),
            'asset_type_breakdown': {}
        }
        
        # 按资产类型统计
        grouped_assets = portfolio.group_by_asset_type()
        for asset_type, assets in grouped_assets.items():
            summary['asset_type_breakdown'][asset_type.cn_name] = len(assets)
        
        return summary