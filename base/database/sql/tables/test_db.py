import os

from base.database.space import sql_base_class
from sqlalchemy import Column, Integer, String
from project import logger


file_name = os.path.splitext(os.path.basename(__file__))[0]
table_name = file_name.capitalize()

logger.debug("数据库:识别到表:"+table_name) # 使用文件名（小写）作为表名，并首字母大写)
class TestDB(sql_base_class):
    __tablename__ = table_name  # 使用文件名（小写）作为表名，并首字母大写
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)