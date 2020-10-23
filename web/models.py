from django.db import models
# Create your models here.


class UserInfo(models.Model):
    username = models.CharField(verbose_name='Username', max_length=32, db_index=True)
    email = models.EmailField(verbose_name='Email',max_length=32)
    mobile_phone = models.CharField(verbose_name='Mobile Number', max_length=32)
    password = models.CharField(verbose_name='Password', max_length=32)
