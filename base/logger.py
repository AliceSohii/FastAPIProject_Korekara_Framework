# logger.py

from loguru import logger as loguru_logger
import sys
from pathlib import Path
from configparser import ConfigParser
import os

# 读取配置文件
# config = ConfigParser()
# config.encoding = 'utf-8'
# config.read("config/log.ini")

from project import config
# 获取配置信息
logger_dir_path = config['logger']['logger_dir_path']
log_to_console = config['logger']['log_to_console'].strip().lower() == 'true'
log_level = config['logger']['log_level'].upper()

# 确保日志目录存在
if not os.path.exists(logger_dir_path):
    os.makedirs(logger_dir_path)

# 配置 loguru
log_file_path = Path(logger_dir_path) / 'app.log'

# 自定义一个函数来模拟 logging.getLogger 的行为
def get_logger(name=None):
    # 对于 loguru，我们不需要传递 name 参数，因为它使用全局的单例 logger。
    # 但为了兼容，我们还是接受这个参数，并在日志消息中可能使用它（尽管 loguru 不需要它）。
    class ProxyLogger:
        def __getattr__(self, item):
            # 当尝试访问 ProxyLogger 的属性（如 info, error 等）时，
            # 将其重定向到 loguru_logger 的相应方法，并绑定一个额外的 context（如果需要）。
            # 这里我们简单地返回 loguru_logger 的方法，不传递 name，因为 loguru 不需要它。
            # 如果您想在日志中包含模块名或其他上下文，您可能需要修改这里的实现。
            return lambda *args, **kwargs: getattr(loguru_logger, item)(*args, **kwargs)

    # 创建一个 ProxyLogger 实例，并返回它。
    # 注意：这个实例实际上并不持有任何状态，它只是一个到 loguru_logger 的代理。
    return ProxyLogger()

# 配置 loguru 的处理器和格式
# 注意：这些配置只需要做一次，所以我们在这里做。
# 如果您的项目中有多个地方尝试配置 logger，则可能需要确保这些配置是幂等的或只执行一次。

# 添加文件处理器
loguru_logger.add(log_file_path,
                  format="{time:YYYY-MM-DD HH:mm:ss} - {level} - {message}",
                  rotation="500 MB",
                  retention="10 days",
                  compression="zip",
                  level=log_level)

# 如果需要将日志输出到控制台，则添加控制台处理器
if log_to_console:
    loguru_logger.add(sys.stdout,
                      format="{time:YYYY-MM-DD HH:mm:ss} - {level} - {message}",
                      level=log_level)

# 提供一个全局的 logger 实例，供项目中的其他模块使用。
# 由于 loguru 是单例的，理论上我们不需要这样做，但为了兼容和减少改动，我们还是提供一个。
logger = get_logger()

# 注意：上面的 get_logger 函数和 ProxyLogger 类只是为了模拟 logging 模块的行为。
# 在实际使用中，您可能会发现直接使用 loguru_logger 更简单和直接。
# 但由于您要求不改动其他文件，所以我们提供了这个兼容层。