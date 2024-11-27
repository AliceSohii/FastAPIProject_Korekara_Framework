class ObjectManager:
    def __init__(self):
        self._objects = {}  # 使用字典来存储对象


    def store(self, key: str, value):
        """
        存储对象。对象可以是任意类型的数据，但不能为空。

        :param key: 字符串作为索引，支持层级结构，如 "int/num"
        :param value: 要存储的对象，不能为空
        :raises ValueError: 如果值为空
        """
        if value is None:
            raise ValueError("Cannot store a None value.")
        self._objects[key] = value
    def get(self, key: str):
        """
        使用字符串精确获取变量。如果失败则返回 KeyError。

        :param key: 字符串索引
        :return: 存储的对象，如果失败则引发 KeyError
        """
        return self._objects[key]

    def search(self, prefix: str):
        """
        使用字符串前缀搜索变量，并返回匹配的对象引用元组。

        :param prefix: 字符串前缀，如 "int/"
        :return: 匹配的对象引用元组，如果没有匹配则返回空元组
        """
        matches = [value for key, value in self._objects.items() if key.startswith(prefix)]
        return tuple(matches)

    def delete(self, key: str):
        """
        使用字符串精确删除某变量。如果成功返回 True，否则返回 False。

        :param key: 字符串索引
        :return: 布尔值，表示删除操作是否成功
        """
        return key in self._objects and (self._objects.pop(key, None) is not None)

    def update(self, key: str, value):
        """
        使用字符串修改某变量。如果键不存在，则存储新变量。

        :param key: 字符串索引
        :param value: 要存储的新对象
        """
        self._objects[key] = value  # 这里不再检查 value 是否为空，因为存储空值是合法的

    def get_by_type(self, obj_type):
        """
        使用类型来搜索全部变量，并返回匹配的对象引用元组。

        :param obj_type: 要搜索的类型
        :return: 匹配的对象引用元组，如果没有匹配则返回空元组
        """
        matches = [value for value in self._objects.values() if isinstance(value, obj_type)]
        return tuple(matches)

    def get_list(self):
        """
        返回所有对象的键。

        :return: 包含所有键的列表
        """
        return list(self._objects.keys())

if __name__ == "__main__":
    # 使用示例
    om = ObjectManager()

    # 存储对象
    om.store("user_num", 42)
    om.store("int/num", 10)
    om.store("int/var", "variable")

    # 精确获取变量
    try:
        user_num = om.get("user_num")
        print(user_num)  # 输出: 42
    except KeyError:
        print("Key not found.")

    # 使用前缀搜索变量
    int_vars = om.search("int/")
    print(int_vars)  # 输出: (10, 'variable')

    # 精确删除变量
    success = om.delete("int/num")
    print(success)  # 输出: True

    # 尝试删除不存在的变量
    failure = om.delete("non_existent_key")
    print(failure)  # 输出: False

    # 修改变量
    om.update("int/var", 20)  # 将 "int/var" 的值从字符串改为了整数
    print(om.get("int/var"))  # 输出: 20

    # 使用类型搜索变量
    all_ints = om.get_by_type(int)
    print(all_ints)  # 输出可能包含 (20, 42) ，具体取决于前面的操作