# Maps tiles from constraints_img, as being either impassable (True) or not (False).
def get_block_dict():
    wall = 1
    empty = 0
    block_array = [wall, empty, wall, empty, empty, empty, empty, wall, wall, empty, wall, empty, wall, wall, empty,
                   empty, empty, wall, empty, wall, empty, empty, empty, empty]
    block_dict = {}
    for i in range(len(block_array)):
        block_dict[i] = block_array[i]

    block_dict[-1] = wall
    return block_dict


def one_or_none_to_blocks(one_or_none_array, block_dict):
    wall_map = [block_dict[i] for i in one_or_none_array]
    return wall_map


def solve_wave(wave, rand=False):
    if rand:
        index = wave.random_index()
    else:
        index = wave.next_index()
        if index == -1:
            print('index: ' + str(index))
            return False
    res = False

    for state in wave.next_state(index):
        if wave.solve(index, state):
            res = True
            break
    return res


def entangle_list(wave, wave_list, xys, wzs, keys):
    index = 0
    for offset in keys:
        wave_b = wave_list[index]

        coords = xys[offset]
        data = wave.copy_from(coords)

        coords = wzs[offset]
        wave_b.write_to(coords, data)

        index += 1


def entangle(wave_a, wave_b, xy_coords, wz_coords):
    data = wave_a.copy_from(xy_coords)
    wave_b.write_to(wz_coords, data)
