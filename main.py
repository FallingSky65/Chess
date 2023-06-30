import sys, os
import pygame as pg
from random import choice
from math import floor
os.environ['SDL_AUDIODRIVER'] = 'dsp'

pg.init()
screen = pg.display.set_mode()
width, height = pg.display.get_window_size()
midwidth, midheight = width//2, height//2
pg.display.set_caption("Chess using pygame | FallingSky65")
pg.display.set_icon(pg.image.load("Assets/icon.png"))
clock = pg.time.Clock()
FPS = 60

BGCOLOR     = [80, 85, 150]
MOVETEXTCOLORS = [[255, 255, 255], [60, 60, 60]]
BLACKPIECE  = 0
WHITEPIECE  = 1
ID_PAWN     = "P"
ID_BISHOP   = "B"
ID_KNIGHT   = "N"
ID_ROOK     = "R"
ID_QUEEN    = "Q"
ID_KING     = "K"
IMAGESPATH      = os.path.join("Assets", "JohnPablok Cburnett Chess set", "PNGs", "No Shadow", "256h")
IMAGESPATHSUB   = "_png_256px.png"

blackPieces = []
whitePieces = []


def sign(x) -> int:
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


class Piece():
    def __init__(self, PieceID, PieceColor, size, board, i, j) -> None:
        self.ID = PieceID
        self.inHand = False
        self.hasMoved = False
        if PieceColor == BLACKPIECE:
            blackPieces.append(self)
        else:
            whitePieces.append(self)
        self.board = board
        self.i = i
        self.j = j
        pieceName = ""
        if PieceID == ID_PAWN:
            pieceName = "pawn"
        elif PieceID == ID_BISHOP:
            pieceName = "bishop"
        elif PieceID == ID_KNIGHT:
            pieceName = "knight"
        elif PieceID == ID_ROOK:
            pieceName = "rook"
        elif PieceID == ID_QUEEN:
            pieceName = "queen"
        elif PieceID == ID_KING:
            pieceName = "king"
        self.pieceName = pieceName
        self.pieceColor = PieceColor
        if PieceColor == BLACKPIECE:
            pieceName = "b_" + pieceName
        elif PieceColor == WHITEPIECE:
            pieceName = "w_" + pieceName
        self.image = pg.image.load(os.path.join(IMAGESPATH, pieceName + IMAGESPATHSUB))
        self.image = pg.transform.scale(self.image, (size * self.image.get_width() / self.image.get_height(), size))
        self.updateRect()
        self.validMoves = []
        self.generateValidMoves()

    def draw(self, screen, boardCenter, boardSize) -> None:
        self.updateRect()
        if self.inHand:
            # mx, my = pg.mouse.get_pos()
            # screen.blit(self.image, (mx - self.image.get_width()/2, my - self.image.get_height()/2))

            screen.blit(self.image, self.imageRect)
        else:
            screen.blit(self.image, self.imageRect)

    def getRect(self) -> pg.Rect:
        return self.imageRect

    def updateRect(self) -> None:
        centeredLeft = self.board.center[0] - self.board.size / 2 + self.board.size / 16
        centeredBottom = self.board.center[1] + self.board.size / 2 - self.board.size / 16
        self.imageRect = self.image.get_rect(
            center=(centeredLeft + self.i * self.board.size / 8, centeredBottom - self.j * self.board.size / 8))

    def validMove(self, x, y) -> bool:
        if x == self.i and y == self.j:
            return False

        if self.board.board[x][y] != None and self.pieceColor == self.board.board[x][y].pieceColor:
            return False

        if self.ID == ID_PAWN:
            if self.board.board[x][y] == None:
                return x == self.i and ((y + (-1 if self.pieceColor == WHITEPIECE else 1) == self.j) or (
                            (y + (-2 if self.pieceColor == WHITEPIECE else 2) == self.j) and not self.hasMoved and
                            self.board.board[x][self.j + (1 if self.pieceColor == WHITEPIECE else -1)] == None))
            else:
                return abs(x - self.i) == 1 and (y + (-1 if self.pieceColor == WHITEPIECE else 1) == self.j)

        if self.ID == ID_KING:
            return abs(x - self.i) <= 1 and abs(y - self.j) <= 1

        if self.ID == ID_KNIGHT:
            return (abs(x - self.i) == 1 and abs(y - self.j) == 2) or (abs(x - self.i) == 2 and abs(y - self.j) == 1)

        if self.ID == ID_ROOK:
            canVert = False
            canHorz = False
            if y == self.j:
                canHorz = True
                for ii in range(min(self.i, x) + 1, max(self.i, x)):
                    if self.board.board[ii][y] != None:
                        canHorz = False
                        break
            if x == self.i:
                canVert = True
                for jj in range(min(self.j, y) + 1, max(self.j, y)):
                    if self.board.board[x][jj] != None:
                        canVert = False
                        break
            return canHorz or canVert

        if self.ID == ID_BISHOP:
            canDiag = True
            if abs(x - self.i) != abs(y - self.j):
                canDiag = False
            else:
                for ii in range(1, abs(x - self.i)):
                    if self.board.board[self.i + sign(x - self.i) * ii][self.j + sign(y - self.j) * ii] != None:
                        canDiag = False
            return canDiag

        if self.ID == ID_QUEEN:
            canDiag = True
            if abs(x - self.i) != abs(y - self.j):
                canDiag = False
            else:
                for ii in range(1, abs(x - self.i)):
                    if self.board.board[self.i + sign(x - self.i) * ii][self.j + sign(y - self.j) * ii] != None:
                        canDiag = False

            canVert = False
            canHorz = False
            if y == self.j:
                canHorz = True
                for ii in range(min(self.i, x) + 1, max(self.i, x)):
                    if self.board.board[ii][y] != None:
                        canHorz = False
                        break
            if x == self.i:
                canVert = True
                for jj in range(min(self.j, y) + 1, max(self.j, y)):
                    if self.board.board[x][jj] != None:
                        canVert = False
                        break

            return canHorz or canVert or canDiag

        return False

    def generateValidMoves(self) -> None:
        self.validMoves.clear()
        for i in range(8):
            for j in range(8):
                if self.validMove(i, j):
                    self.validMoves.append([i, j])

    def kill(self) -> None:
        if self.pieceColor == BLACKPIECE:
            blackPieces.remove(self)
        else:
            whitePieces.remove(self)


