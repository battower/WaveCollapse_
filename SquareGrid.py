import random

#  Basic methods for handling (x, y) positions and indices of a 2d grid.


#  Returns the sum of (x, y) and (w,z)
def add_pos(a, b):
    x, y = a
    w, z = b
    return x + w, y + z


# Returns difference (x, y) and (w, z)
def sub_pos(a, b):
    c = mult_sclr(-1, b)
    return add_pos(a, c)


# Returns  C * (x, y)
def mult_sclr(c, a):
    x, y = a
    return c * x, c * y


# Yields ( (a, b), ((x1, y1), (x2, y2), ...) representing the points in common for two intersecting N X N squares.
# (a, b) is the offset for the position of the second square.
# EXCLUDES the case when a = b = 0
def intersections(N):
    for ay in range(-1 * N + 1, N):
        for ax in range(-1 * N + 1, N):
            if ax == 0 and ay == 0:
                continue
            else:
                xys = tuple((xy for xy in intersect_squares((0, 0), (ax, ay), N)))
                yield (ax, ay), xys


#  Yields the points (k, j) in common for two N X N squares a and b.
def intersect_squares(a, b, N):

    ax, ay = a
    bx, by = b
    width, height = N, N
    xmin = min(ax, bx)
    ymin = min(ay, by)

    for j in range(ymin, ymin + height + 1):
        for k in range(xmin, xmin + width + 1):
            if ax <= k < ax + width and bx <= k < bx + width:
                if ay <= j < ay + height and by <= j < by + height:
                    yield k, j


#  Basic class for mapping indices to positions for a grid of dimensions width, and height.
class GridPos:

    def __init__(self, width, height):
        self._dim = (width, height)
        self.length = width * height

    def dim(self):
        return self._dim

    # returns a random index
    def random_index(self):
        i = random.randint(0, self.length - 1)
        return i

    # Returns the index of position (x, y)
    def get_index(self, pos):
        x, y = pos
        return y * self._dim[0] + x

    # Returns the position (x, y) for an grid element given by index
    def get_pos(self, index):
        w, h = self.dim()
        x, y = index % w, int(index / w)
        return x, y

    # Yeilds the sequence of indices for wavelets to the left, top, right and bottom adjacent to the wavelet at
    # pos (x,y)
    def get_neighbors_from_pos(self, pos):
        nbs = ((-1, 0), (0, -1), (1, 0), (0, 1))
        for j in range(4):
            s = add_pos(nbs[j], pos)
            if self.inbounds(s):
                yield self.get_index(s), j

    # Yeilds the sequence of (x, y) co ordinates to the left, top, right and bottom adjacent cells/tiles
    # for element at given index
    def get_neighbors(self, index):
        return self.get_neighbors_from_pos(self.get_pos(index))

    # Returns True/False if (x, y) is within the boundries of the Grid
    def inbounds(self, a):
        x, y = a
        if x < 0:
            return False
        if x > self._dim[0] - 1:
            return False
        if y < 0:
            return False
        if y > self._dim[1] - 1:
            return False

        return True
