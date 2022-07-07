import common.square_grid as sq


def get_neighbors(offsets, i, length):
    length_offsets = len(offsets)
    for j in range(length_offsets):
        k = i + offsets[j]
        if 0 <= k < length:
            yield k, j


class ConstraintTable:

    def __init__(self, num_tiles, num_contraints):
        self.table = [[] for n in range(num_tiles)]

        for i in range(num_tiles):
            self.table[i] = [set() for j in range(num_contraints)]

        self.length = num_tiles

    def __len__(self):
        return self.length

    def get_table(self):
        return self.table

    def iter(self):
        length = len(self.table)

        for i in range(length):
            yield i, self.table[i]

    def read_constraints(self, reader):

        width, height = reader.input_shape().dim()
        offsets = sq.neighbor_indices(0, width)  # Left, Top, Right, Bottom as relative indices

        input_array = reader.input_as_id_array()
        length = len(input_array)

        for i in range(length):
            tile_id = input_array[i]
            if tile_id != -1:  # ignore none_tile
                for nbr_index, nbr_direction in get_neighbors(offsets, i, length):
                    nbr_id = input_array[nbr_index]
                    if nbr_id != -1:  # ignore none_tile
                        if nbr_id not in self.table[tile_id][nbr_direction]:
                            self.table[tile_id][nbr_direction].add(nbr_id)