class Board():
    def __init__(self, boardsize, boardcenter) -> None:
        self.size = boardsize
        self.center = boardcenter
        self.board = [[None for i in range(8)] for i in range(8)]
        self.classicSetup()
        self.pieceMovementHandler = None

    # Chess Board Setup
    # 8   R N B Q K B N R  Black
    # 7   P P P P P P P P
    # 6
    # 5
    # 4
    # 3
    # 2   P P P P P P P P
    # 1   R N B Q K B N R  White
    #
    #     a b c d e f g h
    def classicSetup(self) -> None:
        whitePieces = ['P' + file + '2' for file in 'abcdefgh'] + ['Ra1', 'Nb1', 'Bc1', 'Qd1', 'Ke1', 'Bf1', 'Ng1',
                                                                   'Rh1']
        blackPieces = ['P' + file + '7' for file in 'abcdefgh'] + ['Ra8', 'Nb8', 'Bc8', 'Qd8', 'Ke8', 'Bf8', 'Ng8',
                                                                   'Rh8']

        for piece in whitePieces:
            self.setPiece(piece[1:3], piece[0], WHITEPIECE)
        for piece in blackPieces:
            self.setPiece(piece[1:3], piece[0], BLACKPIECE)

    def setPiece(self, loc, pieceID, pieceColor) -> None:
        # loc should be in format a1 - h8
        x = self.letterToInt(loc[0])
        y = int(loc[1]) - 1
        self.board[x][y] = Piece(pieceID, pieceColor, 0.75 * self.size / 8, self, x, y)

    def letterToInt(self, char) -> int:
        # a  -> 0, b  -> 1 ...
        char = char.lower()
        return ord(char[0]) - 97

    def updatePieces(self) -> None:
        for piece in blackPieces + whitePieces:
            piece.generateValidMoves()

    def drawBoard(self, screen) -> None:
        Left = self.center[0] - self.size / 2
        Top = self.center[1] - self.size / 2
        Bottom = self.center[1] + self.size / 2

        EDGETHICKNESSOUTER = self.size / 32
        EDGETHICKNESSINNER = self.size / 96
        DOTRADIUS = self.size / 64

        DARKSQUARECOLOR = (101, 62, 62)  # or (54, 54, 54)
        LIGHTSQUARECOLOR = (144, 86, 72)  # or (89, 89, 89)
        BOARDEDGEOUTERCOLOR = (56, 56, 56)
        BOARDEDGEINNERCOLOR = (20, 20, 20)
        MOVECOLOR = (50, 50, 50)

        pg.draw.rect(screen, BOARDEDGEOUTERCOLOR,
                     [Left - EDGETHICKNESSOUTER, Top - EDGETHICKNESSOUTER, self.size + EDGETHICKNESSOUTER * 2,
                      self.size + EDGETHICKNESSOUTER * 2])
        pg.draw.rect(screen, BOARDEDGEINNERCOLOR,
                     [Left - EDGETHICKNESSINNER, Top - EDGETHICKNESSINNER, self.size + EDGETHICKNESSINNER * 2,
                      self.size + EDGETHICKNESSINNER * 2])

        for i in range(8):
            for j in range(8):
                if (i + j) % 2 == 0:
                    pg.draw.rect(screen, DARKSQUARECOLOR,
                                 [Left + i * self.size / 8, Bottom - (j + 1) * self.size / 8, self.size / 8,
                                  self.size / 8])
                else:
                    pg.draw.rect(screen, LIGHTSQUARECOLOR,
                                 [Left + i * self.size / 8, Bottom - (j + 1) * self.size / 8, self.size / 8,
                                  self.size / 8])
                if self.pieceMovementHandler.pieceInHand != None:
                    if [i, j] in self.pieceMovementHandler.pieceInHand.validMoves:
                        if self.board[i][j] == None:
                            pg.draw.circle(screen, MOVECOLOR, (
                            Left + (i * self.size / 8) + self.size / 16, Bottom - (j + 0.5) * self.size / 8), DOTRADIUS)
                        else:
                            pg.draw.circle(screen, MOVECOLOR, (
                            Left + (i * self.size / 8) + self.size / 16, Bottom - (j + 0.5) * self.size / 8),
                                           self.size / 17, int(self.size / 128))
        for piece in blackPieces + whitePieces:
            piece.draw(screen, self.center, self.size)


