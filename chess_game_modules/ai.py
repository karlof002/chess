import chess
import random
import time

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

# Position tables for better piece positioning
PAWN_TABLE = [
    0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0
]

KNIGHT_TABLE = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]

BISHOP_TABLE = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20,
]

ROOK_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     0,  0,  0,  5,  5,  0,  0,  0
]

QUEEN_TABLE = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]

KING_MG_TABLE = [  # Middle game
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -10,-20,-20,-20,-20,-20,-20,-10,
     20, 20,  0,  0,  0,  0, 20, 20,
     20, 30, 10,  0,  0, 10, 30, 20
]

def get_piece_position_value(piece_type, square, is_white):
    tables = {
        chess.PAWN: PAWN_TABLE,
        chess.KNIGHT: KNIGHT_TABLE,
        chess.BISHOP: BISHOP_TABLE,
        chess.ROOK: ROOK_TABLE,
        chess.QUEEN: QUEEN_TABLE,
        chess.KING: KING_MG_TABLE
    }
    table = tables.get(piece_type, [0] * 64)
    if not is_white:
        index = 63 - square
    else:
        index = square
    return table[index]

def evaluate(board):
    if board.is_checkmate():
        return -999999 if board.turn else 999999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0
    score = 0
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece:
            piece_value = PIECE_VALUES[piece.piece_type]
            position_value = get_piece_position_value(piece.piece_type, sq, piece.color == chess.WHITE)
            total_value = piece_value + position_value
            if piece.color == chess.WHITE:
                score += total_value
            else:
                score -= total_value
    white_king_square = board.king(chess.WHITE)
    black_king_square = board.king(chess.BLACK)
    if white_king_square:
        white_king_attacks = len(board.attackers(chess.BLACK, white_king_square))
        score -= white_king_attacks * 20
    if black_king_square:
        black_king_attacks = len(board.attackers(chess.WHITE, black_king_square))
        score += black_king_attacks * 20
    center_squares = [chess.D4, chess.D5, chess.E4, chess.E5]
    for sq in center_squares:
        white_attackers = len(board.attackers(chess.WHITE, sq))
        black_attackers = len(board.attackers(chess.BLACK, sq))
        score += (white_attackers - black_attackers) * 10
    mobility_bonus = len(list(board.legal_moves)) * 2
    if board.turn == chess.WHITE:
        score += mobility_bonus
    else:
        score -= mobility_bonus
    white_pawns = board.pieces(chess.PAWN, chess.WHITE)
    black_pawns = board.pieces(chess.PAWN, chess.BLACK)
    for file in range(8):
        white_file_pawns = sum(1 for sq in white_pawns if chess.square_file(sq) == file)
        black_file_pawns = sum(1 for sq in black_pawns if chess.square_file(sq) == file)
        if white_file_pawns > 1:
            score -= (white_file_pawns - 1) * 15
        if black_file_pawns > 1:
            score += (black_file_pawns - 1) * 15
    for file in range(8):
        white_has_pawn = any(chess.square_file(sq) == file for sq in white_pawns)
        black_has_pawn = any(chess.square_file(sq) == file for sq in black_pawns)
        if white_has_pawn:
            adjacent_files = [f for f in [file-1, file+1] if 0 <= f <= 7]
            if not any(any(chess.square_file(sq) == adj_file for sq in white_pawns) for adj_file in adjacent_files):
                score -= 20
        if black_has_pawn:
            adjacent_files = [f for f in [file-1, file+1] if 0 <= f <= 7]
            if not any(any(chess.square_file(sq) == adj_file for sq in black_pawns) for adj_file in adjacent_files):
                score += 20
    return score

def minimax(board, depth, alpha, beta, maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate(board), None
    best_move = None
    moves = list(board.legal_moves)
    def move_priority(move):
        priority = 0
        if board.is_capture(move):
            captured_piece = board.piece_at(move.to_square)
            if captured_piece:
                priority += PIECE_VALUES[captured_piece.piece_type]
        if move.promotion:
            priority += 800
        if move.to_square in [chess.D4, chess.D5, chess.E4, chess.E5]:
            priority += 10
        board.push(move)
        is_check = board.is_check()
        board.pop()
        if is_check:
            priority += 50
        return priority
    moves.sort(key=move_priority, reverse=True)
    if maximizing:
        max_eval = -1_000_000
        for move in moves:
            board.push(move)
            eval_score, _ = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = 1_000_000
        for move in moves:
            board.push(move)
            eval_score, _ = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval, best_move

class AI:
    def __init__(self, difficulty="Medium"):
        self.set_difficulty(difficulty)
    def set_difficulty(self, diff):
        self.difficulty = diff
        if diff == "Easy":
            self.depth = 2
            self.randomness = 0.25
            self.think_time = 0.5
        elif diff == "Medium":
            self.depth = 3
            self.randomness = 0.10
            self.think_time = 1.0
        else:
            self.depth = 4
            self.randomness = 0.00
            self.think_time = 2.0
    def choose_move(self, board):
        moves = list(board.legal_moves)
        if not moves:
            return None
        if random.random() < self.randomness:
            good_moves = []
            for move in moves:
                if board.is_capture(move):
                    good_moves.append(move)
                else:
                    board.push(move)
                    if board.is_check():
                        good_moves.append(move)
                    board.pop()
            if good_moves:
                return random.choice(good_moves)
            else:
                return random.choice(moves)
        start = time.time()
        _, move = minimax(board, self.depth, -1_000_000, 1_000_000, board.turn == chess.WHITE)
        elapsed = time.time() - start
        to_sleep = self.think_time - elapsed
        if to_sleep > 0:
            time.sleep(to_sleep)
        return move if move else random.choice(moves)
