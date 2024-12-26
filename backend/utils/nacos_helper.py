import nacos
from utils.net_utils import get_host_ip
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from utils.scheduler_helper import SchedulerHelper
from typing import Optional, Callable


class NacosHelper:
    def __init__(self, server_endpoint: str, namespace_id: str, username: str = None, password: str = None):
        # 基础配置
        self.endpoint = server_endpoint
        self.namespace_id = namespace_id
        self.service_ip = get_host_ip()
        
        # 服务配置
        self.service_name: Optional[str] = None
        self.service_port: Optional[int] = None
        self.service_group: Optional[str] = None
        
        # 状态标志
        self.enabled = False
        self.client = None
        
        # 配置管理
        self.config_callback: Optional[Callable] = None
        self.config_data_id: Optional[str] = None
        self.config_group: Optional[str] = None
        
        # 调度器
        self.scheduler = SchedulerHelper()
        self.heartbeat_interval: Optional[int] = None
        
        # 初始化客户端
        self._init_client(username, password)

    def _init_client(self, username: str = None, password: str = None) -> None:
        """初始化 Nacos 客户端"""
        try:
            self.client = nacos.NacosClient(
                self.endpoint,
                namespace=self.namespace_id,
                username=username,
                password=password,
            )
            self._try_initial_connect()
        except Exception as e:
            logger.error(f"Nacos客户端创建失败: {e}")
            self.client = None

    def _try_initial_connect(self) -> None:
        """尝试初始连接"""
        try:
            self._check_connection()
        except Exception as e:
            logger.warning(f"初始连接尝试失败: {e}")
            self.enabled = False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def _check_connection(self) -> bool:
        """检查与 Nacos 服务器的连接"""
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

    # 服务管理相关方法
    def set_service(self, name: str, port: int, group: str) -> None:
        """设置服务信息"""
        self.service_name = name
        self.service_port = port
        self.service_group = group

    def register(self, wait_for_retry: bool = True) -> None:
        """注册服务"""
        if not self._check_service_config():
            return
            
        try:
            self.client.add_naming_instance(
                self.service_name,
                self.service_ip,
                self.service_port,
                group_name=self.service_group,
            )
            self.enabled = True
            logger.info("Nacos服务注册成功")
        except Exception as e:
            logger.error(f"注册服务失败: {e}")
            self.enabled = False
            if wait_for_retry:
                raise

    def unregister(self) -> None:
        """注销服务"""
        if not self._check_service_config():
            return
            
        try:
            self.client.remove_naming_instance(
                self.service_name, 
                self.service_ip, 
                self.service_port
            )
            logger.info("Nacos服务注销成功")
        except Exception as e:
            logger.error(f"注销服务失败: {e}")

    # 配置管理相关方法
    def add_conf_watcher(self, data_id: str, group: str, callback: Callable) -> None:
        """添加配置监听"""
        self.config_data_id = data_id
        self.config_group = group
        self.config_callback = callback
        if self.client and self.enabled:
            self.client.add_config_watcher(data_id=data_id, group=group, cb=callback)

    def load_conf(self, data_id: str, group: str, wait_for_retry: bool = True) -> Optional[str]:
        """加载配置"""
        if not self.client or not self.enabled:
            return None
            
        try:
            return self.client.get_config(data_id=data_id, group=group, no_snapshot=True)
        except Exception as e:
            logger.warning(f"加载配置失败: {e}")
            if wait_for_retry:
                raise
            return None

    # 调度任务管理相关方法
    def start_scheduler(self, beat_interval: Optional[int] = None) -> None:
        """启动调度器"""
        self.heartbeat_interval = beat_interval
        self.scheduler.start()
        
        # 添加重连任务
        self.scheduler.add_job(
            'nacos_reconnect',
            self._reconnect_job,
            'interval',
            hours=1
        )
        
        # 如果已连接且设置了心跳间隔，添加心跳任务
        if self.enabled and beat_interval:
            self._add_heartbeat_job(beat_interval)

    def stop_scheduler(self) -> None:
        """停止调度器"""
        try:
            if self.enabled:
                self.unregister()
        finally:
            self.scheduler.stop()

    def _add_heartbeat_job(self, interval: int) -> None:
        """添加心跳任务"""
        if not self.enabled:
            logger.warning("Nacos未启用，跳过添加心跳任务")
            return
            
        self.scheduler.remove_job('nacos_heartbeat')
        self.scheduler.add_job(
            'nacos_heartbeat',
            self.beat_callback,
            'interval',
            seconds=interval
        )
        logger.info(f"添加心跳任务，间隔：{interval}秒")

    # 辅助方法
    def _check_service_config(self) -> bool:
        """检查服务配置是否完整"""
        if not self.client:
            logger.warning("Nacos客户端未初始化")
            return False
        if not all([self.service_name, self.service_port, self.service_group]):
            logger.warning("服务配置不完整")
            return False
        return True

    # 回调方法
    async def beat_callback(self) -> None:
        """心跳回调"""
        if not self.client or not self.enabled:
            return
            
        try:
            self.client.send_heartbeat(
                self.service_name,
                self.service_ip,
                self.service_port
            )
            logger.debug(f"心跳发送成功: {self.service_name}")
        except Exception as e:
            logger.error(f"心跳发送失败: {e}")
            self.enabled = False

    async def _reconnect_job(self) -> None:
        """重连任务"""
        if not self.enabled and self.client:
            logger.info("执行重连任务")
            try:
                if self._check_connection():
                    await self._restore_service()
            except Exception as e:
                logger.warning(f"重连失败: {e}")

    async def _restore_service(self) -> None:
        """恢复服务状态"""
        try:
            # 重新注册服务
            self.register(wait_for_retry=False)
            
            # 恢复心跳
            if self.heartbeat_interval:
                self._add_heartbeat_job(self.heartbeat_interval)
                
            # 恢复配置监听
            if all([self.config_data_id, self.config_group, self.config_callback]):
                self.add_conf_watcher(
                    self.config_data_id,
                    self.config_group,
                    self.config_callback
                )
                # 重新加载配置
                config = self.load_conf(
                    self.config_data_id,
                    self.config_group,
                    wait_for_retry=False
                )
                if config:
                    self.config_callback(config)
                    
            logger.info("服务状态恢复成功")
        except Exception as e:
            logger.error(f"恢复服务状态失败: {e}")
            self.enabled = False

    async def init_service(self, config_data_id: str, config_group: str, config_callback: Callable) -> None:
        """初始化服务"""
        try:
            if self.client:
                # 注册服务
                self.register(wait_for_retry=False)
                
                # 保存配置信息
                self.config_data_id = config_data_id
                self.config_group = config_group
                self.config_callback = config_callback
                
                # 如果已启用，添加配置监听并加载配置
                if self.enabled:
                    self.add_conf_watcher(config_data_id, config_group, config_callback)
                    initial_config = self.load_conf(
                        config_data_id,
                        config_group,
                        wait_for_retry=False
                    )
                    if initial_config:
                        config_callback(initial_config)
        except Exception as e:
            logger.warning(f"服务初始化失败: {e}，将在后台继续尝试")

    def __del__(self):
        """析构函数"""
        self.stop_scheduler()
