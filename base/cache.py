import configparser
import os
import threading
from collections import OrderedDict


CONFIG_FILE = os.path.join("config/cache.ini")

# 解析配置文件
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

# 获取配置值
maximum_of_results_cached = int(config['cache']['maximum_of_results_cached'])

# 全局缓存字典和锁
_global_cache = {}
_cache_lock = threading.Lock()

class SingletonLRUCache:
    def __init__(self, maxsize=maximum_of_results_cached):
        self.cache = OrderedDict()
        self.maxsize = maxsize
        self._lock = threading.Lock()

    def get(self, key):
        with self._lock:
            return self.cache.pop(key, None) if key in self.cache else None

    def set(self, key, value):
        with self._lock:
            if len(self.cache) >= self.maxsize:
                self.cache.popitem(last=False)  # 弹出最老的项
            self.cache[key] = value

    def clear(self):
        with self._lock:
            self.cache.clear()

# 获取单例缓存实例
def get_singleton_cache():
    if '_singleton_cache' not in _global_cache:
        with _cache_lock:
            if '_singleton_cache' not in _global_cache:
                _global_cache['_singleton_cache'] = SingletonLRUCache()
    return _global_cache['_singleton_cache']

class Cache:
    # 装饰器函数
    @staticmethod
    def lru_cache_decorator(maxsize=maximum_of_results_cached):
        """
        用于昂贵的纯函数计算结果的缓存。
        :param maxsize: 不推荐使用自定义变量，会从配置cache.ini中获取最大缓存数量
        maximum_of_results_cached
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                # 生成唯一的缓存键
                cache_key = (func.__name__, args, tuple(sorted(kwargs.items())))
                # 获取单例缓存实例
                _cache = get_singleton_cache()
                # 尝试从缓存中获取结果
                result = _cache.get(cache_key)
                if result is not None:
                    return result
                # 如果缓存未命中，则计算函数结果并存储到缓存中
                result = func(*args, **kwargs)
                _cache.set(cache_key, result)
                return result
            return wrapper
        return decorator

cache = Cache()

if __name__ == '__main__':
    # 使用装饰器
    @cache.lru_cache_decorator(maxsize=128)  # 可以为不同的函数设置不同的maxsize
    def expensive_function_1(x, y):
        print(f"Computing expensive_function_1({x}, {y})...")
        # 模拟昂贵的计算
        return x + y

    @cache.lru_cache_decorator()  # 使用默认maxsize
    def expensive_function_2(a, b, c=1):
        print(f"Computing expensive_function_2({a}, {b}, {c})...")
        # 模拟昂贵的计算
        return a * b + c

    # 测试
    print(expensive_function_1(2, 3))  # 计算并缓存结果
    print(expensive_function_1(2, 3))  # 从缓存中获取结果
    print(expensive_function_2(4, 5, 2))  # 计算并缓存结果
    print(expensive_function_2(4, 5, c=2))  # 从缓存中获取结果（注意：kwargs的顺序不影响缓存键）