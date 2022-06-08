import pygame as PG
from pygame.locals import *
import SquareGrid as SG
import SpriteSheet as SP
import SimpleTiles as ST
import Wave as W


def main():
    screen, clock = init_pygame('Simple Tile', 900, 768)
    canvas = init_surface(768, 768, (51, 51, 51))
    pxsize = 24

    patdx, tiledx, weights, converted_input = process_input_image(24, 14, 24, 'world/roads_and_trees2.png')

    # Balance the weights abit
    weights[0] = 1
    weights[2] = 24
    wavelet = W.Wavelet({i: weights[i] for i in range(len(weights))})

    rules = infer_rules(24, 14, converted_input, len(tiledx))
    scale_tiles(tiledx, pxsize)
    while True:

        wave = ST.SimpleTiles(32, 32, wavelet, rules)
        startdx = wave.random_index()
        startstate = wave.random_state(startdx)

        for event in PG.event.get():
            if event.type == QUIT:
                return

        wave.solve(startdx, startstate)
        draw_wave(wave, tiledx, pxsize, canvas)

        screen.blit(canvas, (0, 0))
        PG.display.flip()


def scale_tiles(tile_dict, pxsize):
    for i in tile_dict:
        tile_dict[i] = PG.transform.scale(tile_dict[i], (pxsize, pxsize))


def process_input_image(width, height, pxsize, filename):
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
        i += 1

    return patdx, tiledx, weights, converted


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

    for i in range(len(converted)):
        tile_id = converted[i]

        for nb, dir in grid.get_neighbors(i):
            nbr_tile = converted[nb]
            if nbr_tile not in rules[tile_id][dir]:
                rules[tile_id][dir].add(nbr_tile)

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






if __name__ == '__main__': main()
