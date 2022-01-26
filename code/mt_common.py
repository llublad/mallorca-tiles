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
DICT_DISTRICT_NEIGHBOURS_ID_LIST = 'NEIGHBOURS_ID_LIST'
DICT_DISTRICT_NEIGHBOURS_SLICE_LIST = 'NEIGHBOURS_PROB_LIST'


#
# messages
#

LOG_ERROR_DATA_SYNTAX = "Some input data has incorrect syntax"
LOG_ERROR_NUM_ZONES = "'num_zones' must be an integer between 1 and data cardinality"
LOG_ERROR_POP_CARD = "'pop_card' must be an even integer"
