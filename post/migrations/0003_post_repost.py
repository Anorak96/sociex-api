# Generated by Django 5.1.4 on 2025-07-08 11:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0002_remove_repostimage_post_delete_repost_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='repost',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reposts', to='post.post'),
        ),
    ]
