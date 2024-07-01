from django.db import models

# Create your models here.

# 新稱商品表單. 繼承自django內建的 models
class ProductModel(models.Model):
    pname = models.CharField(max_length=30, null=False)
    pprice = models.IntegerField(null=False)
    pimage = models.CharField(max_length=40, null=False)
    pdescription = models.TextField(null=False)