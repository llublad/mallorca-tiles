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

from shapely.geometry.base import BaseGeometry
from shapely.geometry.point import Point
import logging as log
import random
import numpy as np

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

    def __init__(self, data: list, mean_value: float, geodata: dict,
                 valid_area: BaseGeometry,
                 num_zones: int, logger: log.Logger):
        # create an instance of the partition genotype
        #

        # save parameters
        self.data = data
        self.mean_value = mean_value
        self.geodata = geodata
        self.valid_area = valid_area
        self.num_zones = num_zones
        self.logger = logger

        # calculate number of districts to fit
        num_districts = len(data)
        self.num_districts = num_districts

        # say hello
        self.logger.debug(
            our.MG_INFO_PARTITION_INIT.format(
                self.num_districts, self.num_zones, self.mean_value))

        # calc cartesian boundaris (the smaller rectangle that cotains the map)
        [self.x_min, self.y_min, self.x_max, self.y_max] = \
            self.valid_area.bounds

        # our list of zone centers
        self.genotype = list()

        # our list of zones
        # will be populated at compose_partition() method execution
        self.zones = list()

        # our solution score
        self.score = None

        pass

    def get_score(self):
        # return partition score
        #

        if self.score is not None:
            score = self.score
        else:
            raise ValueError(our.MG_DEBUG_INTERNAL_ERROR)

        return score

    def generate_genotype(self):
        # generate as many zone centers as num_zones value
        # and add them to the genotype (a list)

        # initially the centers list must be empty
        if len(self.genotype) > 0:
            raise OverflowError(our.MG_DEBUG_INTERNAL_ERROR)

        # how many zones?
        num_zones = self.num_zones

        for i in range(num_zones):
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

        # initially the zone list must be empty
        if len(self.zones) > 0:
            raise ValueError(our.MG_DEBUG_INTERNAL_ERROR)

        # populate the zones instances list
        # each one with a genotype center point
        for center in self.genotype:
            new_zone = Zone(center=center, logger=self.logger)
            self.zones.append(new_zone)

        # assign each district to the nearest zone center
        # using the district centroid to zone center distance

        for district in self.data:
            # retrieve district interesting data
            dis_code = district[our.LIST_DATA_CODE_COL]
            dis_value = district[our.LIST_DATA_VALUE_COL]
            dis_geodata = self.geodata.get(dis_code)
            dis_centroid = Point(dis_geodata[our.DICT_DISTRICT_CENTROID_POINT])

            # compute a numpy vector with the
            # distances from the district centroid to each zone center
            zone_distances = np.array(
                [dis_centroid.distance(p) for p in self.genotype],
                dtype=float)

            # search the nearest zone center
            zone_at = np.amin(zone_distances)
            nearest_zone_index = \
                np.where(zone_distances == zone_at)[0][0]

            nearest_zone: Zone = self.zones[nearest_zone_index]
            nearest_zone.add_district(dis_code=dis_code,
                                      dis_value=dis_value,
                                      zone_distance=zone_at,
                                      dis_geodata=dis_geodata)

        pass

    def evaluate(self):
        # calculate fitness function value
        # for whole partition

        score = 0.

        for zone in self.zones:
            # calculate the connectivity cost of the zone
            # and the number of unconnected parts
            zone.calc_cost()
            # get the connectivity cost
            zone_cost = zone.get_cost()
            # get the number of unconnected parts
            zone_unconnected = zone.get_unconnected()
            # get the zone value (total zone population)
            zone_value = zone.get_value()
            # calculate the partial score due to this zone configuration
            zone_score = abs(zone_value - self.mean_value) + self.mean_value * (zone_cost + zone_unconnected)
            # carry zone score
            score += zone_score

        self.score = score

        # a debug line
        # self.zones[0]._log_zone_dump()

        pass

    def mutate(self, prob: float):
        # with probability 'prob'
        # apply a random mutation

        for i in range(self.num_zones):
            dice = random.random()
            if dice < prob:
                # create a new valid zone center
                new_p = self._generate_new_valid_point()
                # replace
                self.genotype[i] = new_p

        pass

    def plot(self):

        # TODO

        pass

    def savefig(self, path: str):

        # TODO

        pass
