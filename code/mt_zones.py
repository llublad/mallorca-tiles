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


class Partition:
    def __init__(self, data: pd.DataFrame, conn: dict, num_zones: int, pop_card: int, logger: log.Logger):
        pass

    def fit(self):
        pass

    def save_map(self, output_path):
        pass
