#!/usr/bin/env python3
"""
缓存模块
提供内存缓存和持久化缓存功能，减少重复的API调用
"""

import json
import hashlib
import time
import os
from typing import Dict, Any, Optional, Union, Callable
from pathlib import Path
import threading
from collections import OrderedDict


class CacheEntry:
    """缓存条目"""

    def __init__(self, value: Any, ttl: Optional[int] = None):
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
        self.access_count = 1
        self.last_accessed = self.created_at

    def is_expired(self) -> bool:
        """检查缓存是否过期"""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl

    def touch(self):
        """更新访问时间和次数"""
        self.access_count += 1
        self.last_accessed = time.time()


class MemoryCache:
    """内存缓存，支持LRU策略"""

    def __init__(self, max_size: int = 100, default_ttl: Optional[int] = None):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = {"args": args, "kwargs": sorted(kwargs.items())}
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"{prefix}:{key_hash}"

    def get(self, prefix: str, *args, **kwargs) -> Optional[Any]:
        """获取缓存值"""
        key = self._generate_key(prefix, *args, **kwargs)

        with self._lock:
            if key not in self._cache:
                return None

            entry = self._cache[key]

            # 检查是否过期
            if entry.is_expired():
                del self._cache[key]
                return None

            # 更新访问信息
            entry.touch()
            return entry.value

    def set(
        self, prefix: str, value: Any, ttl: Optional[int] = None, *args, **kwargs
    ) -> None:
        """设置缓存值"""
        key = self._generate_key(prefix, *args, **kwargs)
        ttl = ttl or self.default_ttl
        entry = CacheEntry(value, ttl)

        with self._lock:
            # 如果缓存已满，删除最旧的条目
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._evict_oldest()

            self._cache[key] = entry

    def _evict_oldest(self):
        """淘汰最旧的缓存条目"""
        oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].last_accessed)
        del self._cache[oldest_key]

    def clear(self, prefix_filter: Optional[str] = None) -> None:
        """清除缓存"""
        with self._lock:
            if prefix_filter:
                keys_to_remove = [
                    k for k in self._cache.keys() if k.startswith(f"{prefix_filter}:")
                ]
                for key in keys_to_remove:
                    del self._cache[key]
            else:
                self._cache.clear()

    def size(self) -> int:
        """获取缓存大小"""
        return len(self._cache)

    def stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        with self._lock:
            total_entries = len(self._cache)
            total_accesses = sum(entry.access_count for entry in self._cache.values())

            return {
                "total_entries": total_entries,
                "total_accesses": total_accesses,
                "average_accesses": total_accesses / total_entries
                if total_entries > 0
                else 0,
                "max_size": self.max_size,
                "memory_usage": total_entries,
            }


class FileCache:
    """文件缓存，支持持久化"""

    def __init__(self, cache_dir: str = "cache", default_ttl: Optional[int] = None):
        self.cache_dir = Path(cache_dir)
        self.default_ttl = default_ttl
        self.cache_dir.mkdir(exist_ok=True)
        self._lock = threading.RLock()

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """生成缓存键"""
        key_data = {"args": args, "kwargs": sorted(kwargs.items())}
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"{prefix}:{key_hash}"

    def _get_cache_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f"{key}.json"

    def get(self, prefix: str, *args, **kwargs) -> Optional[Any]:
        """获取缓存值"""
        key = self._generate_key(prefix, *args, **kwargs)
        cache_path = self._get_cache_path(key)

        with self._lock:
            if not cache_path.exists():
                return None

            try:
                with open(cache_path, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)

                # 检查是否过期
                ttl = cache_data.get("ttl") or self.default_ttl
                if ttl and time.time() - cache_data["created_at"] > ttl:
                    cache_path.unlink()  # 删除过期缓存
                    return None

                # 更新访问信息
                cache_data["access_count"] = cache_data.get("access_count", 0) + 1
                cache_data["last_accessed"] = time.time()

                # 保存更新的访问信息
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(cache_data, f)

                return cache_data["value"]

            except Exception:
                # 如果读取失败，尝试删除损坏的缓存文件
                try:
                    cache_path.unlink()
                except Exception:
                    pass
                return None

    def set(
        self, prefix: str, value: Any, ttl: Optional[int] = None, *args, **kwargs
    ) -> None:
        """设置缓存值"""
        key = self._generate_key(prefix, *args, **kwargs)
        cache_path = self._get_cache_path(key)

        cache_data = {
            "value": value,
            "created_at": time.time(),
            "ttl": ttl or self.default_ttl,
            "access_count": 1,
            "last_accessed": time.time(),
        }

        with self._lock:
            try:
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(cache_data, f)
            except Exception:
                pass  # 忽略写入错误

    def clear(self, prefix_filter: Optional[str] = None) -> None:
        """清除缓存"""
        with self._lock:
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    if prefix_filter:
                        with open(cache_file, "r", encoding="utf-8") as f:
                            key = cache_file.stem
                            if not key.startswith(f"{prefix_filter}:"):
                                continue
                    cache_file.unlink()
                except Exception:
                    pass

    def cleanup_expired(self) -> int:
        """清理过期缓存文件，返回清理的文件数量"""
        cleaned = 0

        with self._lock:
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        cache_data = json.load(f)

                    ttl = cache_data.get("ttl") or self.default_ttl
                    if ttl and time.time() - cache_data["created_at"] > ttl:
                        cache_file.unlink()
                        cleaned += 1
                except Exception:
                    try:
                        cache_file.unlink()
                        cleaned += 1
                    except Exception:
                        pass

        return cleaned

    def size(self) -> int:
        """获取缓存文件数量"""
        return len(list(self.cache_dir.glob("*.json")))

    def stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_files = 0
        total_size = 0
        total_accesses = 0

        with self._lock:
            for cache_file in self.cache_dir.glob("*.json"):
                total_files += 1
                total_size += cache_file.stat().st_size

                try:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        cache_data = json.load(f)
                    total_accesses += cache_data.get("access_count", 0)
                except Exception:
                    pass

        return {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "total_accesses": total_accesses,
            "average_accesses": total_accesses / total_files if total_files > 0 else 0,
        }


