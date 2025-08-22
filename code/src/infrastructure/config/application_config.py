#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcn29
@Software:  PyCharm
@File    :  application_config.py
@Time    :  2025-08-22
@Desc    :  应用配置类
"""

import os
from pathlib import Path
from typing import Optional

from loguru import logger

from domain.services.asset_repository import AssetRepository
from domain.services.exchange_rate_service import ExchangeRateService
from domain.services.asset_management_service import AssetManagementService
from domain.services.report_service import ReportService
from infrastructure.repositories.yaml_asset_repository import YamlAssetRepository
from infrastructure.exchange_rates.boc_hk_exchange_rate_service import BocHkExchangeRateService
from infrastructure.providers.boc_hk_provider import BocHkExchangeRateProvider
from application.use_cases.analyze_portfolio_use_case import AnalyzePortfolioUseCase
from application.use_cases.generate_template_use_case import GenerateTemplateUseCase


class ApplicationConfig:
    """应用配置类"""

    def __init__(self, asset_file_path: Optional[str] = None,
                 exchange_rate_provider: str = "boc_hk",
                 supported_providers: Optional[list[str]] = None):
        """
        初始化应用配置
        
        Args:
            asset_file_path: 资产文件路径，如果为None则使用默认路径
            exchange_rate_provider: 汇率提供商，默认为 "boc_hk"
            supported_providers: 支持的汇率提供商列表，如果为None则使用默认列表
        """
        # 支持的汇率提供商列表，允许通过参数自定义
        self._supported_providers = supported_providers or ["boc_hk"]

        self._asset_file_path = asset_file_path or self._get_default_asset_file_path()
        self._exchange_rate_provider = exchange_rate_provider

        # 缓存已创建的实例
        self._asset_repository: Optional[AssetRepository] = None
        self._exchange_service: Optional[ExchangeRateService] = None
        self._asset_service: Optional[AssetManagementService] = None
        self._report_service: Optional[ReportService] = None

        logger.info(f"Application config initialized with asset file: {self._asset_file_path}")
        logger.info(f"Exchange rate provider: {self._exchange_rate_provider}")
        logger.info(f"Supported providers: {', '.join(self._supported_providers)}")

    def get_asset_repository(self) -> AssetRepository:
        """获取资产仓库实例"""
        if self._asset_repository is None:
            self._asset_repository = YamlAssetRepository(self._asset_file_path)
            logger.debug("Created YamlAssetRepository instance")
        return self._asset_repository

    def get_exchange_service(self) -> ExchangeRateService:
        """获取汇率服务实例。
        
        Returns:
            ExchangeRateService: 汇率服务实例
            
        Raises:
            ValueError: 当汇率提供商不支持时抛出异常
        """
        if self._exchange_service is None:
            if self._exchange_rate_provider == "boc_hk":
                provider = BocHkExchangeRateProvider()
                self._exchange_service = BocHkExchangeRateService(provider)
                logger.debug("Created BocHkExchangeRateService instance")
            else:
                raise ValueError(
                    f"Unsupported exchange rate provider: {self._exchange_rate_provider}. "
                    f"Supported providers: {', '.join(self._supported_providers)}"
                )
        return self._exchange_service

    def get_asset_management_service(self) -> AssetManagementService:
        """获取资产管理服务实例"""
        if self._asset_service is None:
            repository = self.get_asset_repository()
            exchange_service = self.get_exchange_service()
            self._asset_service = AssetManagementService(repository, exchange_service)
            logger.debug("Created AssetManagementService instance")
        return self._asset_service

    def get_report_service(self) -> ReportService:
        """获取报表服务实例"""
        if self._report_service is None:
            exchange_service = self.get_exchange_service()
            self._report_service = ReportService(exchange_service)
            logger.debug("Created ReportService instance")
        return self._report_service

    def get_analyze_portfolio_use_case(self) -> AnalyzePortfolioUseCase:
        """获取分析投资组合用例实例"""
        asset_service = self.get_asset_management_service()
        report_service = self.get_report_service()
        return AnalyzePortfolioUseCase(asset_service, report_service)

    def get_generate_template_use_case(self) -> GenerateTemplateUseCase:
        """获取生成模板用例实例"""
        asset_service = self.get_asset_management_service()
        return GenerateTemplateUseCase(asset_service)

    def _get_default_asset_file_path(self) -> str:
        """获取默认资产文件路径"""
        # 尝试从环境变量获取
        env_path = os.getenv('ASSET_INVENTORY_FILE')
        if env_path and Path(env_path).exists():
            return env_path

        # 使用项目根目录下的默认路径
        project_root = Path(__file__).parent.parent.parent.parent.parent
        default_path = project_root / "resources" / "asset_inventory.yaml"

        return str(default_path)

    @property
    def asset_file_path(self) -> str:
        """资产文件路径"""
        return self._asset_file_path

    @property
    def exchange_rate_provider(self) -> str:
        """汇率提供商"""
        return self._exchange_rate_provider

    @property
    def supported_providers(self) -> list[str]:
        """支持的汇率提供商列表"""
        return self._supported_providers.copy()

    def validate_configuration(self) -> bool:
        """验证配置是否有效。
        
        Returns:
            bool: 配置是否有效
        """
        try:
            # 检查资产文件是否存在
            if not Path(self._asset_file_path).exists():
                logger.error(f"Asset file not found: {self._asset_file_path}")
                return False

            # 检查汇率提供商是否支持
            if self._exchange_rate_provider not in self._supported_providers:
                logger.error(f"Unsupported exchange rate provider: {self._exchange_rate_provider}")
                logger.error(f"Supported providers: {', '.join(self._supported_providers)}")
                return False

            logger.info("Configuration validation passed")
            return True

        except Exception as e:
            logger.error(f"Configuration validation failed: {e}")
            return False
