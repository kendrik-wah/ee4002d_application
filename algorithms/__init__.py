import math
import copy

from floormat.floormat import Floormat
from interface.ble_peripheral import blePeripheral
from sklearn.cluster import KMeans, MiniBatchKMeans, SpectralClustering, SpectralBiclustering, SpectralCoclustering, OPTICS

"""
Compare accuracies for three to four algorithms:
	1) KMeans (normal KMeans and MiniBatchKMeans) ==> elbow and silhouette
	2) Spectral Clustering
	3) OPTICS
	
"""

def getSnapshot(peripheral, floormat, rowCnt):

    row = [peripheral.getDateTime()]
    statemat = floormat.get_floormat_states(key=1)
    toSaveData = ""
    
    for i in range(len(statemat)):
        toSaveData += ','.join(list(map(lambda x: str(x), statemat[i])))
        
        if i != rowCnt:
            toSaveData += ','
    
    return [peripheral.getDateTime(), toSaveData]


def createHeatMap(statemat, weightMap, r, c):
    
    heatmap = copy.deepcopy(statemat)
    for i in range(r):
        for j in range(c):
            for key, val in weightMap.items():
                if heatmap[i][j] <= 0:
                    heatmap[i][j] = val["colour"]
                    break

                elif val["min"] <= heatmap[i][j] <= val["max"]:
                    heatmap[i][j] = val["colour"]
                    break

    return heatmap


four_sided_dirs = ((0, -1), (0, 1), (1, 0), (-1, 0))
eight_sided_dirs = ((0, -1), (0, 1), (1, 0), (-1, 0), (-1,-1), (-1,1), (1,-1), (1,1))


def get_clustered_points(data):

    m = len(data)
    n = len(data[0])

    seen = set()
    clusters = dict()

    for i in range(m):
        for j in range(n):

            if data[i][j] != 1:

                points = set()
                idx = data[i][j]
                stk = [(i, j)]

                if idx not in clusters:
                    clusters[idx] = []

                while stk:
                    ci, cj = stk.pop()

                    seen.add((ci, cj))
                    points.add((ci, cj))

                    for di, dj in eight_sided_dirs:
                        ni = ci+di
                        nj = cj+dj
                        
                        if 0 <= ni < m and 0 <= nj < n and data[ni][nj] == idx and (ni, nj) not in seen:
                            stk.append((ni, nj))

                clusters[idx].append(points)

    return clusters
