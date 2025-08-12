import pygame as pg
import chess
import time
import threading
import sys
from .ai import AI
from .utils import load_piece_images, lerp, ease_in_out_cubic
from .ui import Button

BG = (30, 30, 30)
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT_SELECT = (255, 255, 0, 150)
HIGHLIGHT_MOVE = (100, 200, 140, 150)
ACCENT = (100, 170, 255)
ANIM_DURATION = 0.25
PIECE_ORDER = {
    chess.PAWN: 'p',
    chess.KNIGHT: 'n',
    chess.BISHOP: 'b',
    chess.ROOK: 'r',
    chess.QUEEN: 'q',
    chess.KING: 'k',
}

class Game:
    PROMOTION_PIECES = [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]
    PROMOTION_NAMES = {chess.QUEEN: "Queen", chess.ROOK: "Rook", chess.BISHOP: "Bishop", chess.KNIGHT: "Knight"}
    def __init__(self, board_pixel, difficulty, player_color):
        pg.init()
        self.square = board_pixel // 8
        self.screen_width = board_pixel
        self.screen_height = board_pixel
        self.screen = pg.display.set_mode((self.screen_width, self.screen_height))
        pg.display.set_caption("Pygame Chess")
        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont("Arial", 22)
        self.large_font = pg.font.SysFont("Arial", 28, bold=True)
        self.board = chess.Board()
        self.origin = (0, 0)
        self.pieces = load_piece_images(self.square)
        self.selected = None
        self.legal_moves = []
        self.animating = False
        self.anim_start = 0
        self.anim_move = None
        self.anim_t = 1.0
        self.anim_piece = None
        self.ai = AI(difficulty)
        self.player_color = chess.WHITE if player_color == "White" else chess.BLACK
        self.ai_color = not self.player_color
        self.flip_board = (self.player_color == chess.BLACK)
        self.msg = ""
        self.game_over = False
        self.move_history = []
        self.awaiting_promotion = False
        self.promotion_move_base = None
        self.promotion_buttons = []
        self.create_promotion_buttons()
        self.ai_thread = None
        self.ai_move_result = None
        button_width = 180
        button_height = 50
        self.game_over_button = Button(
            rect=(self.screen_width // 2 - button_width // 2, self.screen_height // 2 + 40, button_width, button_height),
            text="Home",
            font=self.font,
            callback=self.back_to_settings
        )
        self.show_game_over_popup = False
        self.running = True
    def back_to_settings(self):
        self.show_game_over_popup = False
        self.running = False
    def quit_game(self):
        pg.quit()
        sys.exit(0)
    def create_promotion_buttons(self):
        btn_w, btn_h = 120, 50
        gap = 15
        total_w = (btn_w * 4) + (gap * 3)
        panel_width = 600
        panel_x = (self.screen_width - panel_width) // 2
        start_x = panel_x + (panel_width - total_w) // 2
        y = self.screen_height - 200 + 70
        self.promotion_buttons = []
        for i, piece in enumerate(self.PROMOTION_PIECES):
            rect = (start_x + i * (btn_w + gap), y, btn_w, btn_h)
            text = self.PROMOTION_NAMES[piece]
            def make_callback(p=piece):
                return lambda: self.handle_promotion_choice(p)
            btn = Button(rect, text, self.font, make_callback())
            self.promotion_buttons.append(btn)
    def handle_promotion_choice(self, piece_type):
        if not self.awaiting_promotion or self.promotion_move_base is None:
            return
        move = chess.Move(self.promotion_move_base.from_square, self.promotion_move_base.to_square, promotion=piece_type)
        if move in self.board.legal_moves:
            self.start_move_animation(move)
            self.awaiting_promotion = False
            self.promotion_move_base = None
            self.selected = None
            self.legal_moves = []
    def start_ai_move_thread(self):
        def ai_task():
            board_copy = self.board.copy()
            move = self.ai.choose_move(board_copy)
            self.ai_move_result = move
        self.ai_move_result = None
        self.ai_thread = threading.Thread(target=ai_task)
        self.ai_thread.daemon = True
        self.ai_thread.start()
    def ai_move(self):
        if (self.animating or self.game_over or self.board.turn != self.ai_color or self.awaiting_promotion or self.show_game_over_popup):
            return
        if self.ai_move_result:
            move = self.ai_move_result
            self.ai_move_result = None
            if move and move in self.board.legal_moves:
                self.start_move_animation(move)
        else:
            if not self.ai_thread or not self.ai_thread.is_alive():
                self.start_ai_move_thread()
    def start_move_animation(self, move):
        if self.animating:
            return
        self.selected = None
        self.legal_moves = []
        self.animating = True
        self.anim_start = time.time()
        self.anim_move = move
        self.anim_piece = self.board.piece_at(move.from_square)
        self.anim_t = 0.0
    def update_animation(self):
        if not self.animating:
            return
        elapsed = time.time() - self.anim_start
        self.anim_t = min(elapsed / ANIM_DURATION, 1.0)
        if self.anim_t >= 1.0:
            self.board.push(self.anim_move)
            self.move_history.append(self.anim_move)
            self.animating = False
            self.anim_move = None
            self.anim_piece = None
            self.anim_t = 1.0
            self.selected = None
            self.legal_moves = []
            self.check_game_over()
    def check_game_over(self):
        if self.board.is_game_over():
            if self.board.is_checkmate():
                self.game_over = True
                self.msg = ("You win!" if self.board.turn != self.player_color else "You lose!")
            elif self.board.is_stalemate():
                self.game_over = True
                self.msg = "Stalemate! Draw."
            elif self.board.is_insufficient_material():
                self.game_over = True
                self.msg = "Draw due to insufficient material."
            else:
                self.game_over = True
                self.msg = "Game Over."
            self.show_game_over_popup = True
    def square_to_coords(self, square):
        file = chess.square_file(square)
        rank = chess.square_rank(square)
        if self.flip_board:
            file = 7 - file
            rank = 7 - rank
        return file, rank
    def coords_to_pos(self, file, rank):
        ox, oy = self.origin
        return ox + file * self.square, oy + (7 - rank) * self.square
    def pos_to_square(self, pos):
        x, y = pos
        if x < 0 or y < 0 or x >= self.screen_width or y >= self.screen_height:
            return None
        file = x // self.square
        rank = 7 - (y // self.square)
        if self.flip_board:
            file = 7 - file
            rank = 7 - rank
        if 0 <= file <= 7 and 0 <= rank <= 7:
            return chess.square(file, rank)
        return None
    def draw_board(self):
        for rank in range(8):
            for file in range(8):
                color = LIGHT_SQUARE if (file + rank) % 2 == 0 else DARK_SQUARE
                pos = self.coords_to_pos(file, rank)
                pg.draw.rect(self.screen, color, (*pos, self.square, self.square))
        self.draw_board_labels()
    def draw_board_labels(self):
        label_font = pg.font.SysFont("Arial", max(12, self.square // 6))
        label_color = (100, 100, 100)
        files = "abcdefgh"
        if self.flip_board:
            files = files[::-1]
        for i, file_char in enumerate(files):
            x = self.square * i + self.square - 15
            y = self.screen_height - 15
            label = label_font.render(file_char, True, label_color)
            self.screen.blit(label, (x, y))
        ranks = "12345678"
        if self.flip_board:
            ranks = ranks[::-1]
        for i, rank_char in enumerate(ranks):
            x = 5
            y = self.square * i + 5
            label = label_font.render(rank_char, True, label_color)
            self.screen.blit(label, (x, y))
    def draw_highlights(self):
        s = pg.Surface((self.square, self.square), pg.SRCALPHA)
        s.fill(HIGHLIGHT_SELECT)
        if self.selected is not None:
            file, rank = self.square_to_coords(self.selected)
            pos = self.coords_to_pos(file, rank)
            self.screen.blit(s, pos)
        s.fill(HIGHLIGHT_MOVE)
        for move in self.legal_moves:
            file, rank = self.square_to_coords(move.to_square)
            pos = self.coords_to_pos(file, rank)
            self.screen.blit(s, pos)
    def draw_pieces(self):
        board = self.board
        anim_move = self.anim_move if self.animating else None
        t = self.anim_t if self.animating else 1.0
        for sq in chess.SQUARES:
            p = board.piece_at(sq)
            if p is None:
                continue
            if anim_move and sq == anim_move.from_square:
                continue
            file, rank = self.square_to_coords(sq)
            pos = self.coords_to_pos(file, rank)
            img = self.pieces.get((PIECE_ORDER[p.piece_type], p.color))
            if img:
                self.screen.blit(img, pos)
        if anim_move and self.anim_piece:
            from_file, from_rank = self.square_to_coords(anim_move.from_square)
            to_file, to_rank = self.square_to_coords(anim_move.to_square)
            fx, fy = self.coords_to_pos(from_file, from_rank)
            tx, ty = self.coords_to_pos(to_file, to_rank)
            eased_t = ease_in_out_cubic(t)
            ix = lerp(fx, tx, eased_t)
            iy = lerp(fy, ty, eased_t)
            img = self.pieces.get((PIECE_ORDER[self.anim_piece.piece_type], self.anim_piece.color))
            if img:
                self.screen.blit(img, (int(ix), int(iy)))
    def draw_message(self):
        if self.msg:
            surf = self.large_font.render(self.msg, True, ACCENT)
            self.screen.blit(surf, (10, 10))
    def draw_promotion_ui(self):
        if self.awaiting_promotion:
            overlay = pg.Surface((self.screen_width, self.screen_height), pg.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            panel_width = 600
            panel_height = 150
            panel_x = (self.screen_width - panel_width) // 2
            panel_y = self.screen_height - 200
            pg.draw.rect(self.screen, (255, 255, 255), (panel_x, panel_y, panel_width, panel_height))
            pg.draw.rect(self.screen, (0, 0, 0), (panel_x, panel_y, panel_width, panel_height), 4)
            info_surf = self.large_font.render("Choose promotion piece:", True, (0, 0, 0))
            info_x = panel_x + (panel_width - info_surf.get_width()) // 2
            self.screen.blit(info_surf, (info_x, panel_y + 20))
            mouse_pos = pg.mouse.get_pos()
            for btn in self.promotion_buttons:
                btn.check_hover(mouse_pos)
                btn.draw(self.screen)
    def draw_game_over_popup(self):
        if self.show_game_over_popup:
            overlay = pg.Surface((self.screen_width, self.screen_height), pg.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            panel_width = 400
            panel_height = 200
            panel_x = (self.screen_width - panel_width) // 2
            panel_y = (self.screen_height - panel_height) // 2
            pg.draw.rect(self.screen, (255, 255, 255), (panel_x, panel_y, panel_width, panel_height))
            pg.draw.rect(self.screen, (0, 0, 0), (panel_x, panel_y, panel_width, panel_height), 4)
            text_surf = self.large_font.render(self.msg, True, (0, 0, 0))
            text_x = panel_x + (panel_width - text_surf.get_width()) // 2
            text_y = panel_y + 40
            self.screen.blit(text_surf, (text_x, text_y))
            mouse_pos = pg.mouse.get_pos()
            self.game_over_button.check_hover(mouse_pos)
            self.game_over_button.draw(self.screen, special_style=True)
    def handle_click(self, pos):
        if self.show_game_over_popup:
            if self.game_over_button.check_click(pos):
                return
            return
        if self.awaiting_promotion:
            for btn in self.promotion_buttons:
                if btn.check_click(pos):
                    return
            return
        if self.animating or self.game_over:
            return
        if self.board.turn != self.player_color:
            return
        square = self.pos_to_square(pos)
        if square is None:
            return
        if self.selected is not None and square in [m.to_square for m in self.legal_moves]:
            move = chess.Move(self.selected, square)
            promotion_moves = [m for m in self.board.legal_moves if m.from_square == self.selected and m.to_square == square and m.promotion]
            if promotion_moves:
                self.awaiting_promotion = True
                self.promotion_move_base = move
                return
            else:
                if move in self.board.legal_moves:
                    self.start_move_animation(move)
        else:
            piece = self.board.piece_at(square)
            if (piece is not None and piece.color == self.board.turn and piece.color == self.player_color):
                self.selected = square
                self.legal_moves = [m for m in self.board.legal_moves if m.from_square == square]
            else:
                self.selected = None
                self.legal_moves = []
    def run(self):
        while self.running:
            self.clock.tick(60)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)
            self.update_animation()
            if not self.game_over and not self.animating:
                if self.board.turn == self.ai_color:
                    self.ai_move()
            self.screen.fill(BG)
            self.draw_board()
            self.draw_highlights()
            self.draw_pieces()
            self.draw_message()
            self.draw_promotion_ui()
            self.draw_game_over_popup()
            pg.display.flip()
        pg.quit()
