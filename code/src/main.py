#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@Author  :  lcn29
@Software:  PyCharm
@File    :  main.py
@Time    :  2025-08-22
@Desc    :  重构后的应用主入口
"""

import sys
import argparse
from pathlib import Path

from loguru import logger

from infrastructure.config.application_config import ApplicationConfig


def setup_logging(debug: bool = False):
    """配置应用程序的日志记录系统。
    
    移除默认日志配置并设置自定义的日志格式和级别。
    
    Args:
        debug: 是否启用调试模式，True时日志级别为DEBUG，False时为INFO
    """
    logger.remove()  # 移除默认配置
    
    log_level = "DEBUG" if debug else "INFO"
    log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    
    logger.add(sys.stdout, level=log_level, format=log_format)


def analyze_portfolio(config: ApplicationConfig, output_format: str = 'text'):
    """执行投资组合分析操作。
    
    创建分析用例并执行完整的投资组合盈亏分析流程，
    将结果输出到控制台。
    
    Args:
        config: 应用配置对象，包含所有必要的服务配置
        output_format: 输出格式，可选值为'text'、'dict'或'both'
        
    Returns:
        bool: 分析是否成功完成
    """
    logger.info("Starting portfolio analysis...")
    
    use_case = config.get_analyze_portfolio_use_case()
    result = use_case.execute(output_format)
    
    if result['success']:
        logger.info("Portfolio analysis completed successfully")
        
        # 输出结果
        if 'report_text' in result:
            print("\n" + result['report_text'])
        
        if 'portfolio_summary' in result and result['portfolio_summary']:
            summary = result['portfolio_summary']
            print(f"\n投资组合概要:")
            print(f"  总资产数量: {summary['total_assets']}")
            print(f"  资产类型数量: {summary['asset_types']}")
            print(f"  资产类型分布: {summary['asset_type_breakdown']}")
        
        return True
    else:
        logger.error(f"Portfolio analysis failed: {result.get('error', 'Unknown error')}")
        return False


def generate_next_month_template(config: ApplicationConfig):
    """生成下月资产配置模板。
    
    创建模板生成用例并执行下月配置模板的生成流程，
    将统计信息输出到控制台。
    
    Args:
        config: 应用配置对象，包含所有必要的服务配置
        
    Returns:
        bool: 模板生成是否成功完成
    """
    logger.info("Starting next month template generation...")
    
    use_case = config.get_generate_template_use_case()
    result = use_case.execute()
    
    if result['success']:
        logger.info("Next month template generation completed successfully")
        
        # 输出统计信息
        if 'statistics' in result and result['statistics']:
            stats = result['statistics']
            print(f"\n下月模板生成完成:")
            print(f"  总资产数量: {stats['total_assets']}")
            print(f"  资产类型数量: {stats['asset_types_count']}")
            print(f"  资产类型分布: {stats['asset_type_breakdown']}")
        
        return True
    else:
        logger.error(f"Template generation failed: {result.get('error', 'Unknown error')}")
        return False


def main():
    """应用程序主入口函数。
    
    负责解析命令行参数、配置日志、验证配置、执行相应操作。
    支持以下命令：
    - analyze: 执行投资组合分析
    - template: 生成下月配置模板  
    - both: 同时执行分析和模板生成
    
    命令行参数：
        command: 要执行的命令（analyze/template/both）
        --file/-f: 资产清单YAML文件路径（可选）
        --provider/-p: 汇率提供商（默认为boc_hk）
        --format: 分析结果输出格式（text/dict/both，默认为text）
        --debug: 启用调试日志（可选）
    
    退出码：
        0: 所有操作成功完成
        1: 发生错误或操作失败
    """
    parser = argparse.ArgumentParser(description="Personal Financial Asset Management Tool")
    parser.add_argument('command', choices=['analyze', 'template', 'both'], 
                       help='Command to execute')
    parser.add_argument('--file', '-f', type=str, 
                       help='Asset inventory YAML file path')
    parser.add_argument('--provider', '-p', type=str, default='boc_hk',
                       choices=['boc_hk'], help='Exchange rate provider')
    parser.add_argument('--format', type=str, default='text',
                       choices=['text', 'dict', 'both'], 
                       help='Output format for analysis')
    parser.add_argument('--debug', action='store_true', 
                       help='Enable debug logging')
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.debug)
    
    try:
        # 创建应用配置
        config = ApplicationConfig(
            asset_file_path=args.file,
            exchange_rate_provider=args.provider
        )
        
        # 验证配置
        if not config.validate_configuration():
            logger.error("Configuration validation failed")
            sys.exit(1)
        
        success = True
        
        # 执行命令
        if args.command in ['analyze', 'both']:
            success &= analyze_portfolio(config, args.format)
        
        if args.command in ['template', 'both']:
            success &= generate_next_month_template(config)
        
        if success:
            logger.info("All operations completed successfully")
            sys.exit(0)
        else:
            logger.error("Some operations failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.debug:
            raise
        sys.exit(1)


if __name__ == '__main__':
    main()