from django.db import models
##文档模型
class ValveDocument(models.Model):
    title = models.CharField("文档名称", max_length=200)
    file = models.FileField("PDF 文件", upload_to='documents/')
    uploaded_at = models.DateTimeField("上传时间", auto_now_add=True)

    def __str__(self):
        return self.title

##产品模型
class CartridgeValve(models.Model):
    name = models.CharField("型号名称", max_length=100)
    series = models.CharField("系列", max_length=100)
    description = models.TextField("产品描述", blank=True)
    application = models.CharField("应用场景", max_length=200, blank=True)

    documents = models.ManyToManyField(
        ValveDocument,
        blank=True,
        related_name="products",
        verbose_name="技术文档"
    )

    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    def __str__(self):
        return f"{self.series} - {self.name}"
