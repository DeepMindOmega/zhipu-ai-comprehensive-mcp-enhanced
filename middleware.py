#!/usr/bin/env python3
"""
中间件模块
提供身份验证、请求限制、日志记录等中间件功能
"""

import time
import json
import logging
from typing import Dict, Any, Optional, Callable, List
from aiohttp import web, ClientSession, Request, Response
import hashlib
import secrets
from collections import defaultdict, deque


class RateLimiter:
    """请求频率限制器"""

    def __init__(self, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        # 使用字典存储每个客户端的请求时间戳
        self.minute_requests: Dict[str, deque] = defaultdict(deque)
        self.hour_requests: Dict[str, deque] = defaultdict(deque)
        self.logger = logging.getLogger(__name__)

    def is_allowed(self, client_id: str) -> tuple[bool, Dict[str, Any]]:
        """
        检查客户端是否被允许请求

        Returns:
            Tuple[是否允许, 限制信息]
        """
        current_time = time.time()

        # 清理过期的请求记录
        self._cleanup_expired_requests(client_id, current_time)

        # 检查分钟限制
        minute_count = len(self.minute_requests[client_id])
        if minute_count >= self.requests_per_minute:
            oldest_request = self.minute_requests[client_id][0]
            reset_time = oldest_request + 60
            return False, {
                "error": "Rate limit exceeded (per minute)",
                "reset_in": int(reset_time - current_time),
                "limit": self.requests_per_minute,
                "window": "minute",
            }

        # 检查小时限制
        hour_count = len(self.hour_requests[client_id])
        if hour_count >= self.requests_per_hour:
            oldest_request = self.hour_requests[client_id][0]
            reset_time = oldest_request + 3600
            return False, {
                "error": "Rate limit exceeded (per hour)",
                "reset_in": int(reset_time - current_time),
                "limit": self.requests_per_hour,
                "window": "hour",
            }

        # 记录新请求
        self.minute_requests[client_id].append(current_time)
        self.hour_requests[client_id].append(current_time)

        return True, {
            "remaining_minute": self.requests_per_minute - minute_count - 1,
            "remaining_hour": self.requests_per_hour - hour_count - 1,
        }

    def _cleanup_expired_requests(self, client_id: str, current_time: float):
        """清理过期的请求记录"""
        # 清理分钟过期的请求
        while (
            self.minute_requests[client_id]
            and current_time - self.minute_requests[client_id][0] > 60
        ):
            self.minute_requests[client_id].popleft()

        # 清理小时过期的请求
        while (
            self.hour_requests[client_id]
            and current_time - self.hour_requests[client_id][0] > 3600
        ):
            self.hour_requests[client_id].popleft()


class APIKeyAuthenticator:
    """API密钥认证器"""

    def __init__(
        self, valid_api_keys: Optional[List[str]] = None, require_auth: bool = False
    ):
        self.valid_api_keys = set(valid_api_keys or [])
        self.require_auth = require_auth
        self.logger = logging.getLogger(__name__)

    def add_api_key(self, api_key: str):
        """添加有效的API密钥"""
        self.valid_api_keys.add(api_key)

    def remove_api_key(self, api_key: str):
        """移除API密钥"""
        self.valid_api_keys.discard(api_key)

    def authenticate(self, request: Request) -> tuple[bool, Optional[str]]:
        """
        认证请求

        Returns:
            Tuple[是否认证成功, 错误消息]
        """
        if not self.require_auth:
            return True, None

        # 从请求头获取API密钥
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            # 也可以从查询参数获取
            api_key = request.query.get("api_key")

        if not api_key:
            return False, "Missing API key"

        if api_key not in self.valid_api_keys:
            return False, "Invalid API key"

        return True, None


class RequestLogger:
    """请求日志记录器"""

    def __init__(self, logger: Optional[logging.Logger] = None, log_body: bool = False):
        self.logger = logger or logging.getLogger(__name__)
        self.log_body = log_body

    def log_request(
        self,
        request: Request,
        start_time: float,
        status_code: int,
        response_body: Any = None,
    ):
        """记录请求日志"""
        duration = (time.time() - start_time) * 1000  # 转换为毫秒

        log_data = {
            "method": request.method,
            "path": request.path_qs,
            "status": status_code,
            "duration_ms": round(duration, 2),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("User-Agent", ""),
        }

        # 记录请求ID（如果有）
        request_id = request.get("request_id")
        if request_id:
            log_data["request_id"] = request_id

        # 如果需要记录请求体
        if self.log_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = request.json()
                log_data["request_body"] = body
            except Exception:
                log_data["request_body"] = "Could not parse JSON body"

        # 如果需要记录响应体
        if self.log_body and status_code != 200:
            log_data["response_body"] = response_body

        # 记录日志
        if status_code >= 400:
            self.logger.warning(f"Request completed with error: {json.dumps(log_data)}")
        else:
            self.logger.info(f"Request completed: {json.dumps(log_data)}")

    def _get_client_ip(self, request: Request) -> str:
        """获取客户端IP地址"""
        # 检查代理头部
        if "X-Forwarded-For" in request.headers:
            return request.headers["X-Forwarded-For"].split(",")[0].strip()

        if "X-Real-IP" in request.headers:
            return request.headers["X-Real-IP"]

        # 返回直接连接的IP
        return request.remote or "unknown"


class CORSHandler:
    """CORS处理器"""

    def __init__(
        self,
        allowed_origins: Optional[List[str]] = None,
        allowed_methods: Optional[List[str]] = None,
        allowed_headers: Optional[List[str]] = None,
        max_age: int = 86400,
    ):
        self.allowed_origins = allowed_origins or ["*"]
        self.allowed_methods = allowed_methods or [
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "OPTIONS",
        ]
        self.allowed_headers = allowed_headers or [
            "Content-Type",
            "Authorization",
            "X-API-Key",
        ]
        self.max_age = max_age

    def add_cors_headers(self, response: Response, origin: Optional[str] = None):
        """添加CORS头部到响应"""
        # 设置允许的源
        if origin and (origin in self.allowed_origins or "*" in self.allowed_origins):
            response.headers["Access-Control-Allow-Origin"] = origin
        elif "*" in self.allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = "*"

        # 设置其他CORS头部
        response.headers["Access-Control-Allow-Methods"] = ", ".join(
            self.allowed_methods
        )
        response.headers["Access-Control-Allow-Headers"] = ", ".join(
            self.allowed_headers
        )
        response.headers["Access-Control-Max-Age"] = str(self.max_age)

    def handle_preflight(self, request: Request) -> Optional[Response]:
        """处理预检请求"""
        if request.method != "OPTIONS":
            return None

        response = web.Response(status=200)
        self.add_cors_headers(response, request.headers.get("Origin"))
        return response


class SecurityHeaders:
    """安全头部处理器"""

    def __init__(
        self,
        content_type_options: bool = True,
        frame_options: bool = True,
        xss_protection: bool = True,
        hsts: bool = False,
        hsts_max_age: int = 31536000,
    ):
        self.content_type_options = content_type_options
        self.frame_options = frame_options
        self.xss_protection = xss_protection
        self.hsts = hsts
        self.hsts_max_age = hsts_max_age

    def add_security_headers(self, response: Response):
        """添加安全头部到响应"""
        if self.content_type_options:
            response.headers["X-Content-Type-Options"] = "nosniff"

        if self.frame_options:
            response.headers["X-Frame-Options"] = "DENY"

        if self.xss_protection:
            response.headers["X-XSS-Protection"] = "1; mode=block"

        if self.hsts:
            response.headers["Strict-Transport-Security"] = (
                f"max-age={self.hsts_max_age}"
            )


class MiddlewareManager:
    """中间件管理器"""

    def __init__(self):
        self.rate_limiter = RateLimiter()
        self.authenticator = APIKeyAuthenticator()
        self.request_logger = RequestLogger()
        self.cors_handler = CORSHandler()
        self.security_headers = SecurityHeaders()

    def configure_rate_limiting(
        self, requests_per_minute: int = 60, requests_per_hour: int = 1000
    ):
        """配置请求频率限制"""
        self.rate_limiter = RateLimiter(requests_per_minute, requests_per_hour)

    def configure_authentication(
        self, api_keys: Optional[List[str]] = None, require_auth: bool = False
    ):
        """配置API密钥认证"""
        self.authenticator = APIKeyAuthenticator(api_keys, require_auth)

    def configure_logging(
        self, logger: Optional[logging.Logger] = None, log_body: bool = False
    ):
        """配置请求日志"""
        self.request_logger = RequestLogger(logger, log_body)

    def configure_cors(self, allowed_origins: Optional[List[str]] = None):
        """配置CORS"""
        self.cors_handler = CORSHandler(allowed_origins)

    def create_middleware(self):
        """创建中间件函数"""

        @web.middleware
        async def middleware(request: Request, handler: Callable):
            # 生成请求ID
            request_id = secrets.token_hex(8)
            request["request_id"] = request_id

            # 获取客户端IP作为标识
            client_id = self.request_logger._get_client_ip(request)

            start_time = time.time()

            try:
                # 处理CORS预检请求
                cors_response = self.cors_handler.handle_preflight(request)
                if cors_response:
                    return cors_response

                # 应用请求频率限制
                allowed, limit_info = self.rate_limiter.is_allowed(client_id)
                if not allowed:
                    response = web.json_response(
                        {
                            "error": limit_info["error"],
                            "reset_in": limit_info["reset_in"],
                            "request_id": request_id,
                        },
                        status=429,
                    )
                    self.cors_handler.add_cors_headers(
                        response, request.headers.get("Origin")
                    )
                    return response

                # 应用身份验证
                auth_success, auth_error = self.authenticator.authenticate(request)
                if not auth_success:
                    response = web.json_response(
                        {"error": auth_error, "request_id": request_id}, status=401
                    )
                    self.cors_handler.add_cors_headers(
                        response, request.headers.get("Origin")
                    )
                    return response

                # 处理请求
                response = await handler(request)

                # 添加CORS和安全头部
                self.cors_handler.add_cors_headers(
                    response, request.headers.get("Origin")
                )
                self.security_headers.add_security_headers(response)

                # 记录请求日志
                self.request_logger.log_request(request, start_time, response.status)

                # 添加频率限制信息到响应头
                response.headers["X-RateLimit-Remaining-Minute"] = str(
                    limit_info.get("remaining_minute", 0)
                )
                response.headers["X-RateLimit-Remaining-Hour"] = str(
                    limit_info.get("remaining_hour", 0)
                )
                response.headers["X-Request-ID"] = request_id

                return response

            except Exception as e:
                # 记录错误
                self.request_logger.logger.error(
                    f"Unhandled exception in middleware: {str(e)}"
                )

                # 创建错误响应
                error_response = web.json_response(
                    {"error": "Internal server error", "request_id": request_id},
                    status=500,
                )

                # 添加CORS和安全头部
                self.cors_handler.add_cors_headers(
                    error_response, request.headers.get("Origin")
                )
                self.security_headers.add_security_headers(error_response)

                # 记录请求日志
                self.request_logger.log_request(request, start_time, 500, str(e))

                return error_response

        return middleware


# 创建默认中间件管理器
default_middleware = MiddlewareManager()
