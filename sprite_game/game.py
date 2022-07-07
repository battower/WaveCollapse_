import settings as sett
import common.square_grid as sq
import pygame as pg
import sys

import wc.reader as r
import random
import numpy as np

import common.flood as flood
import sprite_game.sprites as sprites
import common.util as util
import wc.draw as draw

class BaseDungeonGame:

    def __init__(self):
        title = "Random Dungeon Generation Test"
        self.bgcolr = sett.BGCOLR
        screen_rect = sq.Rect(0, 0, sett.SCREEN_WIDTH, sett.SCREEN_HEIGHT)

        self.tsize = sett.TILESIZE

        pg.init()
        pg.display.set_caption(title)

        self.screen = pg.display.set_mode(screen_rect.dim())
        self.clock = pg.time.Clock()
        self.canvas = pg.Surface(screen_rect.dim()).convert()
        self.canvas.fill(self.bgcolr)

        self.dungeon_shape = (36, 36)
        self.dungeon = np.ones(self.dungeon_shape)

        self.img_dict = self.load_images()
        self.walls_floors = {}
        self.characters = []

        self.treat = None
        self.wizard = None
        self.familiar = None

    def drunken_dungeon(self):
        x = random.randint(0, 35)
        y = random.randint(0, 35)

        for i in range(2):
            self.drunken_walk((x, y), 64)

        x = random.randint(0, 35)
        y = random.randint(0, 35)
        for i in range(2):
            self.drunken_walk((x, y), 64)

        for i in range(4):
            x = random.randint(0, 35)
            y = random.randint(0, 35)
            self.drunken_walk((x, y), 64)

    def drunken_walk(self, start_pos, num_blocks):
        width, height = self.dungeon_shape
        cleared = 0
        pos = start_pos
        while cleared < num_blocks:

            stumble = random.randint(0, 3)
            x, y = pos
            nbrs = sq.neighbours(x, y)

            w, z = nbrs[stumble]
            if 0 <= w < width and 0 <= z < height:
                if self.dungeon[z][w] == 1:
                    self.dungeon[z][w] = 0
                    cleared += 1
                pos = (w, z)

    def place_sprite(self, sprite, pos):
        self.characters.append(sprite)

    def treat_sprite(self, pos):
        img = self.img_dict[3]
        self.treat = sprites.Block(pos, img)
        self.place_sprite(self.treat, pos)

    def familiar_sprite(self, pos):
        img = self.img_dict[2]
        self.familiar = sprites.Brul(pos, img)
        self.familiar.intoxicate(.2)
        self.place_sprite(self.familiar, pos)

    def wizard_sprite(self, pos):
        img = self.img_dict[0]
        self.wizard = sprites.Brul(pos, img)
        self.place_sprite(self.wizard, pos)

    def wall_floor_sprites(self):
        wall_imgs = [self.img_dict[i] for i in {1, 7, 8, 9}]
        floor_imgs = [self.img_dict[i] for i in {4, 5, 6}]
        width, height = self.dungeon_shape
        
        for j in range(height):
            for i in range(width):
                v = self.dungeon[j][i]
                if v == 1:
                    r = random.randint(0, 3)
                    img = wall_imgs[r]
                else:
                    r = random.randint(0, 2)
                    img = floor_imgs[r]


                pos = (i, j)
                self.walls_floors[pos] = sprites.Block(pos, img)

                
    def load_sprites(self):
        treat_pos = self.find_random_floor()
        self.treat_sprite(treat_pos)

        flooded = self.flood_dungeon([treat_pos])

        fam_pos = self.find_non_zero(flooded)
        self.familiar_sprite(fam_pos)
        self.familiar.give_map(flooded, treat_pos)

        wiz_pos = self.find_non_zero(flooded)
        self.wizard_sprite(wiz_pos)

        flooded = self.flood_dungeon([fam_pos])
        self.wizard.give_map(flooded, fam_pos)

        self.wall_floor_sprites()

    def draw(self):
        x, y = self.wizard.pos
        off = (x -6, y -6)
        rect = sq.Rect(x-6, y-6, 12, 12)
        for xy in sq.rect_points(rect):
            if xy in self.walls_floors:
                self.walls_floors[xy].draw(self.canvas, off)
            for c in self.characters:
                if sq.eq(c.pos, xy):
                    c.draw(self.canvas, off)

        self.screen.blit(self.canvas, (0, 0))

    def run(self):

        run = True
        temp = 0.0
        while run:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

            self.canvas.fill(self.bgcolr)
            self.draw()

            dt = self.clock.tick(60)
            self.update(dt)

            pg.display.update()
            run = True

    def update(self, dt):

        self.familiar.update(dt)
        self.wizard.update(dt)

        if self.familiar.found and self.wizard.found:

            flooded = self.flood_dungeon([self.treat.pos])
            treat_pos = self.find_non_zero(flooded)
            self.treat.pos = treat_pos
            flooded = self.flood_dungeon([treat_pos])
            self.familiar.give_map(flooded, treat_pos)
            self.familiar.found = False
            self.wizard.found = False


        flooded = self.flood_dungeon([self.familiar.pos])
        self.wizard.give_map(flooded, self.familiar.pos)


    def find_random_floor(self):
        arr = np.argwhere(self.dungeon == 0)
        length = len(arr)
        if length > 1:
            r = random.randint(0, length-1)
            return arr[r][1], arr[r][0]
        else:
            return -1, -1

    def find_non_zero(self, flooded):
        arr = np.argwhere(flooded != 0)
        length = len(arr)
        if length > 1:
            r = random.randint(0, length-1)
            return arr[r][1], arr[r][0]
        else:
            return -1, -1

    def flood_dungeon(self, start_list):
        start = np.ones(self.dungeon_shape)
        for pos in start_list:
            x, y = pos
            start[y][x] = 0

        return flood.flood(start, self.dungeon)

    def load_images(self):
        player_img = 'images/sprites/boggart.png'
        familiar_img = 'images/sprites/cigotuvis_monster.png'
        treat_img = 'images/sprites/strawberry.png'
        block_img = 'images/sprites/brick_gray0.png'
        block_img_1 = 'images/sprites/catacombs_0.png'
        block_img_2 = 'images/sprites/catacombs_2.png'
        block_img_3 = 'images/sprites/catacombs_7.png'
        block_img_4 = 'images/sprites/catacombs_9.png'

        floor_img_1 = 'images/sprites/black_cobalt_1.png'
        floor_img_2 = 'images/sprites/black_cobalt_6.png'
        floor_img_3 = 'images/sprites/black_cobalt_12.png'

        colors = [(255, 255, 255), (0, 255, 255), (255, 0, 255), (255, 255, 0), (64, 128, 128), (128, 64, 128),
                  (128, 128, 64),
                  (128, 192, 192), (192, 128, 192), (192, 192, 128), (200, 200, 100)]

        sprite_dict = {0: pg.image.load(player_img).convert(),
                       1: pg.image.load(block_img_4).convert(),
                       2: pg.image.load(familiar_img).convert(),
                       3: pg.image.load(treat_img).convert(),
                       4: pg.image.load(floor_img_1).convert(),
                       5: pg.image.load(floor_img_2).convert(),
                       6: pg.image.load(floor_img_3).convert(),
                       7: pg.image.load(block_img_1).convert(),
                       8: pg.image.load(block_img_2).convert(),
                       9: pg.image.load(block_img_3).convert(),
                       }

        sprite_dict[0].set_colorkey((0, 0, 0))
        sprite_dict[2].set_colorkey((0, 0, 0))
        sprite_dict[3].set_colorkey((0, 0, 0))

        for i in range(len(colors)):
            temp = pg.Surface([self.tsize, self.tsize])
            temp.fill(colors[i])

            sprite_dict[i + 10] = temp

        return sprite_dict


