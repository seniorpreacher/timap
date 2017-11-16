from peewee import *

from backend.connection_manager import db
from backend.models.feed import Feed


class Agency(Model):
    id = PrimaryKeyField()
    agency_id = CharField(max_length=100, null=True)
    name = CharField(max_length=100, null=False)
    url = CharField(max_length=300, null=False)
    timezone = CharField(max_length=100, null=False)
    lang = CharField(max_length=100, null=True)
    phone = CharField(max_length=100, null=True)
    fare_url = CharField(max_length=300, null=True)
    email = CharField(max_length=100, null=True)
    feed = ForeignKeyField(Feed, null=False, related_name='agencies')

    def __str__(self) -> str:
        return '{id}/{agency_id} - {name}'.format(id=self.id, agency_id=self.agency_id, name=self.name)

    class Meta:
        database = db
