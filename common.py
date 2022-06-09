# common functions for demo
import pygame as PG
import SquareGrid as SG
import SpriteSheet as SP


def scale_tiles(tile_dict, pxsize):
    for i in tile_dict:
        tile_dict[i] = PG.transform.scale(tile_dict[i], (pxsize, pxsize))


def process_overlap_input(filename, N):
    assert (N > 0)
    input_src = SP.SpriteSheet(filename)
    width, height = input_src.dim()
    images = []

    for j in range(height - (N - 1)):
        for i in range(width - (N - 1)):
            img = input_src.image_at(PG.Rect(i, j, N, N))
            images.append(img)

    return process_input_tiles(images, N)


def process_tile_input(width, height, pxsize, filename):
    input_img = SP.SpriteSheet(filename)
    pxwidth, pxheight = input_img.dim()
    assert (width * pxsize == pxwidth and height * pxsize == pxheight)
    input_tiles = []
    for i in range(height):
        for j in range(width):
            img = input_img.image_at((PG.Rect(j * pxsize, i * pxsize, pxsize, pxsize)))
            input_tiles.append(img)

    return process_input_tiles(input_tiles, pxsize)


# Removes duplicate tiles, assigns ids to tiles, counts weights for each tile
def process_input_tiles(tiles, pxsize):
    patdx = {}
    tiledx = {}
    tile_id = 0
    weights = []  # count the occurance of each image
    cdx = 0
    colormap = {}
    converted = [-1 for i in range(len(tiles))]  # convert input image to matrix with tile ids

    i = 0
    for tile in tiles:
        img_id = tuple_surf(tile, pxsize, pxsize)

        try:

            id = patdx[img_id]
            weights[id] += 1
            converted[i] = id

        except KeyError:

            patdx[img_id] = tile_id
            tiledx[tile_id] = tile
            weights.append(1)
            converted[i] = tile_id
            tile_id += 1

            for px in img_id:
                if px not in colormap:
                    colormap[px] = cdx
                    cdx += 1

        i += 1
    #  map to RGB
    for k in colormap.keys():
        colormap[k] = color_from_int(k)

    return patdx, tiledx, weights, converted, colormap


def compare_pixels(img_a, img_b, offset, commonxys, N):
    grid = SG.GridPos(N, N)

    match = True
    for xy in commonxys:
        wz = SG.sub_pos(xy, offset)
        pxa = img_a[grid.get_index(xy)]
        pxb = img_b[grid.get_index(wz)]
        match = match and pxa == pxb
    return match


def color_from_int(argb_int):
    blue = argb_int & 255
    green = (argb_int >> 8) & 255
    red = (argb_int >> 16) & 255
    alpha = (argb_int >> 24) & 255

    return red, green, blue, alpha


def tuple_surf(surf, width, height):
    pixels2d = PG.surfarray.pixels2d(surf)
    return tuple((pixels2d[j][i] for i in range(height) for j in range(width)))


def infer_rules(width, height, converted, num_tiles):

    grid = SG.GridPos(width, height)
    rules = init_rules(num_tiles, 4)
    directions = ((-1, 0), (0, -1), (1, 0), (0, 1))

    for i in range(len(converted)):
        tile_id = converted[i]

        for nb, dir in grid.get_neighbors(i, directions):
            nbr_tile = converted[nb]
            if nbr_tile not in rules[tile_id][dir]:
                rules[tile_id][dir].add(nbr_tile)

    return rules


def get_overlap_rules(patdx, intersections, N):
    num_nbrs = len(intersections)
    neighbors = tuple(x[0] for x in intersections)
    rules = init_rules(len(patdx), num_nbrs)

    # Compare overlapping pixels for each a,b pair.
    for img_a, i in patdx.items():
        for img_b, j in patdx.items():
            dir = 0
            for x in intersections:
                if compare_pixels(img_a, img_b, x[0], x[1], N):
                    rules[i][dir].add(j)
                dir += 1
    return rules


def init_rules(ntiles, nneighbors):
    rules = [[] for n in range(ntiles)]
    for i in range(ntiles):
        rules[i] = [set() for j in range(nneighbors)]
    return rules


def init_pygame(title, x_width, y_height):
    PG.init()
    screen = PG.display.set_mode((x_width, y_height))
    PG.display.set_caption(title)
    clock = PG.time.Clock()
    return screen, clock


def init_surface(width, height, color):
    s = PG.Surface((width, height))
    s = s.convert()
    s.fill(color)
    return s


def draw_wave(waveform, tile_dict, psize, canvas):
    length = waveform.length
    for i in range(length):
        state = waveform.get_states_index(i)[0]
        img = tile_dict[state]
        x, y = waveform.grid.get_pos(i)
        x, y = x * psize, y * psize
        canvas.blit(img, (x, y))


def draw_overlap(wave, N, colormap, pixeldx, canvas):

    width, height = wave.dim()
    for wh in range(height):
        for ww in range(width):
            i = wave.grid.get_index((ww, wh))
            if len(wave.wm[i]) > 1:
                pixel_color = (51, 51, 51)
                PG.draw.rect(canvas, pixel_color, PG.Rect(ww * 16, wh * 16, 16, 16))
            else:
                pat = pixeldx[wave.wm[i].states()[0]]
                pixel_color = colormap[pat[0]]
                PG.draw.rect(canvas, pixel_color, PG.Rect(ww * 16, wh * 16, 16, 16))


def draw_images(images, width, height, pxsize, canvas):
    num_images = len(images)
    gp = SG.GridPos(width, height)
    for i in range(num_images):
        x, y = gp.get_pos(i)
        x = x * pxsize * 2
        y = y * pxsize
        canvas.blit(images[i], (x, y))


def draw_converted(converted, tile_dict, width, height, pxsize, canvas):
    gp = SG.GridPos(width, height)
    num_imgs = len(converted)
    for i in range(num_imgs):
        x, y = gp.get_pos(i)
        x = x * pxsize
        y = y * pxsize
        tile_id = converted[i]
        img = tile_dict[tile_id]
        canvas.blit(img, (x, y))


def draw_grid(width, height, pixel_size, canvas):
    # draw the grid lines
    w, h = width, height
    y = h * pixel_size
    for i in range(0, w):
        x = i * pixel_size
        PG.draw.line(canvas, (0, 0, 0), (x, 0), (x, y))

    x = w * pixel_size
    for j in range(0, h):
        y = j * pixel_size
        PG.draw.line(canvas, (0, 0, 0), (0, y), (x, y))
