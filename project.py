from base.object_manager import ObjectManager
from base.logger import logger


#初始化过程

"""
    通过 om 变量，可以访问 ObjectManager 类提供的所有方法
    如 store(), get(), search(), delete(), update(), 和 get_by_type()。
"""
logger.info("初始化:实例化全局对象管理器om")
om = ObjectManager()
#注意无法使用om.get("om")获得om，这会导致未来的递归操作出现问题。当然也不太可能出现这种这种需求，我问我在哪里。哈哈哈
logger.info("初始化:实例化全局对象管理器om完成")

om.store("logger",logger)
logger.info("初始化:注册日志器到om完成")

logger.info("初始化:创建线程池")
from base.thread import tp,pool_size
logger.info(f"初始化:创建线程池,最大线程数量{pool_size}")
om.store("tp",tp)
logger.info(f"初始化:创建线程池完成")

logger.info(f"初始化:创建昂贵计算缓存池")
from base.cache import cache, maximum_of_results_cached
logger.info(f"初始化:创建昂贵计算缓存池,最大缓存数量{maximum_of_results_cached}")

om.store("cache",cache)
logger.info("初始化:注册昂贵计算缓存池到om完成")




