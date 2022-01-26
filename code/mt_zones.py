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


def check_data(data):

    is_correct = True

    return is_correct


def check_conn(conn):

    is_correct = True

    return is_correct


def check_num_zones(num_zones: int, data: pd.DataFrame) -> bool:
    # check if num_zones is between 1 and data cardinality
    if not(type(num_zones) is int and type(data) is pd.DataFrame):
        raise TypeError

    is_correct = (num_zones >= 1) and (num_zones <= len(data))

    if not is_correct:
        log.error(our.LOG_ERROR_NUM_ZONES)
        raise ValueError(our.LOG_ERROR_NUM_ZONES)

    return is_correct


def check_pop_card(pop_card: int) -> bool:
    # check if pop_card is even
    if not type(pop_card) is int:
        raise TypeError

    is_correct = (pop_card % 2 == 0)

    if not is_correct:
        log.error(our.LOG_ERROR_POP_CARD)
        raise ValueError

    return is_correct


class Partition:
    def __init__(self, data: pd.DataFrame, conn: dict, num_zones: int, pop_card: int, logger: log.Logger):

        if check_data(data) and check_conn(conn) and \
                check_num_zones(num_zones, data) and check_pop_card(pop_card):
            self.data = data
            self.conn = conn
            self.num_zones = num_zones
            self.pop_card = pop_card
        else:
            logger.error(our.LOG_ERROR_DATA_SYNTAX)

        return

    def fit(self):
        pass

    def save_map(self, output_path):
        pass
