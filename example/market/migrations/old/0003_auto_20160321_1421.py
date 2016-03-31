# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-21 14:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0002_auto_20160321_1349'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invtype',
            name='itemgroup',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='market.ItemGroup', verbose_name='Related Item Group (groupID)'),
        ),
        migrations.AlterField(
            model_name='invtype',
            name='itemmarketgroup',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='market.ItemMarketGroup', verbose_name='Related market Group (marketGroupID)'),
        ),
        migrations.AlterField(
            model_name='itemmarketgroup',
            name='parentGroupID',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='market.ItemMarketGroup', verbose_name='Parent market group'),
        ),
    ]