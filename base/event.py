import weakref
from typing import List, Callable, Dict, Any


class TrieNode:
    """表示前缀树中的节点"""

    def __init__(self):
        # 存储子节点的字典
        self.children: Dict[str, 'TrieNode'] = {}
        # 存储处理器的弱引用集合，以避免循环引用导致内存泄漏
        self.handlers: weakref.WeakSet[Callable] = weakref.WeakSet()


class Trie:
    """实现前缀树的数据结构，支持插入、搜索、清理无效弱引用和列出所有注册的键"""

    def __init__(self):
        # 初始化前缀树，创建根节点
        self.root = TrieNode()

    def insert(self, key: str, handler: Callable):
        """
        插入一个键和处理器到前缀树中。

        :param key: 字符串，表示事件名称或标签
        :param handler: 处理器函数
        """
        node = self.root
        for char in key:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.handlers.add(handler)

    def search(self, key: str) -> List[Callable]:
        """
        查找与给定键完全匹配的处理器。

        :param key: 字符串，表示事件名称或标签
        :return: 匹配的处理器列表
        """
        node = self._traverse_to_node(key)
        return list(node.handlers) if node else []

    def _traverse_to_node(self, key: str) -> TrieNode:
        """
        辅助方法，遍历到指定键对应的节点。

        :param key: 字符串，表示事件名称或标签
        :return: 对应键的节点或者None如果不存在
        """
        node = self.root
        for char in key:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def clean_up(self):
        """清理前缀树中所有无效的弱引用"""
        self._clean_node(self.root)

    def _clean_node(self, node: TrieNode):
        """
        辅助方法，清理节点中的无效弱引用，并移除没有子节点也没有处理器的节点。

        :param node: 当前节点
        """
        dead_keys = [k for k, v in node.children.items() if not v.children and not v.handlers]
        for k in dead_keys:
            del node.children[k]
        for child in node.children.values():
            self._clean_node(child)

    def list_all_keys(self) -> List[str]:
        """
        列出前缀树中所有注册的键。

        :return: 所有注册的键的列表
        """
        keys = []
        self._collect_keys(self.root, '', keys)
        return keys

    def _collect_keys(self, node: TrieNode, prefix: str, keys: List[str]):
        """
        辅助方法，递归收集前缀树中所有有处理器的键。

        :param node: 当前节点
        :param prefix: 当前路径的前缀
        :param keys: 收集到的键的列表
        """
        if node.handlers:
            keys.append(prefix)
        for char, child in node.children.items():
            self._collect_keys(child, prefix + char, keys)


