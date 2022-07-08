import pygame as pg
import common.square_grid as sq

import random
from collections import defaultdict

import common.debugr as dbug
import settings as sett

class Block(pg.sprite.Sprite):

    def __init__(self, pos, img):
        super().__init__()
        self.pos = pos
        self.image = img
        self.rect = self.image.get_rect()
        self.sprite_size = self.rect.width  # sprite is a square rect

    def __str__(self):
        return str(self.pos)

    def draw(self, canvas, offset):
        draw_pos = sq.sub(self.pos, offset)
        draw_pos = sq.mult(draw_pos, self.sprite_size)

        canvas.blit(self.image, draw_pos)


class FogBlock(Block):

    def __init__(self, pos, width, height, color):
        self.color = color
        img = pg.Surface([width, height])
        img.fill(color)
        super().__init__(pos, img)

    def hide(self, flag):
        if flag:
            self.image.set_colorkey(self.color)
        else:
            self.image.set_colorkey((0, 0, 0))

class Player(Block):

    def __init__(self, pos, img):
        super().__init__(pos, img)
        self.direction = pg.Vector2()
        self.speed = 5

    def user_input(self):

        keys = pg.key.get_pressed()

        if keys[pg.K_UP]:
            self.direction.y = -.1
        elif keys[pg.K_DOWN]:
            self.direction.y = .1
        else:
            self.direction.y = 0

        if keys[pg.K_LEFT]:
            self.direction.x = -.1
        elif keys[pg.K_RIGHT]:
            self.direction.x = .1
        else:
            self.direction.x = 0

    def update(self, dt):
        self.user_input()
        self.move(dt)

    def move(self, dt):
        if self.direction.magnitude() != 0:
            movement = 1 / float(dt) * self.speed
            self.direction = self.direction.normalize()
            self.pos += self.direction * movement


class PlayerStep(Block):

    def __init__(self, pos, img):
        super().__init__(pos, img)
        self.direction = pg.Vector2()
        self.speed = 5
        self.timer = 0

    def user_input(self):

        keys = pg.key.get_pressed()

        if keys[pg.K_UP]:
            self.direction.y = -1
        elif keys[pg.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pg.K_LEFT]:
            self.direction.x = -1
        elif keys[pg.K_RIGHT]:
            self.direction.x = 1
        else:
            self.direction.x = 0

    def update(self, dt):

        self.timer += 1/float(dt)
        if self.timer > 1:
            self.user_input()
            self.timer = 0
            self.move()

    def move(self):
        if self.direction.magnitude() != 0:
            self.pos += self.direction


class Brul(Block):

    def __init__(self, pos, img):
        super().__init__(pos, img)

        self.timer = 0
        self.found = False
        self.flooded = None
        self.goal = None
        self.explored = None
        self.drunkeness = 0.0

    def intoxicate(self, val):
        self.drunkeness = val

    def stumble(self):
        return random.random() < self.drunkeness

    def reached_goal(self):
        return self.found

    def update(self, dt):

        if self.found:
            return

        self.timer += dt

        if self.timer > 500:

            self.timer = 0
            flood_map = self.flooded

            x, y = self.pos
            if flood_map[y][x] == 1:
                self.found = True
                return

            nbrs = self.get_flood_nbrs(flood_map)
            vals = list(nbrs.keys())
            vals.sort()
            if len(vals) == 0:
                dbug.log_f('flooded', flood_map, sq.Rect(0, 0, 1, 1), 'flood')
            if self.stumble():
                n = random.randint(0, len(vals) - 1)
                if len(nbrs[vals[n]]) == 1:
                    i = 0
                else:
                    i = random.randint(0, len(nbrs[vals[n]]) - 1)
                nbr = nbrs[vals[n]][i]
            else:
                if len(nbrs[vals[0]]) == 1:
                    i = 0
                else:
                    i = random.randint(0, len(nbrs[vals[0]]) - 1)
                nbr = nbrs[vals[0]][i]

            self.pos = nbr

    def give_map(self, flooded, treat_pos):
        self.flooded = flooded
        self.goal = treat_pos

    def update_explored(self):
        x, y = self.pos
        self.explored[y][x] = 0
        for w, z in sq.adjacent(x, y):
            if 0 <= w < 36 and 0 <= y < 36:
                self.explored[z][w] = 0

    def get_flood_nbrs(self, flood_map):
        h, w = flood_map.shape
        x, y = self.pos
        nbrs = sq.adjacent(x, y)
        floodvals = defaultdict(list)
        for n in nbrs:
            nx, ny = n
            if 0 <= nx < w and 0 <= ny < h:
                val = flood_map[ny][nx]
                if val > 0:
                    floodvals[val].append(n)

        return floodvals


