from django.db import models
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    name = models.CharField(_("Category Name"), max_length=100)
    slug = models.SlugField(_("Slug"), unique=True)
    description = models.TextField(_("Description"), blank=True)
    image = models.ImageField(_("Category Image"), upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name=_("Parent Category"))

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' -> '.join(full_path[::-1])

class ValveDocument(models.Model):
    TYPE_CHOICES = [
        ('datasheet', _('Datasheet')),
        ('drawing', _('Drawing')),
        ('manual', _('Manual')),
        ('other', _('Other')),
    ]
    
    title = models.CharField(_("Document Title"), max_length=200)
    file = models.FileField(_("PDF File"), upload_to='documents/')
    file_type = models.CharField(_("Document Type"), max_length=20, choices=TYPE_CHOICES, default='datasheet')
    version = models.CharField(_("Version"), max_length=20, blank=True, help_text="e.g. v1.0, Rev A")
    uploaded_at = models.DateTimeField(_("Uploaded At"), auto_now_add=True)

    class Meta:
        verbose_name = _("Valve Document")
        verbose_name_plural = _("Valve Documents")

    def __str__(self):
        return f"{self.title} ({self.get_file_type_display()})"

class CartridgeValve(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name=_("Category"), null=True, blank=True)
    name = models.CharField(_("Model Name"), max_length=100)
    series = models.CharField(_("Series"), max_length=100)
    thumbnail = models.ImageField(_("Product Thumbnail"), upload_to='products/thumbnails/', blank=True, null=True)
    description = models.TextField(_("Description"), blank=True)
    application = models.CharField(_("Application"), max_length=200, blank=True)
    
    # Technical Specifications
    max_pressure = models.FloatField(_("Max Pressure (bar)"), help_text=_("Maximum operating pressure in bar"), null=True, blank=True)
    max_flow = models.FloatField(_("Max Flow (l/min)"), help_text=_("Maximum flow rate in l/min"), null=True, blank=True)
    cavity = models.CharField(_("Cavity"), max_length=100, blank=True, help_text=_("Installation cavity dimensions"))
    material = models.CharField(_("Material"), max_length=100, blank=True, default="Steel")
    
    documents = models.ManyToManyField(
        ValveDocument,
        blank=True,
        related_name="products",
        verbose_name=_("Technical Documents")
    )
    
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    class Meta:
        verbose_name = _("Cartridge Valve")
        verbose_name_plural = _("Cartridge Valves")

    def __str__(self):
        return f"{self.series} - {self.name}"
