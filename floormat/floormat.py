from floormat.tile import Tile

import numpy as np

import pymongo
from pymongo import MongoClient

BASE_STATE = 0

database_client = MongoClient('localhost', 27017)

def power_func(x, a, b, c):
    return a*np.power(x, b) + c

class Floormat(object):

    def __init__(self, row, column, ip=None, mac=None, wlan_id=None, ble_id=None, tileFactor=None):
        """
        :param row: int, must be greater than 0
        :param column: int, must be greater than 0
        """
        self.tiles = set()

        self.ip_address = ip
        self.wlan_id = wlan_id

        self.mac = mac
        self.ble_id = ble_id
        
        self.isTared = False
        self.completeTared = False
        
        self.isCal = False
        self.completeCal = False
        
        self.tileFactor = tileFactor

        if row > 0 and column > 0:
            self.row = row
            self.column = column
            self.floormat = [[Tile(row_pos=j, col_pos=i) for j in range(self.column)] for i in range(self.row)]
        else:
            print("Ensure row and column are at least 1.")
            return

    def get_dimensions(self):
        """
        :return: (row, column) as a tuple
        """
        return self.row, self.column
        
    def calculateWeight(self, tileNo, x):
        if not self.tileFactor:
            return x
        
        a = self.tileFactor[tileNo]["a"]
        b = self.tileFactor[tileNo]["b"]
        c = self.tileFactor[tileNo]["c"]
        return power_func(x, a, b, c)

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
            for i in range(dims[0]):
                matRow = []
                for j in range(dims[1]):
                    matRow.append(self.calculateWeight(i+j+1, self.floormat[i][j].get_state()))
                statemat.append(matRow)
                
            return statemat

        elif key == 2:
            statemat = []
            dims = self.get_dimensions()
            for i in range(dims[0]):
                statemat.append(list(map(lambda x: x.get_sentinel_value(), self.floormat[i])))

            return statemat
        else:
            print("Select between 0 (floor mat), 1 (state mat), 2 (sentinel_value mat)")
            return

    def activate_tile(self, i=None, j=None):
        if type(i) != int or type(j) != int:
            print("Please ensure i (column) and j (row) are integer inputs.")
            return
        elif i != None and j != None and j < self.column and i < self.row:
            self.tiles.add((i,j))

    def update_tile_state(self, tiles=None):
        """
        :param tiles: a data structure containing a tuple of (tile_pos, tile_state). If nothing is given, it will reinitialize every tile on the floormat.
        :return: None
        """
        dims = self.get_dimensions()
        
        if not tiles:
            print("Resetting tile states.")
            for i in range(dims[0]):
                for j in range(dims[1]):
                    self.floormat[i][j].change_state(BASE_STATE)

            print("Emptying active tile set.")
            self.tiles = {}
        else:
            for coords, state in tiles:
                if coords in self.tiles:
                    self.floormat[coords[0]][coords[1]].change_state(state)                
    
    def tareStatus(self):
        return (self.isTared, self.completeTared)
        
    def set_isTared(self, flag):
        self.isTared = flag
    
    def set_completeTared(self, flag):
        self.completeTared = flag
        
    def calStatus(self):
        return (self.isCal, self.completeCal)
        
    def set_isCal(self, flag):
        self.isCal = flag
    
    def set_completeCal(self, flag):
        self.completeCal = flag
    
