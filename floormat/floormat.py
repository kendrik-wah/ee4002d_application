from tile import Tile

class Floormat(object):

    def __init__(self, row, column):
        """
        :param row: int, must be greater than 0
        :param column: int, must be greater than 0
        """
        self.tiles = {}

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
        return (self.row, self.column)

    def set_dimensions(self, row, column):
        """
        :param row: int, must be greater than 0
        :param column: int, must be greater than 0
        :return: None
        """
        if not row or not column:
            print("Ensure row and column are at least 1.")
            return
        elif row > 0 and column > 0:
            self.row = row
            self.column = column

    def get_floormat_states(self, key=0):
        """
        :return: self.floormat, a 2-dimensional array of Tiles()
        """
        if not key:
            return self.floormat
        elif key == 1:
            statemat = []
            dims = self.get_dimensions()
            for i in range(dims[1]):
                row = []
                for j in range(dims[0]):
                    row.append(self.floormat[i][j].get_state())

                statemat.append(row)
            return statemat
        elif key == 2:
            statemat = []
            dims = self.get_dimensions()
            for i in range(dims[1]):
                row = []
                for j in range(dims[0]):
                    row.append(self.floormat[i][j].get_sentinel_value())

                statemat.append(row)
            return statemat
        else:
            print("Select between 0 (floor mat), 1 (state mat), 2 (sentinel_value mat)")
            return

    def set_tile_position(self, position, row_pos, col_pos):
        """
        :param position: the position_id of the tile on the floormat (physical, to be set)
        :param row_pos: the row position of the tile on the floormat
        :param col_pos: the column position of the tile on the floormat
        :return: None
        """
        dims = self.get_dimensions
        if row_pos >= dims[0] or col_pos >= dims[1]:
            if row_pos >= dims[0]:
                print("Input row_pos={} is greater than row_dim={} of floormat".format(row_pos, dims[0]))
            if col_pos >= dims[1]:
                print("Input col_pos={} is greater than col_dim={} of floormat".format(col_pos, dims[1]))
            return
        else:
            self.floormat[col_pos][row_pos].set_position(position)
            self.tiles[position] = self.floormat[col_pos][row_pos]
            return

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
                    self.floormat.change_state(1)

            print("Emptying active tiles hashmap.")
            self.tiles = {}
        else:
            for pos, state in tiles:
                self.tiles[pos].change_state(state)

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
                if self.floormat[j][i].is_engaged() and self.floormat[j][i].get_sentinel_value():
                    row = self.floormat[j][i].get_pos()[1]
                    col = self.floormat[j][i].get_pos()[2]
                    clusters += floodfill(self.floormat, row, col)

        return clusters

    def distance_between_clusters(self):
        pass