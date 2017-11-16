from peewee import *

from backend.connection_manager import db
from backend.models.feed import Feed
from backend.models.route import Route
from backend.models.shape import Shape


class Trip(Model):
    id = PrimaryKeyField()
    route = ForeignKeyField(Route, null=False, related_name='trips')
    trip_id = BigIntegerField(null=False)
    short_name = CharField(null=True)
    headsign = CharField(null=True)
    direction = BooleanField(null=True)
    shape = ForeignKeyField(Shape, null=True, related_name='trips')
    feed = ForeignKeyField(Feed, null=False, related_name='trips')

    def __str__(self) -> str:
        return '{s.id} - {s.trip_id} ({s.short_name})'.format(s=self)

    class Meta:
        database = db
