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


from shapely.geometry.base import BaseGeometry
from shapely.geometry.point import Point
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon
import logging as log

#
# ours libraries
#


import mt_common as our
from mt_Partition import Partition


#
# functions
#


def get_func_select_best_value():
    # return the proper function to select the best score
    #

    # for our case is the min() function
    return min


def get_best_value_index(vector: list):
    # return the position (zero indexed) of the best 'vector' value
    #

    # get the min/max function accordingly to our fitness function
    func_select_best_value = get_func_select_best_value()

    # search best value and its position in vector (a list)
    position = vector.index(func_select_best_value(vector))

    return position


def check_data(data: list) -> bool:
    # sanity checks for data list
    #
    if not type(data) is list:
        raise TypeError(our.MG_ERROR_DATA)

    # the list must have at least one row
    # and two fields at each row:
    # - a unique code and
    # - the value to be taken as population
    if len(data) > 0:
        is_correct = True
        i = 0
        while i < len(data) and is_correct:
            is_correct = len(data[i]) >= 2
            i += 1
    else:
        is_correct = False

    if not is_correct:
        raise ValueError(our.MG_ERROR_DATA)

    return is_correct


def check_geodata(geodata: dict, data: list) -> bool:
    # sanity checks for connectivity dictionary
    #
    if not type(geodata) is dict:
        raise TypeError(our.MG_ERROR_CONN)

    is_correct = True

    for entity in data:
        # all loaded entities from csv must have a geospatial entity
        entity_code = entity[our.LIST_DATA_CODE_COL]
        if entity_code not in geodata:
            raise ValueError(our.MG_ERROR_ENTRY_NOT_FOUND.format(entity_code, 'geodata'))
        else:
            entry = geodata.get(entity_code)
            # all the needed geospatial entities must have
            # two lists and a centroid point

            # check centroid point presence
            if our.DICT_DISTRICT_CENTROID_POINT not in entry:
                raise ValueError(
                    our.MG_ERROR_ENTRY_NOT_FOUND.format(our.DICT_DISTRICT_CENTROID_POINT,
                                                        entity_code))

            # one list with all its neighbours
            if our.DICT_DISTRICT_NEIGHBOURS_CODE_LIST not in entry:
                raise ValueError(
                    our.MG_ERROR_ENTRY_NOT_FOUND.format(our.DICT_DISTRICT_NEIGHBOURS_CODE_LIST,
                                                        entity_code))
            # and another with the connectivity neighbour cost
            if our.DICT_DISTRICT_NEIGHBOURS_COST_LIST not in entry:
                raise ValueError(
                    our.MG_ERROR_ENTRY_NOT_FOUND.format(our.DICT_DISTRICT_NEIGHBOURS_COST_LIST,
                                                        entity_code))

    return is_correct


def check_valid_area_map(valid: BaseGeometry) -> bool:
    # sanity checks for valid area map
    #
    if not type(valid) in [BaseGeometry, Polygon, MultiPolygon]:
        raise TypeError(our.MG_ERROR_VALID_AREA_MAP)

    # it must be a valid (closed) polygon or multipolygon
    is_correct = valid.is_valid

    if not is_correct:
        raise ValueError(our.MG_ERROR_VALID_AREA_MAP)

    return is_correct


def check_num_zones(num_zones: int, data: list) -> bool:
    # check if num_zones is between 1 and data cardinality
    #
    if not (type(num_zones) is int and type(data) is list):
        raise TypeError(our.MG_ERROR_NUM_ZONES)

    # not more zones than the available number of districts is possible
    is_correct = (num_zones >= 1) and (num_zones <= len(data))

    if not is_correct:
        raise ValueError(our.MG_ERROR_NUM_ZONES)

    return is_correct


def check_pop_card(pop_card: int) -> bool:
    # check if pop_card is even
    if not type(pop_card) is int:
        raise TypeError(our.MG_ERROR_POP_CARD)

    # population cardinality must be even and greater than 0
    is_correct = (pop_card % 2 == 0) and (pop_card > 0)

    if not is_correct:
        raise ValueError(our.MG_ERROR_POP_CARD)

    return is_correct


#
# Class
#


