from peewee import *

from backend.connection_manager import db
from backend.models.agency import Agency
from backend.models.feed import Feed


class Route(Model):
    id = PrimaryKeyField()
    agency = ForeignKeyField(Agency, null=True, related_name="routes")
    route_id = BigIntegerField(null=False)
    short_name = CharField(null=False)
    long_name = CharField(null=False)
    """
        types:
        0 - Tram, Streetcar, Light rail. Any light rail or street level system within a metropolitan area.
        1 - Subway, Metro. Any underground rail system within a metropolitan area.
        2 - Rail. Used for intercity or long-distance travel.
        3 - Bus. Used for short- and long-distance bus routes.
        4 - Ferry. Used for short- and long-distance boat service.
        5 - Cable car. Used for street-level cable cars where the cable runs beneath the car.
        6 - Gondola, Suspended cable car. Typically used for aerial cable cars where the car is suspended from the cable.
        7 - Funicular. Any rail system designed for steep inclines.
    """
    type = SmallIntegerField(null=False, choices=list(range(0, 7)))
    route_color = CharField(max_length=6, null=True)
    route_text_color = CharField(max_length=6, null=True)
    feed = ForeignKeyField(Feed, null=False, related_name='routes')

    def __str__(self) -> str:
        return '{s.id} - {s.route_id} ({s.short_name})'.format(s=self)

    class Meta:
        database = db
