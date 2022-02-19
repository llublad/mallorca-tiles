# Pràctica de creació de zones electorals per algorismes genètics
#
# IC - MUSI 21 22 - UIB
#
# Alumne: Lluís Bernat Ladaria

"""
Zone class - library
"""

#
# system libraries
#

from shapely.geometry.point import Point
import logging as log

#
# ours libraries
#

import mt_common as our


def _intersection(list1: list, list2: list) -> list:
    # return a list with the common list1 and list2 elements
    #

    temp = set(list2)
    new_list = [value for value in list1 if value in temp]

    return new_list


class Zone:
    """
    Class that encapsulates a zone

    A zone contains a list of (probably connected) districts
    and all the methods to deal with
    """

    def __init__(self, center: Point, logger: log.Logger):
        # create a zone instance
        # centered at 'center' Point

        # check center contains a Point
        if type(center) is not Point:
            raise TypeError(our.MG_DEBUG_INTERNAL_ERROR)

        # save parameters
        self._center = center
        self._logger = logger

        # zone is composed by district entries
        # we save them into this dictionary
        self._districts = dict()

        # and this is the district's counter
        self._n_districts = 0

        # also, must save the total zone value
        # (the sum of each district value)
        self._zone_value = 0  # stores the total population of the zone

        # an internal connectivity cost can be computed
        # based on each district NEIGHBOURS_COST_LIST dict entry
        self._conn_cost = None

        # the number of unconnected parts the zone has
        # for full connected zone is equal to zero
        self._unconnected_parts = None

        pass

    def get_center(self):
        # return the zone assigned center point
        #

        center = self._center

        return center

    def get_value(self):
        # return the total vallue of the zone
        #

        zone_value = self._zone_value

        return zone_value

    def get_cost(self):
        # return the connectivity cost of the whole zone
        #

        if self._conn_cost is not None:
            conn_cost = self._conn_cost
        else:
            raise ValueError(our.MG_DEBUG_INTERNAL_ERROR)

        return conn_cost

    def get_unconnected(self):
        # return the connectivity cost of the whole zone
        #

        if self._unconnected_parts is not None:
            unconnected = self._unconnected_parts
        else:
            raise ValueError(our.MG_DEBUG_INTERNAL_ERROR)

        return unconnected

    def get_districts_codes(self) -> list:
        # return a list of the codes of the distritcs at this zone
        #

        districts = self._districts.keys()

        return list(districts)

    def add_district(self, dis_code: str, dis_value: int,
                     center_distance: float, dis_geodata: dict):
        """
        Add district entry to zone string and its associated value,
        distance to zone center and neighbours data

        :param dis_code: code of the district
        :param dis_value: the value of the district (its population)
        :param center_distance: distance from district centroid to zone center
        :param dis_geodata: dictionary with list of neighbour codes and list of connection cost to each neighbour
        """

        entry = {
            1: dis_value,  # the value of the district (its population)
            2: center_distance,  # distance from district centroid to zone center
            3: dis_geodata  # dictionary with list of neighbour codes and list of connection cost to each neighbour
        }

        self._districts[dis_code] = entry
        self._zone_value += dis_value
        self._n_districts += 1

        pass

    def calc_cost(self):
        # calculate the connectivity cost value
        # as the average of the connectivity cost
        # of each pair of districts that composed the zone
        #
        # also detects the number of isolated parts
        # and updates its attribute accordindly

        # construct our districts list of codes
        district_code_list = list(self._districts.keys())

        total_cost = 0.
        total_connections = 0

        # if there are more than one district at the zone
        # then calculate the connectivity (mean) cost
        if len(district_code_list) > 1:
            for d1_code in self._districts.keys():
                d1_cost = 0.
                d1_connections = 0

                d1_geodata = self._districts.get(d1_code)[3]  # 3: geodata dictionary entry
                d1_neighbours_list = d1_geodata[our.DICT_DISTRICT_NEIGHBOURS_CODE_LIST]
                d1_cost_list = d1_geodata[our.DICT_DISTRICT_NEIGHBOURS_COST_LIST]

                # compute the list with the common districts codes
                my_zone_neighbours_list = _intersection(district_code_list, d1_neighbours_list)

                for code in my_zone_neighbours_list:
                    i = d1_neighbours_list.index(code)
                    d1_cost += d1_cost_list[i]
                    d1_connections += 1

                total_cost += d1_cost
                total_connections += d1_connections

            self._compute_unconnected_parts()
        else:
            self._unconnected_parts = 0  # in 1-district zones there are not unconnected parts

        if total_connections > 0:
            # calculate the average cost
            # the lower, the better
            mean_cost = total_cost / total_connections
        else:
            # assign maximum mean_cost value to penalize 1-district zones
            # or zones with all its distritcs unconnected
            mean_cost = 1.

        self._conn_cost = mean_cost

        pass

    def _log_zone_dump(self):
        # for debugging purposes,
        # log a zone dump

        self._logger.debug("Center:            {}".format(self._center))
        self._logger.debug("Distritcs list:    {}".format(self._districts))
        self._logger.debug("Total zone value:  {}".format(self._zone_value))
        self._logger.debug("Connectivity cost: {}".format(self._conn_cost))

        pass

    def __visit_neighbour(self, districts: list, pos: int):

        # mark this district as visited
        self.visited_status[pos] = True

        # locate its neighbours
        dis_entry = self._districts.get(districts[pos])
        neigbours = dis_entry.get(3).get(our.DICT_DISTRICT_NEIGHBOURS_CODE_LIST)

        neighbours_into_zone = _intersection(neigbours, districts)

        for neig in neighbours_into_zone:
            neig_pos = districts.index(neig)
            if not self.visited_status[neig_pos]:
                self.__visit_neighbour(districts=districts, pos=neig_pos)

        pass

    def _compute_unconnected_parts(self):
        # compute number of unconnected parts the zone has
        #

        # counter at zero
        unconnected = 0

        # get list of own district codes
        districts = self.get_districts_codes()

        # creata a vector of visited districts status (boolean)
        self.visited_status = [False] * len(districts)

        # start tour at first district
        init_pos = 0

        # start tour at first district
        self.__visit_neighbour(districts=districts, pos=init_pos)

        while False in self.visited_status:
            # if there are non visited districts, then
            # increment unconnected counter and make new tour
            # from unvisited district
            unconnected += 1

            init_pos = self.visited_status.index(False)

            # start new tour
            self.__visit_neighbour(districts=districts, pos=init_pos)

        self._unconnected_parts = unconnected

        pass
