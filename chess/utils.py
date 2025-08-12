import pygame as pg
import os
import chess

def load_piece_images(square_size):
    pieces = {}
    base_dir = "img"
    piece_letter = {
        chess.PAWN: 'p',
        chess.KNIGHT: 'n',
        chess.BISHOP: 'b',
        chess.ROOK: 'r',
        chess.QUEEN: 'q',
        chess.KING: 'k',
    }
    for color, cstr in [(chess.WHITE, "l"), (chess.BLACK, "d")]:
        prefix = "Chess_"
        for pt in piece_letter:
            p = piece_letter[pt]
            filename = f"{prefix}{p}{cstr}t60.png"
            path = os.path.join(base_dir, filename)
            if os.path.exists(path):
                img = pg.image.load(path).convert_alpha()
                img = pg.transform.smoothscale(img, (square_size, square_size))
                pieces[(p, color)] = img
            else:
                print(f"Warning: Missing image file {filename}")
    return pieces

def lerp(a, b, t):
    return a + (b - a) * t

def ease_in_out_cubic(t):
    if t < 0.5:
        return 4 * t * t * t
    else:
        return 1 - pow(-2 * t + 2, 3) / 2
