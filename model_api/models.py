from django.db import models


# Create your models here.
class Roles(models.Model):
    name = models.CharField(max_length=50, default='未命名')
    desc = models.TextField(default='暂无描述')
    prompt = models.TextField(null=False, blank=False, default='你是一个AI助手，回答简洁')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.name
