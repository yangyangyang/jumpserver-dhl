from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class IDC(models.Model):
   name  = models.CharField(max_length=64, unique=True)
   def __str__(self):
      return self.name

class Host(models.Model):
   """主机信息"""
   hostname = models.CharField(max_length=64, unique=True)
   ip_addr  = models.GenericIPAddressField(unique=True)
   port     = models.IntegerField(default=22)
   idc      = models.ForeignKey("IDC")
   # host_groups = models.ManyToManyField("HostGroup")
   # host_users = models.ManyToManyField("HostUser")
   enabled = models.BooleanField(default=True)

   def __str__(self):
      return "%s-%s" %(self.hostname,self.ip_addr)

class HostGroup(models.Model):
   """主机组"""
   name  = models.CharField(max_length=64, unique=True)
   host_user_binds = models.ManyToManyField("HostUserBind")
   def __str__(self):
      return self.name

class HostUser(models.Model):
   """主远程机的用户信息"""
   auth_type_choices = ((0,'ssh-password'),(1,'ssh-key'))
   auth_type   = models.SmallIntegerField(choices=auth_type_choices)
   username    = models.CharField(max_length=32)
   password    = models.CharField(blank=True, null=True,max_length=128)

   def __str__(self):
      return "%s-%s-%s" %(self.get_auth_type_display(),self.username,self.password)

   class Meta:
         unique_together = ('username', 'password')

class HostUserBind(models.Model):
   """绑定主机和用户"""
   host = models.ForeignKey("Host")
   host_user = models.ForeignKey("HostUser")

   def __str__(self):
      return "%s-%s" %(self.host, self.host_user)

   class Meta:
      unique_together = ('host','host_user')

class AuditLog(models.Model):
   """审计日志"""
   session = models.ForeignKey("SessionLog")
   command = models.TextField()
   cmd_date = models.DateTimeField(auto_now_add=True)
   def __str__(self):
      return "%s-%s" %(self.session,self.command)


class SessionLog(models.Model):
   account = models.ForeignKey('Account')
   host_user_bind = models.ForeignKey("HostUserBind")
   start_date = models.DateTimeField(auto_now_add=True)
   end_date = models.DateTimeField(blank=True,null=True)

   def __str__(self):
      return "%s-%s" %(self.account,self.host_user_bind)


class Account(models.Model):
   """
   跳板机账号
   1、扩展
   2、继承
   """
   user = models.OneToOneField(User)
   name = models.CharField(max_length=64)
   host_user_binds = models.ManyToManyField("HostUserBind",blank=True)
   host_groups = models.ManyToManyField("HostGroup",blank=True)


