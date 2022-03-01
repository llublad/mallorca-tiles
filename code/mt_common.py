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

# Genetic Algorithm hyper-parameters
GA_MAX_ITERATIONS = 99999  # hard iterations limit
GA_NONIMPROV_ITERATIONS = 3000  # iterations to stop after no improvement
GA_CROSSOVER_PROB = 0.95  # crossover probability for each couple
GA_MUTATION_PROB = 0.01  # probability for gen mutation
GA_TOURNAMENT_ADVERSARIES = 4  # number of adversaries at tournaments for crossover operator
GA_PARENTS_TO_HOLD = 0.20  # maintain at least this percentage of fathers between generations
GA_MARGIN_ZONE_VALUE = 0.25  # tolerable margin for the zone population value
GA_INTO_MARGIN_REDUCTION = 0.50  # score reduction coefficient when zone population value into boundaries
GA_UNCONNECTED_ZONE_WEIGHT = 10.  # weight for of unconnected zones count score contribution
# because it's not possible to compute a connectivity cost for 1-district zones,
# we assign to them a feasible value:
GA_1_DISTRICT_ZONE_MEAN_COST = 0.80  # mean connectivity cost assigned to 1-district zones

# Log progress info at ...
GA_INFO_ITERATIONS = 100  # log info at least each n iterations if there are any score variation
GA_LOG_PC_SCORE_IMPROV = 0.02  # also log score when it improves at least this

# solutions file name
FILE_NAME_SEP = '-'
FILE_PREFIX = 'MT'
FILE_DATESTAMP_FMT = '%Y%m%d_%H%M%S'
FILE_NZ_LIT = 'nz'  # number of zones to obtain
FILE_PC_LIT = 'pc'  # GA used population cardinality
FILE_IT_LIT = 'it'  # actual iteration number
FILE_IS_SOLUTION = 'SOL'
FILE_MAP_SUFFIX = 'MAP'
FILE_MAP_EXT = '.png'
FILE_TXT_SUFFIX = 'ALPHA'
FILE_TXT_EXT = '.json'

# solutions plot
PLOT_FIGSIZE = (20, 15)  # Plot figure size
PLOT_SCORE_MG = "Last best score was: {:.8f}"
PLOT_WINDOW_ZOOM = [0.1, 0.25, 0.5, 0.65]  # [wmin_x, wmin_y, wmax_x, wmax_y]

# what are the interesting fields in loaded from file panda DataFrame
PD_DATA_CODE_FIELD = 'CODE'
PD_DATA_VALUE_FIELD = 'VALUE'

# the name of the GeoDataFrame field that will use to locate
# the geometry corresponding to field PD_DATA_CODE_FIELD value
GPD_DATA_CODE_FIELD = 'CODE'
GPD_GEOMETRY_FIELD = 'geometry'

# what is contained at the columns in the list of data
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
    "The initial best score is {:.8f}"
MG_INFO_LAST_SCORE = \
    "After {} iterations best score is {:.8f}"
MG_INFO_SOLUTION_FOUND = \
    "After {} iterations solution score is {:.8f}"
MG_INFO_SAVING_MAP = \
    "Saving status map at iteration {} to file {}"
MG_INFO_SAVING_TXT = \
    "Saving status json at iteration {} to file {}"
MG_INFO_ZONE_LOWER = \
    "Zone {} with value {} is below the lower margin boundary {:0n}"
MG_INFO_ZONE_UPPER = \
    "Zone {} with value {} is above the upper margin boundary {:0n}"
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
