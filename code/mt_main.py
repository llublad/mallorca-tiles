# Pràctica de creació de zones electorals per algorismes genètics
#
# IC - MUSI 21 22 - UIB
#
# Alumne: Lluís Bernat Ladaria

"""
Zone design - main
==================

Main program for uniform distributed zone design solutions
It loads and prepares input data, then computes a solution
for every tuple of parameters
"""

#
# system libraries
#

import os
import sys
import pandas as pd
import geopandas as gpd
import logging as log

#
# ours libraries and classes
#

import mt_common as our
from mt_PartitionDesigner import PartitionDesigner


#
# main program functions
#

def make_my_neighbours_lists(from_geos: gpd.GeoSeries, me: int, ind_vals: list) -> list:
    """
    Make the 'me' list of neighbours

    The output is a list with two entries (two lists)
    - One with neighbours code list
    - The other is a 'neighbourhood' connectivity cost value that we
      define as 1 minus a p-value proportional to the 'me'
      entity neighbour border common length.
      So the bigger a common borderline segment is,
      the lower is the associated connectivity cost value
    The lists are ordered (ascending) by the connectivity cost value.

    Example:
        Sóller (id: '07061') generated dictionary entry:
        '07061': {
            'NEIGHBOURS_ID_LIST': ['07025', '07010', '07018', '07019'],
            'NEIGHBOURS_COST_LIST': [0.608229, 0.692803, 0.837655, 0.861313]
            }
        As seen, the neighbours entities in ascending cost are:
        - id: '07025' ('Fornalutx'): who has the bigger common border-line segment
        - id: '07010' ('Bunyola')
        - id: '07018' ('Deià')
        - id: '07019' ('Escorca'): the smaller common border-line segment
    """
    assert len(from_geos) == len(ind_vals), \
        "Alert, length of geoserie index values list is not equal to geoserie cardinality"

    # the new list
    my_neighbours = list()

    # who are my neighbours?
    is_in_touch = from_geos.touches(from_geos.iloc[me])

    # how many borderline we share?
    border_thickness = 1  # use 1 meter buffer to calc common 'area' border
    # compute myself 1 meter over-sized
    me_buffered = from_geos.iloc[me].buffer(distance=border_thickness)
    # now compute overlapped area from my 1-meter bigger version vs rest geometric entities
    common_border_area = from_geos.intersection(me_buffered).area

    # calculate relative border areas shared with my neighbours
    #

    # initialize common area accumulator
    total_common_area = 0.

    # calculate total border length
    for j in range(len(is_in_touch)):
        if (me != j) and is_in_touch[j]:
            total_common_area += common_border_area[j]

    # if there are no common area,
    # initialize divisor to non-zero value to avoid
    # the (rare) div/0 case error
    # (i.e. an isolated district)
    if total_common_area == 0.:
        total_common_area = 1.

    # compute ranking list
    for j in range(len(is_in_touch)):
        if (me != j) and is_in_touch[j]:
            new_entry = [
                ind_vals[j],
                round(1.0 - common_border_area[j] / total_common_area, ndigits=6)
            ]
            my_neighbours.append(new_entry)

    # now order list ascending using neighbourhood calculated cost value
    my_neighbours.sort(key=lambda neighbour_entry: neighbour_entry[1])

    # and finally compose a dictionary with each one vector (the two lists)
    my_neighbours_lists = [
        [item for item, _ in my_neighbours],
        [item for _, item in my_neighbours]
    ]

    return my_neighbours_lists


def make_dist_conn_dict(from_geo: gpd.GeoDataFrame, by_field: str) -> dict:
    """
    Calculates a dictionary of lists with the neighbours districts
    and the centroid points

    :param from_geo:
    :param by_field:
    :return:
    """
    # our new dict of lists
    geodata_dict = dict()

    # a GeoSeries object is needed to
    # calculate centroids and intersection areas
    geos = gpd.GeoSeries(from_geo.geometry)
    index_values = list(from_geo[by_field])

    for i in range(len(from_geo)):
        # get district code
        new_district_code = from_geo[by_field].iloc[i]
        # get district centroid
        centroid = geos[i].centroid
        centroid_point = (centroid.x, centroid.y)
        # get district neighbours list and associated connectivity cost list
        [code_list, cost_list] = make_my_neighbours_lists(
            from_geos=geos, me=i, ind_vals=index_values)
        # create a little dictionary containing:
        # - neighbours code list
        # - connectivity cost neighbours list
        # - centroid point
        new_district_entry = {
            our.DICT_DISTRICT_CENTROID_POINT: centroid_point,
            our.DICT_DISTRICT_NEIGHBOURS_CODE_LIST: code_list,
            our.DICT_DISTRICT_NEIGHBOURS_COST_LIST: cost_list
        }
        # and add to the geodata_dict dictionary (a nested dictionary)
        geodata_dict[new_district_code] = new_district_entry

    return geodata_dict


