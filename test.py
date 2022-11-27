from pygocron.pygocron import PyGoCron


pgc = PyGoCron()  # "http://192.168.0.90:5920", "admin", "Hooya911."

response = pgc.get_task_logs(status=1)

print(response["data"][2])
