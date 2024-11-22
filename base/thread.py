
from threading import Lock
from functools import wraps
import os
import configparser
from concurrent.futures import ThreadPoolExecutor
import threading
import functools
import atexit

# 配置文件路径
CONFIG_FILE = os.path.join("config/thread.ini")

# 解析配置文件
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

# 获取配置值
not_used_cpu_num = int(config['thread']['thread_pool_not_used_cpu_num'])
used_cpu_percentage = float(config['thread']['thread_pool_used_cpu_percentage'])

# 获取CPU数量
cpu_count = os.cpu_count()

# 计算两种方式的线程池大小
pool_size_1 = cpu_count - not_used_cpu_num
pool_size_2 = int(used_cpu_percentage / 100 * cpu_count)

# 选择较大的线程池大小，但不超过cpu数量的若干倍（这里假设不超过100倍作为示例）
# 如果used_cpu_percentage非常大，可能会导致线程池大小远超实际CPU数量，这需要根据实际需求调整
max_multiplier = 100  # 最大倍数，可以根据实际情况调整
pool_size = max(pool_size_1, pool_size_2)
if used_cpu_percentage > 100:
    # 如果百分比超过100，则允许线程池大小超过CPU数量，但不超过最大倍数
    pool_size = min(pool_size, int(max_multiplier * cpu_count))
else:
    # 如果百分比不超过100，则线程池大小不会超过CPU数量（除非not_used_cpu_num导致减少）
    pool_size = min(pool_size, cpu_count)


class ThreadPoolManager:
    _instance = None  # 类变量，用于存储单例实例
    _lock = Lock()    # 锁，用于线程安全地创建单例
    _executor = None  # 线程池执行器

    def __new__(cls, *args, **kwargs):
        # 使用锁来确保线程安全地创建单例
        with cls._lock:
            if not cls._instance:
                cls._instance = super(ThreadPoolManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # 注意：由于我们使用了单例模式，这个方法在第一次实例化后不会再被调用
        if self._executor is None:
            self._executor = ThreadPoolExecutor(max_workers=pool_size)

    def submit_task(self, fn, *args, **kwargs):
        """
        提交任务到线程池中
        """
        # 提交任务到线程池，并返回Future对象
        future = self._executor.submit(fn, *args, **kwargs)
        return future

    def shutdown_thread_pool(self, wait=True):
        # 关闭线程池，等待所有任务完成（如果wait=True）
        from project import logger
        logger.info('关闭线程池：等待线程结束')
        self._executor.shutdown(wait=True)
        logger.info('关闭线程池：成功')
    def submit_to_thread_pool(self,fn):
        """

        :param fn: 被装饰的函数，在执行时会会被添加到线程池中运行
        :return: None
        """
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # 提交任务到线程池，不阻塞主线程
            future = self._instance.submit_task(fn, *args, **kwargs)
            # 可以选择返回Future对象，但在这个例子中我们直接返回None
            # 因为我们的目标是不阻塞主线程，并且不等待任务完成
            return None
        return wrapper

    @staticmethod
    def run_in_separate_thread(func):
        """
        :param func: 被装饰的函数，在执行时会立即开一个单独的线程进行执行
        :return: None
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 创建一个新的线程来执行被装饰的函数
            thread = threading.Thread(target=func, args=args, kwargs=kwargs)
            # 设置守护线程，这样主线程结束时，守护线程也会结束
            thread.daemon = True
            # 启动线程
            thread.start()
            # 立即返回 None
            return None

        return wrapper



#线程池
tp = ThreadPoolManager()
#退出程序时自动运行
atexit.register(tp.shutdown_thread_pool)

if __name__ == "__main__":
    @tp.submit_to_thread_pool
    def example_task(name, duration):
        import time
        print(f"Task {name} started")
        time.sleep(duration)  # 模拟耗时操作
        print(f"Task {name} completed")
    # 提交任务到线程池，不会阻塞主线程
    example_task("Task1", 2)
    example_task("Task2", 3)
    example_task("Task3", 1)
    # 使用装饰器
    @tp.run_in_separate_thread
    def some_function(x, y):
        print(f"Executing some_function with x={x}, y={y}")
        # 模拟一些工作
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
    tp.shutdown_thread_pool()
    #通过对象管理器调用om
    #    from project import om
    #    @(om.get("tp")).submit_to_thread_pool