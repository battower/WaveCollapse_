import common.square_grid as sq
import pygame as pg


def draw_tiles(tiles, pos, shape, size, canvas):
    length = len(tiles)

    for i in range(length):

        tile_pos = sq.deindex(i, shape)
        tile_pos = sq.add(pos, tile_pos)
        tile_pos = sq.mult(tile_pos, size)

        canvas.blit(tiles[i], tile_pos)


def draw_wave(wave, pos, tile_size, tile_dict, canvas):
    tiles = [tile_dict[i] for i in wave.one_or_none_array()]
    draw_tiles(tiles, pos, wave.shape, tile_size, canvas)


def draw_wave_list(waves, pos, shape, tile_size, tile_dict, canvas):
    width, height = waves[0].shape.dim()
    new_pos = pos
    for i in range(len(waves)):
        draw_wave(waves[i], new_pos, tile_size, tile_dict, canvas)

        if i % width == width - 1:
            x, y = pos[0], new_pos[1] + height + 1
            new_pos = (x, y)
        else:
            new_pos = sq.add(new_pos, (width + 1, 0))


def draw_wave_list_foo(waves, pos, shape, tile_size, tile_dict, canvas):
    width, height = waves[0].shape.dim()

    new_pos = sq.add(pos, (13, 0))
    draw_wave(waves[0], new_pos, tile_size, tile_dict, canvas)

    new_pos = sq.add(pos, (0, 6))
    draw_wave(waves[1], new_pos, tile_size, tile_dict, canvas)

    new_pos = sq.add(pos, (26, 6))
    draw_wave(waves[2], new_pos, tile_size, tile_dict, canvas)

    new_pos = sq.add(pos, (13, 13))
    draw_wave(waves[3], new_pos, tile_size, tile_dict, canvas)



def draw_grid(shape, pixel_size, canvas):

    w, h = shape.dim()
    y = h * pixel_size

    for i in range(0, w):
        x = i * pixel_size
        pg.draw.line(canvas, (0, 0, 0), (x, 0), (x, y))

    x = w * pixel_size
    for j in range(0, h):
        y = j * pixel_size
        pg.draw.line(canvas, (0, 0, 0), (0, y), (x, y))


def draw_tile_dict(images, pos, shape, size, canvas):
    length = len(images)
    array_rect = shape

    for i in range(length):
        img_pos = sq.deindex(i, array_rect)
        img_pos = sq.add(pos, img_pos)
        img_pos = sq.mult(img_pos, size)

        x, y = img_pos
        x *= 2
        canvas.blit(images[i], (x, y))
