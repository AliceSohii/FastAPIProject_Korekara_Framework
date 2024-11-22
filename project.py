from base.object_manager import ObjectManager
from base.logger import logger


#初始化过程

"""
    通过 om 变量，可以访问 ObjectManager 类提供的所有方法
    如 store(), get(), search(), delete(), update(), 和 get_by_type()。
"""
logger.info("初始化:实例化全局对象管理器om")
om = ObjectManager()
logger.info("初始化:实例化全局对象管理器om完成")
om.store("logger",logger)
logger.info("初始化:注册日志器到om")
logger.info("初始化:实例化全局对象管理器om完成")
logger.info("初始化:创建线程池")
from base.thread import tp,pool_size
logger.info(f"初始化:创建线程池,最大线程数量{pool_size}")
om.store("tp",tp)
logger.info("初始化:注册线程池到om完成")




