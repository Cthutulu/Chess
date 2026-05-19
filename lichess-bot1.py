from lib.lichess_bot import start_program
import sys

if __name__ == "__main__":

    CONFIG = "config-bot1.yml"

    sys.argv = ["lichess-bot1.py", "--config", CONFIG]

    start_program()