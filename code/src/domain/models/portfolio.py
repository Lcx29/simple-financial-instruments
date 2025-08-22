#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcn29
@Software:  PyCharm
@File    :  portfolio.py
@Time    :  2025-08-22
@Desc    :  投资组合领域模型
"""

from decimal import Decimal
from typing import List, Dict, Optional
from dataclasses import dataclass

from domain.models.asset import Asset
from domain.enums.asset_type import AssetType
from domain.enums.money_code import MoneyCode


@dataclass
class ProfitLossInfo:
    """盈亏信息数据类。
    
    存储单个资产的盈亏详细信息。
    
    Attributes:
        name: 资产名称
        money_code: 资产货币类型
        last_month_balance: 上月余额
        current_month_balance: 本月余额
        profit_loss_amount_rmb: 盈亏金额（转换为人民币）
    """
    name: str
    money_code: MoneyCode
    last_month_balance: Decimal
    current_month_balance: Decimal
    profit_loss_amount_rmb: Decimal


@dataclass
class AssetTypeSummary:
    """资产类型汇总信息数据类。
    
    存储某种资产类型的汇总盈亏信息。
    
    Attributes:
        asset_type: 资产类型
        total_profit_loss_rmb: 该类型资产的总盈亏金额（人民币）
        profit_loss_details: 该类型下各个资产的盈亏详情列表
    """
    asset_type: AssetType
    total_profit_loss_rmb: Decimal
    profit_loss_details: List[ProfitLossInfo]


class Portfolio:
    """投资组合领域模型。
    
    代表用户的完整资产组合，管理多个资产并提供组合级别的业务操作。
    
    Attributes:
        _assets: 内部存储的资产列表
    """

    def __init__(self, assets: List[Asset]):
        """初始化投资组合。
        
        Args:
            assets: 资产列表，可以为空列表
        """
        self._assets = assets or []
        self._validate_assets()

    def _validate_assets(self):
        """验证资产列表的合法性。
        
        检查是否存在重复的资产名称，确保组合的唯一性。
        
        Raises:
            ValueError: 当存在重复资产名称时抛出异常
        """
        if not self._assets:
            return

        # 检查是否有重复的资产名称
        names = [asset.name for asset in self._assets]
        if len(names) != len(set(names)):
            raise ValueError("Portfolio contains duplicate asset names")

    @property
    def assets(self) -> List[Asset]:
        """获取所有资产的副本。
        
        返回资产列表的副本，防止外部直接修改内部状态。
        
        Returns:
            资产列表的副本
        """
        return self._assets.copy()

    def add_asset(self, asset: Asset) -> None:
        """向投资组合添加新资产。
        
        Args:
            asset: 要添加的资产对象
            
        Raises:
            ValueError: 当资产名称已存在时抛出异常
        """
        if any(existing.name == asset.name for existing in self._assets):
            raise ValueError(f"Asset with name '{asset.name}' already exists")
        self._assets.append(asset)

    def remove_asset(self, asset_name: str) -> None:
        """从投资组合中移除指定名称的资产。
        
        Args:
            asset_name: 要移除的资产名称
        """
        self._assets = [asset for asset in self._assets if asset.name != asset_name]

    def get_asset_by_name(self, name: str) -> Optional[Asset]:
        """根据名称获取资产。
        
        Args:
            name: 资产名称
            
        Returns:
            找到的资产对象，如果不存在则返回None
        """
        for asset in self._assets:
            if asset.name == name:
                return asset
        return None

    def get_assets_by_type(self, asset_type: AssetType) -> List[Asset]:
        """根据资产类型获取资产列表。
        
        Args:
            asset_type: 资产类型枚举
            
        Returns:
            指定类型的资产列表
        """
        return [asset for asset in self._assets if asset.asset_type == asset_type]

    def get_assets_by_currency(self, currency: MoneyCode) -> List[Asset]:
        """根据货币类型获取资产列表。
        
        Args:
            currency: 货币类型枚举
            
        Returns:
            指定货币类型的资产列表
        """
        return [asset for asset in self._assets if asset.currency == currency]

    def get_asset_types(self) -> List[AssetType]:
        """获取投资组合中包含的所有资产类型。
        
        Returns:
            不重复的资产类型列表
        """
        return list(set(asset.asset_type for asset in self._assets))

    def calculate_total_current_value(self) -> Decimal:
        """计算投资组合的当前总价值。
        
        注意：此方法直接求和，不进行货币转换。
        
        Returns:
            当前总价值（原币种求和）
        """
        return sum(asset.current_balance for asset in self._assets)

    def calculate_total_profit_loss(self) -> Decimal:
        """计算投资组合的总盈亏。
        
        注意：此方法直接求和，不进行货币转换。
        
        Returns:
            总盈亏金额（原币种求和）
        """
        return sum(asset.calculate_profit_loss() for asset in self._assets)

    def has_assets_of_type(self, asset_type: AssetType) -> bool:
        """检查是否包含指定类型的资产。
        
        Args:
            asset_type: 要检查的资产类型
            
        Returns:
            True表示包含该类型资产，False表示不包含
        """
        return any(asset.asset_type == asset_type for asset in self._assets)

    def prepare_next_month_portfolio(self) -> "Portfolio":
        """生成下月投资组合配置。
        
        对每个资产调用其prepare_for_next_month方法，生成新的投资组合。
        
        Returns:
            下月的投资组合对象
        """
        next_month_assets = [asset.prepare_for_next_month() for asset in self._assets]
        return Portfolio(next_month_assets)

    def group_by_asset_type(self) -> Dict[AssetType, List[Asset]]:
        """按资产类型对资产进行分组。
        
        Returns:
            以资产类型为键，资产列表为值的字典
        """
        grouped = {}
        for asset in self._assets:
            if asset.asset_type not in grouped:
                grouped[asset.asset_type] = []
            grouped[asset.asset_type].append(asset)
        return grouped

    def is_empty(self) -> bool:
        """检查投资组合是否为空。
        
        Returns:
            True表示组合为空，False表示非空
        """
        return len(self._assets) == 0

    def size(self) -> int:
        """获取投资组合中的资产数量。
        
        Returns:
            资产总数
        """
        return len(self._assets)

    def __str__(self) -> str:
        return f"Portfolio(assets={len(self._assets)}, types={len(self.get_asset_types())})"

    def __repr__(self) -> str:
        return self.__str__()
