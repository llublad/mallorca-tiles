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


def _intersection(list1: list, list2: list) -> list:
    # return a list with the common list1 and list2 elements
    #

    temp = set(list2)
    new_list = [value for value in list1 if value in temp]

    return new_list


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

    def get_cost(self):
        # return the connectivity cost of the whole zone
        #

        if self._conn_cost is not None:
            conn_cost = self._conn_cost
        else:
            raise ValueError(our.MG_DEBUG_INTERNAL_ERROR)

        return conn_cost

    def add_district(self, dis_code: str, dis_value: int,
                     zone_distance: float, dis_geodata: dict):
        # add district entry to zone string
        # and its associated value

        entry = {
            1: dis_value,
            2: zone_distance,
            3: dis_geodata
        }

        self._districts[dis_code] = entry
        self._zone_value += dis_value
        self._n_districts += 1

        pass

    def calc_cost(self):
        # calculate the connectivity cost value
        # as the average of the connectivity cost
        # of each pair of districts that composed the zone

        # construct our districts list of codes
        district_code_list = list(self._districts.keys())

        total_cost = 0.

        for d1_code in self._districts.keys():
            d1_connections = 0
            d1_cost = 0.

            d1_geodata = self._districts.get(d1_code)[3]
            d1_neighbours_list = d1_geodata[our.DICT_DISTRICT_NEIGHBOURS_CODE_LIST]
            d1_cost_list = d1_geodata[our.DICT_DISTRICT_NEIGHBOURS_COST_LIST]

            common_list = _intersection(district_code_list, d1_neighbours_list)

            for code in common_list:
                i = d1_neighbours_list.index(code)
                d1_cost += d1_cost_list[i]
                d1_connections += 1

            total_cost += d1_cost

        # TODO
        self._conn_cost = total_cost / 1

        pass

    def _print_zone_dump(self):
        # for debugging purposes,
        # print a zone dump

        print("Center:           ", self._center)
        print("Distritcs list:   ", self._districts)
        print("Total zone value: ", self._zone_value)
        print("Connectivity cost:", self._conn_cost)

        pass
