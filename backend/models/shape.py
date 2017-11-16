from peewee import *

from backend.connection_manager import db
from backend.models.feed import Feed


class Shape(Model):
    id = PrimaryKeyField()
    shape_id = BigIntegerField(null=False)

    pt_lat = FloatField(null=False)
    pt_lon = FloatField(null=False)
    pt_sequence = IntegerField(null=False)
    dist_traveled = IntegerField(null=True)

    feed = ForeignKeyField(Feed, null=False, related_name='shapes')

    def __str__(self) -> str:
        return '{s.id} - {s.shape_id} ({s.pt_lat, s.pt_lon})'.format(s=self)

    class Meta:
        database = db
