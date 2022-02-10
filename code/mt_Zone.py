# Pràctica de creació de zones electorals per algorismes genètics
#
# IC - MUSI 21 22 - UIB
#
# Alumne: Lluís Bernat Ladaria

"""
Zone class - library
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

import mt_common as our


class Zone:
    """
    Object that encapsulates a zone

    A zone contains a list of (probably connected) districts
    and all the methods to deal with
    """

    def __init__(self, center: Point):
        # create a zone instance
        #

        # check center contains a Point
        if type(center) is not Point:
            raise TypeError(our.MG_DEBUG_INTERNAL_ERROR)

        # save parameters
        self._center = center

        # zone is composed by district entries
        # we save them into this dictionary
        self._districts = dict()

        # and this is the counter
        self._n_districts = 0

        # also, must save the total zone value
        # (the sum of each district value)
        self._zone_value = 0

        # an internal connectivity cost can be computed
        # based on each district NEIGHBOURS_COST_LIST dict entry
        self._conn_cost = None

        pass

    def get_center(self):
        # return the zone assigned center point
        #

        center = self._center

        return center

    def get_value(self):
        # return the total vallue of the zone
        #

        zone_value = self._zone_value

        return zone_value

    def add_district(self, dis_code: str, dis_value: int,
                     zone_dis: float, dis_geodata: dict):
        # add district entry to zone string
        # and its associated value

        entry = {
            1: dis_value,
            2: zone_dis,
            3: dis_geodata
        }

        self._districts[dis_code] = entry
        self._zone_value += dis_value
        self._n_districts += 1

        pass

    def _print_zone_dump(self):
        # for debugging purposes,
        # print a zone dump

        print("Center:           ", self._center)
        print("Distritcs list:   ", self._districts)
        print("Total zone value: ", self._zone_value)
        print("Connectivity cost:", self._conn_cost)

        pass
