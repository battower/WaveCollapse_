import Wave as W


class SimpleTiles(W.Wave):

    def __init__(self, width, height, wavelet, rules, neighbors):
        super().__init__(width, height, wavelet)
        self.weights = wavelet.weights()
        self.rules = rules
        self.neighbors = neighbors

    # Propagate constraint validation starting from index.
    def check_constraints(self, index):

        to_visit = [index]
        visited = [index]

        while to_visit:  # places to go

            i = to_visit.pop()

            for nb, direction in self.get_neighbors(i):
                if nb not in visited:

                    #  Get constraints for each state in wavelet i
                    rules = set.union(*[self.rules[state][direction] for state in self.wm[i].states()])

                    # Check if nb has any consistent states
                    if not set(self.wm[nb].states()).issubset(rules):
                        allowed_states = rules & set(self.wm[nb].states())
                        if len(allowed_states) == 0:  # neighbor has no valid states.
                            return False

                        #  Remove invalid states from neighbor.
                        self.wm[nb] = W.Wavelet({s: self.weights[s] for s in allowed_states})

                        to_visit.append(nb)  # propagate the change.
                    visited.append(nb)
        return True  # Constraints so-far satisfied.

    def get_neighbors(self, index):
        return self.grid.get_neighbors(index, self.neighbors)
