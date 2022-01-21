# Pràctica de creació de zones electorals per algorismes genètics
#
# IC - MUSI 21 22 - UIB
#
# Alumne: Lluís Bernat Ladaria


# ******************
# Zone design - main
# ******************


#
# system libraries
#

import json
import os
import sys
import shutil
import geopandas
import matplotlib.pyplot as plt
import logging as log


#
# ours libraries and classes
#



#
# main program
#

def compute_zones(bound_abs_path: str, dis_abs_path: str, dat_abs_path: str,
                  out_abs_path: str, pop_card_list: list,
                  logger: log.Logger):
    """
    Principal function.

    It loads the maps, constructs the connection matrix and
    applies the genetic algorithm

    :param bound_abs_path:
    :param dis_abs_path:
    :param dat_abs_path:
    :param out_abs_path:
    :param pop_card_list:
    :param logger:
    :return:
    """

    # Load boundary map
    gpd_bound = geopandas.read_file(bound_abs_path, encoding='utf-8')

    # Load districts map
    gpd_dis = geopandas.read_file(dis_abs_path, encoding='utf-8')

    if logger.level == log.DEBUG:
        gpd_bound.plot()
        gpd_dis.plot()
        plt.show()



    #
    # loader = ls.Loader()
    # for in_dir, out_dir in zip(in_list, out_list):
    #     shutil.rmtree(out_dir)
    #     os.mkdir(out_dir)
    #     print(f"Loading set: {in_dir}")
    #     # Load data from JSON set
    #     loader = ls.Loader()
    #     loader.load(in_dir)
    #
    #     if not loader.error.has_error():
    #         resultados = {}
    #         for ins in num_inst_list:
    #             for met in methods_list:
    #                 # If JSON data set is OK, then make initial population
    #                 population = pop.Population(inputs=loader.data,
    #                                             population_size=ins,
    #                                             met=met,
    #                                             mutation_prob=0.1)
    #
    #                 if not population.error.has_error():
    #                     hiper_parametros = population.get_hiperpar()
    #                     json_key = ls.format_json_key(hiper_parametros)
    #                     # If population is feasible, then make the timetable
    #                     population.fit(iterations=500)
    #
    #                     # At the end of work, save the results
    #                     saver = ls.Saver(population.get_champion(),
    #                                      population.get_results(),
    #                                      population.get_hiperpar())
    #                     resultados[json_key] = saver.save_results(out_dir)
    #                 else:
    #                     population.error.print()
    #
    #         with open(os.path.normpath(f"{out_dir}/horarios.json"), 'w') as json_file:
    #             json.dump(resultados, json_file, cls=ls.NumpyEncoder)
    #     else:
    #         loader.error.print()

    return


if __name__ == '__main__':
    #
    # constants
    #

    BOUNDARY_REL_PATH = '../maps/products/coast_line_geometry.geojsonl.json'
    DISTRICTS_REL_PATH = '../maps/products/districts_geometry.geojsonl.json'
    DATA_REL_PATH = '../habs/PAD2020.csv'
    OUTPUT_REL_PATH = '../outputs'
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

    compute_zones(boundary_abs_path, districts_abs_path, data_abs_path,
                  outputs_abs_path, population_card_list, logger)

    # say goodbye
    logger.info("*** End of process ***")
