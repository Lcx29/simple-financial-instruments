#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcn29
@Software:  PyCharm
@File    :  yaml_asset_repository.py
@Time    :  2025-08-22
@Desc    :  YAML格式资产仓库实现
"""

from decimal import Decimal
from typing import List, Dict, Any
from pathlib import Path

from loguru import logger

from domain.models.asset import Asset
from domain.models.portfolio import Portfolio
from domain.enums.asset_type import AssetType
from domain.enums.money_code import MoneyCode
from domain.services.asset_repository import AssetRepository, RepositoryError
from utils.file_parse import parse_yaml_file, write_yaml_file


class YamlAssetRepository(AssetRepository):
    """基于YAML文件的资产数据仓库实现。
    
    实现了AssetRepository接口，提供YAML格式的资产数据持久化功能。
    支持投资组合的加载、保存和下月模板生成。
    
    Attributes:
        _file_path: YAML文件的完整路径
    """
    
    def __init__(self, file_path: str):
        """初始化YAML资产仓库。
        
        Args:
            file_path: YAML文件的完整路径
            
        Raises:
            RepositoryError: 当文件路径无效时抛出异常
        """
        self._file_path = file_path
        self._validate_file_path()
    
    def _validate_file_path(self) -> None:
        """验证YAML文件路径的有效性。
        
        检查文件路径是否为空以及文件扩展名是否正确。
        
        Raises:
            RepositoryError: 当文件路径无效时抛出异常
        """
        if not self._file_path:
            raise RepositoryError("File path cannot be empty")
        
        path = Path(self._file_path)
        if not path.suffix.lower() in ['.yaml', '.yml']:
            raise RepositoryError(f"File must be a YAML file: {self._file_path}")
    
    def load_portfolio(self) -> Portfolio:
        """从YAML文件加载投资组合。
        
        读取并解析YAML文件，将数据转换为资产对象并构建投资组合。
        
        Returns:
            包含所有资产的投资组合对象
            
        Raises:
            RepositoryError: 当文件读取或解析失败时抛出异常
        """
        try:
            data = parse_yaml_file(self._file_path)
            if data is None:
                raise RepositoryError(f"Failed to parse YAML file: {self._file_path}")
            
            assets = self._convert_data_to_assets(data)
            portfolio = Portfolio(assets)
            
            logger.info(f"Loaded portfolio with {len(assets)} assets from {self._file_path}")
            return portfolio
            
        except Exception as e:
            if isinstance(e, RepositoryError):
                raise
            raise RepositoryError(f"Failed to load portfolio from {self._file_path}", e)
    
    def save_portfolio(self, portfolio: Portfolio) -> None:
        """将投资组合保存到YAML文件。
        
        将投资组合对象转换为YAML格式并保存到文件中。
        
        Args:
            portfolio: 要保存的投资组合对象
            
        Raises:
            RepositoryError: 当文件保存失败时抛出异常
        """
        try:
            data = self._convert_portfolio_to_data(portfolio)
            write_yaml_file(self._file_path, data)
            logger.info(f"Saved portfolio with {portfolio.size()} assets to {self._file_path}")
            
        except Exception as e:
            raise RepositoryError(f"Failed to save portfolio to {self._file_path}", e)
    
    def save_next_month_portfolio(self, portfolio_data: Dict[str, List[Dict[str, Any]]]) -> None:
        """保存下月投资组合模板数据。
        
        将下月投资组合数据保存到自动生成的文件名中。
        
        Args:
            portfolio_data: 下月投资组合的字典数据
            
        Raises:
            RepositoryError: 当文件保存失败时抛出异常
        """
        try:
            # 生成下月文件路径
            next_month_file_path = self._generate_next_month_file_path()
            write_yaml_file(next_month_file_path, portfolio_data)
            logger.info(f"Saved next month portfolio data to {next_month_file_path}")
            
        except Exception as e:
            raise RepositoryError(f"Failed to save next month portfolio data", e)
    
    def _convert_data_to_assets(self, data: Dict[str, Any]) -> List[Asset]:
        """将YAML数据转换为资产对象列表。
        
        解析YAML数据结构，为每个资产创建Asset对象。
        
        Args:
            data: 从YAML文件解析的数据字典
            
        Returns:
            资产对象列表
        """
        assets = []
        
        for asset_type_str, asset_list in data.items():
            try:
                asset_type = AssetType.convert_from_en_str(asset_type_str)
            except ValueError:
                logger.warning(f"Unknown asset type: {asset_type_str}, skipping")
                continue
            
            if not isinstance(asset_list, list):
                logger.warning(f"Invalid asset list format for {asset_type_str}, skipping")
                continue
            
            for asset_data in asset_list:
                try:
                    asset = self._create_asset_from_data(asset_type, asset_data)
                    assets.append(asset)
                except Exception as e:
                    logger.warning(f"Failed to create asset from data: {asset_data}, error: {e}")
                    continue
        
        return assets
    
    def _create_asset_from_data(self, asset_type: AssetType, asset_data: Dict[str, Any]) -> Asset:
        """从字典数据创建单个资产对象。
        
        验证必要字段并创建Asset实例。
        
        Args:
            asset_type: 资产类型枚举
            asset_data: 资产的字典数据
            
        Returns:
            创建的资产对象
            
        Raises:
            ValueError: 当数据格式不正确时抛出异常
        """
        required_fields = ['name', 'money_code', 'current_account_balance', 'last_month_account_balance']
        
        for field in required_fields:
            if field not in asset_data:
                raise ValueError(f"Missing required field: {field}")
        
        try:
            money_code = MoneyCode.convert_from_str(asset_data['money_code'])
        except ValueError as e:
            raise ValueError(f"Invalid money code: {asset_data['money_code']}") from e
        
        return Asset(
            name=asset_data['name'],
            asset_type=asset_type,
            currency=money_code,
            current_balance=Decimal(str(asset_data['current_account_balance'])),
            previous_balance=Decimal(str(asset_data['last_month_account_balance']))
        )
    
    def _convert_portfolio_to_data(self, portfolio: Portfolio) -> Dict[str, Any]:
        """将投资组合对象转换为YAML数据格式。
        
        将Portfolio对象转换为适合YAML序列化的字典结构。
        
        Args:
            portfolio: 投资组合对象
            
        Returns:
            可序列化为YAML的字典数据
        """
        data = {}
        grouped_assets = portfolio.group_by_asset_type()
        
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
            
            data[asset_type.en_name] = asset_list
        
        return data
    
    def _generate_next_month_file_path(self) -> str:
        """生成下月文件的路径。
        
        基于当前文件路径生成下月模板文件的路径名。
        
        Returns:
            下月文件的完整路径
        """
        path = Path(self._file_path)
        parent = path.parent
        stem = path.stem
        suffix = path.suffix
        
        next_month_filename = f"{stem}_next_month{suffix}"
        return str(parent / next_month_filename)