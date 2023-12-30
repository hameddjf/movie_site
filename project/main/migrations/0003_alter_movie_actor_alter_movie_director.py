# Generated by Django 5.0 on 2023-12-28 09:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_alter_movie_actor_alter_movie_director'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='actor',
            field=models.ManyToManyField(blank=True, related_name='movies_actor', to='main.actor', verbose_name='بازیگران'),
        ),
        migrations.AlterField(
            model_name='movie',
            name='director',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='movies_directed', to='main.director', verbose_name='کارگردان'),
        ),
    ]