def prepare_data(bound_path: str,
                 dis_path: str, dis_index_field: str,
                 dat_path: str, dat_index_field: str, dat_value_field: str,
                 logger: log.Logger) -> object:
    """
    Load maps, and alpha data.
    Also constructs the district connection matrix (actually a nested dict)
    and the valid area, that is a map that represents
    the area that can contain a valid zone centroid

    :param bound_path:
    :param dis_path:
    :param dis_index_field:
    :param dat_path:
    :param dat_index_field:
    :param dat_value_field:
    :param logger:
    :return:
    """

    # load alphanumeric data
    logger.info(f"Loading alphanumeric data from {dat_path}")
    pd_dat = pd.read_csv(filepath_or_buffer=dat_path, sep=";", encoding='utf-8')
    # change relevant columns names
    mapper = {
        dat_index_field: our.PD_DATA_CODE_FIELD,
        dat_value_field: our.PD_DATA_VALUE_FIELD
    }
    pd_dat.rename(mapper=mapper, axis=1, inplace=True)
    logger.debug(f"\n{pd_dat.info}")

    # construct comprehension list from data panda DataFrame
    dat_list = [[row[0], row[1]]
                for row in zip(pd_dat[our.PD_DATA_CODE_FIELD],
                               pd_dat[our.PD_DATA_VALUE_FIELD])]

    # load districts map
    logger.info(f"Loading district map from {dis_path}")
    gpd_dis = gpd.read_file(filename=dis_path, encoding='utf-8')
    # project it to meters (EPSG:3857)
    # to be able to calculate distances
    gpd_dis = gpd_dis.to_crs(crs="EPSG:3857")

    # load boundary map
    logger.info(f"Loading boundary map from {bound_path}")
    # project it to meters (EPSG:3857)
    gpd_bound = gpd.read_file(filename=bound_path, encoding='utf-8').to_crs(crs="EPSG:3857")

    if logger.level == log.DEBUG:
        gpd_bound.plot()
        gpd_dis.plot()
        # plt.show()

    logger.info(our.MG_INFO_COMPUTING_VALID_AREA)
    valid_area = gpd_dis.geometry.unary_union

    logger.info("Making district connectivity matrix from districts map. Really its a dictionary of lists...")
    conn_dict = make_dist_conn_dict(from_geo=gpd_dis, by_field=dis_index_field)
    logger.debug("District connectivity matrix:")
    logger.debug(conn_dict)
    logger.info("...done district connectivity matrix")

    return gpd_bound, gpd_dis, valid_area, dat_list, conn_dict


#
# main program
#

if __name__ == '__main__':
    #
    # constants
    #

    BOUNDARY_REL_PATH = '../maps/products/coast_line_geometry.geojsonl.json'

    DISTRICTS_REL_PATH = '../maps/products/districts_geometry.geojsonl.json'
    DISTRICTS_INDEX_FIELD = 'CODE'

    DATA_REL_PATH = '../habs/PAD2020.csv'
    DATA_INDEX_FIELD = 'Cod_Terri'
    DATA_VALUE_FIELD = 'Total'

    OUTPUT_REL_PATH = '../outputs'

    NUM_ZONES = [10]  # [2, 3, 10, 20, 30]
    POPULATION_CARDINALITIES = [10]  # [10, 20]

    LOG_LEVEL = log.INFO
    # LOG_LEVEL = log.DEBUG

    #
    # setup logger
    #

    logger = log.getLogger('mt_logger')
    logger.setLevel(LOG_LEVEL)
    log_format = log.Formatter('[%(asctime)s] [%(levelname)s] - %(message)s')
    # writing to stderr
    handler = log.StreamHandler(sys.stderr)
    handler.setFormatter(log_format)
    logger.addHandler(handler)

    #
    # setting parameters
    #

    # test different population cardinalities
    population_card_list = POPULATION_CARDINALITIES

    # calculate path
    current_program_path = os.path.dirname(os.path.realpath(__file__))
    boundary_abs_path = os.path.normpath(current_program_path + '/' + BOUNDARY_REL_PATH)
    districts_abs_path = os.path.normpath(current_program_path + '/' + DISTRICTS_REL_PATH)
    data_abs_path = os.path.normpath(current_program_path + '/' + DATA_REL_PATH)
    outputs_abs_path = os.path.normpath(current_program_path + '/' + OUTPUT_REL_PATH)

    # say hello
    logger.info("*** Starting process ***")

    # load and prepare all the data, also compute districts connectivity dictionary
    # and valid zone centroid area
    gpd_bound, gpd_dis, valid_area, dat_list, geodata_dict = \
        prepare_data(bound_path=boundary_abs_path, dis_path=districts_abs_path, dis_index_field=DISTRICTS_INDEX_FIELD,
                     dat_path=data_abs_path, dat_index_field=DATA_INDEX_FIELD, dat_value_field=DATA_VALUE_FIELD,
                     logger=logger)

    # compute zones for all the tuples {NUM_ZONES x POPULATION_CARDINALITIES}
    for nz in NUM_ZONES:
        for pc in POPULATION_CARDINALITIES:

            solution = PartitionDesigner(
                data=dat_list, geodata=geodata_dict,
                valid_area=valid_area,
                num_zones=nz, pop_card=pc,
                logger=logger,
                gpd_bound=gpd_bound, gpd_dis=gpd_dis,
                save_maps_to=outputs_abs_path)

            # compute best partition and
            # plot each relevant hit
            solution.fit()

            # free memory
            del solution

    # say goodbye
    logger.info("*** End of process ***")