class PieceMovementHandler():
    def __init__(self, board, ai = None) -> None:
        self.board = board
        self.ai = ai
        self.pieceInHand = None
        self.colorToMove = WHITEPIECE
        self.moveNumber = 1
        self.moveLog = []

    def swapColors(self) -> None:
        if self.colorToMove == WHITEPIECE:
            self.colorToMove = BLACKPIECE
        else:
            self.colorToMove = WHITEPIECE

    def makeMove(self, piece, moveToX, moveToY) -> None:
        self.board.board[piece.i][piece.j] = None

        piece.i = moveToX
        piece.j = moveToY

        if self.board.board[piece.i][piece.j] != None:
            self.board.board[piece.i][piece.j].kill()

        self.board.board[piece.i][piece.j] = piece
        piece.hasMoved = True
        piece.updateRect()
        self.board.updatePieces()
        self.swapColors()

    def handleMouseClickDown(self, event) -> None:
        mousePos = pg.mouse.get_pos()
        mx = mousePos[0]
        my = mousePos[1]
        if event.button == 1:  # left click
            if self.pieceInHand == None:
                for piece in blackPieces + whitePieces:
                    r = piece.getRect()
                    if r.left <= mx and mx <= r.right and r.top <= my and my <= r.bottom:
                        if piece.pieceColor == self.colorToMove:
                            self.pieceInHand = piece
                            self.pieceInHand.inHand = True
                            break
            else:
                for piece in blackPieces + whitePieces:
                    r = piece.getRect()
                    if r.left <= mx and mx <= r.right and r.top <= my and my <= r.bottom:
                        if piece.pieceColor == self.colorToMove:
                            self.pieceInHand.inHand = False
                            self.pieceInHand = piece
                            self.pieceInHand.inHand = True
                            return

                bcenterx, bcentery = board.center
                bsize = board.size
                if abs(mx - bcenterx) <= bsize / 2 and abs(my - bcentery) <= bsize / 2:
                    moveToX = floor((mx - bcenterx + bsize / 2) / (bsize / 8))
                    moveToY = 7 - floor((my - bcentery + bsize / 2) / (bsize / 8))

                    if not self.pieceInHand.validMove(moveToX, moveToY):
                        self.pieceInHand.inHand = False
                        self.pieceInHand = None
                    else:
                        move = f"{self.moveNumber}. {'' if self.pieceInHand.ID == ID_PAWN else self.pieceInHand.ID}{'abcdefgh'[self.pieceInHand.i]}{self.pieceInHand.j + 1}{'-' if self.board.board[moveToX][moveToY] == None else 'x'}{'abcdefgh'[moveToX]}{moveToY + 1}"
                        self.moveLog.append(move)
                        print(move)
                        self.moveNumber += 1

                        self.makeMove(self.pieceInHand, moveToX, moveToY)

                        self.pieceInHand.inHand = False
                        self.pieceInHand = None

                        self.ai.makeMove()


        elif event.button == 3:  # right click
            ...


