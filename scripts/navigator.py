"""Navigator

Finds the optimal path for the Death Star through a pseudo-randomly generated
map
"""

from __future__ import print_function  # Python 2/3 compatibility
import time
import random
from StringIO import StringIO
import numpy as np
import pandas as pd
import boto3
from botocore.exceptions import ProfileNotFound
import cartographer as cart


def build_heuristics(rt_map):
    """Creates the heuristic matrix for a route map
    """
    dims  = rt_map.shape
    x_lim = dims[0]
    y_lim = dims[1]
    dest_col = y_lim - 9
    H_mat = np.zeros(shape=(x_lim, y_lim), dtype=np.int)
    H_mat[:, dest_col] = [2, 1, 0, 1, 2, 3, 4, 5, 6, 7]
    for i in range(dest_col + 1, y_lim):
        H_mat[:, i] = H_mat[:, (i - 1)] + 1
    for x in range(dest_col, 0, -1):
        H_mat[:, (x - 1)] = H_mat[:, x] + 1

    return H_mat


def keep_track(input_list, input_node):
    """Builds a list of squares that have been expanded
    """
    input_list.append(input_node)

    return input_list


def is_obstacle(square):
    """Checks the submitted location for the presence of an obstacle
    """
    if square == 1:
        return True
    else:
        return False


def find_route(rt_map, h_mat):
    """Calculates the optimized route through the map
    """
    # Starting coordinates for x and y
    dims = rt_map.shape
    y_dest = dims[1] - 9
    x_dest = dims[0] - 8
    coordinate_list = list()
    x_co = 4
    y_co = 4
    node = (x_co, y_co, 1000)

    for i in range(150):
        coordinate_list = keep_track(coordinate_list, node)
        if rt_map[x_dest, y_dest] != 7:
             # make the obstacle squares impossible for the algorithm
             # to traverse
            if is_obstacle(rt_map[(x_co - 1), (y_co)]):
                north = (x_co - 1, y_co, 1000)
            else:
                north = (x_co - 1, y_co, 1 + h_mat[(x_co - 1), (y_co)])

            if is_obstacle(rt_map[(x_co + 1), (y_co)]):
                south = (x_co + 1, y_co, 1000)
            else:
                south = (x_co + 1, y_co, 1 + h_mat[(x_co + 1), (y_co)])

            if is_obstacle(rt_map[(x_co), (y_co + 1)]):
                east = (x_co, y_co + 1, 1000)
            else:
                east = (x_co, y_co + 1, 1 + h_mat[(x_co), (y_co + 1)])

            if is_obstacle(rt_map[(x_co), (y_co - 1)]):
                west = (x_co, y_co - 1, 1000)
            else:
                west = (x_co, y_co - 1, 1 + h_mat[(x_co), (y_co - 1)])

            # Choose lowest valued sum of the heuristic matrix and the
            # movement cost.
            # The Death Star is Holonomic:
            #       currently, all movement is 1
            try_lst = [north, south, east, west]
            minimum = min(try_lst, key = lambda t: t[2])
            if minimum == north and north not in coordinate_list:
                rt_map[(x_co - 1), (y_co)] = 7
                x_co = x_co - 1
                node = north
            elif minimum == south and south not in coordinate_list:
                rt_map[(x_co + 1), (y_co)] = 7
                x_co = x_co + 1
                node = south
            elif minimum == east and east not in coordinate_list:
                rt_map[(x_co), (y_co + 1)] = 7
                y_co = y_co + 1
                node = east
            elif minimum == west and west not in coordinate_list:
                rt_map[(x_co), (y_co - 1)] = 7
                y_co = y_co - 1
                node = west
            elif south[2] == east[2]:
                rt_map[(x_co + 1), (y_co)] = 7
                x_co = x_co + 1
                node = south
            elif north[2] == east[2]:
                rt_map[(x_co), (y_co + 1)] = 7
                y_co = y_co + 1
                node = east
            elif south[2] == west[2]:
                rt_map[(x_co + 1), (y_co)] = 7
                x_co = x_co + 1
                node = south
            elif north[2] == west[2]:
                rt_map[(x_co - 1), (y_co)] = 7
                x_co = x_co - 1
                node = west
            elif north[2] == south[2]:
                rt_map[(x_co + 1)(y_co)] = 7
                x_co = x_co + 1
                node = south

            # else:
                # print("can't move anywhere")
                # check the tracking list for earlier nodes


    return rt_map


if __name__ == '__main__':
    SESS = cart.create_storage_session()

    tile_lst = []
    for i in range(8):
        tile_lst.append(cart.get_tiles(SESS))

    route_map  = cart.stitch_tiles(tile_lst)
    heuristics = build_heuristics(route_map)

    path = find_route(route_map, heuristics)
    printable = pd.DataFrame(path)
    printable.replace(0, '', inplace=True)
    print(printable.to_string(header=False, max_cols=None, max_rows=None))
