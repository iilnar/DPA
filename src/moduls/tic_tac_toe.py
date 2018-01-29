from answer import AssistantAnswer
from collections import defaultdict
from enum import Enum
from PIL import Image, ImageFont, ImageDraw
from string import ascii_uppercase
from configs.config_constants import TicTacToeFontPath
from io import BytesIO

class TicTacToeModule:

    def __init__(self, config):
        self.is_started = False
        self.__game = None
        self.__config = config

    @property
    def is_active(self):
        return self.is_started


    def run(self, assistant, parameters_dict):
        intent = parameters_dict["Intent"]
        answer = None
        if intent == "Start Tic-Tac-Toe Game":
            answer = self.start(assistant, parameters_dict)
        elif intent == "Turn":
            answer = self.turn(assistant, parameters_dict)
        return answer

    def start(self, assistant, parameters_dict):
        self.is_started = True
        self.__game = TicTacToeLogic(font_path=self.__config[TicTacToeFontPath])
        board = self.__game.get_image_board()
        return AssistantAnswer(None, message_str="Start TicTacToe Game", picture=board)

    def turn(self, assistant, parameters_dict):
        pos = parameters_dict["Position"].lower()
        x_pos = (ord(pos[0]) - ord("a"))
        y_pos = int(pos[1])-1
        self.__game.move((x_pos, y_pos))
        game_status = self.__game.get_status()[0]
        board = self.__game.get_image_board()
        par = {}
        if game_status == GameStatus.PLAYING:
            message_key = "tictactoe_bot_turn"
        elif game_status == GameStatus.WIN:
            message_key = "tictactoe_win"
            self.is_started = False
        elif game_status == GameStatus.LOSE:
            message_key = "tictactoe_lose"
            self.is_started = False
        elif game_status == GameStatus.ERROR:
            message_key = "tictactoe_error"
            error_message = self.__game.get_status()[1]
            par["message"] = error_message
        else:
            message_key = "tictactoe_draw_error"

        return AssistantAnswer(message_key, par, picture=board)


class GameStatus(Enum):
    PLAYING, WIN, LOSE, DRAW, ERROR = range(5)


class TicTacToe:
    _EMPTY = "."

    def __init__(self, n=3):
        self.n = n
        self.board = [[TicTacToe._EMPTY for _ in range(self.n)] for _ in range(self.n)]

    def check_game(self):
        def check_seq(seq):
            return seq[0] != TicTacToe._EMPTY and seq[0] * self.n == seq

        for i in range(self.n):
            row = "".join(self.board[i])
            col = "".join(self.board[j][i] for j in range(self.n))
            if check_seq(col):
                return col[0], tuple((j, i) for j in range(self.n))
            if check_seq(row):
                return row[0], tuple((i, j) for j in range(self.n))

        main_dia = "".join(self.board[i][i] for i in range(self.n))
        side_dia = "".join(self.board[i][self.n - i - 1] for i in range(self.n))
        if check_seq(main_dia):
            return main_dia[0], tuple((i, i) for i in range(self.n))
        if check_seq(side_dia):
            return side_dia[0], tuple((i, self.n - i - 1) for i in range(self.n))
        return TicTacToe._EMPTY, None

    def _can_move(self):
        for i in range(self.n):
            for j in range(self.n):
                if self.board[i][j] == TicTacToe._EMPTY:
                    return True
        return False

    def game_status(self):
        who_wins, _ = self.check_game()
        if who_wins != TicTacToe._EMPTY:
            return GameStatus.WIN, who_wins
        if not self._can_move():
            return GameStatus.DRAW, "Board is full"
        return GameStatus.PLAYING, None

    def make_move(self, xy, player):
        x, y = xy
        if self.game_status()[0] in (GameStatus.LOSE, GameStatus.DRAW, GameStatus.WIN):
            return GameStatus.ERROR, "Game already is over"

        if x < 0 or self.n <= x or y < 0 or self.n <= y:
            return GameStatus.ERROR, "Board out of range"
        if self.board[x][y] != ".":
            return GameStatus.ERROR, "Cell is not empty"
        self.board[x][y] = player
        return self.game_status()


class SillyBot:
    def __init__(self, *args, **kwargs):
        pass

    def move(self, board):
        for i in range(len(board)):
            for j in range(len(board[i])):
                if board[i][j] == TicTacToe._EMPTY:
                    return i, j


