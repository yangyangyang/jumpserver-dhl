__author__ = 'Administrator'
import subprocess, random, string, datetime
from django.contrib.auth import authenticate
from django.conf import settings
from audit import models
from audit.backend import ssh_interactive

class UserShell(object):
    """用户登录跳板机后的shell"""
    def __init__(self, sys_argv):
        self.sys_argv = sys_argv
        self.user = None

    def token_auth(self):
        count = 0
        while count < 3:
            user_input = input("请输入token:").strip()
            if len(user_input) == 0:
                return
            if len(user_input) != 12:
                print("token长度为12位")
            else:
                time_obj = datetime.datetime.now() - datetime.timedelta(seconds=1800)  # 30min ago
                token_obj = models.Token.objects.filter(val=user_input,date__gt=time_obj).first()
                if token_obj:
                    # token_obj = token_objs
                    if token_obj.val == user_input:
                        self.user = token_obj.account.user
                        return token_obj
            count += 1


    def auth(self):
        count = 0
        while count  < 3:
            username = input("username: ").strip()
            password = input("password: ").strip()
            user = authenticate(username=username,password=password)
            if not user:
                count += 1
                print("账户或密码错误，请重新输入!")
            else:
                self.user = user
                return True
        else:
            print("输入3次错误！")

    def start(self):
        """启动交互程序"""
        token_obj = self.token_auth()
        if token_obj:
            ssh_interactive.ssh_session(token_obj.host_user_bind, self.user)
            exit()
        if self.auth():
            # print(self.user.account.host_user_binds.all())
            while True:
                host_groups = self.user.account.host_groups.all()
                for index,group in enumerate(host_groups):
                    print("%s.\t%s[%s]" %(index,group,group.host_user_binds.count()))
                print("%s.\t未分组机器[%s]" % (len(host_groups), self.user.account.host_user_binds.count()))
                try:
                    choice = input("请选择主机组(exit/quit 退出):").strip()
                    if choice.isdigit():
                        choice = int(choice)
                        host_bind_list = None
                        if choice >= 0 and choice < len(host_groups):
                            selected_group = host_groups[choice]
                            host_bind_list = selected_group.host_user_binds.all()
                        elif choice == len(host_groups): # 选择未分组机器
                            host_bind_list = self.user.account.host_user_binds.all()
                        if host_bind_list:
                            while True:
                                for index, host in enumerate(host_bind_list):
                                    print("%s.\t%s" % (index, host))
                                choice2 = input("请选择主机(按q 返回上一级):").strip()
                                if choice2.isdigit():
                                    choice2 = int(choice2)
                                    print(choice2)
                                    if choice2 >= 0 and choice2 < len(host_bind_list):
                                        selected_host = host_bind_list[choice2]

                                        ssh_interactive.ssh_session(selected_host,self.user)

                                        # s = string.ascii_lowercase + string.digits
                                        # random_tag = ''.join(random.sample(s,10))
                                        # session_obj = models.SessionLog.objects.create(account=self.user.account,host_user_bind=selected_host)
                                        # # 修改openssh源码（ssh.c）
                                        # cmd = "sshpass -p %s ssh %s@%s -p %s -o StrictHostKeyChecking=no" %(selected_host.host_user.password,selected_host.host_user.username,selected_host.host.ip_addr,selected_host.host.port )
                                        #
                                        # # start strace, and sleep 1 random_tag,session_obj.id
                                        # session_tracker_script = "sh %s %s %s " %(settings.SESSION_TRACKER_SCRIPT,random_tag,session_obj.id)
                                        # session_tracker_obj = subprocess.Popen(session_tracker_script, shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                                        #
                                        # ssh_channel = subprocess.run(cmd,shell=True)
                                        # print(session_tracker_obj.stdout.read(), session_tracker_obj.stderr.read())

                                elif choice2 == 'q':
                                    break
                    if choice == 'quit' or choice == 'exit':
                        break

                except KeyboardInterrupt as e:
                    pass


