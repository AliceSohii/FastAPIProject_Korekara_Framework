import redis
from redis.connection import ConnectionPool


redis_db =None
def create_redis_client(config):
    """
    根据提供的配置对象创建并返回一个Redis客户端对象。

    :param config: 一个包含Redis配置信息的configparser.ConfigParser对象。
    :return: 一个配置好的redis.Redis客户端对象。
    如果配置中use_redis为false，则返回 None
    """
    redis_section = 'redis_db'
    use_redis = config[redis_section]['use_redis']
    if not use_redis:
        return None
    redis_host = config[redis_section]['redis_host']
    redis_port = int(config[redis_section]['redis_port'])
    redis_password = config[redis_section].get('redis_password', fallback=None)
    redis_db_index = int(config[redis_section].get('redis_db_index', fallback=0))  # 默认数据库索引为0

    # 连接池配置
    max_connections = int(config[redis_section].get('redis_max_connections', fallback=100))
    min_idle_connections = int(config[redis_section].get('redis_min_idle_connections', fallback=10))
    socket_connect_timeout = int(config[redis_section].get('redis_connect_timeout', fallback=5))
    idle_timeout = int(config[redis_section].get('redis_idle_timeout', fallback=300))

    # 创建连接池
    pool = ConnectionPool(
        host=redis_host,
        port=redis_port,
        password=redis_password,
        max_connections=max_connections,
        min_idle_connections=min_idle_connections,
        socket_connect_timeout=socket_connect_timeout,
        max_idle_time=idle_timeout,
    )
    global redis_db
    # 创建Redis客户端并设置数据库索引
    redis_db = redis.Redis(connection_pool=pool, db=redis_db_index)

    return redis_db
