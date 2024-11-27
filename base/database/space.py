import configparser
import importlib
import os

from sqlalchemy import Engine
from sqlalchemy.orm import declarative_base

CONFIG_FILE = os.path.join("config/database.ini")

# 解析配置文件
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

# 获取配置值
from base.database.table_db import MultiTableDB

simple_db_dir_path = config['mul_table_db']['mul_table_db_dir_path']



mt_db = simple_mul_tab_db = MultiTableDB(simple_db_dir_path)

from base.database.sql.sql_db_engine import get_main_sql_session
sql_db = None
main_sql_session =None
def init_sql_engine():
    from base.database.sql.sql_db_engine import create_sql_engine
    global sql_db
    sql_db = create_sql_engine(config)

    global main_sql_session
    main_sql_session = get_main_sql_session()
    return sql_db
#数据库基类



sql_base_class = declarative_base()
def get_sql_base_class():
    return sql_base_class




# def create_all_tables(_sql_db : Engine):
#     from base.database.sql.tables.user import User
#
#     sql_base_class.metadata.create_all(_sql_db)
#     logger.debug("Tables created")
#动态导入表格
def snake_to_camel(snake_str):
    """
    将下划线命名法转换为驼峰命名法
    :param snake_str: 下划线命名法的字符串
    :return: 驼峰命名法的字符串
    """
    components = snake_str.split('_')
    # 第一个单词保持小写，其余单词首字母大写
    return components[0] + ''.join(word.capitalize() for word in components[1:])


def create_all_tables(_sql_db: Engine):
    # 假设你的表文件都放在 'base/database/sql/tables/' 目录下
    tables_dir = 'base/database/sql/tables'
    from project import logger

    # 获取该目录下的所有文件
    for filename in os.listdir(tables_dir):
        if filename.endswith('.py') and filename != '__init__.py':
            # 去掉文件扩展名
            base_name = filename[:-3]

            # 将文件名转换为类名（驼峰命名法）
            class_name = snake_to_camel(base_name)

            # 动态导入模块
            module_name = f'{tables_dir.replace("/", ".")}.{base_name}'
            spec = importlib.util.find_spec(module_name)
            # if spec is not None:
            #     module = importlib.util.module_from_spec(spec)
            #     spec.loader.exec_module(module)
            #
            #     # 尝试从模块中获取类
            #     try:
            #         table_class = getattr(module, class_name)
            #         # 这里不需要额外操作，因为create_all会处理所有已注册的表类
            #     except AttributeError:
            #         logger.warning(f"No class {class_name} found in module {module_name}")

    # 创建所有表
    sql_base_class.metadata.create_all(_sql_db)
    logger.debug("Tables created")