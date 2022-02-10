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

GA_MAX_ITERATIONS = 10
GA_NOIMPROV_ITERATIONS = 2
GA_CROSSOVER_PROB = 0.95
GA_MUTATION_PROB = 0.001

# what are the interesting fields in loaded from file panda DataFrame
PD_DATA_CODE_FIELD = 'CODE'
PD_DATA_VALUE_FIELD = 'VALUE'

# what are containig the columns in the list of data
LIST_DATA_CODE_COL = 0
LIST_DATA_VALUE_COL = 1

DICT_DISTRICT_NEIGHBOURS_CODE_LIST = 'NEIGHBOURS_CODE_LIST'
DICT_DISTRICT_NEIGHBOURS_COST_LIST = 'NEIGHBOURS_COST_LIST'
DICT_DISTRICT_CENTROID_POINT = 'CENTROID'

#
# messages
#

MG_DEBUG_INTERNAL_ERROR = \
    "Please debug this internal error"

MG_INFO_COMPUTING_VALID_AREA = \
    "Computing the feasible zone centers region map"
MG_INFO_PARTITION_DESIGNER_INIT = \
    "Created a new PartitionDesigner object to accommodate {} districts " \
    "into {} zones. Using an initial population of {} partition instances"
MG_INFO_PARTITION_INIT = \
    "Created a new Partition object to accommodate {} districts " \
    "into {} zones"
MG_INFO_PARTITIONS_RESTORED = \
    "All partition objects have been restored (stats zeroed and zone list deleted)"
MG_ERROR_DATA = \
    f"'data' must be a DataFrame with '{PD_DATA_CODE_FIELD}' and '{PD_DATA_VALUE_FIELD}' fields"
MG_ERROR_CONN = \
    f"'geodata' must be a dictionary with a key entry for each 'data' '{PD_DATA_CODE_FIELD}' value"
MG_ERROR_VALID_AREA_MAP = \
    "'valid_area' must be a geometric object representing the valid zone centers area"
MG_ERROR_NUM_ZONES = \
    "'num_zones' must be an integer between 1 and data cardinality"
MG_ERROR_POP_CARD = \
    "'pop_card' must be an even positive integer"
MG_ERROR_ENTRY_NOT_FOUND = \
    "'{}' key not found in '{}' dictionary"
