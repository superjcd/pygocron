# pygocron
定时任务管理系统[gocron](https://github.com/ouqiang/gocron)的python sdk。

## 安装
pypi:
```shell
pip install pygocron
```

## 使用

### 初始化PyGoCron实例

```python
from pygocron.pygocron import PyGoCron

pgc = PyGoCron(gocron_address="http://127.0.0.1:5920", # 你部署的地址,如果设置了环境变量GOCRON_ADDRESS,可以不填
        gocron_admin_user= "your admin username",  # 你的管理员账号,如果设置了环境变量GOCRON_ADMIN_USER,可以不填
        gocron_admin_password="your password")  # 你的管理员密码,如果设置了环境变量GOCRON_ADMIN_PASSWORD,可以不填
```

### 创建任务
```python
pgc.create_task(
        name: "测试任务",
        spec: "0 0 0 * * *", # cron 表达式， gocron支持精确到秒
        command: "echo 1", # 命令
        tag: str = "测试",    
)
```
**PS: 详细参数说明， 请使用`help(pgc.create_task)`进行查看， 后面的接口说明也是同样**

### 通过任务名获取任务id

```python
task_id = pgc.get_task_id_by_name(name="测试任务")

print(task_id)
```

### 手动执行任务

```python
pgc.run_task(task_id=1)
```

### 获取任务运行日志
```python
logs = pgc.get_task_logs(task_id=1)

print(logs)
```
注意返回的结果中的`status`字段, 1表示正在运行, 2表示运行成功; 然而在请求的的时候：status字段, 0表示所有任务(可省略), 1表示失败的任务, 2表示正在运行的任务, 所以你要获取正在运行的所有任务日志， 可以执行下面的命令:
```python
logs = pgc.get_task_logs(status=2)

print(logs)
```

### 获取所有节点
```python
nods = pgc.get_nodes()

print(nodes)
```

### 关闭任务
```python
pgc.disable_task(task_id=1)
```

### 开启任务
```python
pgc.enable_task(task_id=1)
```