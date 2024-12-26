import nacos
from utils.net_utils import get_host_ip
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class NacosHelper:
    service_name = None
    service_port = None
    service_group = None

    def __init__(self, server_endpoint, namespace_id, username=None, password=None):
        self.enabled = False
        self.endpoint = server_endpoint
        self.service_ip = get_host_ip()
        self.namespace_id = namespace_id
        self.username = username
        self.password = password
        self.scheduler = AsyncIOScheduler()
        
        # 只创建客户端，不进行连接测试
        try:
            self.client = nacos.NacosClient(
                self.endpoint,
                namespace=self.namespace_id,
                username=self.username,
                password=self.password,
            )
            logger.info("Nacos客户端创建成功")
            # 初始化时尝试连接一次，但不阻塞
            try:
                self._try_connect()
            except Exception as e:
                logger.warning(f"初始连接尝试失败: {e}")
        except Exception as e:
            logger.error(f"Nacos客户端创建失败: {e}")
            self.client = None

        # 添加定时重连任务
        self.scheduler.add_job(self._reconnect_job, 'interval', hours=1)
        self.scheduler.start()
        logger.info("添加定时重连任务")

    async def _reconnect_job(self):
        """定时重连任务"""
        if not self.enabled and self.client:
            logger.info("执行定时重连任务")
            try:
                self._try_connect()
            except Exception as e:
                logger.warning(f"定时重连失败: {e}")

    def __del__(self):
        """析构函数，确保调度器被正确关闭"""
        try:
            self.scheduler.shutdown()
        except:
            pass

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def _try_connect(self):
        """尝试连接到Nacos服务器"""
        if not self.client:
            return False
        try:
            self.client.get_config("health_check_test", "DEFAULT_GROUP", no_snapshot=True)
            self.enabled = True
            logger.info("Nacos服务器连接成功")
            return True
        except Exception as e:
            if "config data not exist" in str(e):
                self.enabled = True
                logger.info("Nacos服务器连接成功")
                return True
            logger.warning(f"Nacos服务器连接失败: {e}")
            self.enabled = False
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def register(self):
        """注册服务，失败时会重试"""
        if not self.client:
            logger.warning("Nacos客户端未初始化，跳过注册")
            return
        
        # 如果未启用，先尝试连接
        if not self.enabled:
            try:
                self._try_connect()
            except Exception:
                logger.warning("Nacos服务器连接失败，跳过注册")
                return

        try:
            self.client.add_naming_instance(
                self.service_name,
                self.service_ip,
                self.service_port,
                group_name=self.service_group,
            )
            logger.info("Nacos服务注册成功")
        except Exception as e:
            logger.error(f"注册服务失败: {e}")
            self.enabled = False
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def load_conf(self, data_id, group):
        """加载配置，失败时会重试"""
        if not self.client:
            logger.warning("Nacos客户端未初始化，跳过加载配置")
            return None
            
        # 如果未启用，先尝试连接
        if not self.enabled:
            try:
                self._try_connect()
            except Exception:
                logger.warning("Nacos服务器连接失败，跳过加载配置")
                return None

        return self.client.get_config(data_id=data_id, group=group, no_snapshot=True)

    async def beat_callback(self):
        """发送心跳"""
        if not self.client:
            return
            
        if not self.enabled:
            try:
                self._try_connect()
            except Exception:
                return

        try:
            logger.info(
                f"发送心跳： ServerName{self.service_name} IP: {self.service_ip} Port:{self.service_port}"
            )
            self.client.send_heartbeat(
                self.service_name, self.service_ip, self.service_port
            )
        except Exception as e:
            logger.error(f"心跳发送失败: {e}")
            self.enabled = False

    def is_enabled(self) -> bool:
        return self.enabled

    def unregister(self):
        self.client.remove_naming_instance(
            self.service_name, self.service_ip, self.service_port
        )

    def set_service(self, service_name, service_port, service_group):
        self.service_name = service_name
        self.service_port = service_port
        self.service_group = service_group

    def add_conf_watcher(self, data_id, group, callback):
        self.client.add_config_watcher(data_id=data_id, group=group, cb=callback)
