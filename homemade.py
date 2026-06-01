"""
Some example classes for people who want to create a homemade bot.

With these classes, bot makers will not have to implement the UCI or XBoard interfaces themselves.
"""
from inspect import AGEN_RUNNING

import chess
from chess.engine import PlayResult, Limit
import random
from lib.engine_wrapper import MinimalEngine
from lib.lichess_types import MOVE, HOMEMADE_ARGS_TYPE
import logging
import time



# Use this logger variable to print messages to the console or log files.
# logger.info("message") will always print "message" to the console or log file.
# logger.debug("message") will only print "message" if verbose logging is enabled.
logger = logging.getLogger(__name__)


class ExampleEngine(MinimalEngine):
    """An example engine that all homemade engines inherit."""

# region RandomMove
class RandomMove(ExampleEngine):
    """Get a random move."""

    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:  # noqa: ARG002
        """Choose a random move."""
        return PlayResult(random.choice(list(board.legal_moves)), None)
# endregion RandomMove

# region AgressiveMove
class AgressiveMove(ExampleEngine):
    """Take enemy piece when possible"""

    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:

        legal_moves = list(board.legal_moves)

        capture_moves = []

        for move in legal_moves:
            if board.is_capture(move):
                capture_moves.append(move)

        if capture_moves:
            chosen_move = random.choice(capture_moves)
            logger.info(f"Aggressive move played: {chosen_move}")
            return PlayResult(chosen_move, None)

        chosen_move = random.choice(legal_moves)
        logger.info(f"Random move played: {chosen_move}")
        return PlayResult(chosen_move, None)
# endregion AgressiveMove

# region CheckAgressiveMove
class CheckAgressiveMove(ExampleEngine):
    """Value Check & Take pieces highest
       then value check
       then value take piece
    """


    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:

        legal_moves = list(board.legal_moves)

        capture_moves = {move for move in legal_moves if board.is_capture(move)}

        check_moves = {move for move in legal_moves if board.gives_check(move)}

        capture_check_moves = capture_moves & check_moves

        # Priority 1: Capture + Check
        if capture_check_moves:
            chosen_move = random.choice(list(capture_check_moves))
            logger.info(f"Capture + Check move played: {chosen_move}")
            return PlayResult(chosen_move, None)

        # Priority 2: Check
        elif check_moves:
            chosen_move = random.choice(list(check_moves))
            logger.info(f"Check move played: {chosen_move}")
            return PlayResult(chosen_move, None)

        # Priority 3: Capture
        elif capture_moves:
            chosen_move = random.choice(list(capture_moves))
            logger.info(f"Capture move played: {chosen_move}")
            return PlayResult(chosen_move, None)

        # Priority 4: Random
        chosen_move = random.choice(legal_moves)
        logger.info(f"Random move played: {chosen_move}")
        return PlayResult(chosen_move, None)
#  endregion CheckAgressiveMove

# region AgressiveCheckMove
class AgressiveCheckMove(ExampleEngine):
    """Value Check & Take pieces highest
       then value take piece
       then value check
    """

    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:

        legal_moves = list(board.legal_moves)

        capture_moves = {move for move in legal_moves if board.is_capture(move)}

        check_moves = {move for move in legal_moves if board.gives_check(move)}

        capture_check_moves = capture_moves & check_moves

        # Priority 1: Capture + Check
        if capture_check_moves:
            chosen_move = random.choice(list(capture_check_moves))
            logger.info(f"Capture + Check move played: {chosen_move}")
            return PlayResult(chosen_move, None)

        # Priority 2: Capture
        elif capture_moves:
            chosen_move = random.choice(list(capture_moves))
            logger.info(f"Capture move played: {chosen_move}")
            return PlayResult(chosen_move, None)

        # Priority 3: Check
        elif check_moves:
            chosen_move = random.choice(list(check_moves))
            logger.info(f"Check move played: {chosen_move}")
            return PlayResult(chosen_move, None)

        # Priority 4: Random
        chosen_move = random.choice(legal_moves)
        logger.info(f"Random move played: {chosen_move}")
        return PlayResult(chosen_move, None)
# endregion AgressiveCheckMove


