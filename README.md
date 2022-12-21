# pygocron
Python Sdk for [gocron](https://github.com/ouqiang/gocron)

## Install
### pypi:
```shell
pip install pygocron
```

## How to use

### Prerequisite
#### Install the gocron 
Go to [gocron](https://github.com/ouqiang/gocron) homepage,  for those don't understand Chinese, you can follow my brief instruction here to delpoy it:

- firt, go to [gocron relase page](https://github.com/ouqiang/gocron/releases) and find a proper `gocron` version, for Linux user, u can download the `gocron-v{VERSION}-linux-amd64.tar.gz`, unzip the downloaded file, and u will find a executable file named `gocron`, then you can just run `./gocron web`(run `nohup ./gocron web &` to run a backgroudly)
- second, go to [gocron relase page](https://github.com/ouqiang/gocron/releases) again,this time we will download the `gocron-node-v{VERSION}-linux-amd64.tar.gz`, unzip the downloaded file, and u will find a executable file named `gocron-node`, then you can just run `./gocron-node`(run `nohup ./gocron &` to run it backgroudly) 

- last, u can open the browser and go to the url of `http://{your server address}:5920`, the page u saw was a  `Configuration page`, you need to define such as `admin username` and `password` sort of things, and donn't forget to provide a database connection too(`mysql` or `postgresql`)


### Instantiate a PyGoCron object

```python
from pygocron.pygocron import PyGoCron

pgc = PyGoCron(gocron_address="http://127.0.0.1:5920", 
        gocron_admin_user= "your admin username", 
        gocron_admin_password="your password")
```

Off course, u can initialize it by run `pgc = PyGoCron()`, after u setted the following environment variables:
-  `GOCRON_ADDRESS`
-  `GOCRON_ADMIN_USER`
-  `GOCRON_ADMIN_PASSWORD`


### Create a task
```python
pgc.create_task(
        name: "test job",
        spec: "0 0 0 * * *", # cron expression, differ from normal cron expression, it can be set at `second` level(the third `0` here)
        command: "echo 1", # system command
        tag: str = "Test",   
)
```

**PS: To see descriptions for all arguments, u can use `help(pgc.create_task)`, same for following methods**

### Get a task id by name

```python
task_id = pgc.get_task_id_by_name(name="test job")

print(task_id)
```

### Run a task off manualy

```python
pgc.run_task(task_id=1)
```

### Get task log
```python
logs = pgc.get_task_logs(task_id=1)

print(logs)
```
Note the `status` field in the return object, 0 stands for `failed`, 1 for `running`, and 2 for `success`; 
While running `get_task_logs` and use `status` as an argument, things will be totally different, 0 now for all tasks(default value), 1 for faild tasks and 2 for running tasks.
For instance if u want to get all running tasks u can run:
```python
logs = pgc.get_task_logs(status=2)

print(logs)
```
>Better idea is to keep the meanning of `status` identical, unfortunately this is the `gocron` design
> 
### Get all existing nodes
```python
nods = pgc.get_nodes()

print(nodes)
```

### Disable a task
```python
pgc.disable_task(task_id=1)
```

### Enable a task 
```python
pgc.enable_task(task_id=1)
```

### Other methods
run`pgc.get_all_methods()` to get all exsiting methods
