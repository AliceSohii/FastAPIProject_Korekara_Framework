import pickle
import threading
import os

class TableDB:
    def __init__(self, filename):
        """
        初始化数据库对象。
        表单数据库
        :param filename: 数据库文件的名称，用于持久化存储数据。
        """
        self.filename = filename  # 数据库文件名
        self.lock = threading.Lock()  # 线程锁，用于确保线程安全
        self.data = {}  # 使用字典来存储数据库数据
        self._load_data()  # 从文件中加载数据（如果存在）

    def _load_data(self):
        """
        从文件中加载数据。

        如果指定的文件存在，则使用pickle模块将文件内容反序列化为字典对象，并赋值给self.data。
        """
        if os.path.exists(self.filename):
            with open(self.filename, 'rb') as file:
                self.data = pickle.load(file)

    def _save_data(self):
        """
        将数据保存到文件中。

        使用pickle模块将self.data字典对象序列化为二进制数据，并写入到指定的文件中。
        """
        with open(self.filename, 'wb') as file:
            pickle.dump(self.data, file)

    def insert(self, key, value):
        """
        插入新的键值对到数据库中。

        :param key: 要插入的键。
        :param value: 与键关联的值。
        """
        with self.lock:  # 确保线程安全
            self.data[key] = value  # 将键值对添加到字典中
            self._save_data()  # 将数据保存到文件

    def get(self, key):
        """
        根据键从数据库中获取值。

        :param key: 要获取值的键。
        :return: 与键关联的值，如果键不存在则返回None。
        """
        with self.lock:  # 确保线程安全
            return self.data.get(key)  # 从字典中获取值

    def update(self, key, value):
        """
        更新数据库中指定键的值。

        :param key: 要更新的键。
        :param value: 新的值。

        注意：如果键不存在，则不会进行任何操作。
        """
        with self.lock:  # 确保线程安全
            if key in self.data:  # 检查键是否存在
                self.data[key] = value  # 更新值
                self._save_data()  # 将数据保存到文件

    def delete(self, key):
        """
        从数据库中删除指定的键值对。

        :param key: 要删除的键。
        """
        with self.lock:  # 确保线程安全
            if key in self.data:  # 检查键是否存在
                del self.data[key]  # 删除键值对
                self._save_data()  # 将数据保存到文件

    def keys(self):
        """
        获取数据库中的所有键。

        :return: 包含所有键的列表。
        """
        with self.lock:  # 确保线程安全
            return list(self.data.keys())  # 从字典中获取所有键

    def values(self):
        """
        获取数据库中的所有值。

        :return: 包含所有值的列表。
        """
        with self.lock:  # 确保线程安全
            return list(self.data.values())  # 从字典中获取所有值

    def items(self):
        """
        获取数据库中的所有键值对。

        :return: 包含所有键值对的列表（每个键值对都是一个元组）。
        """
        with self.lock:  # 确保线程安全
            return list(self.data.items())  # 从字典中获取所有键值对


class MultiTableDB:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.tables = {}
        # 确保文件夹存在
        os.makedirs(self.folder_path, exist_ok=True)
        # 从文件夹中的PKL文件恢复表
        self._initialize_tables_from_files()

    def _initialize_tables_from_files(self):
        for filename in os.listdir(self.folder_path):
            if filename.endswith('.pkl'):
                table_name = os.path.splitext(filename)[0]
                file_path = os.path.join(self.folder_path, filename)
                if table_name not in self.tables:
                    self.tables[table_name] = TableDB(file_path)

    def create_table(self, table_name):
        """
        创建一个新的表，如果表已存在则抛出异常。

        :param table_name: 表名。
        """
        if table_name in self.tables:
            raise ValueError(f"Table '{table_name}' already exists.")
        filename = os.path.join(self.folder_path, f"{table_name}.pkl")
        self.tables[table_name] = TableDB(filename)

    def ensure_table_exists(self, table_name):
        """
        确保指定的表存在。如果表不存在，则创建一个新的表；如果已存在，则加载它。

        :param table_name: 表名。
        """
        if table_name not in self.tables:
            filename = os.path.join(self.folder_path, f"{table_name}.pkl")
            self.tables[table_name] = TableDB(filename)
        # 注意：这里不需要额外的逻辑来加载已存在的表，因为当表已经存在时，
        # self.tables[table_name] 已经包含了对应的 TableDB 对象。

    def get_table(self, table_name):
        """
        通过表名获取表对象，如果表不存在则返回None。

        :param table_name: 表名。
        :return: 对应的TableDB对象或None。
        """
        return self.tables.get(table_name)

    def __getitem__(self, table_name):
        """
        通过表名获取表对象（支持字典式访问），如果表不存在则抛出KeyError。

        :param table_name: 表名。
        :return: 对应的TableDB对象。
        :raises KeyError: 如果表不存在。
        """
        return self.tables[table_name]

# Example usage:
if __name__ == "__main__":
    db = TableDB('database.pkl')

    # Insert some data
    db.insert('name', 'Alice')
    db.insert('age', 30)

    # Retrieve some data
    print(db.get('name'))  # Output: Alice
    print(db.get('age'))   # Output: 30

    # Update some data
    db.update('age', 31)
    print(db.get('age'))   # Output: 31

    # Delete some data
    db.delete('name')
    print(db.get('name'))  # Output: None

    # List all keys, values, and items
    print(db.keys())       # Output: ['age']
    print(db.values())     # Output: [31]
    print(db.items())      # Output: [('age', 31)]
    ####
    # 示例用法
    # 示例用法
    db_folder = "./db_files"  # 文件夹路径
    db = MultiTableDB(db_folder)

    # 假设db_files文件夹中已经存在User.pkl和Order.pkl文件
    # 那么db.tables现在应该包含'User'和'Order'两个表的TableDB对象

    # 检查已初始化的表
    print(db.tables.keys())  # 应该输出: dict_keys(['User', 'Order'])

    # 使用表对象
    user_db = db['User']
    order_db = db.get_table('Order')

    # 插入新数据（这将更新PKL文件）
    user_db.insert('user2', {'name': 'Bob', 'age': 25})
    order_db.insert('order2', {'product': 'Gadget', 'quantity': 10})

    # 获取数据
    print(user_db.get('user2'))  # 应该输出: {'name': 'Bob', 'age': 25}
    print(order_db.get('order2'))  # 应该输出: {'product': 'Gadget', 'quantity': 10}
