import common.sprite_sheet as ss
import wc.constraint_table as ct

import wc.wave as w
import wc.constraint_propagator as p
import wc.reader_utils as utils

import common.square_grid as sq
import pygame as pg

# Reads Wave states and constraints from image files.
# Init with a single image representing all the constraints with all of the tiles.


class Reader:

    def __init__(self, img_filename, tile_size, img_shape, none_tile_location):
        self.src_img = ss.SpriteSheet(img_filename)

        src_width, src_height = self.src_img.dim()

        self._tsize = tile_size
        self._ishape = img_shape
        self.npos = none_tile_location
        width, height = img_shape.dim()

        #  Ensure image is correct size
        assert (width * tile_size == src_width and height * tile_size == src_height)

        self.input_as_tiles = utils.read_input(width, height, tile_size, self.src_img)
        self.input_as_pixels = utils.convert_to_pixels(self.input_as_tiles, tile_size)

        #  generate ids for uniqe tiles read from the input image.
        #  These are dictionaries mapping pixel-tuples to tiles, pixel_tuples to a generated id, and finally
        #  those ids to the tiles.
        self.pixels_tile = utils.map_pixels_to_img(self.input_as_pixels, self.input_as_tiles, tile_size)
        self.pixels_id = utils.map_pixels_to_id(self.pixels_tile, tile_size, self.src_img, self.npos)
        self.ids_tile = utils.map_ids_to_img(self.pixels_id, self.pixels_tile)

        #  convert the input array into an array of tile ids
        self.input_as_ids = utils.convert_to_ids(self.input_as_pixels, self.pixels_id)

        #  all work done, now populate the constraints table from the input.
        self.constraints_table = self.read_constraints_table()

    def get_tiles(self):
        return self.ids_tile

    def get_constraints_table(self):
        return self.constraints_table

    def input_shape(self):
        return self._ishape

    def input_as_id_array(self):
        return self.input_as_ids

    def number_tiles(self):
        return len(self.ids_tile) - 1  # Don't include 'None' Tile

    def get_raw_tiles(self):
        return self.input_as_tiles

    def get_raw_pixel_tuples(self):
        return self.input_as_pixels

    def get_pixel_tuple_id_dict(self):
        return self.pixels_id

    def read_wave(self, wave_img_file, wave_shape, weights=None):

        width, height = wave_shape.dim()

        wave_img = ss.SpriteSheet(wave_img_file)
        pxwidth, pxheight = wave_img.dim()

        assert (width * self._tsize == pxwidth and height * self._tsize == pxheight)

        input_tiles = utils.read_input(width, height, self._tsize, wave_img)
        input_pixels = utils.convert_to_pixels(input_tiles, self._tsize)

        input_ids = utils.convert_to_ids(input_pixels, self.pixels_id)

        initial_state = self.read_initial_state(input_ids, weights)
        propagator = p.ConstraintPropagator(self.constraints_table)

        return w.Wave(wave_shape, propagator, initial_state)

    def save_wave(self, wave, rect, filename):

        tiles = self.get_tiles()
        ids = wave.one_or_none_array()
        wave_tiles = [tiles[i] for i in ids]
        wave_shape = rect
        wav_dim = rect.dim()
        wav_pixel_dim = sq.mult(wav_dim, self._tsize)
        canvas = pg.Surface(wav_pixel_dim).convert()

        for i in range(len(wave_tiles)):
            pos = sq.deindex(i, wave_shape)
            pos = sq.mult(pos, self._tsize)
            canvas.blit(wave_tiles[i], pos, pg.Rect(0, 0, self._tsize, self._tsize))

        pg.image.save(canvas, filename)

    def read_initial_state(self, wave_input, weights):

        initial_state = []
        num_tiles = self.number_tiles()

        if weights is None:
            weights = [1 for i in range(num_tiles)]

        uncertain = {i: weights[i] for i in range(num_tiles)}

        for i in wave_input:
            if i == -1:
                initial_state.append(uncertain.copy())
            else:
                initial_state.append({i: 1})

        return initial_state

    def read_constraints_table(self):
        table = ct.ConstraintTable(self.number_tiles(), 4)
        table.read_constraints(self)
        return table
