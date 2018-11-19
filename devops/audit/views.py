from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json, random, string, datetime
from audit import models, task_handler

@login_required
def index(request):
    return render(request, 'index.html')

def Login(request):
    error = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username,password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get('next') or '/')
        else:
            error = "密码或用户名错误"
    return render(request, 'login.html', {'error': error})

@login_required
def Logout(request):
    logout(request)
    return redirect('/login/')

@login_required
def hostList(request):

    return render(request, 'hostlist.html')

@login_required
def GetHostList(request):
    gid = request.GET.get('gid')
    if gid:
        if gid == '-1':  # 未分组
            host_list = request.user.account.host_user_binds.all()
        else:
            group_obj = request.user.account.host_groups.get(id=gid)
            host_list = group_obj.host_user_binds.all()
        data = json.dumps(list(host_list.values('id','host__hostname','host__ip_addr','host__port','host_user__username')))
        return HttpResponse(data)

@login_required
def getToken(request):
    """生成token并返回，设置过期时间为5min"""
    bind_host_id = request.POST.get('bind_host_id')
    time_obj = datetime.datetime.now() - datetime.timedelta(seconds=1800) # 30min ago 5min太短
    exist_token_objs = models.Token.objects.filter(account_id=request.user.account.id,
                                                   host_user_bind_id=bind_host_id,
                                                   date__gt = time_obj)
    if exist_token_objs:
        token_data = {'token': exist_token_objs[0].val}
    else:
        token_val = ''.join(random.sample(string.ascii_lowercase+string.digits,12))  #设置token值为12位
        token_obj = models.Token.objects.create(
            host_user_bind_id = bind_host_id,
            account = request.user.account,
            val = token_val
        )
        token_data = {'token': token_val}
    # print(token_data)
    return HttpResponse(json.dumps(token_data))

@login_required
def multiCmd(request):
    return render(request, 'multi_cmd.html')

@login_required
def multiTask(request):
    task_obj = task_handler.Task(request)
    if task_obj.is_valid():
        result = task_obj.run()
        return HttpResponse(json.dumps({'task_id':result}))

    return HttpResponse(json.dumps(task_obj.errors))

@login_required
def multiCmdResult(request):
    task_id = request.GET.get('task_id')
    task_obj = models.Task.objects.get(id=task_id)
    results = list(task_obj.tasklog_set.values('id','status','host_user_bind__host__hostname','host_user_bind__host__ip_addr','result'))

    return HttpResponse(json.dumps(results))