class TicTacToeLogic:

    _FIGURES = ["X", "O"]
    def __init__(self, n=3, font_path=""):
        is_bot_first = 0

        self.__field_size = n
        self.plr_fig = self._FIGURES[is_bot_first]
        self.state = TicTacToe(self.__field_size)
        self.bot = SillyBot(self.__field_size)
        self.bot_fig = self._FIGURES[1-is_bot_first]
        self.image = Board(n, font_path)

        if is_bot_first:
            self.state.make_move(self.bot_fig, self.bot.move(self.state.board))

        self.status = self.state.game_status()

    def move(self, xy):
        self.status = self.state.make_move(xy, self.plr_fig)
        if self.status[0] != GameStatus.ERROR:
            self.image.put(xy, self.plr_fig)
        if self.status[0] == GameStatus.WIN:
            _, positions = self.state.check_game()
            self.image.straight_line(positions[0], positions[-1])

        if self.status[0] != GameStatus.PLAYING:
            return self.get_board()

        bot_xy = self.bot.move(self.state.board)
        self.status = self.state.make_move(bot_xy, self.bot_fig)
        if self.status[0] != GameStatus.ERROR:
            self.image.put(bot_xy, self.bot_fig)
        if self.status[0] == GameStatus.WIN:
            _, positions = self.state.check_game()
            self.image.straight_line(positions[0], positions[-1])
        return self.get_board()

    def get_status(self):
        code, comment = self.status
        if code == GameStatus.WIN:
            if comment != self.plr_fig:
                code, comment = GameStatus.LOSE, self.plr_fig
        if code == GameStatus.LOSE:
            if comment != self.plr_fig:
                code, comment = GameStatus.WIN, self.plr_fig
        return code, comment

    def get_board(self):
        return "".join("".join(row) for row in self.state.board)

    def get_image_board(self):
        out = BytesIO()
        out.name = "Board"
        self.image.im.save(out, format="PNG")
        out.seek(0)
        return out

    @property
    def field_size(self):
        return self.__field_size


class Board:
    def __init__(self, rows=3, font_path=""):
        self.cell = 100
        self.rows = rows
        self.pad = 20
        self.board = self.cell * rows
        self.header = int(self.cell / 2)
        self.pix = self.header + self.board
        self.width = 10

        self.centers = []
        for j in range(rows):
            centers = []
            for i in range(rows):
                posx = self.header + i * self.cell + self.cell / 2
                posy = self.header + j * self.cell + self.cell / 2
                centers.append((posx, posy))
            self.centers.append(centers)

        self.im = Image.new('RGBA', (self.pix, self.pix), (255, 255, 255, 0))
        draw = ImageDraw.Draw(self.im)

        common = {
            "fill": "blue",
            "width": self.width
        }

        draw.line((0, self.header, self.pix, self.header), **common)
        draw.line((self.header, 0, self.header, self.pix), **common)

        for i in range(1, self.rows):
            pos = i * (self.board / self.rows) + self.header
            draw.line((0, pos, self.pix, pos), **common)
            draw.line((pos, 0, pos, self.pix), **common)

        font = ImageFont.truetype(font_path, 30)

        for i in range(self.rows):
            pos = i * (self.board / self.rows) + self.header + self.cell / 2
            fsize = font.getsize(str(i+1))
            draw.text((pos - fsize[0] / 2, self.header / 2 - fsize[1]), str(i+1), fill="red", font=font)
            letter = ascii_uppercase[i]
            fsize2 = font.getsize(letter)
            draw.text((self.header / 2 - fsize2[0] / 2, pos - fsize2[1] / 2), letter, fill="red", font=font)

    def put(self, xy, kind):
        x, y = xy
        cen = self.centers[x][y]

        lcx, lcy = cen[0] - self.cell / 2 + self.pad, cen[1] - self.cell / 2 + self.pad
        rcx, rcy = cen[0] + self.cell / 2 - self.pad, cen[1] + self.cell / 2 - self.pad

        draw = ImageDraw.Draw(self.im)
        if kind == "O":
            draw.ellipse((lcx, lcy, rcx, rcy), fill="red")
            draw.ellipse((lcx+self.width, lcy+self.width, rcx-self.width, rcy-self.width), fill="white")
        elif kind == "X":
            draw.line((lcx, lcy, rcx, rcy), fill="red", width=10)
            draw.line((lcx, rcy, rcx, lcy), fill="red", width=10)

    def straight_line(self, from_xy, to_xy):
        draw = ImageDraw.Draw(self.im)
        fx, fy = from_xy
        tx, ty = to_xy
        lcx, lcy = self.centers[fx][fy]
        rcx, rcy = self.centers[tx][ty]
        draw.line((lcx, lcy, rcx, rcy), fill="yellow", width=10)