class ChessAI():
    def __init__(self, board, pieceMovementHandler, color, pieces) -> None:
        self.board = board
        self.pieceMovementHandler = pieceMovementHandler
        self.color = color
        self.pieces = pieces

    def makeMove(self) -> None:
        self.makeRandomMove()

    def makeRandomMove(self) -> None:
        if sum([len(piece.validMoves) for piece in self.pieces]) == 0:
            return
        randomPiece = choice(self.pieces)
        while len(randomPiece.validMoves) == 0:
            randomPiece = choice(self.pieces)
        randomMove = choice(randomPiece.validMoves)
        self.pieceMovementHandler.makeMove(randomPiece, randomMove[0], randomMove[1])

board = Board(0.9 * min(width, height), (min(midwidth, midheight), min(midwidth, midheight)))
pieceMovementHandler = PieceMovementHandler(board)
chessAI = ChessAI(board, pieceMovementHandler, BLACKPIECE, blackPieces)
board.pieceMovementHandler = pieceMovementHandler
pieceMovementHandler.ai = chessAI

movesFont = pg.font.SysFont("impact", int(height / 24))


def drawText(screen) -> None:
    TOP = 0.025 * height
    LEFT = 1 * height
    for move in pieceMovementHandler.moveLog[::2]:
        moveText = movesFont.render(move, True, MOVETEXTCOLORS[0])
        screen.blit(moveText, (LEFT, TOP))
        TOP += height / 20

    TOP = 0.025 * height
    LEFT = 1.3 * height
    for move in pieceMovementHandler.moveLog[1::2]:
        moveText = movesFont.render(move, True, MOVETEXTCOLORS[1])
        screen.blit(moveText, (LEFT, TOP))
        TOP += height / 20


while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        if event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()
        if event.type == pg.MOUSEBUTTONDOWN:
            pieceMovementHandler.handleMouseClickDown(event)

    screen.fill(BGCOLOR)

    board.drawBoard(screen)
    drawText(screen)

    pg.display.update()
    clock.tick(FPS)