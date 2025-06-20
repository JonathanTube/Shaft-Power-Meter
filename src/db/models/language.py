from peewee import CharField

from ..base import BaseModel


class Language(BaseModel):
    code = CharField(verbose_name="code")

    chinese = CharField(verbose_name="Chinese")

    english = CharField(verbose_name="English")

    class Meta:
        table_name = 'language'
