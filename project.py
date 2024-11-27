import atexit

from base.database.space import get_main_sql_session
from base.object_manager import ObjectManager
from base.logger import logger

from base.plugins import load_plugins

#初始化过程

################## 对象管理器 om ##################
logger.info("初始化:实例化全局对象管理器om")
om = ObjectManager()
#注意无法使用om.get("om")获得om，这会导致未来的递归操作出现问题。当然也不太可能出现这种这种需求，我问我在哪里。哈哈哈
logger.info("初始化:实例化全局对象管理器om完成")

om.store("logger",logger)
logger.info("初始化:注册日志器到om完成")

################# 线程池 tp ###################
logger.info("初始化:创建线程池" )
from base.thread import tp,pool_size
logger.info(f"初始化:创建线程池,最大线程数量{pool_size}")
om.store("tp",tp)
logger.info(f"初始化:创建线程池完成")

################## 缓存 cache ###################
logger.info(f"初始化:创建昂贵计算缓存池")
from base.cache import cache, maximum_of_results_cached
logger.info(f"初始化:创建昂贵计算缓存池,最大缓存数量{maximum_of_results_cached}")

om.store("cache",cache)
logger.info("初始化:注册昂贵计算缓存池到om完成")

################### 初始化表单数据库 ###################
logger.info("初始化:多表单数据库")
from base.database.space import mt_db, get_sql_base_class, create_all_tables

logger.info("初始化:连接simple_table_01表单数据库")
mt_db.ensure_table_exists("simple_table_01")

mt_db["simple_table_01"].insert("say","nihao")
mt_db["simple_table_01"].get("say")
mt_db["simple_table_01"].delete("say")
logger.info("初始化:连接simple_table_01表单数据库成功")

logger.info("初始化:连接simple_table_02表单数据库")
mt_db.ensure_table_exists("simple_table_02")
mt_db["simple_table_02"].insert("say","nihao")
mt_db["simple_table_02"].get("say")
mt_db["simple_table_02"].delete("say")
logger.info("初始化:连接simple_table_02表单数据库成功")

om.store("mt_db",mt_db)
logger.info("初始化:注册多表单数据库到对象管理器完成")

################### 初始化Sql 数据库 ###################

from base.database.space import init_sql_engine
logger.info("初始化:主sql数据库引擎初始化")
sql_db = None
sql_base_class = None
main_sql_session = None
try:
    sql_db = init_sql_engine()
    logger.info("初始化:主sql数据库引擎创建成功")
    om.store("sql_db",sql_db)
    logger.info("初始化:注册主sql数据库引擎到对象管理器完成")
    sql_base_class = get_sql_base_class()
    om.store("sql_base_class",sql_base_class)
    logger.info("初始化:表基类注册到对象管理器完成")
    create_all_tables(sql_db)
    logger.info("创建所有表成功")
    logger.info("初始化:获取数据库主对话")
    main_sql_session = get_main_sql_session()
    om.store("sql_db",main_sql_session)
    logger.info("初始化:获取数据库主对话对象到对象管理器完成")
except:
    logger.info("初始化:注册主sql数据库引擎到对象管理器失败")



################### 插件 plugins ###################
logger.info("初始化:插件加载")
plugins_list = load_plugins()
# 输出加载了几个插件的汇总消息
logger.info(f"初始化:加载了{len(plugins_list)}个插件:")
# 遍历插件列表，每行列出一个插件的名称和版本
for plugin in plugins_list:
    plugin_info = plugin.get_info()
    logger.info(f"  - {plugin_info.name}，版本：{plugin_info.version}")

logger.info("初始化:插件加载完成")





