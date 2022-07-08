import math
import random
import common.square_grid as sq
import common.debugr as dbug

import time

#  Wave Form Collapse Simple Tile Constraint Propagation:

# Returns the Shannon entropy of from the based on the weights of the avialable choices
def entropy(states_weights):
    if isinstance(states_weights, int) or len(states_weights) == 1:
        return 0

    ws = sum(states_weights.values())
    return math.log(ws) - sum(map(lambda x: x * math.log(x), states_weights.values())) / ws


#  Randomly choose random key from given the dictionary[key] = weight
def choose(state_dict):
    s, w = list(state_dict.keys()), list(state_dict.values())
    elem = random.choices(s, weights=w)[0]
    return elem


class Wave:

    #  Initialize the Wave
    def __init__(self, shape, propagator, initial_state):
        self.start_time = None
        self.shape = shape
        self.prop = propagator

        if isinstance(initial_state, list):
            assert len(shape) == len(initial_state)
            self.wm = [i.copy() for i in initial_state]
            self.fuzziness = [entropy(i) for i in initial_state]
        else:
            self.wm = [initial_state.copy() for i in range(len(shape))]
            # entropy matrix
            e = entropy(initial_state)
            self.fuzziness = [e for i in range(len(shape))]

        # backtrack
        self.bk_stack = []
        self.bk_cur = []
        self.reject_count = 0
        self.max_rejects = float('inf')
        self.abort = False
        self.pause = False
        self.timer = 0.0
        self.index = -1
        self.state = -1

    #  copy the given wave
    def read(self, wave):
        for i in range(len(self.shape)):
            self.wm[i] = wave.wm[i].copy()
        self.calc_entropy()

        self.bk_stack = wave.bk_stack.copy()
        self.reject_count = wave.reject_count
        self.max_rejects = wave.max_rejects
        self.abort = wave.abort

    # return a copy of this object
    def copy(self):
        state = [i.copy() for i in self.wm]
        copy = Wave(self.shape, self.prop, state)
        return copy

    def one_or_none_array(self):
        temp = []
        for i in range(len(self.shape)):
            if self.fuzziness[i] == 0:  # if state of this tile is certain append the state id.
                temp.append(next(iter(self.wm[i])))
            else:
                temp.append(-1)  # append the uncertain id

        return temp

    # yields copies of the tile states located at the given (x, y) co ords
    def copy_from(self, positions):
        for i in sq.indices_from(positions, self.shape):
            yield self.wm[i].copy()

    # sets the tile states at the given (x, y) co ords to the given state
    def write_to(self, positions, state):
        for i in sq.indices_from(positions, self.shape):
            try:
                self.wm[i] = next(state)
                self.fuzziness[i] = entropy(self.wm[i])
            except StopIteration:
                print('more data expected for Wave.write_to().  Expected length: ' + str(len(positions)))

    # Calculate the entropies of each wavelet
    def calc_entropy(self):
        for i in range(len(self.shape)):
            self.fuzziness[i] = entropy(self.wm[i])

    #  Returns True/False
    def no_entropy(self):
        if all([v == 0 for v in self.fuzziness]):  # no uncertainty at any index.
            return True
        return False

    # Returns the minimun nonzero entropy value found.
    def min_entropy(self):
        m = float("inf")
        for i in range(len(self.shape)):
            if 0 < self.fuzziness[i] < m:
                m = self.fuzziness[i]
        return m

    def random_index(self):
        return random.randint(0, len(self.shape) - 1)

    def next_index(self):
        e = self.min_entropy()  # May be 'inf'
        if e < float('inf'):
            # return position of first occurance of min e.
            for i in range(len(self.shape)):
                if self.fuzziness[i] == e:
                    return i
            # not found.
        return -1

    def next_state(self, index):
        copy = {s: w for s, w in self.wm[index].items()}
        for i in range(len(copy)):
            c = choose(copy)
            del copy[c]
            yield c

    # returns true if constraints violated
    def reject(self, index, state):
        res, modified = self.prop.propagate_constraints(index, state, self.shape, self.wm)
        self.bk_stack.append(modified)
        self.bk_cur.append((index, state))

        return not res

    def solved(self):
        self.calc_entropy()
        return self.no_entropy()

    # Find a state of the Wave where each wavlet is in a single state consistent with the constraints
    # Solve for wavelet at given position having the given state.
    def solve(self, index, state):

        if self.abort:
            return False

        #print('reject_count: ' + str(self.reject_count))

        # Propagate change of state starting at index.  Reject if violates constraints
        if self.reject(index, state):
            self.backtrack()
            return False

        if self.solved():
            return True

        next_i = self.next_index()

        for next_state in self.next_state(next_i):
            if self.solve(next_i, next_state):  # solution found.
                return True

        self.reject_count += 1

        self.backtrack()
        return False

    def set_max_rejects(self, max):
        self.max_rejects = max

    def backtrack(self):
        if self.reject_count > self.max_rejects:
            self.abort = True
        elif not self.abort:
            modified = self.bk_stack.pop()
            for i in modified:
                self.wm[i] = modified[i].copy()

    def backjump(self):
        pass

