import os
import configparser
from sqlalchemy import create_engine, Column, Integer, String, Sequence, Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from project import logger
sql_engine = None
def create_sql_engine(config: configparser.ConfigParser) ->  Engine:
    # 获取数据库类型
    db_type = config['sql_db']['type']
    logger.info(f"主数据库类型: {db_type}")
    echo = config['sql_db'].getboolean('echo')  # 读取echo配置，并转换为布尔值

    # 根据数据库类型构建连接字符串
    if db_type == 'sqlite':
        # SQLite 数据库连接字符串
        sqlite_path = config['sql_db']['sqlite_path']
        # 确保sqlite_path是绝对路径或正确拼接为绝对路径
        sqlite_path = os.path.abspath(sqlite_path) if not os.path.isabs(sqlite_path) else sqlite_path
        # 注意：这里可能需要处理路径分隔符问题，但在大多数情况下，os.path.abspath 会正确处理
        connection_string = f'sqlite:///{sqlite_path}'
    elif db_type == 'mysql':
        # MySQL 数据库连接字符串（需要额外配置）
        username = config['sql_db']['username']  # 你需要在配置文件中添加这个字段
        password = config['sql_db']['password']  # 你需要在配置文件中添加这个字段
        hostname = config['sql_db']['hostname']  # 你需要在配置文件中添加这个字段
        dbname = config['sql_db']['dbname']  # 你需要在配置文件中添加这个字段
        # 构建 MySQL 连接字符串
        connection_string = f'mysql+pymysql://{username}:{password}@{hostname}/{dbname}'
    else:
        logger.error(f"主数据库: 连接失败 "+ f"Unsupported database type: {db_type}")
        raise ValueError(f"Unsupported database type: {db_type}")
    logger.info(f"主数据库: 连接成功")
    # 创建数据库引擎
    global sql_engine
    sql_engine = create_engine(connection_string, echo=echo)
    return sql_engine

def get_sql_engine():
    global sql_engine
    return sql_engine

