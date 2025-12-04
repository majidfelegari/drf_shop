from django.db import models

class UpperCaseCharField(models.CharField):
    def from_db_value(self, value, *args, **kwargs):
        pass

    def to_python(self, value):
        val = super().to_python(value)
        if isinstance(val, str):
            return val.upper()
        return val