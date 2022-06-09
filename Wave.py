import math
import random
import SquareGrid


#  Classes implementing WFC


#  Randomly choose a element from given a dictionary of weighted choices.
def choose(state_dict):
    s, w = list(state_dict.keys()), list(state_dict.values())
    elem = random.choices(s, weights=w)[0]
    return elem


# Returns the Shannon entropy of the wavelet
def entropy(wavelet):
    state_space = wavelet.get_dict()

    if isinstance(state_space, int) or len(state_space) == 1:
        return 0
    ws = sum(state_space.values())

    return math.log(ws) - sum(map(lambda x: x * math.log(x), state_space.values())) / ws


#  Element of Wave Matrix
class Wavelet:

    #  states_weights: is a dictionary possible states and the weights of each
    def __init__(self, states_weights):
        self.states_weights = states_weights

    def __len__(self):
        return len(self.states_weights)

    def __str__(self):
        states = str(self.states_weights.items())
        return str(states)

    def random_state(self):
        return choose(self.states_weights)

    def copy(self):
        sw = {k: v for k, v in self.states_weights.items()}
        return Wavelet(sw)

    # Removes state s from the wavelet if so doing doesn't empty it.
    # Returns False only if state s is the only remaining state.
    def constrain_state(self, s):
        if s in self.states_weights:
            if len(self) > 1:
                del self.states_weights[s]
                return True
            return False
        return True

    # yeilds a random sequence of states based on the weights for each state.
    def generate_choices(self):
        copy = {k: v for k, v in self.states_weights.items()}
        n = len(copy)
        for i in range(n):
            c = choose(copy)
            del copy[c]
            yield c

    def states(self):
        return list(self.states_weights.keys())

    def weights(self):
        return list(self.states_weights.values())

    def get_dict(self):
        return self.states_weights


# Virtual Class.
# Requires implementation of method: check_constraints(pos, state)
# Implements WFC Adjacency Constraint Propagation with Backtracking
class Wave:

    #  Initialize the Wave matrix with the given wavelet and dimensions
    def __init__(self, width, height, wavelet):
        self.grid = SquareGrid.GridPos(width, height)
        self._dim = self.grid.dim()
        self.length = self.grid.length

        # wave matrix
        self.wm = [wavelet.copy() for i in range(self.length)]

        # entropy matrix
        e = entropy(wavelet)
        self.fuzziness = [e for i in range(self.length)]

        # back track stack
        self.stack = {}

    def dim(self):
        return self._dim

    def random_index(self):
        return self.grid.random_index()

    #  Return a random state from the wavelet at position index
    def random_state(self, index):
        try:
            return self.wm[index].random_state()
        except IndexError:
            print('Index error: ' + str(index))

    # Return the wavelet at index i
    def get_wavelet(self, i):
        return self.wm[i]

    # Return the list of states for the wavelet at given index
    def get_states_index(self, index):
        return self.wm[index].states()

    # Calculate the entropies of each wavelet
    def calc_entropy(self):
        for i in range(self.length):
            self.fuzziness[i] = entropy(self.wm[i])

    #  Returns the index of wavelet with fewest choices remaining
    def fewest_choices(self):
        e = self.min_entropy()  # May be 'inf'
        if e < float('inf'):
            # return position of first occurance.
            for i in range(self.length):
                if self.fuzziness[i] == e:
                    return i
            # not found.
        return -1

    # Returns the minimun nonzero entropy value found. Entropy indices and position indices not equal.
    def min_entropy(self):
        m = float("inf")
        for i in range(self.length):
            if 0 < self.fuzziness[i] < m:
                m = self.fuzziness[i]
        return m

    # Find a state of the Wave where each wavlet is in a single state consistent with the constraints
    # Solve for wavelet at given position having the given state.
    def solve(self, index, state):

        # Add the current state of the grid to the stack for backtracking
        self.copy_matrix(index)

        # Set wavelet state
        self.wm[index] = Wavelet({state: 1})

        # Propagate change of state starting at index.  Reject if violates constraints
        if self.reject(index):
            self.restore_matrix(index)  # Restore Wave to previous state.
            return False

        # Check if this is a solution
        self.calc_entropy()
        if self.no_entropy():  # Solved.
            return True

        #  Continue searching.
        fpos = self.fewest_choices()  # choose location with fewest choices, then check each.
        guesses = self.get_wavelet(fpos).generate_choices()
        for g in guesses:
            if self.solve(fpos, g):  # solution found.
                return True

        # All paths extending from here are inconsistent.
        self.restore_matrix(index)
        return False

    #  Returns True/False
    def no_entropy(self):
        if all([v == 0 for v in self.fuzziness]):  # no uncertainty.
            return True
        return False  # some uncertainty.

    # Returns a list of states randomized by likleyhood weight for the wavelet at given index.
    def get_guesses(self, i):
        if i != -1:
            guesses = self.get_wavelet(i).generate_choices()
            return len(guesses), guesses
        return -1, None  # No more guesses for this position.

    # Returns True if constraint violation
    def reject(self, index):
        return not self.check_constraints(index)  # implement check_constraints in subclasss

    # Validates the current state of the Wave state.
    def validate(self):
        self.calc_entropy()
        if not self.no_entropy():  # Not all elements in single state.
            return False

        #  Ensure each element satisfies all constraints.
        for i in range(self.length):
            if not self.check_constraints(i):
                return False

        # Current state of Wave is a solution.
        return True

    # Copies the current state of the Grid to stack dictionary.
    # Needs improvement, storing the entire matrix is unnecessary but is easy.
    def copy_matrix(self, key):
        copy = [self.wm[i].copy() for i in range(self.length)]  # copy state as list.
        self.stack[key] = copy  # and add to stack.

    # Restores state of grid with key
    def restore_matrix(self, key):
        try:
            copy = self.stack[key]
            for i in range(self.length):  # Restore
                self.wm[i] = copy[i].copy()
            del self.stack[key]  # Remove from stack.
        except KeyError:
            raise KeyError
