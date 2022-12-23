import time
import requests
import os
import json
import datetime
from copy import deepcopy
from urllib.parse import urljoin
from enum import Enum
from rich import print as rprint


class RunStatus(Enum):
    FAILED: int = 0
    RUNNING: int = 1
    SUCCESS: int = 2
    PENDING: int = 3


class LogLevel(Enum):
    INFO: str = "INFO"
    SUCCESS: str = "SUCCESS"
    WARN: str = "WARN"
    ERROR: str = "ERROR"
    DEBUG: str = "DEBUG"


class PyGocronException(Exception):
    pass


def logger_print(message: str, level: LogLevel = LogLevel.INFO):
    this_moment = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    message_prefix = f"{this_moment}-pygocron"
    if level == LogLevel.INFO:
        message_prefix = message_prefix + f"[blue b] :{level.value}: [/]"
    if level == LogLevel.SUCCESS:
        message_prefix = message_prefix + f"[green b] :{level.value}: [/]"
    if level == LogLevel.WARN:
        message_prefix = message_prefix + f"[red b] :{level.value}: [/]"
    if level == LogLevel.ERROR:
        message_prefix = message_prefix + f"[red b] :{level.value}: [/]"
    if level == LogLevel.DEBUG:
        message_prefix = message_prefix + f"[blue b] :{level.value}: [/]"
    message = message_prefix + message
    rprint(message)


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
        if self._base_url == "" or username == "" or password == "":
            raise ValueError(
                "If you don't explicitly give PyGoCron` enough parameters("
                "`gocron_address`, `gocron_admin_user`, `gocron_admin_password`),"
                "then make sure set all of following enviroment varibles:`GOCRON_ADDRESS`,"
                "`GOCRON_ADMIN_USER`, `GOCRON_ADMIN_PASSWORD`"
            )

        url = urljoin(self._base_url, "/api/user/login")
        payload = {"username": username, "password": password}
        response = requests.post(url, params=payload)
        if response.status_code == 200:
            data = json.loads(response.text)
            if data["message"] == "操作成功":
                self._headers = {"Auth-Token": data["data"]["token"]}
            else:
                raise PyGocronException(f"Authentication Error, details: {str(data)}")
        else:
            raise PyGocronException(
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
        host_id: int = 1,
        timeout: int = 0,
        multi: int = 2,
        notify_status: int = 1,
        notify_type: int = 2,
        notify_keyword: str = "",
        notify_receiver_id: str = "",
        retry_times: int = 0,
        retry_interval: int = 0,
        remark: str = "",
    ) -> int:
        """
        Create a task, and return the task id

        Params
        -----
        name: task name
        spec: cron expression
        command: command, for instance `echo 1`
        tag: task tag, useful to group tasks
        level: task level(or type);1: main task 2: sub task; if you define a `sub` task, then you donn't need to set a `spec`(it will run after main task)
        dependency_status: 1:task will run only if the main task ran successfuly 2:task will run no matter its dependant task ran successfully or not
        dependency_task_id: dependency task id
        protocol: 1 for `http` and  2 for `shell`, default is 2
        http_method: http_method, 1 for `get` method and 2 for `post` method
        host_id: host id or node id 
        timeout: timeout(seconds)
        multi: can be run in multi-instance or not 
        notify_status: 0: not notify 1: notify when task fails,  2: notify when task finished
        notify_type: notify method 1: mail 2: slack 3: webhook
        notify_keyword: notify keyword
        notify_receiver_id: receiver ID, seperated by `,` when multiple receiver ID are given
        retry_times: retry times
        retry_interval: retry interval(seconds)
        remark: comment fot task
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
                logger_print(f"Task Created:`{name}` Successfully", LogLevel.SUCCESS)
                return self.get_task_id_lagged(name=name)
            else:
                raise PyGocronException(
                    f"Create Task:`{name}` Error, Details: {response.text}"
                )
        else:
            raise PyGocronException(
                f"Create Task:`{name}` Error, Details: {response.text}"
            )

    def run_task(self, task_id) -> int:
        """
        Run task and return a task run id 
        """
        url = urljoin(self._base_url, f"api/task/run/{task_id}")
        response = requests.get(url, headers=self._headers)
        if response.status_code == 200:
            data = json.loads(response.text)
            if data["message"] == "任务已开始运行, 请到任务日志中查看结果":
                logger_print("Task Triggerd Successfully", LogLevel.SUCCESS)
                return self.get_latest_run_id(task_id)
            else:
                raise PyGocronException(f"Canot Trigger Task, Details: {response.text}")
        else:
            raise PyGocronException(f"Canot Trigger Task, Details: {response.text}")

    def get_tasks(
        self,
        page=1,
        page_size=50,
        task_id: int = None,
        protocol: int = None,
        name: str = None,
        tag: str = None,
        host_id: int = None,
        status: int = None,
    ):
        """
        Get a task list

        Params
        -----
        page: page 
        page_size: page size
        task id: task id
        protocol: protocol, 1 for http and 2 for shell
        name: task name
        tag: tag
        host_id: host id
        status: status, 0 for `disabled`， 1 for `enabled`
        """
        url = urljoin(self._base_url, "api/task")

        payload = {
            "page_size": page_size,
            "page": page,
            "id": task_id,
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
                raise PyGocronException(
                    f"Can not Fetch Task List, Details: {response.text}"
                )
        else:
            raise PyGocronException(f"Can not Fetch Task List, Details: {response.text}")

    def get_task_id_by_name(self, name: str):
        """
        Get a task id by task name, note that task name can never duplicated, so the number of task id associated with the task name will be just one

        Params
        -----
        name: task name 
        """
        data = self.get_tasks(name=name)
        if data:
            try:
                task_id = data["data"][0]["id"]
            except IndexError:
                raise PyGocronException(f"Task Name `{name}` Not Found")
            else:
                return task_id

    def get_task_logs(
        self,
        task_id: int = None,
        page: int = 1,
        page_size: int = 20,
        protocol: int = None,
        status: int = None,
    ):
        """
        Get task logs

        Params
        -----
        task_id: task id 
        page:  page 
        page_size: page size
        protocol:  protocol, 1 for http and 2 for shell, default is 2
        status: task staus， 0 for all, 1 for failed, and for running tasks
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
                raise PyGocronException(
                    f"Can not Fetch Task Log, Details: {response.text}"
                )
        else:
            raise PyGocronException(f"Can not Fetch Task Log, Details: {response.text}")

    def check_run_status(self, task_id, run_id) -> RunStatus:  # 0 失败 1 在运行 2 成功
        """
        Check and reuturn a task tun status `RunStatus`, `RunStatus` is a Enum and has following status: RunStatus.FAILED, RunStatus.RUNNING and RunStatus.SUCCESS;
        Task usually has multiple runs ,so you need to specify ad `run_id` to retrieve a specific run log

        Params:
        ----
        task_is: task id
        run_id: run id
        """
        logs = self.get_task_logs(task_id=task_id, page_size=100)
        logs_data = logs["data"]
        if logs_data:
            for record in logs_data:  # 有序的， 按开始时间倒序
                if record["id"] == run_id:
                    status = record["status"]
                    if status == 0:
                        return RunStatus.FAILED
                    elif status == 1:
                        return RunStatus.RUNNING
                    elif status == 2:
                        return RunStatus.SUCCESS
                    else:
                        raise ValueError(f"Wrong status number: {status}")
            logger_print("run id not found", LogLevel.WARN)
            return None

    def get_nodes(self):
        """
        Get all nodes(server adddress info)
        """
        url = urljoin(self._base_url, "api/host/all")
        response = requests.get(url, headers=self._headers)

        if response.status_code == 200:
            data = json.loads(response.text)

            if data["message"] == "操作成功":
                return data["data"]
            else:
                raise PyGocronException(
                    f"Can not Fetch All Nodes(hosts), Details: {response.text}"
                )
        else:
            raise PyGocronException(
                f"Can not Fetch All Nodes(hosts), Details: {response.text}"
            )

    def disable_task(self, task_id: int):
        """
        Disable a task by task id 

        Params:
        ----
        task_id: task id 
        """
        url = urljoin(self._base_url, f"api/task/disable/{task_id}")

        response = requests.post(url, headers=self._headers)

        if response.status_code == 200:
            data = json.loads(response.text)
            if data["message"] == "操作成功":
                logger_print("Task Disabled Successfully", LogLevel.SUCCESS)
            else:
                raise PyGocronException(
                    f"Can Not Disable Task, Details: {response.text}"
                )
        else:
            raise PyGocronException(f"Can Not Disable Task, Details: {response.text}")

    def enable_task(self, task_id: int):
        """
        Enable a task
        -----
        task_id: task id 
        """
        url = urljoin(self._base_url, f"api/task/enable/{task_id}")

        response = requests.post(url, headers=self._headers)

        if response.status_code == 200:
            data = json.loads(response.text)
            if data["message"] == "操作成功":
                logger_print("Task Enabled Successfully", LogLevel.SUCCESS)
            else:
                raise PyGocronException(f"Can Not Enable Task, Details: {response.text}")
        else:
            raise PyGocronException(f"Can Not Enable Task, Details: {response.text}")

    def get_task_id_lagged(self, name, wait=1) ->  int:
        """
        Get a task id after waitting some second

        Params
        ----
        name: task name
        """
        time.sleep(wait)  # wait until the record be ready in database
        return self.get_task_id_by_name(name=name)

    def get_latest_run_id(self, task_id, wait=1) -> int:
        """
        Get most recent run id of a task

        Params
        ----
        task_id: task id
        """
        time.sleep(1)  # wait until the record be ready in database
        logs = self.get_task_logs(task_id=task_id,)
        logs_data = logs["data"]
        if logs_data:
            first_record = logs_data[0]
            return first_record["id"]


    def delete_task_by_tag(self, tag: str):
        """
        Delete all tasks related to the `tag`

        Params
        ----
        tag: tag
        """
        tasks = self.get_tasks(tag=tag)

        if tasks["total"] >= 1:
            data = tasks["data"]
            task_ids = [dat["id"] for dat in data]
        else:
            logger_print(f"No tasks associated with tag `{tag}`", LogLevel.WARN)
            return
        for task_id in task_ids:
            self.delete_task(task_id)

    def delete_task(self, task_id: int):
        """
        Delete a task by a `task id`

        Params
        ----
        task_id: task id 
        """
        url = urljoin(
            self._base_url, f"api/task/remove/{task_id}"
        )  # Gocron will not report an error even tge task id is not existed
        response = requests.post(url, headers=self._headers)
        if response.status_code == 200:
            data = json.loads(response.text)
            if data["message"] == "操作成功":
                logger_print("Task Deleted Successfully", LogLevel.SUCCESS)
            else:
                raise PyGocronException(
                    f"Can Not Delete the Task, Details: {response.text}"
                )
        else:
            raise PyGocronException(f"Can Not Delete the Task, Details: {response.text}")


    def get_all_methods(self):
        all_methods = dir(self)
        methods= [
            method
            for method in all_methods
            if not method.startswith("_") and method != "get_all_methods"
        ]
        print("\n".join(sorted(methods)))