from .geomutils import togeometry
from qgis.core import (
    QgsFeature,
    QGis
)
import osgeo.ogr as ogr
from .ogrspatialite import OGRSPatialite


class Reporter(object):

    def __init__(self, output_path):
        # output file is path and filename is a db based on timestamp
        self.layer = None
        self.driver = None
        self.feature = None
        self.data_source = None
        self.output_path = output_path
        self._initialize_db()

    # Maybe take a Rule as first argument? Rule knows its name and should now what types are touched
    def reportError(self, rulename, typeinfo, message, geometry):
        self.report(rulename, typeinfo, message, geometry, "error")

    def reportWarning(self, rulename, typeinfo, message, geometry):
        self.report(rulename, typeinfo, message, geometry, "warning")

    def report(self, rulename, typeinfo, message, geometry, level):
        geometry = togeometry(geometry)
        fields = [
            ('rulename', unicode(rulename).encode('utf-8')),
            ('typeinfo', unicode(typeinfo).encode('utf-8')),
            ('message', unicode(message).encode('utf-8')),
            ('level', unicode(level).encode('utf-8'))
        ]
        print fields
        # QGis.flatType if we don't care about 25D and whatnot
        if QGis.flatType(geometry.wkbType()) == QGis.WKBLineString:
            self.db.add_feature_to_layer(
                'linestring',
                fields,
                geometry
            )

        if QGis.flatType((geometry.wkbType())) == QGis.WKBPoint:
            self.db.add_feature_to_layer(
                'point',
                fields,
                geometry
            )

        if QGis.flatType((geometry.wkbType())) == QGis.WKBPolygon:
            self.db.add_feature_to_layer(
                'polygon',
                fields,
                geometry
            )

    def _initialize_db(self):
        self.db = OGRSPatialite(self.output_path)
        fields = [
            ('rulename', ogr.OFTString),
            ('typeinfo', ogr.OFTString),
            ('message', ogr.OFTString),
            ('level', ogr.OFTString)
        ]
        # Add layer for linestring
        self.db.add_layer(
            'linestring',
            ogr.wkbLineString25D,
            fields
        )
        # Add layer for points
        self.db.add_layer(
            'point',
            ogr.wkbPoint25D,
            fields
        )
        # Add layer for polygons
        self.db.add_layer(
            'polygon',
            ogr.wkbPolygon25D,
            fields
        )
