import pymongo
from pymongo import MongoClient

database_client = MongoClient('localhost', 27017)

BASIC_STATE = 1

class Tile(object):

    """
    Basic floor tile, where multiple Tile objects will form a floor mat. A floormat of 1x1 is essentially a tile.
    Only attribute is self.value

        self.value (int) ==> state of floor tile, range of value = [1, 8], where 1 is the basic state
    """

    def __init__(self, position=None, row_pos=None, col_pos=None):
        """
        :param position: (int) the user-defined index of the tile in the floormat.
        :param row_pos: (int) the row position of the tile in the virtual floormat.
        :param col_pos: (int) the column position of the tile in the virtual floormat.

        :attr self.position: refer to :param position
        :attr self.row_pos: refer to :param row_pos
        :attr self.col_pos: refer to :param col_pos
        :attr self.state: the exact engagement state of the floor tile.
        :attr self.sentinel_value: used for search algorithms to denote whether tile is being engaged/ cluster detection/ etc.

        """
        self.position = position
        self.row_pos = row_pos
        self.col_pos = col_pos
        self.state = BASIC_STATE
        self.sentinel_value = 0

    """
    Methods related to the state of the floor tile.
    """
    def get_state(self):
        return self.state

    def is_engaged(self):
        return self.get_state() > 1

    def get_sentinel_value(self):
        return self.sentinel_value

    def change_state(self, val):
        if val < 1:
            self.state = max(val, BASIC_STATE)
        else:
            self.state = val

        if val > 1:
            self.change_sentinel_value(1)
        else:
            self.change_sentinel_value(0)

    def change_sentinel_value(self, sen_val):
        self.sentinel_value = sen_val

    """
    Methods related to the positions of the floor tile. Such positions include index, row and column.
    """
    def get_pos(self):
        return self.position, self.row_pos, self.col_pos

    def set_position(self, pos):
        self.position = pos