"""Cartographer

Generates map tiles for navigating the Death Star
"""


from __future__ import print_function  # Python 2/3 compatibility
import time
import random
from StringIO import StringIO
import numpy as np
import boto3
from botocore.exceptions import ProfileNotFound


MAP_SIZE   = 10
BATCH_SIZE = 4
STARTTIME  = time.time()


class MapTile(object):
    """A map tile used to build a route to the destination planet

    __Attributes__

        Size:      the number of rows and columns in the tile
        Obstacles: a list of planetary sized obstacles to be placed in the tile
        Response:  the response from the S3 API after storing the tile in S3
        Tile:      a matrix representing the free and occupied space in the map

    """


    def __init__(self, size=10):
        """Return a celestial object for placement in a map tile
        """
        self.size      = size
        self.obstacles = []
        self.response  = "No tile object has been stored yet."
        self.tile      = np.zeros(shape=(size, size), dtype=np.int)


    def gen_celestial_object(self):
        """Return a celestial body to place in the map tile
        """
        count = random.randint(1, 3)

        # obstacle attributes:
        obstacle_size  = [0, 1, 2]
        obstacle_type  = ["solid", "gaseous", "multi-bodied"]

        # Sampling the range of the map tile size will prevent obstacles from
        # being placed outside the limits of the matrix.
        xco = random.sample(range(self.size), count)
        yco = random.sample(range(self.size), count)

        for obstacle in range(count):
            celestial_object            = {}
            celestial_object["Size"]    = random.choice(obstacle_size)
            celestial_object["Type"]    = random.choice(obstacle_type)
            celestial_object["X_coord"] = xco[obstacle]
            celestial_object["Y_coord"] = yco[obstacle]
            self.obstacles.append(celestial_object)

        return self.obstacles


    def place_obstacles(self):
        """Return the map tile with a celestial object placed within it
        """
        if not self.obstacles:
            # Not a great design pattern
            # consider generating obstacles within this method
            raise RuntimeError("\n\n"\
                               "You must first generate obstacles before you"\
                               "can place them in the map tile.")

        else:
            for obstacle in self.obstacles:
                xco                 = obstacle["X_coord"]
                yco                 = obstacle["Y_coord"]
                radius              = obstacle["Size"]
                self.tile[xco][yco] = 1
                limit               = len(self.tile)
                for length in range(radius):
                    grow  = length + 1
                    north = xco - grow
                    south = xco + grow
                    east  = yco + grow
                    west  = yco - grow

                    if north < 0:
                        north = south
                    if south >= limit:
                        south = north
                    if east >= limit:
                        east = west
                    if west < 0:
                        west = east

                    self.tile[north][yco]  = 1
                    self.tile[south][yco]  = 1
                    self.tile[xco][east]   = 1
                    self.tile[xco][west]   = 1
                    self.tile[north][east] = 1
                    self.tile[north][west] = 1
                    self.tile[south][east] = 1
                    self.tile[south][west] = 1

                    # Trim the edges as an added measure against unroutable
                    # maps and for cleaner looking obstacles.
                    if grow == radius:
                        self.tile[south][east] = 0
                        self.tile[south][west] = 0
                        self.tile[north][east] = 0
                        self.tile[north][west] = 0

        return self.tile


    def store(self, sdk_session, bucket='galactic-map-tiles'):
        """Send the map tile to s3
        """
        if sdk_session.get_credentials()._is_expired():
            sdk_session = create_storage_session()
            s3 = sdk_session.resource("s3")
        else:
            s3 = sdk_session.resource("s3")

        key  = build_key()
        body = StringIO(self.tile)

        self.response = s3.Object(bucket, key).put(Body=body)

        return self.response


def create_storage_session():
    """Establish a session with S3
    """
    try:
        session = boto3.session.Session(profile_name='training')
    except ProfileNotFound:
        session = boto3.session.Session()

    return session


def build_key():
    """Create a prefix for the object sent to s3
    """
    hash_str = ''
    letter   = [chr(x) for x in range(65, 70)]
    number   = [x for x in range(1, 6)]

    for char in range(3):
        options = []
        options.append(random.choice(letter))
        options.append(random.choice(number))
        hash_str = hash_str + str(random.choice(options))

    obj_key = 'map-set-alpha/{}.txt'.format(hash_str)

    return obj_key


def get_tiles(sdk_session, bucket='galactic-map-tiles'):
    """Retrieve tiles from the Galactic Map Tiles inventory in S3
    """
    if sdk_session.get_credentials()._is_expired():
        sdk_session = create_storage_session()
        s3 = sdk_session.resource("s3")
    else:
        s3 = sdk_session.resource("s3")

    key      = build_key()
    response = s3.Object(bucket, key).get()
    raw_tile = response.get('Body').read()
    fmt_tile = raw_tile.replace('[', '')
    fmt_tile = fmt_tile.replace(']', '')

    map_tile = np.genfromtxt(StringIO(fmt_tile), dtype=int)

    return map_tile


def stitch_tiles(tile_list):
    """Stitch tiles together to make a map of the galaxy.
    """
    size           = len(tile_list[0])
    star_map       = np.zeros(shape=(size, size), dtype=np.int)
    star_map[4, 4] = "8" # Starting location of the Death Star
    dest_tile      = make_planet(size)

    for tile in tile_list:
        star_map = np.append(star_map, tile, axis=1)

    star_map = np.append(star_map, dest_tile, axis=1)

    return star_map


def make_planet(size):
    """Create a destination planet
    """
    planet_map = np.zeros(shape=(size, size), dtype=np.int)
    # planet_map[6][5] = u"\u03A6"
    # top:
    planet_map[5][1] = 1
    planet_map[6][1] = 1
    planet_map[7][1] = 1
    # bottom:
    planet_map[5][9] = 1
    planet_map[6][9] = 1
    planet_map[7][9] = 1
    # left:
    planet_map[3][4] = 1
    planet_map[3][5] = 1
    planet_map[3][6] = 1
    # right:
    planet_map[9][4] = 1
    planet_map[9][5] = 1
    planet_map[9][6] = 1

    # top left:
    planet_map[4][2] = 1
    planet_map[3][3] = 1
    # bottom left:
    planet_map[4][8] = 1
    planet_map[3][7] = 1
    # top right:
    planet_map[9][3] = 1
    planet_map[8][2] = 1
    # bottom right:
    planet_map[9][7] = 1
    planet_map[8][8] = 1

    return planet_map


def initialize_map_library(sdk_session, number):
    """Create and store the initial set of map tiles in S3. This should only be
    run once.
    """
    for i in range(number):
        tile = MapTile()
        tile.gen_celestial_object()
        tile.place_obstacles()
        tile.store(sdk_session)


if __name__ == '__main__':
    SESS = create_storage_session()
    # initialize_map_library(SESS, 2000)

    tile_lst = []
    for i in range(8):
        tile_lst.append(get_tiles(SESS))
    route_map = stitch_tiles(tile_lst)
    print(np.array_str(route_map, max_line_width=1000000))
