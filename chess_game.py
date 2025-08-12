from chess.ui import settings_screen
from chess.game import Game

def main():
    while True:
        board_pixel, difficulty, player_color = settings_screen()
        game = Game(board_pixel, difficulty, player_color)
        game.run()

if __name__ == "__main__":
    main()