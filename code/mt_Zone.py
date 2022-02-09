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

        # save parameters
        self.center = center

        # zone is composed by district entries
        # we save them into this list
        self.districts = list()

        # also, must save the value of each district to be optimized
        self.values = list()
        # and the total zone value
        self.zone_value = 0

        # an internal connectivity cost can be computed
        # based on each district NEIGHBOURS_COST_LIST dict entry
        self.conn_cost = None

        pass

    def get_center(self):
        # return the zone assigned center point
        #

        center = self.center

        return center

    def get_value(self):
        # return the total vallue of the zone
        #

        zone_value = self.zone_value

        return zone_value

    def add_district(self, dis_entry: list, dat_value: int):
        # add district entry to zone string
        # and its associated value

        self.districts.append(dis_entry)
        self.values.append(dat_value)
        self.zone_value += dat_value

        pass

    def _print_zone_dump(self):
        # for debugging purposes,
        # print a zone dump

        print("Center:           ", self.center)
        print("Distritcs list:   ", self.districts)
        print("Values list:      ", self.values)
        print("Total zone value: ", self.zone_value)
        print("Connectivity cost:", self.conn_cost)

        pass
