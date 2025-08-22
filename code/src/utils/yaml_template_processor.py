#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcn29
@Software:  PyCharm
@File    :  yaml_template_processor.py
@Time    :  2025-08-22
@Desc    :  YAML模板处理器，支持保留注释和格式
"""

from pathlib import Path
from typing import Dict, List, Any
from decimal import Decimal

from ruamel.yaml import YAML
from loguru import logger

from domain.models.asset import Asset
from domain.models.portfolio import Portfolio
from domain.enums.asset_type import AssetType
from domain.enums.money_code import MoneyCode


class YamlTemplateProcessor:
    """YAML模板处理器。
    
    使用ruamel.yaml库来保持YAML文件的原始格式，包括注释、缩进和顺序。
    支持生成下月模板时保持与原文件完全一致的格式。
    """
    
    def __init__(self):
        """初始化YAML处理器。"""
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.width = 4096  # 避免长行被折叠
        self.yaml.indent(mapping=2, sequence=4, offset=2)
    
    def load_portfolio_with_format(self, file_path: str) -> tuple[Portfolio, Any]:
        """加载投资组合并保留原始YAML格式。
        
        Args:
            file_path: YAML文件路径
            
        Returns:
            tuple: (Portfolio对象, 原始YAML数据结构)
            
        Raises:
            Exception: 当文件读取或解析失败时
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                yaml_data = self.yaml.load(file)
            
            assets = self._convert_yaml_to_assets(yaml_data)
            portfolio = Portfolio(assets)
            
            logger.info(f"Loaded portfolio with {len(assets)} assets from {file_path}")
            return portfolio, yaml_data
            
        except Exception as e:
            logger.error(f"Failed to load portfolio from {file_path}: {e}")
            raise
    
    def generate_next_month_template(self, file_path: str, output_path: str = None) -> str:
        """生成下月模板，保持与原文件相同的格式。
        
        Args:
            file_path: 原始文件路径
            output_path: 输出文件路径，如果为None则自动生成
            
        Returns:
            str: 生成的模板文件路径
        """
        try:
            # 加载原始文件
            portfolio, yaml_data = self.load_portfolio_with_format(file_path)
            
            # 生成下月模板数据
            next_month_portfolio = portfolio.prepare_next_month_portfolio()
            
            # 更新YAML数据但保持格式
            self._update_yaml_data_for_next_month(yaml_data, next_month_portfolio)
            
            # 确定输出路径
            if output_path is None:
                output_path = self._generate_next_month_file_path(file_path)
            
            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as file:
                self.yaml.dump(yaml_data, file)
            
            logger.info(f"Generated next month template: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to generate next month template: {e}")
            raise
    
    def _convert_yaml_to_assets(self, yaml_data: Dict[str, Any]) -> List[Asset]:
        """将YAML数据转换为资产对象列表。
        
        Args:
            yaml_data: 从YAML文件加载的数据
            
        Returns:
            List[Asset]: 资产对象列表
        """
        assets = []
        
        for asset_type_str, asset_list in yaml_data.items():
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
                    asset = self._create_asset_from_yaml_data(asset_type, asset_data)
                    assets.append(asset)
                except Exception as e:
                    logger.warning(f"Failed to create asset from data: {asset_data}, error: {e}")
                    continue
        
        return assets
    
    def _create_asset_from_yaml_data(self, asset_type: AssetType, asset_data: Dict[str, Any]) -> Asset:
        """从YAML数据创建资产对象。
        
        Args:
            asset_type: 资产类型
            asset_data: 资产数据字典
            
        Returns:
            Asset: 创建的资产对象
        """
        required_fields = ['name', 'money_code', 'current_account_balance', 'last_month_account_balance']
        
        for field in required_fields:
            if field not in asset_data:
                raise ValueError(f"Missing required field: {field}")
        
        money_code = MoneyCode.convert_from_str(asset_data['money_code'])
        
        return Asset(
            name=asset_data['name'],
            asset_type=asset_type,
            currency=money_code,
            current_balance=Decimal(str(asset_data['current_account_balance'])),
            previous_balance=Decimal(str(asset_data['last_month_account_balance']))
        )
    
    def _update_yaml_data_for_next_month(self, yaml_data: Dict[str, Any], 
                                        next_month_portfolio: Portfolio) -> None:
        """更新YAML数据为下月模板数据。
        
        在保持原始格式的前提下，更新数据值为下月模板的值。
        
        Args:
            yaml_data: 原始YAML数据结构
            next_month_portfolio: 下月投资组合
        """
        # 按资产类型分组
        grouped_assets = next_month_portfolio.group_by_asset_type()
        
        for asset_type_str, asset_list in yaml_data.items():
            try:
                asset_type = AssetType.convert_from_en_str(asset_type_str)
            except ValueError:
                continue
            
            if asset_type not in grouped_assets:
                continue
            
            next_month_assets = grouped_assets[asset_type]
            
            # 按名称创建资产字典以便快速查找
            asset_by_name = {asset.name: asset for asset in next_month_assets}
            
            # 更新每个资产的数据
            for asset_data in asset_list:
                asset_name = asset_data.get('name')
                if asset_name in asset_by_name:
                    asset = asset_by_name[asset_name]
                    
                    # 更新余额数据，但保持其他格式不变
                    asset_data['current_account_balance'] = float(asset.current_balance)
                    asset_data['last_month_account_balance'] = float(asset.previous_balance)
    
    def _generate_next_month_file_path(self, original_path: str) -> str:
        """生成下月文件路径。
        
        Args:
            original_path: 原始文件路径
            
        Returns:
            str: 下月文件路径
        """
        path = Path(original_path)
        parent = path.parent
        stem = path.stem
        suffix = path.suffix
        
        next_month_filename = f"{stem}_next_month{suffix}"
        return str(parent / next_month_filename)