class HybridCache:
    """混合缓存，结合内存缓存和文件缓存"""

    def __init__(
        self,
        cache_dir: str = "cache",
        memory_max_size: int = 50,
        default_ttl: Optional[int] = None,
    ):
        self.memory_cache = MemoryCache(memory_max_size, default_ttl)
        self.file_cache = FileCache(cache_dir, default_ttl)

    def get(self, prefix: str, *args, **kwargs) -> Optional[Any]:
        """获取缓存值，先查内存缓存，再查文件缓存"""
        # 先检查内存缓存
        value = self.memory_cache.get(prefix, *args, **kwargs)
        if value is not None:
            return value

        # 再检查文件缓存
        value = self.file_cache.get(prefix, *args, **kwargs)
        if value is not None:
            # 将文件缓存的值加载到内存缓存
            self.memory_cache.set(prefix, value, *args, **kwargs)
            return value

        return None

    def set(
        self, prefix: str, value: Any, ttl: Optional[int] = None, *args, **kwargs
    ) -> None:
        """设置缓存值，同时写入内存缓存和文件缓存"""
        self.memory_cache.set(prefix, value, ttl, *args, **kwargs)
        self.file_cache.set(prefix, value, ttl, *args, **kwargs)

    def clear(self, prefix_filter: Optional[str] = None) -> None:
        """清除所有缓存"""
        self.memory_cache.clear(prefix_filter)
        self.file_cache.clear(prefix_filter)

    def cleanup_expired(self) -> int:
        """清理过期缓存"""
        return self.file_cache.cleanup_expired()

    def stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        return {
            "memory_cache": self.memory_cache.stats(),
            "file_cache": self.file_cache.stats(),
        }


def cache_decorator(
    cache: Union[MemoryCache, FileCache, HybridCache],
    prefix: str,
    ttl: Optional[int] = None,
    use_args: bool = True,
):
    """
    缓存装饰器

    Args:
        cache: 缓存实例
        prefix: 缓存键前缀
        ttl: 过期时间（秒）
        use_args: 是否使用函数参数作为缓存键的一部分
    """

    def decorator(func: Callable):
        async def async_wrapper(*args, **kwargs):
            # 如果使用参数生成键
            cache_args = args[1:] if use_args else ()  # 跳过self参数
            cache_kwargs = kwargs if use_args else {}

            # 尝试从缓存获取
            cached_result = cache.get(prefix, *cache_args, **cache_kwargs)
            if cached_result is not None:
                return cached_result

            # 执行函数
            result = await func(*args, **kwargs)

            # 存储到缓存
            cache.set(prefix, result, ttl, *cache_args, **cache_kwargs)
            return result

        def sync_wrapper(*args, **kwargs):
            # 如果使用参数生成键
            cache_args = args[1:] if use_args else ()  # 跳过self参数
            cache_kwargs = kwargs if use_args else {}

            # 尝试从缓存获取
            cached_result = cache.get(prefix, *cache_args, **cache_kwargs)
            if cached_result is not None:
                return cached_result

            # 执行函数
            result = func(*args, **kwargs)

            # 存储到缓存
            cache.set(prefix, result, ttl, *cache_args, **cache_kwargs)
            return result

        # 判断函数是否是协程函数
        import inspect

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# 创建默认缓存实例
default_cache = HybridCache()