class SmartAggressiveMove(ExampleEngine):
    """Prioritize valuable captures and checks."""

    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:

        legal_moves = list(board.legal_moves)

        piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9
        }

        capture_moves = {move for move in legal_moves if board.is_capture(move)}

        check_moves = {move for move in legal_moves if board.gives_check(move)}

        capture_check_moves = capture_moves & check_moves

        def best_capture(moves):

            best_move = None
            best_value = 0

            for move in moves:

                captured_piece = board.piece_at(move.to_square)

                if captured_piece:

                    value = piece_values[captured_piece.piece_type]

                    if value > best_value:
                        best_value = value
                        best_move = move

            return best_move

        # Priority 1: Capture + Check
        best_move = best_capture(capture_check_moves)

        if best_move:
            logger.info(f"Capture + Check move played: {best_move}")
            return PlayResult(best_move, None)

        # Priority 2: Capture
        best_move = best_capture(capture_moves)

        if best_move:
            logger.info(f"Capture move played: {best_move}")
            return PlayResult(best_move, None)

        # Priority 3: Check
        if check_moves:
            chosen_move = random.choice(list(check_moves))
            logger.info(f"Check move played: {chosen_move}")
            return PlayResult(chosen_move, None)

        # Priority 4: Random
        chosen_move = random.choice(legal_moves)
        logger.info(f"Random move played: {chosen_move}")
        return PlayResult(chosen_move, None)


class EvaluationTest1(ExampleEngine):
    """Simple evaluation with piece score:
       Possetive for White, Negative for Black
       Simple evaluation will mean try every legal move.
       And evaluate the board to see which one was best.
    """
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9
    }

    def evaluate_board(self, board: chess.Board):

        score = 0

        for piece_type in self.piece_values:

            value = self.piece_values[piece_type]

            #White possetive:
            score += len(board.pieces(piece_type, chess.WHITE)) * value

            #Black negative:
            score -= len(board.pieces(piece_type, chess.BLACK)) * value

        return score

    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:

        legal_moves = list(board.legal_moves)

        best_move = None

        if board.turn == chess.WHITE:
            best_score = -999
        else:
            best_score = 999

        for move in legal_moves:

            board.push(move)
            score = self.evaluate_board(board)
            board.pop()

            if board.turn == chess.WHITE:

                if score > best_score:
                    best_score = score
                    best_move = move

            else:

                if score < best_score:
                    best_score = score
                    best_move = move

        logger.info(f"Best move: {best_move}, Score: {best_score}")

        return PlayResult(best_move, None)


class EvaluationTest2(ExampleEngine):
    """
    Advanced evaluation with piece score:
    Possetive for White, Negative for Black
    Will evaluate and chose the best move.
    within a ceartain number of turns.
    depth=
    """

    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9
    }

    def evaluate_board(self, board: chess.Board):

        score = 0

        for piece_type, value in self.piece_values.items():

            # White pieces = positive
            score += len(board.pieces(piece_type, chess.WHITE)) * value

            # Black pieces = negative
            score -= len(board.pieces(piece_type, chess.BLACK)) * value

        return score

    def minimax(self, board, depth, maximizing):

        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board)

        # White needs possetive
        if maximizing:

            best_score = -999

            for move in board.legal_moves:

                board.push(move)

                score = self.minimax(
                    board,
                    depth - 1,
                    False
                )

                board.pop()

                best_score = max(best_score, score)

            return best_score

        # Black needs negative
        else:

            best_score = 999

            for move in board.legal_moves:

                board.push(move)

                score = self.minimax(
                    board,
                    depth - 1,
                    True
                )

                board.pop()

                best_score = min(best_score, score)

            return best_score


    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:
        start = time.time()
        best_move = None

        maximizing = board.turn == chess.WHITE

        if maximizing:
            best_score = -999
        else:
            best_score = 999

        for move in board.legal_moves:

            board.push(move)

            # Change "depth=" to match the amount of moves to look ahead
            score = self.minimax(
                board,
                depth=2,
                maximizing=not maximizing
            )

            board.pop()

            if maximizing:

                if score > best_score:
                    best_score = score
                    best_move = move

            else:

                if score < best_score:
                    best_score = score
                    best_move = move

        logger.info(f"Best move: {best_move}, Score: {best_score}")
        print("Move took:", time.time() - start)
        return PlayResult(best_move, None)




# fix horizon effect





