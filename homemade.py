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


# Use this logger variable to print messages to the console or log files.
# logger.info("message") will always print "message" to the console or log file.
# logger.debug("message") will only print "message" if verbose logging is enabled.
logger = logging.getLogger(__name__)


class ExampleEngine(MinimalEngine):
    """An example engine that all homemade engines inherit."""


class RandomMove(ExampleEngine):
    """Get a random move."""

    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:  # noqa: ARG002
        """Choose a random move."""
        return PlayResult(random.choice(list(board.legal_moves)), None)

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


class CheckAgressiveMove(ExampleEngine):
    """Value Check & Take pieces highest
       then value check
       then value take piece
    """


    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:

        legal_moves = list(board.legal_moves)

        capture_moves = []
        check_moves = []

        for move in legal_moves:
            if board.gives_check(move) and board.is_capture(move):
                capture_moves.append(move)
            elif board.gives_check(move):
                check_moves.append(move)
            elif board.is_capture(move):
                capture_moves.append(move)

        if check_moves:
            chosen_move = random.choice(check_moves)
            logger.info(f"Check move played: {chosen_move}")
            return PlayResult(chosen_move, None)

        elif capture_moves:
            chosen_move = random.choice(capture_moves)
            logger.info(f"Aggressive move played: {chosen_move}")
            return PlayResult(chosen_move, None)

        chosen_move = random.choice(legal_moves)
        logger.info(f"Random move played: {chosen_move}")
        return PlayResult(chosen_move, None)


class AgressiveCheckMove(ExampleEngine):
    """Value Check & Take pieces highest
       then value take piece
       then value check
    """

    def search(self, board: chess.Board, *args: HOMEMADE_ARGS_TYPE) -> PlayResult:

        legal_moves = list(board.legal_moves)

        capture_moves = []
        check_moves = []

        for move in legal_moves:
            if board.gives_check(move) and board.is_capture(move):
                capture_moves.append(move)
            elif board.is_capture(move):
                capture_moves.append(move)
            elif board.gives_check(move):
                check_moves.append(move)

        if capture_moves:
            chosen_move = random.choice(capture_moves)
            logger.info(f"Aggressive move played: {chosen_move}")
            return PlayResult(chosen_move, None)

        elif check_moves:
            chosen_move = random.choice(check_moves)
            logger.info(f"Check move played: {chosen_move}")
            return PlayResult(chosen_move, None)

        chosen_move = random.choice(legal_moves)
        logger.info(f"Random move played: {chosen_move}")
        return PlayResult(chosen_move, None)

#     set
