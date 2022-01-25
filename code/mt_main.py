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
import matplotlib.pyplot as plt


#
# ours libraries and classes
#

import mt_common as our
from mt_zones import Partition


#
# main program functions
#

def make_my_neighbours_list(from_geos: gpd.GeoSeries, me: int, ind_vals: list) -> dict:
    """
    Make the 'me' list of neighbours

    The output is a dictionary with two entries:
    - One with neighbours id codes list
    - The other is a p-value proportional to the 'me'
      entity neighbour border common lenght
    The lists are ascending ordered by the p-value.

    Example:
        {
            'NEIGHBOURS_ID_LIST': ['07019', '07018', '07010', '07025'],
            'NEIGHBOURS_PROB_LIST': [0.138687, 0.162345, 0.307197, 0.391771]
        }
    """
    assert len(from_geos) == len(ind_vals), \
        "Alert, length of geos index values list is not equal to geos cardinality"

    # The new list
    my_neighbours = list()

    # Who are my neighbours?
    is_in_touch = from_geos.touches(from_geos.iloc[me])

    # How many borderline we share?
    border_thickness = 1  # use 1 meter buffer to calc common 'area' border
    # compute myself 1 meter oversized
    me_buffered = from_geos.iloc[me].buffer(distance=border_thickness)
    # now compute overlapped area from my 1-meter bigger version vs rest
    common_border_area = from_geos.intersection(me_buffered).area

    # Calculate relative border areas shared with my neighbours

    # initialize divisor to non-zero value to avoid the (rare) div/0 case error
    # (i.e. an isolated district)
    total_common_area = 1e-6

    # Calculate total border length
    for j in range(len(is_in_touch)):
        if (me != j) and is_in_touch[j]:
            total_common_area += common_border_area[j]

    # Compute ranking list
    for j in range(len(is_in_touch)):
        if (me != j) and is_in_touch[j]:
            new_entry = [
                ind_vals[j],
                round(common_border_area[j] / total_common_area, ndigits=6)
            ]
            my_neighbours.append(new_entry)

    # Now order list ascending using common border coefficient
    my_neighbours.sort(key=lambda neighbour_entry: neighbour_entry[1])

    # And finnally compose a dictionary with each one vector (the two lists)
    my_neighbours_dict = {
        our.DICT_DISTRICT_NEIGHBOURS_ID_LIST:
            [item for item, _ in my_neighbours],
        our.DICT_DISTRICT_NEIGHBOURS_SLICE_LIST:
            [item for _, item in my_neighbours]
    }

    return my_neighbours_dict


def make_dist_conn_dict(from_geo: gpd.GeoDataFrame, by_field: str) -> dict:
    """
    Calculates a dictionary of lists with the neighbours districts

    :param from_geo:
    :param by_field:
    :return:
    """
    # Our new dict of lists
    conn_dict = dict()

    # A GeoSeries object is needed to calc distances
    # Project it to meters (EPSG:3857)
    geos = gpd.GeoSeries(from_geo.geometry).to_crs(crs="EPSG:3857")
    index_values = list(from_geo[by_field])

    for i in range(len(from_geo)):
        new_district_id = from_geo[by_field].iloc[i]
        conn_dict[new_district_id] = make_my_neighbours_list(from_geos=geos, me=i, ind_vals=index_values)

    return conn_dict


def prepare_data(bound_path: str,
                 dis_path: str, dis_index_field: str,
                 dat_path: str, dat_index_field: str,
                 logger: log.Logger) -> object:
    """
    Load maps, and alpha data. Also constructs the connection matrix

    :param bound_path:
    :param dis_path:
    :param dis_index_field:
    :param dat_path:
    :param dat_index_field:
    :param logger:
    :return:
    """

    # Load alphanumeric data
    logger.info(f"Loading alphanumeric data from {dat_path}")
    pd_dat = pd.read_csv(filepath_or_buffer=dat_path, sep=";", encoding='utf-8')
    pd_dat.set_index(dat_index_field)
    logger.debug(f"\n{pd_dat.info}")

    # Load boundary map
    logger.info(f"Loading boundary map from {bound_path}")
    gpd_bound = gpd.read_file(filename=bound_path, encoding='utf-8')

    # Load districts map
    logger.info(f"Loading district map from {dis_path}")
    gpd_dis = gpd.read_file(filename=dis_path, encoding='utf-8')

    if logger.level == log.DEBUG:
        gpd_bound.plot()
        gpd_dis.plot()
        # plt.show()

    logger.info("Making district connectivity matrix from districts map. Really its a dictionary of lists...")
    conn_dict = make_dist_conn_dict(from_geo=gpd_dis, by_field=dis_index_field)
    logger.debug("District connectivity matrix:")
    logger.debug(conn_dict)
    logger.info("...done district connectivity matrix")

    return gpd_bound, gpd_dis, pd_dat, conn_dict


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
    OUTPUT_REL_PATH = '../outputs'
    NUM_ZONES = [10, 20]
    POPULATION_CARDINALITIES = [20, 50]
    LOG_LEVEL = log.DEBUG

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

    # load and prepare all the data, also compute districts connection dictionary
    gpd_bound, gpd_dis, pd_dat, conn_dict = \
        prepare_data(bound_path=boundary_abs_path, dis_path=districts_abs_path, dis_index_field=DISTRICTS_INDEX_FIELD,
                     dat_path=data_abs_path, dat_index_field=DATA_INDEX_FIELD, logger=logger)

    # compute zones for all the tuples {NUM_ZONES x POPULATION_CARDINALITIES}
    for nz in NUM_ZONES: 
        for pc in POPULATION_CARDINALITIES:
            solution = Partition(
                data=pd_dat, conn=conn_dict,
                num_zones=nz, pop_card=pc,
                logger=logger)
            solution.fit()
            solution.save_map(output_path=outputs_abs_path)
            del solution

    # say goodbye
    logger.info("*** End of process ***")
