import atexit
import configparser
import functools
import os
import threading
from concurrent.futures import ThreadPoolExecutor, CancelledError, TimeoutError
from functools import wraps
from threading import Lock

from project import logger
# # # 配置文件路径
# CONFIG_FILE = os.path.join("config/thread.ini")
#
# # 解析配置文件
# config = configparser.ConfigParser()
# config.read(CONFIG_FILE)
from project import config
# 获取配置值
not_used_cpu_num = int(config['thread']['thread_pool_not_used_cpu_num'])
used_cpu_percentage = float(config['thread']['thread_pool_used_cpu_percentage'])
timeout = int(config['thread']['timeout'])

# not_used_cpu_num = 0
# used_cpu_percentage = 100
# timeout = 120
# 获取CPU数量
cpu_count = os.cpu_count()

# 计算两种方式的线程池大小
pool_size_1 = cpu_count - not_used_cpu_num
pool_size_2 = int(used_cpu_percentage / 100 * cpu_count)

max_multiplier = 100  # 最大倍数，可以根据实际情况调整
pool_size = max(pool_size_1, pool_size_2)
if used_cpu_percentage > 100:
    pool_size = min(pool_size, int(max_multiplier * cpu_count))
else:
    pool_size = min(pool_size, cpu_count)


class ThreadPoolManager:
    _instance = None  # 类变量，用于存储单例实例
    _lock = Lock()    # 锁，用于线程安全地创建单例
    _executor = None  # 线程池执行器

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                cls._instance = super(ThreadPoolManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._executor is None:
            self._executor = ThreadPoolExecutor(max_workers=pool_size)

    def submit_task(self, fn, *args, _timeout=None, **kwargs):
        """
        提交任务到线程池中，并可选地设置超时时间。
        """
        future = self._executor.submit(fn, *args, **kwargs)
        if _timeout is not None:
            try:
                _result = future.result(timeout=_timeout)
            except TimeoutError:
                future.cancel()  # 任务超时，尝试取消任务
                raise TimeoutError(f"任务 {fn.__name__} 超时，执行时间 {_timeout} seconds")
            except CancelledError:
                raise CancelledError(f"任务 {fn.__name__} ")
            except Exception as e:
                from project import logger
                logger.warning("线程池发生错误:", e)
                raise e

            else:
                return _result
        else:
            return future

    def shutdown_thread_pool(self, wait=True):
        from project import logger
        logger.info('关闭线程池：等待线程结束')
        self._executor.shutdown(wait=True)
        logger.info('关闭线程池：成功')

    def submit_to_thread_pool(self, fn):
        """
        装饰器，将函数提交到线程池中执行。
        """
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # 提交任务到线程池，不阻塞主线程，使用默认超时时间
            try:
                self.submit_task(fn, *args, **kwargs, _timeout=timeout)
            except (TimeoutError, CancelledError, Exception) as e:
                print(f"Error executing task {fn.__name__}: {e}")
            return None
        return wrapper

    @staticmethod
    def run_in_separate_thread(func):
        """
        装饰器，立即在新的线程中执行函数。
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            thread = threading.Thread(target=func, args=args, kwargs=kwargs)
            thread.daemon = True
            thread.start()
            return None
        return wrapper


# 线程池
tp = ThreadPoolManager()
# 退出程序时自动运行
atexit.register(tp.shutdown_thread_pool)

if __name__ == "__main__":
    @tp.submit_to_thread_pool
    def example_task(name, duration):
        import time
        print(f"Task {name} started")
        time.sleep(duration)  # 模拟耗时操作
        print(f"Task {name} completed")

    # 提交任务到线程池，不会阻塞主线程
    example_task("Task1", 3)
    example_task("Task2", 15)  # 这个任务会超时
    example_task("Task3", 1)

    # 使用装饰器
    @tp.run_in_separate_thread
    def some_function(x, y):
        print(f"Executing some_function with x={x}, y={y}")
        import time
        time.sleep(5)
        print(f"some_function finished with x={x}, y={y}")

    # 调用被装饰的函数
    result = some_function(1, 2)
    print(f"Result of some_function: {result}")  # 这将打印 None，因为函数在另一个线程中执行

    # 主线程继续执行，不会等待 some_function 完成
    print("Main thread continues...")

    # 注意：在实际应用中，你需要在程序结束时关闭线程池。
    # 这可以通过在程序的主要退出点（如主函数的末尾）调用ThreadPoolManager的shutdown_thread_pool方法来实现。
    # 在这个示例中，为了演示功能，我们手动在程序末尾调用它。
    # 但是，在更复杂的应用中，你可能需要使用atexit模块或其他机制来确保线程池在程序退出时被正确关闭。