from peewee import *

from backend.connection_manager import db


class Feed(Model):
    id = PrimaryKeyField()
    feed_id = CharField(max_length=100, null=False)
    title = CharField(max_length=100, null=False)
    zip_url = CharField(max_length=300, null=False)
    city_name = CharField(max_length=100, null=False)
    city_lat = FloatField(null=True)
    city_lng = FloatField(null=True)

    def __str__(self) -> str:
        return '{s.id} - {s.title} ({s.city_name})'.format(s=self)

    class Meta:
        database = db
