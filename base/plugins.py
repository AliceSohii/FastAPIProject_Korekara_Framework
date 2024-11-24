import os
import importlib.util
import sys
from typing import List, Dict, Any
from project import logger
class PluginInfo:
    def __init__(self, name: str, version: str, info: dict = None):
        """
        初始化插件对象

        :param name: 插件名称
        :param version: 插件版本
        :param info: 信息
        """
        self.name = name
        self.version = version
        self.info = info if info else {}

    def get_info(self) -> dict:
        """
        获取插件的基本信息

        :return: 包含插件名称和版本的字典
        """
        return {
            'name': self.name,
            'version': self.version,
            'info': self.info
        }

class Plugin:
    def __init__(self, info: PluginInfo):
        # self.fn = None
        self.info = info
    def get_info(self) -> PluginInfo:
        return self.info
    # def reg_init_plugin_func(self,fn):
    #     self.fn = fn
    # def run(self):
    #
    #     logger.info(f"初始化插件:{self.info.name}")
    #     self.fn()
    #     logger.info(f"初始化插件:{self.info.name}完成")


def load_plugins(plugin_dir: str = "plugins") -> List[Plugin]:
    plugins = []
    for plugin_name in os.listdir(plugin_dir):
        plugin_path = os.path.join(plugin_dir, plugin_name)
        if os.path.isdir(plugin_path) and os.path.exists(os.path.join(plugin_path, 'space.py')):
            spec = importlib.util.spec_from_file_location(f"{plugin_name}.space", os.path.join(plugin_path, 'space.py'))
            module = importlib.util.module_from_spec(spec)
            sys.modules[f"{plugin_name}.space"] = module
            spec.loader.exec_module(module)

            # 尝试从模块中获取PluginInfo和Plugin对象以及init_plugin函数
            try:
                plugin_info = module.plugin_info
                plugin_class_instance = module.plugin

                # 检查是否正确获取了所需的对象
                if not isinstance(plugin_info, PluginInfo):
                    raise TypeError(f"Expected PluginInfo instance in {plugin_name}/space.py, got {type(plugin_info)}")
                if not isinstance(plugin_class_instance, Plugin):
                    raise TypeError(
                        f"Expected Plugin instance in {plugin_name}/space.py, got {type(plugin_class_instance)}")

                # 将插件实例添加到列表中
                plugins.append(plugin_class_instance)

            except (AttributeError, TypeError) as e:
                logger.error(f"Failed to load plugin from {plugin_name}/space.py: {e}")
    return plugins


