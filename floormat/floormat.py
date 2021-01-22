from floormat.tile import Tile
import pymongo
from pymongo import MongoClient

BASE_STATE = 1

database_client = MongoClient('localhost', 27017)

class Floormat(object):

    def __init__(self, row, column, ip=None, mac=None, wlan_id=None, ble_id=None):
        """
        :param row: int, must be greater than 0
        :param column: int, must be greater than 0
        """
        self.tiles = set()

        self.ip_address = ip
        self.wlan_id = wlan_id

        self.mac = mac
        self.ble_id = ble_id

        if row > 0 and column > 0:
            self.row = row
            self.column = column
            self.floormat = [[Tile(row_pos=j, col_pos=i) for j in range(self.row)] for i in range(self.column)]
        else:
            print("Ensure row and column are at least 1.")
            return

    def get_dimensions(self):
        """
        :return: (row, column) as a tuple
        """
        return self.row, self.column

    def get_floormat_states(self, key=0):
        """
        :param: key, defaulted to 0
                if key = 0, it returns the entire floormat with Tile objects.
                if key = 1, it returns the existing quantized weight values of the floormat.
                if key = 2, it returns the existing sentinel values of the floormat.

        :return: self.floormat, a 2-dimensional array of Tiles()
        """
        if not key:
            return self.floormat

        elif key == 1:
            statemat = []
            dims = self.get_dimensions()
            for i in range(dims[1]):
                statemat.append(list(map(lambda x: x.get_state(), self.floormat[i])))

            return statemat

        elif key == 2:
            statemat = []
            dims = self.get_dimensions()
            for i in range(dims[1]):
                statemat.append(list(map(lambda x: x.get_sentinel_value(), self.floormat[i])))

            return statemat
        else:
            print("Select between 0 (floor mat), 1 (state mat), 2 (sentinel_value mat)")
            return

    def activate_tile(self, i=None, j=None):
        if type(i) != int or type(j) != int:
            print("Please ensure i (column) and j (row) are integer inputs.")
            return
        elif i != None and j != None and i < self.column and j < self.row:
            self.tiles.add((i,j))

    def update_tile_state(self, tiles=None):
        """
        :param tiles: a data structure containing a tuple of (tile_pos, tile_state). If nothing is given, it will reinitialize every tile on the floormat.
        :return: None
        """
        dims = self.get_dimensions()
        if not tiles:
            print("Resetting tile states.")
            for i in range(dims[1]):
                for j in range(dims[0]):
                    self.floormat[i][j].change_state(BASE_STATE)

            print("Emptying active tile set.")
            self.tiles = {}
        else:
            for coords, state in tiles:
                if coords in self.tiles:
                    self.floormat[coords[0]][coords[1]].change_state(state)

    def find_clusters(self):
        """
        Generic floodfill algorithm to be used here, with values in dir to be changed during experimentation and calibration.
        Purpose is to find the number of clusters that may exist in a floormat.
        A floormat is essentially an implicit graph of Tiles that can have binary (sentinel_value) and non-binary (state) values.

        :return: (int) number of clusters
        """

        def floodfill(AM, r, c):
            """
            :param AM: self.floormat
            :param r:  index of row tile I want to call
            :param c:  index of column tile I want to call

            :return: 1 or 0

            floodfill(AM, r, c) is only called whenever the floor tile is being engaged. There are two ways to determine whether a tile is being engaged:
                1) tile.state > 1
                2) tile.sentinel_value = 1
            """
            dir = ((0, -1), (0, 1), (1, 0), (-1, 0))

            if r < 0 or r >= self.row or c < 0 or c >= self.column or not (AM[c][r].get_sentinel_value or AM[c][r].is_engaged()):
                return

            AM[c][r].change_sentinel_value(0)

            for d in dir:
                nx = r + d[1]
                ny = c + d[0]
                floodfill(AM, nx, ny)

            return 1

        clusters = 0
        dims = self.get_dimensions()
        for i in range(dims[1]):
            for j in range(dims[0]):
                if self.floormat[i][j].is_engaged() and self.floormat[i][j].get_sentinel_value():
                    row = self.floormat[i][j].get_pos()[1]
                    col = self.floormat[i][j].get_pos()[2]
                    clusters += floodfill(self.floormat, row, col)
        return clusters

    def distance_between_clusters(self):

        AM = self.get_floormat_states(key=1)
        
        pass