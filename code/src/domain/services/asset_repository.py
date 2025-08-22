#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcn29
@Software:  PyCharm
@File    :  asset_repository.py
@Time    :  2025-08-22
@Desc    :  资产仓库接口
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any

from domain.models.portfolio import Portfolio


class AssetRepository(ABC):
    """资产数据仓库接口。
    
    定义资产数据的持久化操作，支持多种存储格式的实现。
    遵循仓库模式，将数据访问逻辑与业务逻辑分离。
    """
    
    @abstractmethod
    def load_portfolio(self) -> Portfolio:
        """从存储中加载投资组合。
        
        读取并解析存储的资产数据，构建完整的投资组合对象。
        
        Returns:
            完整的投资组合对象，包含所有资产信息
            
        Raises:
            RepositoryError: 当加载操作失败时抛出异常
        """
        pass
    
    @abstractmethod
    def save_portfolio(self, portfolio: Portfolio) -> None:
        """将投资组合保存到存储中。
        
        将投资组合对象序列化并保存到指定的存储位置。
        
        Args:
            portfolio: 要保存的投资组合对象
            
        Raises:
            RepositoryError: 当保存操作失败时抛出异常
        """
        pass
    
    @abstractmethod
    def save_next_month_portfolio(self, portfolio_data: Dict[str, List[Dict[str, Any]]]) -> None:
        """保存下月投资组合模板数据。
        
        将生成的下月投资组合模板数据保存到指定位置，
        通常用于为下个月的资产管理提供基础数据。
        
        Args:
            portfolio_data: 下月投资组合的字典数据格式
            
        Raises:
            RepositoryError: 当保存操作失败时抛出异常
        """
        pass


class RepositoryError(Exception):
    """数据仓库操作异常。
    
    用于表示资产数据的加载、保存等操作中发生的错误。
    
    Attributes:
        message: 错误消息
        cause: 引起此异常的原始异常（可选）
    """
    
    def __init__(self, message: str, cause: Exception = None):
        """初始化仓库异常。
        
        Args:
            message: 错误消息描述
            cause: 引起此异常的原始异常，可选
        """
        super().__init__(message)
        self.message = message
        self.cause = cause
    
    def __str__(self) -> str:
        if self.cause:
            return f"RepositoryError: {self.message} (caused by: {self.cause})"
        return f"RepositoryError: {self.message}"