class PartitionDesigner:
    """
    Object that encapsulates all methods and information
    to compute a solution for the Zone Design problem using
    a Genetic Algorithm described at

    Bação, F., Lobo, V. & Painho, M.
    Applying genetic algorithms to zone design.
    Soft Comput 9, 341–348 (2005).
    https://doi.org/10.1007/s00500-004-0413-4

    :param data: a list with all entities (that we call districts)
        (a row for each one) that will conform
        the smaller units of the partition.
        At least must contain three entries by each row:
        - a unique code to identify the row at pos LIST_DATA_CODE_COL
        - the population value for the entity at pos LIST_DATA_VALUE_COL
        - the centroid point of the entity at pos LIST_DATA_CENTROID_COL
        (see mt_common.py)
    :param geodata: a dictionary with an entry for each
        minimum entity (district) of the partition.
        Every entry must contain:
        - key: the 'CODE' value for the entity.
          Must be one of the 'CODE' values form 'data' DataFrame
        - dictionary (nested) with at least centroid point and two lists:
            - CENTROID_POINT: the centroid of the geometry (Point type)
            - NEIGHBOURS_CODE_LIST: the neighbours CODE values list
            - NEIGHBOURS_COST_LIST: the neighbour cost list (floats in [0, 1] range)
            The two lists must be sorted by cost (ascending)
    :param num_zones: an integer with the
        number of desired zones to generate.
        Each zone will contain at least one distritc
    :param pop_card: an integer with the (initial) population cardinality
    :param logger: a Logger object

    Example for geodata dict:
    ----------------------
    geodata = {
        ... ,
        '07005':
            {
            'CENTROID': (267760.62484048156, 4805381.809370395),
            'NEIGHBOURS_CODE_LIST': ['07011', '07021'],
            'NEIGHBOURS_COST_LIST': [0.134141, 0.865859]
            },
        '07006':
            {
            'CENTROID': (370548.407976895, 4824561.963611906),
            'NEIGHBOURS_CODE_LIST': ['07014', '07062', '07051', '07041', '07055'],
            'NEIGHBOURS_COST_LIST': [0.695894, 0.737653, 0.74953, 0.901107, 0.915817]
            },
        ...
        }
        Note: according to example, the 'neighbourhood cost'
        of the zone '07005'-'07011' is 0.134141 (a low value)
    """

    def __init__(self, data: list, geodata: dict, valid_area: BaseGeometry,
                 num_zones: int, pop_card: int, logger: log.Logger):
        # create object instance, if params syntax are correct
        all_correct = \
            check_data(data) and \
            check_geodata(geodata, data) and \
            check_valid_area_map(valid_area) and \
            check_num_zones(num_zones, data) and \
            check_pop_card(pop_card)

        if all_correct:

            # save all the params
            self.logger = logger
            self.data = data
            self.geodata = geodata
            self.valid_area = valid_area
            self.num_zones = num_zones
            self.pop_card = pop_card

            num_districts = len(data)
            self.num_districts = num_districts

            self._calc_total_value()

            self.logger.info(
                our.MG_INFO_PARTITION_DESIGNER_INIT.format(
                    self.total_value,
                    self.num_districts,
                    self.num_zones,
                    self.pop_card))

            # calculate the mean value per zone
            # i.e. the desired number of people per zone
            self.mean_value = self.total_value / self.num_zones

            # the genotypes list
            self.partition = list()
            # wich one is the best?
            self.best_partition = None
            # what is the last best partition score?
            self.last_best_score = None
            # also save the score history
            self.best_score_history = list()

        else:
            # this will never be executed,
            # because raise clauses in check_whatever functions...
            # ...but in case would run,
            # we force a generic Exception to be noticed about and debug it
            raise Exception(our.MG_DEBUG_INTERNAL_ERROR)

        pass

    def _calc_total_value(self):
        # calculate the sum of the districts value
        # this value is expected to be total population
        # of the study region

        total_value = 0

        for district in self.data:
            total_value += district[our.LIST_DATA_VALUE_COL]

        self.total_value = total_value

        pass

    def fit(self):
        # apply the described GA
        # and find the best solution
        #

        # make an initial population
        # creating Partition instances
        self._generate_initial_population()

        # iteration counters
        #
        # global counter
        it = 0
        # no improvement counter
        it_ni = 0
        # log frequency about progress info
        it_module = max(1, our.GA_MAX_ITERATIONS // 10)

        # for each district,
        # find the closest zone center
        # and assign the district to the zone string
        self._compose_partitions()

        # then evaluate the fitness of each string
        self._evaluate_partitions()

        # which is the best partition?
        self._select_best_partition()

        # update our score with the best one
        self._update_our_score()

        self.logger.info(our.MG_INFO_INITIAL_SCORE.format(self.last_best_score))

        while it < our.GA_MAX_ITERATIONS and \
                it_ni < our.GA_NOIMPROV_ITERATIONS:
            # select parental couples
            # by tournament
            self._generate_parental_couples()

            # apply crossover operator
            self._apply_crossover_operator()

            # apply mutation operator
            self._apply_mutation_operator()

            # reset partitions, because crossover and mutation
            # operators have created new zone centers lists (the genotype)
            self._restore_partitions()

            # compose zone strings
            self._compose_partitions()

            # evaluate the fitness
            self._evaluate_partitions()

            # select survivors
            self._select_next_generation()

            # which is the best partition?
            self._select_best_partition()

            # update our score with the best one
            self._update_our_score()

            # if new score is better, then reset no improvement iterations counter
            if self._is_new_score_better():
                it_ni = 0
            else:
                it_ni += 1

            # go to next iteration
            it += 1

            # say something about our progress
            if it % it_module == 0:
                self.logger.info(our.MG_INFO_LAST_SCORE.format(it, self.last_best_score))

        # also log the last best score if not logged previously
        if it % it_module != 0:
            self.logger.info(our.MG_INFO_LAST_SCORE.format(it, self.last_best_score))

        pass

    def _generate_initial_population(self):
        # populate (empty) list of genotypes
        #
        if len(self.partition) > 0:
            raise OverflowError(our.MG_DEBUG_INTERNAL_ERROR)

        # will generate pop_card Partition objects
        for i in range(self.pop_card):
            # create a new one
            new_part = Partition(data=self.data, mean_value=self.mean_value, geodata=self.geodata,
                                 valid_area=self.valid_area, num_zones=self.num_zones,
                                 logger=self.logger)

            # also populate it with random zone future centers
            new_part.generate_genotype()

            # and finally add to our collection
            self._append_partition(part=new_part)

        pass

    def _append_partition(self, part: Partition):
        # append Partition instance to
        # partitions list

        self.partition.append(part)

        pass

    def _select_best_partition(self):
        # scan Partition object list
        # looking for the best one
        # and select it

        # according to our fitness score function,
        # get the best score value selection function
        func_select_best_value = get_func_select_best_value()

        # select the best partition instance
        self.best_partition = func_select_best_value(
            self.partition, key=lambda part: part.score)

        pass

    def _update_our_score(self):
        # update the designer score
        # with the best partition score

        # save the last known best score into its list
        if self.last_best_score is not None:
            self.best_score_history.append(self.last_best_score)

        self.last_best_score = self.best_partition.score

        pass

    def _is_new_score_better(self):
        # return true if the new last score is better than the old last one
        # return false otherwise

        # if there are any data to compare ...
        if len(self.best_score_history) > 0:
            # ... then if the better one is the
            # last_best_score ... True
            is_new_score_better = get_best_value_index(
                [self.best_score_history[-1],
                 self.last_best_score]) == 1
        else:
            is_new_score_better = False

        return is_new_score_better

    def _restore_partitions(self):
        # reset partition zones and stats

        for part in self.partition:
            part.restore_partition()

        self.logger.debug(
            our.MG_INFO_PARTITIONS_RESTORED)

        pass

    def _compose_partitions(self):
        # compose partition
        # assigning the distrits to the nearest
        # zone centroid point

        for part in self.partition:
            part.compose_partition()

        pass

    def _evaluate_partitions(self):
        # calculate fitness function value
        # for each partition

        for part in self.partition:
            part.evaluate()

        pass

    def _generate_parental_couples(self):
        # generate parental couples
        # by tournament

        # TODO

        pass

    def _apply_crossover_operator(self):
        # apply crossover operator
        # with GA_CROSSOVER_PROB probability value

        # TODO

        pass

    def _apply_mutation_operator(self):
        # apply mutation operator
        # with GA_MUTATION_PROB probability value

        for part in self.partition:
            part.mutate(prob=our.GA_MUTATION_PROB)

        pass

    def _select_next_generation(self):
        # apply elitist strategy
        # to select only the best partitions

        # how many partitions must maintain?
        pop_card = self.pop_card

        # obtain an ordered partition list by partition score
        new_partition_list = sorted(self.partition, key=lambda part: part.score)

        # and save only the first 'pop_card' ones
        self.partition = new_partition_list[:pop_card]

        pass

    def save_map(self, output_path):
        # save a plot of the result at disk
        #

        if type(self.best_partition) == Partition:
            self.best_partition.plot()
            self.best_partition.savefig(output_path)

        pass