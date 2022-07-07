import pygame as pg


def read_input(width, height, tile_size, image_input):
    tiles = []
    size = tile_size

    for i in range(height):
        for j in range(width):
            tile_img = image_input.image_at(pg.Rect(j * size, i * size, size, size))
            tiles.append(tile_img)

    return tiles


def get_pixel_tuple(image, width, height):
    pixels = pg.surfarray.pixels2d(image)
    return tuple((pixels[j][i] for i in range(height) for j in range(width)))


def convert_to_pixels(input_tiles, tile_size):
    size = tile_size
    pixels_array = []

    for img in input_tiles:
        pixels = get_pixel_tuple(img, size, size)
        pixels_array.append(pixels)

    return pixels_array


def convert_to_ids(pixel_array, pixels_ids):
    id_array = []
    for i in range(len(pixel_array)):
        pixels = pixel_array[i]
        id = pixels_ids[pixels]
        id_array.append(id)
    return id_array


def map_pixels_to_img(pixels_array, imgs_array, tile_size):
    size = tile_size
    pixels_img = {}

    for pixels, img in zip(pixels_array, imgs_array):
        if pixels not in pixels_img:
            pixels_img[pixels] = img.copy()

    return pixels_img


def map_pixels_to_id(pixels_tile, tile_size, input_image, none_position):
    size = tile_size
    pixels_id = {}

    # None tile is special case
    x, y = none_position
    none_tile = input_image.image_at(pg.Rect(x, y, size, size))
    none_pixels = get_pixel_tuple(none_tile, size, size)

    id = 0
    found = False

    #  loop through each pixel-tuple and assign ids.  Skip the none_tile.  Once none_tile is encountered
    #  no longer need to worry about finding it again in the input.

    pixels_id[none_pixels] = -1  # assign id of -1 for none_tile
    for pixels in pixels_tile:
        #  skip none tile
        if not found and all(a == b for a, b in zip(pixels, none_pixels)):  # is this the none_tile?
            found = True
        else:
            pixels_id[pixels] = id
            id += 1

    return pixels_id


def map_ids_to_img(pixels_id, pixels_img):
    ids_img = {}
    for pixels in pixels_img:
        id = pixels_id[pixels]
        img = pixels_img[pixels]
        ids_img[id] = img

    return ids_img
