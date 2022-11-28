import requests
import os
import json
from copy import deepcopy
from urllib.parse import urljoin


class PyGoCron:
    def __init__(
        self,
        gocron_address: str = os.environ.get("GOCRON_ADDRESS", ""),
        gocron_admin_user: str = os.environ.get("GOCRON_ADMIN_USER", ""),
        gocron_admin_password: str = os.environ.get("GOCRON_ADMIN_PASSWORD", ""),
    ):
        self._base_url = gocron_address
        self._headers = None
        self._authenticate(gocron_admin_user, gocron_admin_password)

    def _authenticate(self, username, password):
        url = urljoin(self._base_url, "/api/user/login")
        payload = {"username": username, "password": password}
        response = requests.post(url, params=payload)
        if response.status_code == 200:
            data = json.loads(response.text)
            if data["message"] == "操作成功":
                self._headers = {"Auth-Token": data["data"]["token"]}
            else:
                raise Exception(f"Authentication Error, details: {str(data)}")
        else:
            raise Exception(
                f"Authentication Error, Status code: {response.status_code}"
            )

    def create_task(
        self,
        name: str,
        spec: str,
        command: str,
        tag: str = "",
        level: int = 1,
        dependency_status: int = 1,
        dependency_task_id: str = "",
        protocol: int = 2,
        http_method: int = 1,
        host_id: int = 3,
        timeout: int = 0,
        multi: int = 2,
        notify_status: int = 1,
        notify_type: int = 2,
        notify_keyword: str = "",
        notify_receiver_id: str = "",
        retry_times: int = 0,
        retry_interval: int = 0,
        remark: str = "",
    ):
        """
        创建任务

        参数
        -----
        name: 任务名称
        spec: cron 表达式
        command: 任务命令
        tag: 任务标签
        level: 任务等级，1: 主任务 2: 依赖任务(子任务)
        dependency_status: 依赖关系 1:强依赖 主任务执行成功, 依赖任务才会被执行 2:弱依赖
        dependency_task_id: 依赖任务ID,多个ID逗号分隔
        protocol: 执行范式 1:http 2:shell
        http_method: http_method, 1: get 2: post
        host_id: 节点id
        timeout: 任务执行超时时间(单位秒),0不限制
        multi: 是否允许多实例运行
        notify_status:任务执行结束是否通知 0: 不通知 1: 失败通知;2: 执行结束通知;3: 任务执行结果关键字匹配通知
        notify_type: 通知类型 1: 邮件 2: slack 3: webhook
        notify_keyword: 通知关键字
        notify_receiver_id: 通知接受者ID, 多个ID逗号分隔
        retry_times: 重试次数
        retry_interval: 重试间隔
        remark: 备注
        """

        payload = {
            "id": "",
            "name": name,
            "spec": spec,
            "command": command,
            "tag": tag,
            "level": level,
            "dependency_status": dependency_status,
            "dependency_task_id": dependency_task_id,
            "spec": spec,
            "protocol": protocol,
            "http_method": http_method,
            "host_id": host_id,
            "timeout": timeout,
            "multi": multi,
            "notify_status": notify_status,
            "notify_type": notify_type,
            "notify_keyword": notify_keyword,
            "notify_receiver_id": notify_receiver_id,
            "retry_times": retry_times,
            "retry_interval": retry_interval,
            "remark": remark,
        }
        url = urljoin(self._base_url, "/api/task/store")
        headers = deepcopy(self._headers)
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        response = requests.post(url, headers=headers, params=payload)
        if response.status_code == 200:
            data = json.loads(response.text)
            if data["message"] == "保存成功":
                print("Task Created Successfully")
            else:
                raise Exception(f"Create Task Error, Details: {response.text}")
        else:
            raise Exception(f"Create Task Error, Details: {response.text}")

    def run_task(self, task_id):
        url = urljoin(self._base_url, f"api/task/run/{task_id}")
        response = requests.get(url, headers=self._headers)
        if response.status_code == 200:
            data = json.loads(response.text)
            if data["message"] == "任务已开始运行, 请到任务日志中查看结果":
                print("Task Triggerd Successfully")
            else:
                raise Exception(f"Canot Trigger Task, Details: {response.text}")
        else:
            raise Exception(f"Canot Trigger Task, Details: {response.text}")

    def get_tasks(
        self,
        page=1,
        page_size=20,
        id: int = None,
        protocol: int = None,
        name: str = None,
        tag: str = None,
        host_id: int = None,
        status: int = None,
    ):
        """
        获取任务列表

        参数
        -----
        page: 页码
        page_szie: 每页大小
        id: 任务id
        protocol: 协议 1:http 2:系统命令
        name: 任务名称
        tag: 标签
        host_id: 节点id
        status: 状态  0:停止， 1： 正常
        """
        url = urljoin(self._base_url, "api/task")

        payload = {
            "page_size": page_size,
            "page": page,
            "id": id,
            "protocol": protocol,
            "name": name,
            "tag": tag,
            "host_id": host_id,
            "status": status,
        }
        response = requests.get(url, headers=self._headers, params=payload)
        if response.status_code == 200:
            data = json.loads(response.text)

            if data["message"] == "操作成功":
                return data["data"]
            else:
                raise Exception(f"Can not Fetch Task List, Details: {response.text}")
        else:
            raise Exception(f"Can not Fetch Task List, Details: {response.text}")

    def get_task_id_by_name(self, name: str):
        """
        通过任务名获取一个task id(任务名是不会重复的， 所以有且只会返回一个id)

        参数
        -----
        name: 任务名称 
        """
        data = self.get_tasks(name=name)
        if data:
            try:
                task_id = data["data"][0]["id"]
            except IndexError:
                raise Exception(f"Task Name `{name}` Not Found")
            else:
                return task_id

    def get_task_logs(
        self,
        task_id: int=None,
        page: int = 1,
        page_size: int = 20,
        protocol: int = None,
        status: int = None,
    ):
        """
        获取任务的运行日志

        参数
        -----
        task_id: 任务id
        page: 页码
        page_size: 每页数量
        protocol: 协议 1:http 2:系统命令
        status: 任务状态， 0:所有, 1: 失败, 2: 正在运行
        """
        url = urljoin(self._base_url, "api/task/log")

        payload = {
            "task_id": task_id,
            "page": page,
            "page_size": page_size,
            "protocol": protocol,
            "status": status,
        }

        response = requests.get(url, headers=self._headers, params=payload)

        if response.status_code == 200:
            data = json.loads(response.text)

            if data["message"] == "操作成功":
                return data["data"]
            else:
                raise Exception(f"Can not Fetch Task Log, Details: {response.text}")
        else:
            raise Exception(f"Can not Fetch Task Log, Details: {response.text}")

    def get_nodes(self):
        """
        获取所有节点
        """
        url = urljoin(self._base_url, "api/host/all")
        response = requests.get(url, headers=self._headers)

        if response.status_code == 200:
            data = json.loads(response.text)

            if data["message"] == "操作成功":
                return data["data"]
            else:
                raise Exception(f"Can not Fetch All Nodes(hosts), Details: {response.text}")
        else:
            raise Exception(f"Can not Fetch All Nodes(hosts), Details: {response.text}")

    def disable_task(self, task_id:int):
        """
        停止任务
        """
        url = urljoin(self._base_url, f"api/task/disable/{task_id}")

        response = requests.post(url, headers=self._headers)

        if response.status_code == 200:
            data = json.loads(response.text)
            if data["message"] == "操作成功":
                print("Job Disabled Successfully")
            else:
                raise Exception(f"Can Not Disable Job, Details: {response.text}")
        else:
            raise Exception(f"Can Not Disable Job, Details: {response.text}")

    def enable_task(self, task_id:int):
        """
        启动任务
        """
        url = urljoin(self._base_url, f"api/task/enable/{task_id}")

        response = requests.post(url, headers=self._headers)

        if response.status_code == 200:
            data = json.loads(response.text)
            if data["message"] == "操作成功":
                print("Job Enabled Successfully")
            else:
                raise Exception(f"Can Not Enable Job, Details: {response.text}")
        else:
            raise Exception(f"Can Not Enable Job, Details: {response.text}")