# board.is_checkmate     -999/999  maybe
"""
if board.is_checkmate():

    board.turn == chess.WHITE:
        return -10000
        
    else:
        return 10000
        
stalemate included
"""

# alpha beta pruning?


class EvaluationTestWithCheckmate(ExampleEngine):
    """
    Advanced evaluation with piece score:
    Possetive for White, Negative for Black
    Will evaluate and chose the best move.
    within a ceartain number of turns.
    depth=
    And can see and avoid checkmate?
    """

    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9
    }

    def evaluate_board(self, board: chess.Board):
        score = 0

        for piece_type, value in self.piece_values.items():
            # White pieces = positive
            score += len(board.pieces(piece_type, chess.WHITE)) * value

            # Black pieces = negative
            score -= len(board.pieces(piece_type, chess.BLACK)) * value

        return score

    def minimax(self, board, depth, maximizing):

        if board.is_checkmate():

            # White is checkmated
            if board.turn == chess.WHITE:
                return -10000

            # Black is checkmated
            else:
                return 10000

        if board.is_stalemate():
            return 0

        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board)

        # White needs possetive
        if maximizing:

            best_score = -999

            for move in board.legal_moves:

                board.push(move)

                score = self.minimax(
                    board,
                    depth - 1,
                    False
                )

                board.pop()

                best_score = max(best_score, score)

            return best_score

        # Black needs negative
        else:

            best_score = 999

            for move in board.legal_moves:

                board.push(move)

                score = self.minimax(
                    board,
                    depth - 1,
                    True
                )

                board.pop()

                best_score = min(best_score, score)

            return best_score


    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:
        start = time.time()
        best_move = None

        maximizing = board.turn == chess.WHITE

        if maximizing:
            best_score = -999
        else:
            best_score = 999

        for move in board.legal_moves:

            board.push(move)

            # Change "depth=" to match the amount of moves to look ahead
            score = self.minimax(
                board,
                depth=2,
                maximizing=not maximizing
            )

            board.pop()

            if maximizing:

                if score > best_score:
                    best_score = score
                    best_move = move

            else:

                if score < best_score:
                    best_score = score
                    best_move = move

        logger.info(f"Best move: {best_move}, Score: {best_score}")
        print("Move took:", time.time() - start)
        return PlayResult(best_move, None)




class AlphaBetaPruning1(ExampleEngine):

    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9
    }

    def evaluate_board(self, board: chess.Board):
        score = 0

        for piece_type, value in self.piece_values.items():
            # White pieces = positive
            score += len(board.pieces(piece_type, chess.WHITE)) * value

            # Black pieces = negative
            score -= len(board.pieces(piece_type, chess.BLACK)) * value

        return score

    def minimax(self, board, depth, maximizing, alpha, beta):

        if board.is_checkmate():

            # White is checkmated
            if board.turn == chess.WHITE:
                return -10000

            # Black is checkmated
            else:
                return 10000

        if board.is_stalemate():
            return 0

        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board)

        # White needs possetive
        if maximizing:

            best_score = float("-inf")

            for move in board.legal_moves:
                board.push(move)

                score = self.minimax(
                    board,
                    depth - 1,
                    False,
                    alpha,
                    beta
                )

                board.pop()

                best_score = max(best_score, score)

                alpha = max(alpha, score)

                if beta <= alpha:
                    break

            return best_score


        # you are here, for now finish black and search



        # Black needs negative
        else:

            best_score = 999

            for move in board.legal_moves:
                board.push(move)

                score = self.minimax(
                    board,
                    depth - 1,
                    True
                )

                board.pop()

                best_score = min(best_score, score)

            return best_score

    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:
        start = time.time()
        best_move = None

        maximizing = board.turn == chess.WHITE

        if maximizing:
            best_score = -999
        else:
            best_score = 999

        for move in board.legal_moves:

            board.push(move)

            # Change "depth=" to match the amount of moves to look ahead
            score = self.minimax(
                board,
                depth=2,
                maximizing=not maximizing
            )

            board.pop()

            if maximizing:

                if score > best_score:
                    best_score = score
                    best_move = move

            else:

                if score < best_score:
                    best_score = score
                    best_move = move

        logger.info(f"Best move: {best_move}, Score: {best_score}")
        print("Move took:", time.time() - start)
        return PlayResult(best_move, None)


