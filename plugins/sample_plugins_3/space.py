from base.plugins import PluginInfo,Plugin
from project import logger
info ={
    "mail" : "test@test.com",
}
plugin_info = PluginInfo(name = "sample_plugins_3", version="0.0.3",info = info)
plugin = Plugin(plugin_info)

logger.info(f"开始初始化插件{plugin_info.name},{plugin_info.version} ")

logger.info(f"初始化插件完成{plugin_info.name}")


# plugin.reg_init_plugin_func(init_plugin)