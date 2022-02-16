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

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import numpy as np
from shapely.geometry.base import BaseGeometry
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon
import logging as log
import random

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


def check_geodata(geodata: dict, gpd_dis: gpd.GeoDataFrame, data: list) -> bool:
    # sanity checks for connectivity dictionary
    #

    if type(geodata) is not dict:
        raise TypeError(our.MG_ERROR_CONN)
    if type(gpd_dis) is not gpd.GeoDataFrame:
        raise TypeError(our.MG_ERROR_DIS)

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
    is_correct = (num_zones >= 2) and (num_zones <= len(data))

    if not is_correct:
        raise ValueError(our.MG_ERROR_NUM_ZONES)

    return is_correct


def check_pop_card(pop_card: int) -> bool:
    # check if pop_card is even
    #

    if not type(pop_card) is int:
        raise TypeError(our.MG_ERROR_POP_CARD)

    # population cardinality must be even and greater than 0
    is_correct = (pop_card % 2 == 0) and (pop_card > 0)

    if not is_correct:
        raise ValueError(our.MG_ERROR_POP_CARD)

    return is_correct


def check_gpd_boundary(gpd_bound: gpd.GeoDataFrame):
    # basic checkings for GeoDataframe
    # of the map boundary

    if not type(gpd_bound) is gpd.GeoDataFrame:
        raise ValueError(our.MG_DEBUG_INTERNAL_ERROR)

    is_correct = len(gpd_bound) == 1

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
    :param gpd_bound: a GeoDataFrame containing the map boundary
    :param gpd_dis: a GeoDataFrame containig the district geo-entities

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
                 num_zones: int, pop_card: int, logger: log.Logger,
                 gpd_bound: gpd.GeoDataFrame, gpd_dis: gpd.GeoDataFrame):
        # create object instance, if params syntax are correct
        all_correct = \
            check_data(data=data) and \
            check_geodata(geodata=geodata, gpd_dis=gpd_dis, data=data) and \
            check_valid_area_map(valid=valid_area) and \
            check_num_zones(num_zones=num_zones, data=data) and \
            check_pop_card(pop_card=pop_card) and \
            check_gpd_boundary(gpd_bound=gpd_bound)

        if all_correct:

            # save all the params
            self.logger = logger
            self.data = data
            self.geodata = geodata
            self.valid_area = valid_area
            self.num_zones = num_zones
            self.pop_card = pop_card

            # also, the GeoPandas to be able to plot maps
            self.gpd_bound = gpd_bound
            self.gpd_dis = gpd_dis

            num_districts = len(data)
            self.num_districts = num_districts

            self.__calc_total_value()

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

            # daddy and mummy list (crossover)
            self.daddy = list()
            self.mummy = list()

            # our list of children
            self.offspring = list()

        else:
            # this will never be executed,
            # because raise clauses in check_whatever functions...
            # ...but in case would run,
            # we force a generic Exception to be noticed about and debug it
            raise Exception(our.MG_DEBUG_INTERNAL_ERROR)

        pass

    def __calc_total_value(self):
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
        # last score reference value
        reference_score: float

        # for each district,
        # find the closest zone center
        # and assign the district to the zone string
        self._compose_parents()

        # then evaluate the fitness of each string
        self._evaluate_parents()

        # which is the best partition?
        self._select_best_partition()

        # update our score with the best one
        self._update_our_score()
        reference_score = self.last_best_score

        self.logger.info(our.MG_INFO_INITIAL_SCORE.format(self.last_best_score).replace(',', ' '))

        while it < our.GA_MAX_ITERATIONS and \
                it_ni < our.GA_NOIMPROV_ITERATIONS:
            # select parental couples
            # by tournament
            self._generate_parental_couples()

            # apply crossover operator
            # over parents couples
            # with GA_CROSSOVER_PROB probability
            self._apply_crossover_operator(prob=our.GA_CROSSOVER_PROB)

            # apply mutation operator over children
            # with GA_MUTATION_PROB probability
            self._apply_mutation_offspring(prob=our.GA_MUTATION_PROB)

            # compose children zone strings
            self._compose_offspring()

            # evaluate the fitness
            #
            # the parents
            # self._evaluate_parents()
            # and also the children
            self._evaluate_offspring()

            # select survivors
            self._select_next_generation(hold=our.GA_NEXT_GENERATION_HOLD)

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
            if it % it_module == 0 or \
                    reference_score - self.last_best_score > our.GA_LOG_PC_SCORE_IMPROV * reference_score:
                self.logger.info(our.MG_INFO_LAST_SCORE.format(it, self.last_best_score).replace(',', ' '))
                reference_score = self.last_best_score

        # also log the last best score if not logged previously
        if it % it_module != 0:
            self.logger.info(our.MG_INFO_LAST_SCORE.format(it, self.last_best_score).replace(',', ' '))

        pass

    def _generate_initial_population(self):
        # populate (empty) list of genotypes
        #
        if len(self.partition) > 0:
            raise ValueError(our.MG_DEBUG_INTERNAL_ERROR)

        # will generate pop_card Partition objects
        for i in range(self.pop_card):
            # create a new one
            new_part = Partition(data=self.data, mean_value=self.mean_value, geodata=self.geodata,
                                 valid_area=self.valid_area, num_zones=self.num_zones,
                                 logger=self.logger)

            # also populate it with random zone future centers
            new_part.generate_genotype()

            # and finally add to our collection
            self.partition.append(new_part)

        pass

    def _compose_parents(self):
        # compose parents partitions
        # assigning the distrits to the nearest
        # zone centroid point

        for part in self.partition:
            part.compose_partition()

        pass

    def _compose_offspring(self):
        # compose children partitions
        # assigning the distrits to the nearest
        # zone centroid point

        for part in self.offspring:
            part.compose_partition()

        pass

    def _evaluate_parents(self):
        # calculate fitness function value
        # for each parent

        for part in self.partition:
            part.evaluate()

        pass

    def _evaluate_offspring(self):
        # calculate fitness function value
        # for each child

        for part in self.offspring:
            part.evaluate()

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
            self.partition, key=lambda part: part.get_score())

        pass

    def _update_our_score(self):
        # update the designer score
        # with the best partition score

        # save the last known best score into its list
        if self.last_best_score is not None:
            self.best_score_history.append(self.last_best_score)

        self.last_best_score = self.best_partition.get_score()

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

    def __tournament_selection(self, n_adversaries: int):
        # return the tournament winner
        #

        # construct the candidates list
        candidates = list(set(self.partition) - set(self.daddy) - set(self.mummy))

        # select at most n_adversaries (with reemplacement)
        adversaries = random.choices(candidates, k=n_adversaries)

        best = None

        for part in adversaries:
            if best is None or get_best_value_index([best.get_score(), part.get_score()]) == 1:
                best = part

        return best

    def _generate_parental_couples(self):
        # generate parental couples
        # by tournament

        # mummy and daddy lists must be empty
        if type(self.daddy) != list or type(self.mummy) != list or \
                len(self.daddy) > 0 or len(self.mummy) > 0:
            raise ValueError(our.MG_DEBUG_INTERNAL_ERROR)

        n_couples = self.pop_card // 2

        for i in range(n_couples):
            daddy = self.__tournament_selection(n_adversaries=our.GA_TOURNAMENT_ADVERSARIES)
            self.daddy.append(daddy)
            mummy = self.__tournament_selection(n_adversaries=our.GA_TOURNAMENT_ADVERSARIES)
            self.mummy.append(mummy)

        pass

    def __compute_crossover(self, dad: Partition, mum: Partition) -> [Partition, Partition]:
        # compute crossover over dad and mum
        # and generate two sons with information from dad and mum

        # how many zones are coded into dad genotype?
        num_zones = dad.num_zones

        # initially sons have no DNA (empty genotype)
        son1 = Partition(data=self.data, mean_value=self.mean_value, geodata=self.geodata,
                         valid_area=self.valid_area, num_zones=self.num_zones,
                         logger=self.logger)
        son2 = Partition(data=self.data, mean_value=self.mean_value, geodata=self.geodata,
                         valid_area=self.valid_area, num_zones=self.num_zones,
                         logger=self.logger)

        # how many zone genotypes will remain on dad?
        # at least 1 but no more than the total minus 1
        zones_to_hold = random.randint(a=1, b=num_zones - 1)

        son1_genotype = dad.genotype[:zones_to_hold] + mum.genotype[zones_to_hold:]
        son2_genotype = mum.genotype[:zones_to_hold] + dad.genotype[zones_to_hold:]

        son1.genotype = son1_genotype
        son2.genotype = son2_genotype

        return son1, son2

    def _apply_crossover_operator(self, prob: float):
        # apply crossover operator
        # with GA_CROSSOVER_PROB probability value

        if type(self.offspring) != list or len(self.offspring) > 0:
            raise ValueError(our.MG_DEBUG_INTERNAL_ERROR)

        for daddy, mummy in zip(self.daddy, self.mummy):
            dice = random.random()
            if dice < prob:
                [son1, son2] = self.__compute_crossover(dad=daddy, mum=mummy)
                self.offspring.append(son1)
                self.offspring.append(son2)

        # clean parents lists
        self.daddy = list()
        self.mummy = list()

        pass

    def _apply_mutation_offspring(self, prob: float):
        # apply mutation operator to children
        # with 'prob' probability value

        for part in self.offspring:
            part.mutate(prob=prob)

        pass

    def _select_next_generation(self, hold: float):
        # apply elitist strategy
        # to mantain at least 'hold' per-unit of the best parents
        # and select only the best children partitions until
        # population cardinality is reached

        # sorting order?
        # the more, the better ?
        reverse_sorting = get_best_value_index([0, 1]) == 1

        # obtain an ordered partition list by partition score
        parents_list = sorted(self.partition, key=lambda part: part.score,
                              reverse=reverse_sorting)

        # obtain an ordered childs list by score
        child_list = sorted(self.offspring, key=lambda part: part.score,
                            reverse=reverse_sorting)

        # how many partitions must survive?
        n_population = self.pop_card

        # how many of them must be childs?
        n_childs = int((1 - hold) * n_population)

        # due to crossover probability
        # it can happen to have an insuficient offspring cardinality,
        # so we must assure a constant population
        n_childs = min(n_childs, len(self.offspring))

        # how many of them must be parents?
        n_parents = n_population - n_childs

        # and save the new list formed by each one top partitions
        self.partition = parents_list[:n_parents] + child_list[:n_childs]

        # also delete the offspring
        self.offspring = list()

        pass

    def save_best_map(self, output_file_name: str):
        # save a plot of the best result at disk
        #

        if type(self.best_partition) != Partition or \
                len(self.best_partition.get_zones()) == 0:
            raise TypeError(our.MG_DEBUG_INTERNAL_ERROR)

        # figsize
        plt.rcParams['figure.figsize'] = our.PLOT_FIGSIZE

        # plot map boundary
        self.gpd_bound.plot()

        # get the zones of the best partition
        district_zone_id_list = self.best_partition.get_district_zone_id_list()

        gdf = self.gpd_dis[[our.GPD_DATA_CODE_FIELD, our.GPD_GEOMETRY_FIELD]]
        # add zone's ids column to be able to color it
        gdf['Zone'] = district_zone_id_list

        # compute palette
        num_colors = len(self.best_partition.get_zones())
        colors_vector = [(0.8, 0.1, 0.1),
                         (0.1, 0.8, 0.1),
                         (0.1, 0.1, 0.8),
                         (0.8, 0.8, 0.1),
                         (0.1, 0.8, 0.8)]  # (R,G,B)
        cmap_name = 'my_part_colors'
        cmap = colors.LinearSegmentedColormap.from_list(cmap_name, colors_vector, N=num_colors)
        palette = [cmap(i) for i in np.linspace(0, 1, num_colors)]

        # plot each zone using diferent colors
        gdf.plot(column='Zone', cmap=cmap)

        color_column = []
        [color_column.append(palette[i]) for i in district_zone_id_list]
        gdf.plot(color=color_column)

        # plot zone centers
        centers = self.best_partition.get_centers()

        for n, point in enumerate(centers):
            plt.plot(point.x, point.y,
                     marker='o', linestyle='', markersize=8, mec='k', alpha=0.8,
                     label=our.PLOT_ZONE_LEGEND.format(n), color=palette[n])

        # get current axes
        ax = plt.gca()

        # hide axes and borders
        plt.axis('off')

        # title
        plt.title("Proposed solution")

        # legend
        plt.legend(loc='best', shadow=True, fancybox=True)

        plt.savefig(output_file_name)
        plt.close()

        pass
