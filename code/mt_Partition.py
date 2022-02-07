# Pràctica de creació de zones electorals per algorismes genètics
#
# IC - MUSI 21 22 - UIB
#
# Alumne: Lluís Bernat Ladaria

"""
Partition class - library
"""

#
# system libraries
#

import pandas as pd
import geopandas as gpd
from shapely.geometry.base import BaseGeometry
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.point import Point
import logging as log
import random

#
# ours libraries
#

from mt_Zone import Zone
import mt_common as our


class Partition:
    """
    Object that encapsulates the genotype of a map partition
    and all the necessary methods to work with

    A partition is a list of zones that covers a region map
    """

    def __init__(self, data: pd.DataFrame, conn: dict,
                 valid_area: BaseGeometry,
                 num_zones: int, logger: log.Logger):
        # create an instance of the partition genotype
        self.data = data
        self.conn = conn
        self.valid_area = valid_area
        self.num_zones = num_zones
        self.logger = logger

        [self.x_min, self.y_min, self.x_max, self.y_max] = \
            self.valid_area.bounds

        num_districts = len(data)
        self.num_districts = num_districts

        self.logger.debug(
            our.MG_INFO_PARTITION_INIT.format(self.num_districts, self.num_zones))

        self.genotype = list()
        self._generate_genotype()

        pass

    def _generate_genotype(self):
        # generate as many zone centroids as num_zones value
        #

        # initially the centroids list must be empty
        if len(self.genotype) > 0:
            raise OverflowError(our.MG_DEBUG_INTERNAL_ERROR)

        i = 0
        while i < self.num_zones:
            # generate a random (x, y) point into map cartesian bounds
            x = random.uniform(self.x_min, self.x_max)
            y = random.uniform(self.y_min, self.y_max)
            p = Point(x, y)
            # the point must be into the region of interest
            # and of course must be unique to this instance
            if self.valid_area.contains(p) and p not in self.genotype:
                i += 1
                self.genotype.append(p)

        pass

    def fit(self):

        pass
