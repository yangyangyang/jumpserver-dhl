import os, time, sys, multiprocessing, paramiko
from django.conf import settings

def cmd_run(tasklog_id,task_id,cmd_str):
    try:
        import django
        django.setup()
        from audit import models
        print("bind host id",bind_host_id,task_id)
        # tasklog_obj = models.TaskLog.objects.get(host_user_bind_id=bind_host_id,task_id=task_id)
        tasklog_obj = models.TaskLog.objects.get(id=tasklog_id)
        print('run cmd:',tasklog_obj,cmd_str)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(tasklog_obj.host_user_bind.host.ip_addr,
                    tasklog_obj.host_user_bind.host.port,
                    tasklog_obj.host_user_bind.host_user.username,
                    tasklog_obj.host_user_bind.host_user.password,
                    timeout=10)
        stdin, stdout, stderr = ssh.exec_command(cmd_str)

        result = stdout.read() + stderr.read()
        ssh.close()

        tasklog_obj.result = result or 'cmd has no result output.'
        tasklog_obj.status = 0  # 0 成功
        tasklog_obj.save()

    except Exception as e:
        print("error: ",e)

def file_transfer(bind_host_obj):
    pass


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    sys.path.append(BASE_DIR)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "devops.settings")
    import django
    django.setup()
    from audit import models
    task_id = sys.argv[1]

    #1、根据taskid获取任务对象，及任务关联的所有主机
    #2、调用多进程，每个子任务执行完毕后，把结果写入数据库

    task_obj = models.Task.objects.get(id=task_id)
    pool = multiprocessing.Pool(processes=10)

    if task_obj.task_type == 0: # cmd
        task_func = cmd_run
    else:
        task_func = file_transfer

    for bind_host in task_obj.tasklog_set.all():
    # for bind_host in ['10.0.0.32','10.0.0.29']:
        print(bind_host)
        pool.apply_async(task_func,args=(bind_host.id,task_obj.id,task_obj.content))


    pool.close()

    print("-------task_obj",task_obj)
    pool.join()