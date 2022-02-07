# Pràctica de creació de zones electorals per algorismes genètics
#
# IC - MUSI 21 22 - UIB
#
# Alumne: Lluís Bernat Ladaria

"""
Zone design - library
=====================

Provides the objects and functions to compute a solution for
districts assignation to almost uniform population distribution zones
using genetic algorithms
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
from mt_Partition import Partition


#
# functions
#

def check_data(data: pd.DataFrame) -> bool:
    # sanity checks for DataFrame
    #
    if not type(data) is pd.DataFrame:
        raise TypeError(our.MG_ERROR_DATA)

    fields = list(data)

    # the DataFrame must have at least two fields
    #

    # a unique code and the value to be taken as population
    is_correct = our.DATA_CODE_FIELD in fields and our.DATA_VALUE_FIELD in fields

    if not is_correct:
        raise ValueError(our.MG_ERROR_DATA)

    return is_correct


def check_conn(conn: dict, data: pd.DataFrame) -> bool:
    # sanity checks for connectivity dictionary
    #
    if not type(conn) is dict:
        raise TypeError(our.MG_ERROR_CONN)

    is_correct = True

    for entity_code in data[our.DATA_CODE_FIELD]:
        # all loaded entities from csv must have a geospatial entity
        if entity_code not in conn:
            raise ValueError(our.MG_ERROR_ENTRY_NOT_FOUND.format(entity_code, 'conn'))
        else:
            entry = conn.get(entity_code)
            # all the needed geospatial entities must have
            # two lists

            # one with all his neighbours
            if our.DICT_DISTRICT_NEIGHBOURS_CODE_LIST not in entry:
                raise ValueError(
                    our.MG_ERROR_ENTRY_NOT_FOUND.format(our.DICT_DISTRICT_NEIGHBOURS_CODE_LIST,
                                                        entity_code))
            # and another with the cost to 'cross to' the neighbour
            if our.DICT_DISTRICT_NEIGHBOURS_COST_LIST not in entry:
                raise ValueError(
                    our.MG_ERROR_ENTRY_NOT_FOUND.format(our.DICT_DISTRICT_NEIGHBOURS_COST_LIST,
                                                        entity_code))

    return is_correct


def check_valid_area_map(valid: BaseGeometry) -> bool:
    # sanity checks for valid area map
    #
    if not type(valid) in [BaseGeometry, Polygon, MultiPolygon]:
        raise TypeError(our.MG_ERROR_VALID_AREA_MAP)

    # it must be a valid (closed) polygon or multipolygon
    is_correct = valid.is_valid

    if not is_correct:
        raise ValueError(our.MG_ERROR_VALID_AREA_MAP)

    return is_correct


def check_num_zones(num_zones: int, data: pd.DataFrame) -> bool:
    # check if num_zones is between 1 and data cardinality
    #
    if not (type(num_zones) is int and type(data) is pd.DataFrame):
        raise TypeError(our.MG_ERROR_NUM_ZONES)

    # not more zones than the available number of districts is possible
    is_correct = (num_zones >= 1) and (num_zones <= len(data))

    if not is_correct:
        raise ValueError(our.MG_ERROR_NUM_ZONES)

    return is_correct


def check_pop_card(pop_card: int) -> bool:
    # check if pop_card is even
    if not type(pop_card) is int:
        raise TypeError(our.MG_ERROR_POP_CARD)

    # population cardinality must be even and greater than 0
    is_correct = (pop_card % 2 == 0) and (pop_card > 0)

    if not is_correct:
        raise ValueError(our.MG_ERROR_POP_CARD)

    return is_correct


#
# Classes
#


class PartitionDesigner:
    """
    Object that encapsulates all methods and information
    to compute a solution for the Zone Design problem using
    a Genetic Algorithm described at

    Bação, F., Lobo, V. & Painho, M.
    Applying genetic algorithms to zone design.
    Soft Comput 9, 341–348 (2005).
    https://doi.org/10.1007/s00500-004-0413-4

    :param data: a pandas DataFrame with all entities
        (a register for each one) that will conform
        the minimum units (that we call distritcs)
        of the partition.
        At least must contain two columns:
        - 'CODE' field: unique code to identify the row
        - 'VALUE' field: the population value for the entity
    :param conn: a dictionary with an entry for each
        minimum entity (district) of the partition.
        Every entry must contain:
        - key: the 'CODE' value for the entity.
          Must be one of the 'CODE' values form 'data' DataFrame
        - dictionary (nested) with at least two lists:
            - NEIGHBOURS_CODE_LIST: the neighbours CODE values list
            - NEIGHBOURS_COST_LIST: the neighbour cost list (floats in [0, 1] range)
            The two lists must be sorted by cost (ascending)
    :param num_zones: an integer with the
        number of desired zones to generate.
        Each zone will contain at least one distritc
    :param pop_card: an integer with the (initial) population cardinality
    :param logger: a Logger object

    Example for conn dict:
    ======================
    conn = {
        ... ,
        '07005':
            {
            'NEIGHBOURS_CODE_LIST': ['07011', '07021'],
            'NEIGHBOURS_COST_LIST': [0.134141, 0.865859]
            },
        '07006':
            {
            'NEIGHBOURS_CODE_LIST': ['07014', '07062', '07051', '07041', '07055'],
            'NEIGHBOURS_COST_LIST': [0.695894, 0.737653, 0.74953, 0.901107, 0.915817]
            },
        ...
        }
        Note: according to example, the 'neighbourhood cost'
        of the zone '07005'-'07011' will be 0.134141
    """

    def __init__(self, data: pd.DataFrame, conn: dict, valid_area: BaseGeometry,
                 num_zones: int, pop_card: int, logger: log.Logger):
        # create object instance, if params syntax are correct
        all_correct = \
            check_data(data) and \
            check_conn(conn, data) and \
            check_valid_area_map(valid_area) and \
            check_num_zones(num_zones, data) and \
            check_pop_card(pop_card)

        if all_correct:
            # save all the params
            self.logger = logger
            self.data = data
            self.conn = conn
            self.valid_area = valid_area
            self.num_zones = num_zones
            self.pop_card = pop_card

            num_districts = len(data)
            self.num_districts = num_districts

            self.logger.info(
                our.MG_INFO_PARTITION_DESIGNER_INIT.format(
                    self.num_districts,
                    self.num_zones,
                    self.pop_card))

            self.partition = list()
            self._generate_initial_population()
        else:  # will never be executed, cause raise clauses in check_whatever functions...
            # ...but in case would run, we force a generic Exception to be noticed about
            raise Exception(our.MG_DEBUG_INTERNAL_ERROR)

        pass

    def _generate_initial_population(self):
        # populate (empty) list of genotypes
        #
        if len(self.partition) > 0:
            raise OverflowError(our.MG_DEBUG_INTERNAL_ERROR)

        # will generate pop_card Partition objects
        for i in range(self.pop_card):
            self.partition.append(
                Partition(data=self.data, conn=self.conn,
                          valid_area=self.valid_area, num_zones=self.num_zones,
                          logger=self.logger)
            )

        pass

    def fit(self):
        # apply the described GA
        # and find the best solution
        #
        for part in self.partition:
            part.fit()

        pass

    def save_map(self, output_path):
        pass
