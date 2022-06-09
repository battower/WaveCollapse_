import SquareGrid
import common as C
import Wave as W
import SimpleTile as ST
import pygame as PG
from pygame.locals import *



def main():

    screen, clock = C.init_pygame('Overlap Demo', 900, 768)
    canvas = C.init_surface(768, 768, (51, 51, 51))
    pxsize = 24
    N = 3

    intersections = tuple(SquareGrid.intersections(N))
    patdx, tiledx, weights, converted_input, colormap = C.process_overlap_input('overlap/Flowers1.png', N)
    pixeldx = {v: k for k, v in patdx.items()}

    rules = C.get_overlap_rules(patdx, intersections, N)
    neighbors = tuple(x[0] for x in intersections)

    wavelet = W.Wavelet({i: weights[i] for i in range(len(weights))})

    C.scale_tiles(tiledx, pxsize)
    while True:

        wave = ST.SimpleTiles(16, 16, wavelet, rules, neighbors)
        startdx = wave.random_index()
        startstate = wave.random_state(startdx)

        for event in PG.event.get():
            if event.type == QUIT:
                return

        wave.solve(startdx, startstate)
        C.draw_overlap(wave, N, colormap, pixeldx, canvas)

        screen.blit(canvas, (0, 0))
        PG.display.flip()





if __name__ == '__main__': main()
