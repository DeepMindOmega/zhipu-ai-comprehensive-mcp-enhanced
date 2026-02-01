#!/usr/bin/env python3
"""
错误处理模块
提供统一的错误处理和友好的错误消息
"""

import logging
from typing import Dict, Any, Optional, Callable, Union
from enum import Enum
import json


class ErrorCode(Enum):
    """错误代码枚举"""

    # 通用错误
    UNKNOWN_ERROR = 1000
    INVALID_REQUEST = 1001
    MISSING_PARAMETER = 1002
    INVALID_PARAMETER = 1003

    # 认证错误
    API_KEY_MISSING = 2001
    API_KEY_INVALID = 2002
    UNAUTHORIZED = 2003

    # 服务错误
    SERVICE_UNAVAILABLE = 3001
    TIMEOUT_ERROR = 3002
    RATE_LIMIT_EXCEEDED = 3003

    # 功能特定错误
    WEB_SEARCH_FAILED = 4001
    WEB_CONTENT_NOT_ACCESSIBLE = 4002
    REPOSITORY_NOT_FOUND = 4003
    IMAGE_PROCESSING_FAILED = 4004
    TEXT_GENERATION_FAILED = 4005


class MCPError(Exception):
    """MCP服务器基础异常类"""

    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.UNKNOWN_ERROR,
        details: Optional[Dict[str, Any]] = None,
        original_exception: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.original_exception = original_exception

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，便于JSON序列化"""
        return {
            "error": self.message,
            "error_code": self.error_code.value,
            "error_type": self.error_code.name,
            "details": self.details,
        }

    def __str__(self) -> str:
        return f"[{self.error_code.name}] {self.message}"


class ErrorHandler:
    """错误处理器"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)

    def handle_exception(
        self,
        exception: Exception,
        context: Optional[str] = None,
        user_friendly_message: Optional[str] = None,
    ) -> MCPError:
        """
        将原始异常转换为MCPError

        Args:
            exception: 原始异常
            context: 错误发生的上下文
            user_friendly_message: 用户友好的错误消息

        Returns:
            MCPError实例
        """
        # 记录原始错误
        self.logger.error(
            f"Exception in {context or 'unknown context'}: {str(exception)}"
        )

        # 根据异常类型创建相应的MCPError
        if isinstance(exception, MCPError):
            return exception

        if isinstance(exception, ConnectionError):
            return MCPError(
                message=user_friendly_message or "网络连接错误",
                error_code=ErrorCode.SERVICE_UNAVAILABLE,
                details={"original_error": str(exception)},
                original_exception=exception,
            )

        if isinstance(exception, TimeoutError):
            return MCPError(
                message=user_friendly_message or "请求超时",
                error_code=ErrorCode.TIMEOUT_ERROR,
                details={"original_error": str(exception)},
                original_exception=exception,
            )

        if isinstance(exception, json.JSONDecodeError):
            return MCPError(
                message=user_friendly_message or "JSON解析错误",
                error_code=ErrorCode.INVALID_REQUEST,
                details={"original_error": str(exception)},
                original_exception=exception,
            )

        if isinstance(exception, ValueError):
            return MCPError(
                message=user_friendly_message or "输入值无效",
                error_code=ErrorCode.INVALID_PARAMETER,
                details={"original_error": str(exception)},
                original_exception=exception,
            )

        # 默认处理
        return MCPError(
            message=user_friendly_message or "处理请求时发生未知错误",
            error_code=ErrorCode.UNKNOWN_ERROR,
            details={"original_error": str(exception)},
            original_exception=exception,
        )

    def create_error_response(
        self, error: Union[Exception, MCPError], context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建错误响应

        Args:
            error: 错误对象
            context: 错误上下文

        Returns:
            错误响应字典
        """
        if not isinstance(error, MCPError):
            error = self.handle_exception(error, context)

        response = error.to_dict()
        response["success"] = False
        response["context"] = context

        return response


def error_handler_decorator(
    error_handler: ErrorHandler,
    context: str,
    user_friendly_message: Optional[str] = None,
    return_dict: bool = True,
):
    """
    错误处理装饰器

    Args:
        error_handler: 错误处理器实例
        context: 错误上下文
        user_friendly_message: 用户友好的错误消息
        return_dict: 是否返回字典格式的错误响应
    """

    def decorator(func: Callable):
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if return_dict:
                    return error_handler.create_error_response(e, context)
                else:
                    raise error_handler.handle_exception(
                        e, context, user_friendly_message
                    )

        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if return_dict:
                    return error_handler.create_error_response(e, context)
                else:
                    raise error_handler.handle_exception(
                        e, context, user_friendly_message
                    )

        # 判断函数是否是协程函数
        import inspect

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# 预定义的错误消息
ERROR_MESSAGES = {
    ErrorCode.API_KEY_MISSING: "需要提供有效的智谱AI API密钥",
    ErrorCode.API_KEY_INVALID: "提供的API密钥无效",
    ErrorCode.WEB_SEARCH_FAILED: "网络搜索失败，请稍后重试",
    ErrorCode.WEB_CONTENT_NOT_ACCESSIBLE: "无法访问网页内容，请检查URL是否正确",
    ErrorCode.REPOSITORY_NOT_FOUND: "找不到指定的代码仓库，请检查仓库URL是否正确",
    ErrorCode.IMAGE_PROCESSING_FAILED: "图像处理失败，请确保图像格式正确",
    ErrorCode.TEXT_GENERATION_FAILED: "文本生成失败，请稍后重试",
    ErrorCode.RATE_LIMIT_EXCEEDED: "请求频率过高，请稍后重试",
}


def get_error_message(error_code: ErrorCode) -> str:
    """获取预定义的错误消息"""
    return ERROR_MESSAGES.get(error_code, "未知错误")


# 创建默认错误处理器
default_error_handler = ErrorHandler()
