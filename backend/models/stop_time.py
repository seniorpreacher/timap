from playhouse.postgres_ext import *

from backend.connection_manager import db
from backend.models.feed import Feed
from backend.models.stop import Stop
from backend.models.trip import Trip


class StopTime(Model):
    id = PrimaryKeyField()
    trip = ForeignKeyField(Trip, null=False, related_name='stop_times')
    # To convert this to a time: (datetime.datetime.min + StopTime.get(id=1).arrival_time).time()
    arrival_time = IntervalField(null=False)
    departure_time = IntervalField(null=False)
    stop = ForeignKeyField(Stop, null=False, related_name='stop_times')
    stop_sequence = IntegerField(null=False)
    stop_headsign = CharField(null=True)
    shape_dist_traveled = FloatField(null=True)
    feed = ForeignKeyField(Feed, null=False, related_name='stop_times')

    def __str__(self) -> str:
        return '{s.id} - {s.trip.id} ({s.arrival_time} » {s.departure_time})'.format(s=self)

    class Meta:
        database = db
