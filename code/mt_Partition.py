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
        #

        # save parameters
        self.data = data
        self.conn = conn
        self.valid_area = valid_area
        self.num_zones = num_zones
        self.logger = logger

        # calculate number of districts to fit
        num_districts = len(data)
        self.num_districts = num_districts

        # say hello
        self.logger.debug(
            our.MG_INFO_PARTITION_INIT.format(self.num_districts, self.num_zones))

        # calc cartesian boundaris (the smaller rectangle that cotains the map)
        [self.x_min, self.y_min, self.x_max, self.y_max] = \
            self.valid_area.bounds

        # our list of centroids
        self.genotype = list()

        # our list of zones
        # will be populated at compose_partition() method
        self.zones = list()

        # our solution score
        self.score = None

        pass

    def generate_genotype(self):
        # generate as many zone centroids as num_zones value
        # and add them to the genotype (a list)

        # initially the centroids list must be empty
        if len(self.genotype) > 0:
            raise OverflowError(our.MG_DEBUG_INTERNAL_ERROR)

        for i in range(self.num_zones):
            p = self._generate_new_valid_point()
            self.genotype.append(p)

        pass

    def _generate_new_valid_point(self):
        # return a new valid point
        # (a no repeated point that is contained
        # into the study region)

        p = self._generate_point()

        # the point must be into the study region
        # and of course must be unique to this instance
        while not self.valid_area.contains(p) or p in self.genotype:
            # get a new point
            # while point is not valid or point is not unique
            p = self._generate_point()

        return p

    def _generate_point(self):
        # return a point into rectangular map boundaries
        # the point can be invalid
        # (to be valid must be contained
        # into the study region)

        # generate a random (x, y) point into map cartesian bounds
        x = random.uniform(self.x_min, self.x_max)
        y = random.uniform(self.y_min, self.y_max)
        p = Point(x, y)

        return p

    def compose_partition(self):
        # for each district, locate the nearest
        # zone future centroid and add it
        # to this zone string

        # TODO

        pass

    def evaluate(self):
        # calculate fitness function value
        # for whole partition

        self.score = 0
        # TODO

        pass

    def mutate(self, prob: float):
        # with probability 'prob'
        # apply a random mutation

        # TODO

        pass

    def plot(self):

        # TODO

        pass

    def savefig(self, path: str):

        # TODO

        pass
