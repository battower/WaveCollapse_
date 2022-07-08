from math import floor, ceil, sqrt

# A butchered rewrite of square_grid, namely left-top orientation from right-bot, and  basic Rect class and such.

edge_length = 1


def add(a, b):
    x, y = a
    w, z = b
    return x + w, y + z


def sub(a, b):
    c = mult(b, -1)
    return add(a, c)


def mult(pos, c):
    x, y = pos
    return int(c * x), int(c * y)


def eq(a, b):
    x, y = a
    w, z = b
    return x == w and y == z

def len(a):
    x, y = a
    return x * y


def neighbours(x, y):
    """Returns the squares that share an edge with the given square"""
    return (x - 1, y), (x, y - 1), (x + 1, y), (x, y + 1)

def adjacent(x, y):
    return (x - 1, y), (x - 1, y - 1), (x, y - 1), (x + 1, y - 1), (x + 1, y), (x + 1, y + 1), (x, y + 1), (x - 1, y + 1)

def neighbor_indices(i, width):
    return i - 1, i - width, i + 1, i + width



class Rect:
    @staticmethod
    def from_shape(shape):
        w, h = shape
        return Rect(0, 0, w, h)

    def __init__(self, x, y, width, height):
        self._pos = (x, y)
        self._dim = (width, height)
        self.length = width * height

    def __str__(self):
        x, y = self._pos
        width, height = self._dim
        return 'sq.Rect' + str((x, y, width, height))

    def __len__(self):
        return self.length

    def is_square(self):
        return self._dim[0] == self._dim[1]

    def width(self):
        return self._dim[0]

    def height(self):
        return self._dim[1]

    def dim(self):
        return self._dim

    def set_pos(self, pos):
        self._pos = pos

    def pos(self):
        return self._pos

    def copy(self):
        x, y = self._pos
        width, height = self._dim
        return Rect(x, y, width, height)

    def get_border_xys(self):
        x, y = self._pos
        w, h = self._dim
        xys = set()
        lines = (((x, y), (x + w - 1, y)),
                 ((x + w - 1, y), (x + w - 1, y + h - 1)),
                 ((x + w - 1, y + h - 1), (x, y + h - 1)),
                 ((x, y + h - 1), (x, y)))

        for l in lines:
            x2, y2 = l[0]
            x1, y1 = l[1]

            for xy in square_line_intersect(x1, y1, x2, y2):
                xys.add(xy)

        return xys


def middle(rect):
    x, y = rect.pos()
    width, height = rect.dim()
    x2 = x + width
    y2 = y + height

    xCenter = (x + x2) / 2
    yCenter = (y + y2) / 2

    return pick_square(xCenter, yCenter)


def pick_square(x, y):
    """Returns the square that contains a given cartesian co-ordinate point"""
    return (
        floor(x / edge_length),
        floor(y / edge_length),
    )


def square_center(x, y):
    """Returns the center of a given square in cartesian co-ordinates"""
    return (x + 0.5) * edge_length, (y + 0.5) * edge_length


def rect_points(rect):
    x, y = rect.pos()
    width, height = rect.dim()
    for dy in range(height):
        for dx in range(width):
            yield x + dx, y + dy


def square_rect_intersect(x, y, width, height):
    """Returns the square that intersect the rectangle specified in cartesian co-ordinates"""
    minx = floor(x / edge_length)
    maxx = ceil((x + width) / edge_length)
    miny = floor(y / edge_length)
    maxy = ceil((y + height) / edge_length)

    for y in range(miny, maxy):
        for x in range(minx, maxx):
            yield x, y


def square_line_intersect(x1, y1, x2, y2):
    """Returns squares that intersect the line specified in cartesian co-ordinates"""
    x1 /= edge_length
    y1 /= edge_length
    x2 /= edge_length
    y2 /= edge_length
    dx = x2 - x1
    dy = y2 - y1
    x = floor(x1)
    y = floor(x2)
    stepx = 1 if dx > 0 else -1
    stepy = 1 if dy > 0 else -1
    tx = (x + int(dx >= 0) - x1) / dx if dx != 0 else float('inf')
    ty = (y + int(dy >= 0) - y1) / dy if dy != 0 else float('inf')
    idx = abs(1 / dx) if dx != 0 else float('inf')
    idy = abs(1 / dy) if dy != 0 else float('inf')

    yield (x, y)

    while True:
        if tx <= ty:
            if tx > 1: return
            x += stepx
            tx += idx
        else:
            if ty > 1: return
            y += stepy
            ty += idy

        yield (x, y)


"""Returns the squares in a shortest path from one square to another, staying as close to the straight line as 
    possible """


def square_line(x1, y1, x2, y2):
    (fx1, fy1) = square_center(x1, y1)
    (fx2, fy2) = square_center(x2, y2)
    return square_line_intersect(fx1, fy1, fx2, fy2)


"""Given a square and a rectangle, gives a linear position of the square.
    The index is an integer between zero and square_rect_size - 1.
    This is useful for array storage of rectangles.
    Returns None if the square is not in the rectangle.
    Equivalent to list(square_rect(...)).index((x, y))"""


def index(pos, rect):
    x, y = pos
    rect_x, rect_y = rect.pos()
    width, height = rect.dim()

    dx = x - rect_x
    dy = y - rect_y

    if dx < 0 or dx >= width or dy < 0 or dy >= height:
        return None
    return dx + dy * width


def indices_from(positions, rect):
    for pos in positions:
        i = index(pos, rect)
        if i is not None:
            yield i


"""Performs the inverse of square_rect_index
    Equivalent to list(square_rect(...))[index]"""


def deindex(index, rect):
    rect_x, rect_y = rect.pos()
    width, height = rect.dim()
    dx = index % width
    dy = int(index / width)
    assert dx >= 0 and dy < height
    return rect_x + dx, rect_y + dy


# Yields ( (a, b), ((x1, y1), (x2, y2), ...) representing the points in common for two intersecting N X N squares.
# (a, b) is the offset for the position of the second square.
# EXCLUDES the case when a = b = 0
def intersect_squares(N):
    for ay in range(-1 * N + 1, N):
        for ax in range(-1 * N + 1, N):
            if ax == 0 and ay == 0:
                continue
            else:
                xys = tuple((xy for xy in intersect((0, 0), (ax, ay), N)))
                yield (ax, ay), xys


#  Yields the points (k, j) in common for two N X N squares a and b.
def intersect(a, b, N):
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
