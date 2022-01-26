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
import logging as log

#
# ours libraries
#

import mt_common as our


class Zone:
    def __init__(self):
        pass


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


class PartitionDesigner:
    def __init__(self, data: pd.DataFrame, conn: dict,
                 num_zones: int, pop_card: int, logger: log.Logger):
        """
        Object that encapsulates all methods and information
        to compute a solution for the Zone Design problem

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
        all_correct = \
            check_data(data) and \
            check_conn(conn, data) and \
            check_num_zones(num_zones, data) and \
            check_pop_card(pop_card)

        if all_correct:
            self.data = data
            self.conn = conn
            self.num_zones = num_zones
            self.pop_card = pop_card
            logger.info(our.MG_INFO_PARTITION_INIT.format(num_zones, pop_card))
        else:  # will never be executed, cause raise clauses in check_whatever...
            raise  # ...but in case will run, we force a generic Exception

        return

    def fit(self):
        pass

    def save_map(self, output_path):
        pass