class EventManager:
    """管理事件和标签，支持注册、注销、触发事件，并提供通过前缀匹配触发事件的功能"""

    def __init__(self):
        # 初始化事件管理器，创建两个前缀树分别存储普通事件和标签事件
        self.event_trie = Trie()
        self.tag_trie = Trie()

    def register(self, event_name: str, handler: Callable):
        """
        注册一个普通事件。

        :param event_name: 字符串，表示事件名称
        :param handler: 处理器函数
        """
        self.event_trie.insert(event_name, handler)

    def unregister(self, event_name: str, handler: Callable):
        """
        注销一个普通事件。

        :param event_name: 字符串，表示事件名称
        :param handler: 处理器函数
        """
        handlers = self.event_trie.search(event_name)
        if handler in handlers:
            handlers.remove(handler)

    def register_tagged(self, tag: str, handler: Callable):
        """
        注册一个标签事件。

        :param tag: 字符串，表示标签
        :param handler: 处理器函数
        """
        self.tag_trie.insert(tag, handler)

    def unregister_tagged(self, tag: str, handler: Callable):
        """
        注销一个标签事件。

        :param tag: 字符串，表示标签
        :param handler: 处理器函数
        """
        handlers = self.tag_trie.search(tag)
        if handler in handlers:
            handlers.remove(handler)

    def emit(self, event_name: str, *args, **kwargs):
        """
        触发一个普通事件。

        :param event_name: 字符串，表示事件名称
        :param args: 可变位置参数
        :param kwargs: 可变关键字参数
        """
        for handler in self.event_trie.search(event_name):
            handler(*args, **kwargs)

    def emit_tagged(self, tag: str, *args, **kwargs):
        """
        触发一个标签事件。

        :param tag: 字符串，表示标签
        :param args: 可变位置参数
        :param kwargs: 可变关键字参数
        """
        for handler in self.tag_trie.search(tag):
            handler(*args, **kwargs)

    def emit_and_collect_results(self, event_name: str, *args, **kwargs) -> List[Any]:
        """
        触发一个普通事件并收集所有处理器的返回结果。

        :param event_name: 字符串，表示事件名称
        :param args: 可变位置参数
        :param kwargs: 可变关键字参数
        :return: 所有处理器的返回结果列表
        """
        results = []
        for handler in self.event_trie.search(event_name):
            result = handler(*args, **kwargs)
            results.append(result)
        return results

    def emit_tagged_and_collect_results(self, tag: str, *args, **kwargs) -> List[Any]:
        """
        触发一个标签事件并收集所有处理器的返回结果。

        :param tag: 字符串，表示标签
        :param args: 可变位置参数
        :param kwargs: 可变关键字参数
        :return: 所有处理器的返回结果列表
        """
        results = []
        for handler in self.tag_trie.search(tag):
            result = handler(*args, **kwargs)
            results.append(result)
        return results

    def clean_up(self):
        """清理前缀树中所有无效的弱引用"""
        self.event_trie.clean_up()
        self.tag_trie.clean_up()

    def list_events(self) -> List[str]:
        """
        列出所有注册的普通事件。

        :return: 所有注册的普通事件的列表
        """
        return self.event_trie.list_all_keys()

    def list_tagged_events(self) -> List[str]:
        """
        列出所有注册的标签事件。

        :return: 所有注册的标签事件的列表
        """
        return self.tag_trie.list_all_keys()


# 示例使用：

def handle_event1(a, b):
    print(f"handle_event1 called with arguments {a} and {b}")
    return a + b


def handle_event2(a, b):
    print(f"handle_event2 called with arguments {a} and {b}")
    return a - b


def handle_tagged_event1(a, b):
    print(f"handle_tagged_event1 called with arguments {a} and {b}")
    return a * b


def handle_tagged_event2(a, b):
    print(f"handle_tagged_event2 called with arguments {a} and {b}")
    return a / b

if __name__ == "__main__":
    manager = EventManager()
    event_manager = EventManager()

    # 注册普通事件
    event_manager.register('func/abc', handle_event1)
    event_manager.register('func/jkl', handle_event2)

    # 注册标签事件
    event_manager.register_tagged('func/mno', handle_tagged_event1)
    event_manager.register_tagged('func/pqr', handle_tagged_event2)

    # 列出所有注册的普通事件
    print("Registered events:", event_manager.list_events())

    # 列出所有注册的标签事件
    print("Registered tagged events:", event_manager.list_tagged_events())

    # 触发普通事件并收集结果
    results = event_manager.emit_and_collect_results('func/abc', 10, 5)
    print("Results from func/abc:", results)

    # 触发标签事件并收集结果
    tag_results = event_manager.emit_tagged_and_collect_results('func/mno', 10, 5)
    print("Results from func/mno:", tag_results)

    # 模拟方法被销毁
    del handle_event1
    del handle_tagged_event1

    # 清理无效的弱引用
    event_manager.clean_up()

    # 再次列出所有注册的普通事件和标签事件
    print("Registered events after cleanup:", event_manager.list_events())
    print("Registered tagged events after cleanup:", event_manager.list_tagged_events())

    # 再次触发已销毁的方法
    results = event_manager.emit_and_collect_results('func/abc', 10, 5)
    print("Results from func/abc after cleanup:", results)

    tag_results = event_manager.emit_tagged_and_collect_results('func/mno', 10, 5)
    print("Results from func/mno after cleanup:", tag_results)