# Pràctica de creació de zones electorals per algorismes genètics
#
# IC - MUSI 21 22 - UIB
#
# Alumne: Lluís Bernat Ladaria

#
# Zone design - main
#

#
# system libraries
#
import json
import os
import sys
import shutil
import geopandas
import matplotlib.pyplot as plt

#
# main program
#

def compute_zones(bound_abs_path, dis_abs_path, dat_abs_path, out_abs_path, num_instances_list):


    gpd_bound = geopandas.read_file(bound_abs_path)
    gpd_bound.plot()

    gpd_dis = geopandas.read_file(dis_abs_path)
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
    BOUNDARY_REL_PATH = '../maps/products/coast_line_geometry.geojsonl.json'
    DISTRICTS_REL_PATH = '../maps/products/districts_geometry.geojsonl.json'
    DATA_REL_PATH = '../habs/PAD2020.csv'
    OUTPUT_REL_PATH = '../outputs'

    current_program_path = os.path.dirname(os.path.realpath(__file__))

    boundary_abs_path = os.path.normpath(current_program_path + '/' + BOUNDARY_REL_PATH)
    districts_abs_path = os.path.normpath(current_program_path + '/' + DISTRICTS_REL_PATH)
    data_abs_path = os.path.normpath(current_program_path + '/' + DATA_REL_PATH)
    outputs_abs_path = os.path.normpath(current_program_path + '/' + OUTPUT_REL_PATH)

    num_instances_list = [20, 50]  # test different population cardinalities

    compute_zones(boundary_abs_path, districts_abs_path, data_abs_path, outputs_abs_path, num_instances_list)

    print("End of process.")
