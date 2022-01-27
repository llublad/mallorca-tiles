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


#
# functions
#

def check_data(data: pd.DataFrame) -> bool:
    # sanity checks for DataFrame
    if not type(data) is pd.DataFrame:
        raise TypeError(our.MG_ERROR_DATA)

    fields = list(data)

    is_correct = our.DATA_CODE_FIELD in fields and our.DATA_VALUE_FIELD in fields

    if not is_correct:
        raise ValueError(our.MG_ERROR_DATA)

    return is_correct


def check_conn(conn: dict, data: pd.DataFrame) -> bool:
    # sanity checks for connectivity dictionary
    if not type(conn) is dict:
        raise TypeError(our.MG_ERROR_CONN)

    is_correct = True

    for entity_code in data[our.DATA_CODE_FIELD]:
        if entity_code not in conn:
            raise ValueError(our.MG_ERROR_ENTRY_NOT_FOUND.format(entity_code, 'conn'))
        else:
            entry = conn.get(entity_code)
            if our.DICT_DISTRICT_NEIGHBOURS_CODE_LIST not in entry:
                raise ValueError(
                    our.MG_ERROR_ENTRY_NOT_FOUND.format(our.DICT_DISTRICT_NEIGHBOURS_CODE_LIST,
                                                        entity_code))
            if our.DICT_DISTRICT_NEIGHBOURS_COST_LIST not in entry:
                raise ValueError(
                    our.MG_ERROR_ENTRY_NOT_FOUND.format(our.DICT_DISTRICT_NEIGHBOURS_COST_LIST,
                                                        entity_code))

    return is_correct


def check_valid_area_map(valid: BaseGeometry) -> bool:
    # sanity checks for valid area map
    if not type(valid) in [BaseGeometry, Polygon, MultiPolygon]:
        raise TypeError(our.MG_ERROR_VALID_AREA_MAP)

    is_correct = valid.is_valid

    if not is_correct:
        raise ValueError(our.MG_ERROR_VALID_AREA_MAP)

    return is_correct


def check_num_zones(num_zones: int, data: pd.DataFrame) -> bool:
    # check if num_zones is between 1 and data cardinality
    if not (type(num_zones) is int and type(data) is pd.DataFrame):
        raise TypeError(our.MG_ERROR_NUM_ZONES)

    is_correct = (num_zones >= 1) and (num_zones <= len(data))

    if not is_correct:
        raise ValueError(our.MG_ERROR_NUM_ZONES)

    return is_correct


def check_pop_card(pop_card: int) -> bool:
    # check if pop_card is even
    if not type(pop_card) is int:
        raise TypeError(our.MG_ERROR_POP_CARD)

    is_correct = (pop_card % 2 == 0) and (pop_card > 0)

    if not is_correct:
        raise ValueError(our.MG_ERROR_POP_CARD)

    return is_correct


#
# Classes
#


class Zone:
    def __init__(self):
        pass


class Partition:
    """
    Object that encapsulates the genotype of a zone partition
    and all the necessary methods to work with
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

        return

    def _generate_genotype(self):
        # generate as many zone centroids as num_zones value
        if len(self.genotype) > 0:
            raise OverflowError  # TODO

        i = 0
        while i < self.num_zones:
            x = random.uniform(self.x_min, self.x_max)
            y = random.uniform(self.y_min, self.y_max)
            p = Point(x, y)
            if self.valid_area.contains(p):
                i += 1
                self.genotype.append(p)

        return


class PartitionDesigner:
    """
    Object that encapsulates all methods and information
    to compute a solution for the Zone Design problem using
    a Genetic Algorithm

    :param data: a pandas DataFrame with all entities
        that will conform the partition (a register for each one).
        At least must contain two columns:
        - 'CODE' field: unique code to identify the row
        - 'VALUE' field: the population value for the entity
    :param conn: a dictionary with an entry for every entity of the partition.
        Every entry must contain:
        - key: the 'CODE' value for the entity.
          Must be one of the 'CODE' values form 'data' DataFrame
        - dictionary (nested) with at least two lists:
            - NEIGHBOURS_CODE_LIST: the neighbours CODE values list
            - NEIGHBOURS_COST_LIST: the neighbour cost list (floats in [0, 1] range)
            The two lists must be sorted by cost (ascending)
    :param num_zones: an integer with the number of desired zones
    :param pop_card: an integer with the population cardinality
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

            self.partition_population = list()
            self._generate_initial_population()
        else:  # will never be executed, cause raise clauses in check_whatever functions...
            raise  # ...but in case will run, we force a generic Exception

        return

    def _generate_initial_population(self):
        # populate (empty) list of genotypes
        if len(self.partition_population) > 0:
            raise OverflowError  # TODO

        for i in range(self.pop_card):
            self.partition_population.append(
                Partition(data=self.data, conn=self.conn, valid_area=self.valid_area, num_zones=self.num_zones,
                          logger=self.logger)
            )

        return

    def fit(self):
        pass

    def save_map(self, output_path):
        pass