class WaveDungeonGame(BaseDungeonGame):

    def __init__(self):
        super().__init__()

        constraints_img = 'images/wave_input/crawler_constraints.png'
        self.wave_reader = r.Reader(constraints_img, 27, sq.Rect(0, 0, 24, 20), (0, 0))
        self.start_wave = None
        self.final_waves = None
        self.rooms = None
        self.safe_rooms = []
        self.count = 0
        left = sq.Rect(0, 12, 12, 12)
        top = sq.Rect(12, 0, 12, 12)
        right = sq.Rect(24, 12, 12, 12)
        bot = sq.Rect(12, 24, 12, 12)
        self.center_rect = sq.Rect(12, 12, 12, 12)
        self.room_rects = [left, top, right, bot]


    def draw(self):


        tiles = self.wave_reader.get_tiles()
        draw.draw_wave(self.start_wave, (14, 12), 27, tiles, self.canvas)
        draw.draw_wave(self.final_waves[0], (2, 12), 27, tiles, self.canvas)
        draw.draw_wave(self.final_waves[1], (14, 0), 27, tiles, self.canvas)
        draw.draw_wave(self.final_waves[2], (26, 12), 27, tiles, self.canvas)
        draw.draw_wave(self.final_waves[3], (14, 24), 27, tiles, self.canvas)

        super().draw()


    def update(self, dt):
        self.familiar.update(dt)
        self.wizard.update(dt)
        if self.familiar.found and self.wizard.found:

            # copy current room into the center room
            # recalc positions of familiar and wizard for center room
            i = self.get_index_from_pos(self.treat.pos)
            if i is not None:
                self.start_wave = self.final_waves[i]

                self.treat.pos = self.new_pos(i, self.treat.pos)
                self.wizard.pos = self.new_pos(i, self.wizard.pos)
                self.familiar.pos = self.new_pos(i, self.familiar.pos)

            self.generate_dungeon(self.start_wave)

            flooded = self.flood_dungeon([self.treat.pos])
            treat_pos = self.find_non_zero(flooded)
            self.treat.pos = treat_pos
            flooded = self.flood_dungeon([treat_pos])
            self.familiar.give_map(flooded, treat_pos)
            self.familiar.found = False


            self.walls_floors.clear()
            self.wall_floor_sprites()
        self.wizard.found = False
        flooded = self.flood_dungeon([self.familiar.pos])
        self.wizard.give_map(flooded, self.familiar.pos)

    def get_index_from_pos(self, pos):
        for i in range(4):
            rect = self.room_rects[i]
            index = sq.index(pos, rect)
            if index is not None:
                return i

    def new_pos(self, room_index, pos):
        i = room_index
        if i == 0:  # left room
            pos = sq.add(pos, (12, 0))
        elif i == 1:
            pos = sq.add(pos, (0, 12))
        elif i == 2:
            pos = sq.add(pos, (-12, 0))
        elif i == 3:
            pos = sq.add(pos, (0, -12))

        return pos


    def generate_dungeon(self, start_wave):
        print('generate dungeon')
        self.dungeon = np.ones(self.dungeon_shape)
        self.start_wave = start_wave
        self.make_rooms(start_wave)  # sets safe_rooms and riins

        # write rooms to dungeon
        rects = self.room_rects
        start_room = self.convert_wave(start_wave)  # wave->room
        self.write_room_to_dungeon(start_room, self.center_rect)

        for i in self.safe_rooms:
            room = self.rooms[i]
            rect = rects[i]
            self.write_room_to_dungeon(room, rect)

    # make neighboring rooms from start_wave, sets: start_wave, rooms, final_rooms, safe_rooms
    def make_rooms(self, start_wave):
        self.safe_rooms.clear()

        room_offsets = [(-6, 0), (0, -6), (6, 0), (0, 6)]
        num_offsets = len(room_offsets)
        wave_xys = {}

        for offset_xy, coords in sq.intersect_squares(12):
            if offset_xy in room_offsets:
                wave_xys[offset_xy] = coords

        wave_wzs = {room_offsets[0]: tuple(sq.add(xy, (6, 0)) for xy in wave_xys[room_offsets[0]]),
                    room_offsets[1]: tuple(sq.add(xy, (0, 6)) for xy in wave_xys[room_offsets[1]]),
                    room_offsets[2]: tuple(sq.add(xy, (-6, 0)) for xy in wave_xys[room_offsets[2]]),
                    room_offsets[3]: tuple(sq.add(xy, (0, -6)) for xy in wave_xys[room_offsets[3]])}

        shape = sq.Rect(0, 0, 12, 12)
        reader = self.wave_reader

        a = [self.new_wave() for i in range(num_offsets)]
        b = [self.new_wave() for i in range(num_offsets)]

        util.entangle_list(start_wave, a, wave_xys, wave_wzs, room_offsets)

        solved = self.safe_rooms
        for i in range(num_offsets):

            off = room_offsets[i]
            xy = wave_xys[off]
            wz = wave_wzs[off]

            a[i].set_max_rejects(1000)
            b[i].set_max_rejects(1000)

            a_res = util.solve_wave(a[i], rand=False)
            util.entangle(a[i], b[i], xy, wz)

            if util.solve_wave(b[i], rand=False) and a_res:
                solved.append(i)

        self.final_waves = b
        self.rooms = [self.convert_wave(b[i]) for i in range(num_offsets)]

    def write_room_to_dungeon(self, room, r_rect):

        for xy in sq.rect_points(r_rect):
            x, y = xy
            j = sq.index(xy, r_rect)
            self.dungeon[y][x] = room[j]

    def new_wave(self):
        start_img = 'images/wave_input/start_room.png'  # #
        wave_rect = sq.Rect(0, 0, 12, 12)
        return self.wave_reader.read_wave(start_img, wave_rect)

    def convert_wave(self, wave):
        block_dict = util.get_block_dict()
        one_or_none = wave.one_or_none_array()
        room = util.one_or_none_to_blocks(one_or_none, block_dict)

        return room

