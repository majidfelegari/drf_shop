from django.db import models
from treebeard.mp_tree import MP_Node
from djshop.apps.catalog.managers import CategoryQuerySet
from djshop.libs.db.fields import UpperCaseCharField
from djshop.libs.db.models import AuditableModel
# Create your models here.


class Category(MP_Node):
    title = models.CharField(max_length=255, db_index=True)
    description = models.CharField(max_length=2048, null=True, blank=True)
    is_public = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, allow_unicode=True)


    objects = CategoryQuerySet.as_manager()
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title
    
class OptionGroup(models.Model):
    title = models.CharField(max_length=255, db_index=True)


    class Meta:
        verbose_name = "option group"
        verbose_name_plural = "option groups"

    def __str__(self):
        return self.title
    
class OptionGroupValue(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    group = models.ForeignKey(OptionGroup, on_delete=models.CASCADE)


    class Meta:
        verbose_name = "option group value"
        verbose_name_plural = "option groups values"

    def __str__(self):
        return self.title
    
class ProductClass(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    description = models.CharField(max_length=2048, null=True, blank=True)
    slug = models.SlugField(unique=True, allow_unicode=True)

    track_stock = models.BooleanField(default=True)
    require_shipping = models.BooleanField(default=True)

    options = models.ManyToManyField('Option', blank=True)

    @property
    def has_attribute(self):
        return self.attributes.exists()

    class Meta:
        verbose_name = "product class"
        verbose_name_plural = "product classes"

    def __str__(self):
        return self.title


class ProductAttribute(models.Model):
    class AttributeTypeChoice(models.TextChoices):
        text = 'text'
        integer = 'integer'
        float = 'float'
        option = 'option'
        multi_option = 'multi_option'

    product_class = models.ForeignKey(ProductClass, on_delete=models.CASCADE, null=True, related_name='attributes')
    title = models.CharField(max_length=64)
    type = models.CharField(max_length=16, choices=AttributeTypeChoice.choices, default=AttributeTypeChoice.text)
    option_group = models.ForeignKey(OptionGroup, on_delete=models.PROTECT, null=True, blank=True)
    required = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "product attribute"
        verbose_name_plural = "product attributes"


class Option(models.Model):
    class OptionTypeChoice(models.TextChoices):
        text = 'text'
        integer = 'integer'
        float = 'float'
        option = 'option'
        multi_option = 'multi_option'


    title = models.CharField(max_length=64)
    type = models.CharField(max_length=16, choices=OptionTypeChoice.choices, default=OptionTypeChoice.text)
    option_group = models.ForeignKey(OptionGroup, on_delete=models.PROTECT, null=True, blank=True)
    required = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "option"
        verbose_name_plural = "options"


class Product(AuditableModel):
    class ProdcutTypeChoice(models.TextChoices):
        standalone = 'standalone'
        parent = 'parent'
        child = 'child'

    structure = models.CharField(max_length=16, choices=ProdcutTypeChoice.choices, default=ProdcutTypeChoice.standalone)
    parent = models.ForeignKey("self", related_name="children", on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=128, null=True, blank=True)
    upc = UpperCaseCharField(max_length=24, unique=True, null=True, blank=True)
    is_public = models.BooleanField(default=True)
    slug = models.SlugField(unique=True, allow_unicode=True)
    meta_title = models.CharField(max_length=128, null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)

    product_class = models.ForeignKey(ProductClass, on_delete=models.PROTECT, null=True, blank=True, related_name='products')
    attributes = models.ManyToManyField(ProductAttribute, through='ProductAttributeValue')

    recommended_products = models.ManyToManyField('catalog.Product', through='ProductRecommendation', blank=True)
    categories = models.ManyToManyField(Category, related_name='categories')

    @property
    def main_image(self):
        if self.images.exists():
            return self.images.first()
        else:
            return None

    class Meta:
       verbose_name = "Product"
       verbose_name_plural = "products" 

class ProductAttributeValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE)

    value_text = models.TextField(null=True, blank=True)
    value_integer = models.IntegerField(null=True, blank=True)
    value_float = models.FloatField(null=True, blank=True)
    value_option = models.ForeignKey(OptionGroupValue, on_delete=models.PROTECT)
    value_multi_option = models.ManyToManyField(OptionGroupValue, blank=True, related_name='multi_value_attribute_value')

    class Meta:
       verbose_name = "attribute value"
       verbose_name_plural = "attribute values"
       unique_together = ('product','attribute') 

    
class ProductRecommendation(models.Model):
    primary = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='primary_recommendation')
    recommendation = models.ForeignKey(Product, on_delete=models.CASCADE)
    rank = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ('primary', 'recommendation')
        ordering = ('primary', '-rank')

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ForeignKey('media.Image', on_delete=models.PROTECT)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('display_order',)

    def delete(self, *args, **kwargs ):
        super().delete(*args, **kwargs)

        for index, image in enumerate(self.product.images.all()):
            image.display_order = index
            image.save()