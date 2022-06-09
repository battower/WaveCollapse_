
import common as C
import Wave as W
import SimpleTile as ST
import pygame as PG
from pygame.locals import *


def main():
    screen, clock = C.init_pygame('Simple Tile Demo', 900, 768)
    canvas = C.init_surface(768, 768, (51, 51, 51))
    pxsize = 24

    patdx, tiledx, weights, converted_input, colormap = C.process_tile_input(24, 14, 24, 'roads_and_trees2.png')

    # Balance the weights abit
    weights[0] = 1
    weights[2] = 24
    wavelet = W.Wavelet({i: weights[i] for i in range(len(weights))})

    rules = C.infer_rules(24, 14, converted_input, len(tiledx))
    C.scale_tiles(tiledx, pxsize)

    neighbors = ((-1, 0), (0, -1), (1, 0), (0, 1))
    while True:

        wave = ST.SimpleTiles(8, 8, wavelet, rules, neighbors)
        startdx = wave.random_index()
        startstate = wave.random_state(startdx)

        for event in PG.event.get():
            if event.type == QUIT:
                return

        wave.solve(startdx, startstate)
        C.draw_wave(wave, tiledx, pxsize, canvas)

        screen.blit(canvas, (0, 0))
        PG.display.flip()





if __name__ == '__main__': main()
