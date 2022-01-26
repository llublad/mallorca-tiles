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
DATA_CODE_FIELD = 'CODE'
DATA_VALUE_FIELD = 'VALUE'

DICT_DISTRICT_NEIGHBOURS_CODE_LIST = 'NEIGHBOURS_CODE_LIST'
DICT_DISTRICT_NEIGHBOURS_COST_LIST = 'NEIGHBOURS_COST_LIST'


#
# messages
#

MG_INFO_PARTITION_INIT = \
    "Created a new PartitionDesigner object with zones={} and population={}"
MG_ERROR_DATA = \
    "'data' must be a DataFrame with 'CODE' and 'VALUE' fields"
MG_ERROR_CONN = \
    "'conn' must be a dictionary with a key entry for each 'data' 'CODE' value"
MG_ERROR_NUM_ZONES = \
    "'num_zones' must be an integer between 1 and data cardinality"
MG_ERROR_POP_CARD = \
    "'pop_card' must be an even positive integer"
MG_ERROR_ENTRY_NOT_FOUND = \
    "'{}' key not found in '{}' dictionary"