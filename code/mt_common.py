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
# some constants
#
EPS_DIV0 = 1e-6  # A very small number to avoid divide by zero errors at some geo-calcs

DATA_CODE_FIELD = 'CODE'
DATA_VALUE_FIELD = 'VALUE'

DICT_DISTRICT_NEIGHBOURS_CODE_LIST = 'NEIGHBOURS_CODE_LIST'
DICT_DISTRICT_NEIGHBOURS_COST_LIST = 'NEIGHBOURS_COST_LIST'

#
# messages
#

MG_DEBUG_INTERNAL_ERROR = \
    "Please debug this internal error"
MG_INFO_COMPUTING_VALID_AREA = \
    "Computing the valid zone centroid map"
MG_INFO_PARTITION_DESIGNER_INIT = \
    "Created a new PartitionDesigner object to accommodate {} districts " \
    "into {} zones. Using an initial population of {} partition instances"
MG_INFO_PARTITION_INIT = \
    "Created a new Partition object to accommodate {} districts " \
    "into {} zones"
MG_ERROR_DATA = \
    "'data' must be a DataFrame with 'CODE' and 'VALUE' fields"
MG_ERROR_CONN = \
    "'conn' must be a dictionary with a key entry for each 'data' 'CODE' value"
MG_ERROR_VALID_AREA_MAP = \
    "'valid_area' must be a geometric object representing the valid zone centroids area"
MG_ERROR_NUM_ZONES = \
    "'num_zones' must be an integer between 1 and data cardinality"
MG_ERROR_POP_CARD = \
    "'pop_card' must be an even positive integer"
MG_ERROR_ENTRY_NOT_FOUND = \
    "'{}' key not found in '{}' dictionary"
