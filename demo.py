from floormat.floormat import Floormat


def demo_processFloormatData():
    
    test_cases = open("test_cases.txt", "rb")

    for test_case in test_cases:

        floormat = Floormat(row=4, column=2)
        dims = floormat.get_dimensions()
        m = dims[1]
        n = dims[0]
        tiles = set()

        test_case = list(map(lambda x: float(x), test_case.decode('utf-8').split('|')))
        mul = 0

        for i in range(m):
            for j in range(n):
                print("idx: {}, state: {}".format(mul*i+j, test_case[mul*i+j]))
                tiles.add(((i, j), test_case[mul*i+j]))
                floormat.activate_tile(i, j)

            mul += n

        floormat.update_tile_state(tiles)
        statemat = floormat.get_floormat_states(key=1)
        print(statemat)



if __name__ == "__main__":
    demo_processFloormatData()