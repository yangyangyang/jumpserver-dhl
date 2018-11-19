# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-18 07:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0005_remove_task_host_user_binds'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tasklog',
            name='result',
            field=models.TextField(default='init...'),
        ),
        migrations.AlterField(
            model_name='tasklog',
            name='status',
            field=models.SmallIntegerField(choices=[(0, '成功'), (1, '失败'), (2, '超时'), (3, '初始化')]),
        ),
    ]
