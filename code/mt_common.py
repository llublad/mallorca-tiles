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

# solutions file name
FILE_NAME_SEP = '-'
FILE_MAP_PREFIX = 'MT'
FILE_MAP_SUFFIX = 'MAP'
FILE_MAP_EXT = '.png'

# solutions plot
PLOT_FIGSIZE = (15, 10)  # Plot figure size

# Genetic Algorithm hiperparameters
GA_MAX_ITERATIONS = 1000  # hard iterations limit
GA_NOIMPROV_ITERATIONS = 200  # iterations to stop after no improvement
GA_LOG_PC_SCORE_IMPROV = 0.05  # print log about score when it improves at least this
GA_CROSSOVER_PROB = 0.95
GA_MUTATION_PROB = 0.01
GA_TOURNAMENT_ADVERSARIES = 4
GA_NEXT_GENERATION_HOLD = 0.20  # mantain at least this percentage of fathers between generations

# math constants
EPS_DIV0 = 1e-6  # A very small number to avoid divide by zero errors at some geo-calcs

# what are the interesting fields in loaded from file panda DataFrame
PD_DATA_CODE_FIELD = 'CODE'
PD_DATA_VALUE_FIELD = 'VALUE'

# the name of the GeoDataFrame field that will use to locate
# the geometry corresponding to field PD_DATA_CODE_FIELD value
GPD_DATA_CODE_FIELD = 'CODE'
GPD_GEOMETRY_FIELD = 'geometry'

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
    "Created a new PartitionDesigner object to accommodate a total of {} people at {} districts " \
    "into {} zones. Using an initial population of {} partition instances"
MG_INFO_PARTITION_INIT = \
    "Created a new Partition object to accommodate {} districts " \
    "into {} zones. The target value are {:.0f} people / zone"
MG_INFO_PARTITIONS_RESTORED = \
    "All partition objects have been restored (stats zeroed and zone list deleted)"
MG_INFO_INITIAL_SCORE = \
    "The initial best score is {:,.0f}"
MG_INFO_LAST_SCORE = \
    "After {} iterations best score is {:,.0f}"
MG_ERROR_DATA = \
    f"'data' must be a DataFrame with '{PD_DATA_CODE_FIELD}' and '{PD_DATA_VALUE_FIELD}' fields"
MG_ERROR_CONN = \
    f"'geodata' must be a dictionary with a key entry for each 'data' '{PD_DATA_CODE_FIELD}' value"
MG_ERROR_DIS = \
    f"'gpd_dis' must be a GeoDataFrame with a field called {GPD_DATA_CODE_FIELD} " \
    f"and containing an entry for each 'data' '{PD_DATA_CODE_FIELD}' value"
MG_ERROR_VALID_AREA_MAP = \
    "'valid_area' must be a geometric object representing the valid zone centers area"
MG_ERROR_NUM_ZONES = \
    "'num_zones' must be an integer between 2 and data cardinality"
MG_ERROR_POP_CARD = \
    "'pop_card' must be an even positive integer"
MG_ERROR_ENTRY_NOT_FOUND = \
    "'{}' key not found in '{}' dictionary"
