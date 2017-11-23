from peewee import *
from playhouse.fields import ManyToManyField

from backend.connection_manager import db
from backend.models.feed import Feed
from backend.models.route import Route


class Stop(Model):
    id = PrimaryKeyField()
    stop_id = BigIntegerField(null=False)
    name = CharField(null=False)
    lat = FloatField(null=False)
    lng = FloatField(null=False)
    timezone = CharField(max_length=100, null=True)
    feed = ForeignKeyField(Feed, null=False, related_name='stops')
    routes = ManyToManyField(Route, related_name='stops')

    def __str__(self) -> str:
        return '{s.id} - {s.stop_id} ({s.name})'.format(s=self)

    class Meta:
        database = db
