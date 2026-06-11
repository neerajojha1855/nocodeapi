import uuid
from django.db import models, connection
from django.contrib.auth.models import User

class DynamicAPI(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='dynamic_apis'
    )
    name = models.CharField(max_length=80)
    slug = models.SlugField(
        max_length=100,
        unique=True
    )
    description = models.TextField(blank=True)
    original_prompt = models.TextField()
    llm_raw_response = models.JSONField()
    active = models.BooleanField(default=True)
    requires_auth = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sys_dynamic_api'

class APIField(models.Model):
    DATA_TYPE_CHOICES = [
        ('char', 'CharField'),
        ('text', 'TextField'),
        ('int', 'IntegerField'),
        ('float', 'FloatField'),
        ('bool', 'BooleanField'),
        ('date', 'DateField'),
        ('json', 'JSONField'),
    ]

    api = models.ForeignKey(
        DynamicAPI,
        on_delete=models.CASCADE,
        related_name='fields'
    )
    field_name = models.CharField(max_length=50)
    data_type = models.CharField(
        max_length=20,
        choices=DATA_TYPE_CHOICES
    )
    is_required = models.BooleanField(default=True)
    max_length = models.IntegerField(
        null=True,
        blank=True,
        default=255
    )
    default_value = models.CharField(
        max_length=255,
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'sys_api_field'
        unique_together = ('api', 'field_name')

def compile_virtual_model(api_instance):
    attrs = {
        '__module__': 'engine.models',
        'Meta': type('Meta', (), {'db_table': f"runtime_table_{api_instance.slug}"})
    }
    type_matrix = {
        'char': lambda f: models.CharField(
            max_length=f.max_length, null=not f.is_required, blank=not f.is_required
        ),
        'text': lambda f: models.TextField(
            null=not f.is_required,
            blank=not f.is_required
        ),
        'int': lambda f: models.IntegerField(
            null=not f.is_required,
            blank=not f.is_required
        ),
        'float': lambda f: models.FloatField(
          null=not f.is_required  
        ),
        'bool': lambda f: models.BooleanField(
            default=False
        ),
        'date': lambda f: models.DateField(
            null=not f.is_required
        ),
        'json': lambda f: models.JSONField(
            default=dict,
            blank=True
        ),
    }

    for f in api_instance.fields.all():
        attrs[f.field_name] = type_matrix[f.data_type](f)
    
    return type(str(api_instance.name), (models.Model,), attrs)

def execute_runtime_migration(model_class):
    with connection.schema_editor() as schema_editor:
        if model_class._meta.db_table not in connection.introspection.table_names():
            schema_editor.create_model(model_class)