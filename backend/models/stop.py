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

    @classmethod
    def get_nearby(cls, lat, lng, distance):
        cursor = db.execute_sql('''
                        SELECT
                            stop.id AS id,
                            %(distance_unit)s * DEGREES(ACOS(COS(RADIANS(%(lat)s))
                                             * COS(RADIANS(stop.lat))
                                             * COS(RADIANS(%(lng)s - stop.lng))
                                             + SIN(RADIANS(%(lat)s))
                                             * SIN(RADIANS(stop.lat)))) AS distance
                        FROM stop

                        WHERE stop.lat
                              BETWEEN %(lat)s - (%(radius)s / %(distance_unit)s)
                              AND %(lat)s + (%(radius)s / %(distance_unit)s)
                              AND stop.lng
                              BETWEEN %(lng)s - (%(radius)s / (%(distance_unit)s * COS(RADIANS(%(lat)s))))
                              AND %(lng)s + (%(radius)s / (%(distance_unit)s * COS(RADIANS(%(lat)s))))
                    ''', {
            "lat": lat,
            "lng": lng,
            "radius": distance / 1000,
            "distance_unit": 111.045,
        })

        result = []

        for nearby in cursor.fetchall():
            result.append(cls.get(id=nearby[0]))

        return result

    class Meta:
        database = db
