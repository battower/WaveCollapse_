import sprite_game.game as g
import common.util as util
import settings as sett

sett.DEBUG = False
sett.SAVE_OUTPUT = False


def main():
    wavegame()


def wavegame():
    game = g.WaveDungeonGame()

    start_wave = game.new_wave()
    start_wave.set_max_rejects(5500)
    util.solve_wave(start_wave, rand=True)

    game.generate_dungeon(start_wave)
    game.load_sprites()
    game.run()


def basegame():
    game = g.BaseDungeonGame()
    game.drunken_dungeon()
    game.load_sprites()

    game.run()


if __name__ == '__main__': main()
