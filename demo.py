import json

from floormat.floormat import Floormat


def demo_acquireSensorClassMapping():

    with open("weightMapping.json", "r") as json_file:
        loadedData = json.load(json_file)

    weightMapping = dict()
    for key, val in loadedData.items():
        weightMapping[int(key)] = val
    
    return weightMapping
    
def demo_processFloormatData():
    
    test_cases = open("test_cases.txt", "rb")
    weightMap = demo_acquireSensorClassMapping()

    for test_case in test_cases:

        floormat = Floormat(row=2, column=2)
        dims = floormat.get_dimensions()
        m = dims[1]
        n = dims[0]
        tiles = set()

        test_case = list(map(lambda x: float(x), test_case.decode('utf-8').split('|')))
        mul = 0

        for i in range(m):
            for j in range(n):
                tiles.add(((i, j), test_case[mul*i+j]))
                floormat.activate_tile(i, j)

            mul += n

        floormat.update_tile_state(tiles)
        statemat = floormat.get_floormat_states(key=1)

        print(weightMap)

        for i in range(m):
            for j in range(n):
                for key, val in weightMap.items():
                    if statemat[i][j] <= 0:
                        statemat[i][j] = val["colour"]
                        break

                    elif val["min"] <= statemat[i][j] <= val["max"]:
                        statemat[i][j] = val["colour"]
                        break

        for row in statemat:
            print(row)
        print()


if __name__ == "__main__":

    # weightMap = demo_acquireSensorClassMapping()
    # print(weightMap)
    demo_processFloormatData()