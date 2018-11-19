import json, subprocess
from audit import models
# from threading import Thread
from django.conf import settings
from django.db.transaction import atomic


class Task(object):
    """批量任务：包括命令和文件传输"""
    def __init__(self,request):
        self.request = request
        self.errors = []
        self.task_data = None


    def is_valid(self):
        """验证命令和主机列表是否合法"""
        task_data = self.request.POST.get('task_data')
        if task_data:
            self.task_data = json.loads(task_data)
            if self.task_data.get('task_type') == 'cmd':
                if self.task_data.get('cmd') and self.task_data.get('selected_host_ids'):
                    return True
                self.errors.append({'invalid_argument': 'cmd or host_list is empty.'})
            elif self.task_data.get('task_type') == 'file_transfer':
                self.errors.append({'invalid_argument':'cmd or host_list is empty.'})
            else:
                self.errors.append({'invalid_argument': 'task_type is invalid.'})
        self.errors.append({'invalid_data':'task_data is not exist.'})

    def run(self):
        """启动任务，并返回task_id"""
        task_func = getattr(self, self.task_data.get('task_type'))
        task_id = task_func()
        return task_id

    @atomic
    def cmd(self):
        """批量任务"""
        # print("run multi task ...")
        task_obj = models.Task.objects.create(
            # task_type = self.task_data.get('task_type'),
            task_type = 0,
            account = self.request.user.account,
            content = self.task_data.get('cmd'),
            # host_user_binds =
        )
        # task_obj.host_user_binds.add(*self.task_data.get('selected_host_ids'))
        tasklog_objs = []
        host_ids = set(self.task_data.get('selected_host_ids'))
        for host_id in host_ids:
            tasklog_objs.append(
                models.TaskLog(task_id=task_obj.id,
                               host_user_bind_id=host_id,
                               status = 3
                                )
            )
        models.TaskLog.objects.bulk_create(tasklog_objs,100)


        # 执行任务
        # for host_id in self.task_data.get('selected_host_ids'):
        #     t = Thread(target=self.run_cmd,args=(host_id,self.task_data.get('cmd')))
        #     t.start()
        # 可能会出现进程未执行完，而视图函数一直等待的情况，
        # 故使用subprocess单独启动一个独立的进程
        cmd_str = "python %s %s"  %(settings.MULTI_TASK_SCRIPT,task_obj.id)
        # cmd_str = "/home/denghonglin/env/py35/bin/python3 /home/denghonglin/demo/devops/multitask.py %s" %task_obj.id
        multitask_obj = subprocess.Popen(cmd_str,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        # print("task result: ",multitask_obj.stdout.read(),multitask_obj.stderr.read().decode('utf8'))
        return task_obj.id

    def run_cmd(self):
        pass

    def file_transfer(self):
        """批量文件"""