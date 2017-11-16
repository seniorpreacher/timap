from peewee import *

from backend.connection_manager import db
from backend.models.feed import Feed


class Stop(Model):
    id = PrimaryKeyField()
    stop_id = BigIntegerField(null=False)
    name = CharField(null=False)
    lat = FloatField(null=False)
    lng = FloatField(null=False)
    timezone = CharField(max_length=100, null=True)
    feed = ForeignKeyField(Feed, null=False, related_name='stops')

    def __str__(self) -> str:
        return '{id} - {stop_id} ({name})'.format(id=self.id, stop_id=self.stop_id, name=self.name)

    class Meta:
        database = db
