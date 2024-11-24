import configparser
import os



CONFIG_FILE = os.path.join("config/database.ini")

# 解析配置文件
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

# 获取配置值
from base.database.table_db import MultiTableDB

simple_db_dir_path = config['mul_table_db']['mul_table_db_dir_path']
mt_db = simple_mul_tab_db = MultiTableDB(simple_db_dir_path)
