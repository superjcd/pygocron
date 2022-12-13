from pygocron.pygocron import PyGoCron


pgc = PyGoCron()

# task_id = pgc.create_task(name="test001", spec="0 0 0 * * *", command="sleep 15")

# print(task_id)

# pgc.run_task(task_id=58)

# run_id = pgc.get_latest_run_id(task_id=58)

# print(run_id)

status = pgc.check_run_status(task_id=58, run_id=9607)

print(status)

# response = pgc.get_task_logs(42)

# print(response["data"][0])
