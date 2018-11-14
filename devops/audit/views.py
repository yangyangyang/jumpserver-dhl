from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json

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
        data = json.dumps(list(host_list.values('id','host__hostname','host__ip_addr','host__port','host__idc__name','host_user__username')))
        return HttpResponse(data)