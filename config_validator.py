#!/usr/bin/env python3
"""
配置验证模块
用于验证配置文件的有效性和完整性
"""

import json
import os
from typing import Dict, Any, List, Optional, Tuple


class ConfigValidator:
    """配置验证器"""

    REQUIRED_FIELDS = {
        "server": ["host", "port"],
        "zhipu": ["api_key", "default_model", "timeout"],
        "mcp": ["name", "version", "description"],
        "features": [
            "web_search",
            "web_reader",
            "repo_analyzer",
            "vision_analyzer",
            "text_generator",
        ],
    }

    FIELD_TYPES = {
        "server": {"host": str, "port": int, "debug": bool},
        "zhipu": {"api_key": str, "default_model": str, "timeout": int},
        "mcp": {"name": str, "version": str, "description": str},
        "features": {
            "web_search": bool,
            "web_reader": bool,
            "repo_analyzer": bool,
            "vision_analyzer": bool,
            "text_generator": bool,
        },
    }

    @classmethod
    def validate_config(
        cls, config_path: str
    ) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        验证配置文件

        Args:
            config_path: 配置文件路径

        Returns:
            Tuple[是否有效, 错误信息列表, 配置字典]
        """
        errors = []

        # 检查文件是否存在
        if not os.path.exists(config_path):
            errors.append(f"配置文件不存在: {config_path}")
            return False, errors, {}

        # 尝试加载JSON文件
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"配置文件JSON格式错误: {str(e)}")
            return False, errors, {}
        except Exception as e:
            errors.append(f"读取配置文件失败: {str(e)}")
            return False, errors, {}

        # 验证顶级字段
        for section, required_fields in cls.REQUIRED_FIELDS.items():
            if section not in config:
                errors.append(f"缺少配置节: {section}")
                continue

            # 验证必填字段
            for field in required_fields:
                if field not in config[section]:
                    errors.append(f"缺少必填字段: {section}.{field}")

            # 验证字段类型
            if section in cls.FIELD_TYPES:
                for field, expected_type in cls.FIELD_TYPES[section].items():
                    if field in config[section] and not isinstance(
                        config[section][field], expected_type
                    ):
                        errors.append(
                            f"字段类型错误: {section}.{field} 应为 {expected_type.__name__}，实际为 {type(config[section][field]).__name__}"
                        )

        # 特殊验证
        cls._validate_special_fields(config, errors)

        return len(errors) == 0, errors, config

    @classmethod
    def _validate_special_fields(
        cls, config: Dict[str, Any], errors: List[str]
    ) -> None:
        """验证特殊字段"""
        # 验证端口号范围
        if "server" in config and "port" in config["server"]:
            port = config["server"]["port"]
            if not (1 <= port <= 65535):
                errors.append(f"无效的端口号: {port}，应在1-65535范围内")

        # 验证API密钥不为占位符
        if "zhipu" in config and "api_key" in config["zhipu"]:
            api_key = config["zhipu"]["api_key"]
            placeholder_values = [
                "输入你的智谱api insert your api here",
                "YOUR_ZHIPU_API_KEY_HERE",
                "",
            ]
            if api_key in placeholder_values:
                errors.append("API密钥为占位符，请设置有效的智谱AI API密钥")

        # 验证超时设置
        if "zhipu" in config and "timeout" in config["zhipu"]:
            timeout = config["zhipu"]["timeout"]
            if timeout <= 0:
                errors.append(f"无效的超时设置: {timeout}，应大于0")

    @classmethod
    def create_default_config(cls, output_path: str) -> bool:
        """
        创建默认配置文件

        Args:
            output_path: 输出文件路径

        Returns:
            是否成功创建
        """
        default_config = {
            "server": {
                "host": "localhost",
                "port": 8000,
                "debug": False,
            },
            "zhipu": {
                "api_key": "YOUR_ZHIPU_API_KEY_HERE",
                "default_model": "glm-4",
                "timeout": 30,
            },
            "mcp": {
                "name": "zhipu-comprehensive-mcp",
                "version": "1.0.0",
                "description": "智谱AI综合性MCP服务器，提供多种AI能力",
            },
            "features": {
                "web_search": True,
                "web_reader": True,
                "repo_analyzer": True,
                "vision_analyzer": True,
                "text_generator": True,
            },
        }

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"创建默认配置文件失败: {str(e)}")
            return False


if __name__ == "__main__":
    # 测试配置验证器
    import sys

    config_file = "zhipu_comprehensive_config.json"
    if len(sys.argv) > 1:
        config_file = sys.argv[1]

    is_valid, errors, config = ConfigValidator.validate_config(config_file)

    if is_valid:
        print("✓ 配置文件验证通过")
    else:
        print("✗ 配置文件验证失败:")
        for error in errors:
            print(f"  - {error}")
