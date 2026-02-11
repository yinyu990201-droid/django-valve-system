from django.db import models
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    name = models.CharField(_("分类名称"), max_length=100)
    slug = models.SlugField(_("Slug"), unique=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children', 
        verbose_name=_("父级分类")
    )
    image = models.ImageField(_("分类图片"), upload_to='categories/', blank=True, null=True)
    description = models.TextField(_("描述"), blank=True)

    class Meta:
        verbose_name = _("分类")
        verbose_name_plural = _("分类")

    def __str__(self):
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' -> '.join(full_path[::-1])

class Product(models.Model):
    model_code = models.CharField(_("型号代码"), max_length=50, primary_key=True, help_text="唯一标识符，例如 CBEG-LJN")
    series = models.CharField(_("系列"), max_length=50, blank=True)
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='products', 
        verbose_name=_("所属分类")
    )
    description = models.TextField(_("产品描述"), blank=True)
    cavity = models.CharField(_("插孔标准"), max_length=50, blank=True, help_text="例如 T-10A")
    material = models.CharField(_("材质"), max_length=50, blank=True, default="Steel")
    
    # Images
    schematic_image = models.ImageField(_("原理图"), upload_to='products/schematics/', blank=True, null=True)
    product_image = models.ImageField(_("产品实物图"), upload_to='products/images/', blank=True, null=True)
    
    # Technical Specifications (JSON)
    specifications = models.JSONField(_("技术参数"), default=dict, blank=True, help_text="存储键值对形式的技术参数")
    
    is_active = models.BooleanField(_("是否上架"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("产品")
        verbose_name_plural = _("产品")

    def __str__(self):
        return f"{self.model_code}"

class ProductAttachment(models.Model):
    TYPE_CHOICES = [
        ('datasheet', _('数据表')),
        ('drawing', _('图纸')),
        ('manual', _('手册')),
        ('other', _('其他')),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(_("文件"), upload_to='products/attachments/')
    file_type = models.CharField(_("文件类型"), max_length=20, choices=TYPE_CHOICES, default='datasheet')
    title = models.CharField(_("标题"), max_length=100, blank=True)

    class Meta:
        verbose_name = _("产品附件")
        verbose_name_plural = _("产品附件")

    def __str__(self):
        return f"{self.product.model_code} - {self.get_file_type_display()}"

class PerformanceCurve(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='performance_curves')
    curve_type = models.CharField(_("曲线类型"), max_length=50, help_text="例如：压降 vs 流量")
    data_points = models.JSONField(_("数据点"), default=list, help_text="存储 [{'x': 10, 'y': 20}, ...] 格式的数据")

    class Meta:
        verbose_name = _("性能曲线")
        verbose_name_plural = _("性能曲线")

    def __str__(self):
        return f"{self.product.model_code} - {self.curve_type}"
