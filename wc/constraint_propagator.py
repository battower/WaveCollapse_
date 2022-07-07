import common.square_grid as sq


class ConstraintPropagator:

    def __init__(self, constraints_table):
        self.constraints_table = constraints_table
        self.constraints = constraints_table.get_table()

    def propagate_constraints(self, index, state, shape, wave_array):
        #print('\npropagate...')
        length = len(shape)
        neighbors = sq.neighbor_indices(0, shape.width())

        to_visit = [index]
        visited = [index]
        modified = {index: wave_array[index].copy()}

        wave_array[index] = {state: 1}

        while to_visit:

            i = to_visit.pop()
            states = set(wave_array[i].keys())
            #print('propagate: \ti ' + str(i))
            for nbr, rules in self.neighbors_rules(i, neighbors, states, length):
                #print('\t\tnbr, rules: ' + str((nbr, rules)))
                nbr_states = set(wave_array[nbr].keys())
                if nbr not in visited:
                    #nbr_states = set(wave_array[nbr].keys())
                    #print('\t\tnbr state: ' + str(nbr_states))
                    #print('\t\tis subset: ' + str(nbr_states.issubset(rules)))
                    if not nbr_states.issubset(rules):
                        allowed_states = rules & nbr_states
                        disallowed_states = (rules | nbr_states) - allowed_states

                        #print('\t\t\tallowed: ' + str(allowed_states))
                        #print('\t\t\tdisallowed: ' + str(disallowed_states))
                        if len(allowed_states) == 0:  # neighbor has no valid states.
                            #print('\t\t\tnbr NOT OK\n')
                            return False, modified

                        # add nb to modified list copy its data
                        modified[nbr] = wave_array[nbr].copy()

                        #  Remove invalid states from neighbor.
                        temp = {s: wave_array[nbr][s] for s in allowed_states}
                        wave_array[nbr] = temp

                        #print('\t\t\tnbr state modified.')

                        to_visit.append(nbr)

                    #print('\t\tnbr OK\n')
                    visited.append(nbr)
                else:
                    #print('\t\t already visited.  state: ' + str(nbr_states))
                    pass

        return True, modified

    def neighbors_rules(self, index, neighbors, states, length):
        table = self.constraints
        for direction in range(len(neighbors)):
            nbr = index + neighbors[direction]
            if 0 <= nbr < length:
                yield nbr, set.union(*[table[state][direction] for state in states])
