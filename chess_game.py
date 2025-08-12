from chess_game_modules.ui import settings_screen
from chess_game_modules.game import Game

def main():
    while True:
        board_pixel, difficulty, player_color = settings_screen()
        game = Game(board_pixel, difficulty, player_color)
        game.run()

if __name__ == "__main__":
    main()