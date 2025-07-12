from django.db import models


class VideoQuerySet(models.query.QuerySet):

    def get_count(self):
        return self.count()

    def get_published_list(self):
        return self.order_by('-create_time')

    def get_search_list(self, keyword):
        if keyword:
            return self.filter(title__contains=keyword).order_by('-create_time')
        else:
            return self.order_by('-create_time')

    def get_recommend_list(self):
        return self.order_by('-view_count')[:4]


class Classify(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    pass


class Video(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True, verbose_name="标题")
    desc = models.CharField(max_length=10, blank=True, null=True, verbose_name="描述")
    file = models.FileField(max_length=255, verbose_name="视频文件", upload_to='video/')
    cover = models.ImageField(upload_to='cover/', blank=True, null=True, verbose_name="封面")
    view_count = models.IntegerField(default=0, blank=True, verbose_name="观看次数")
    create_time = models.DateTimeField(auto_now_add=True, blank=True, max_length=20, verbose_name="创建时间")

    objects = VideoQuerySet.as_manager()

    class Meta:
        db_table = "videos"

    def increase_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])
