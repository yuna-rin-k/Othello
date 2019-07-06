#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import json
import logging
import random
import webapp2
import time

# Reads json description of the board and provides simple interface.
class Game:
    # Takes json or a board directly.
    def __init__(self, body=None, board=None):
                if body:
                        game = json.loads(body)
                        self._board = game["board"]
                else:
                        self._board = board

    # Returns piece on the board.
    # 0 for no pieces, 1 for player 1, 2 for player 2.
    # None for coordinate out of scope.
    def Pos(self, x, y):
        return Pos(self._board["Pieces"], x, y)

    # Returns who plays next.
    def Next(self):
        return self._board["Next"]

    # Returns the array of valid moves for next player.
    # Each move is a dict
    #   "Where": [x,y]
    #   "As": player number
    def ValidMoves(self):
                moves = []
                for y in xrange(1,9):
                        for x in xrange(1,9):
                                move = {"Where": [x,y],
                                        "As": self.Next()}
                                if self.NextBoardPosition(move):
                                        moves.append(move)
                return moves

    # Helper function of NextBoardPosition.  It looks towards
    # (delta_x, delta_y) direction for one of our own pieces and
    # flips pieces in between if the move is valid. Returns True
    # if pieces are captured in this direction, False otherwise.
    def __UpdateBoardDirection(self, new_board, x, y, delta_x, delta_y):
        player = self.Next()
        opponent = 3 - player
        look_x = x + delta_x
        look_y = y + delta_y
        flip_list = []
        while Pos(new_board, look_x, look_y) == opponent:
            flip_list.append([look_x, look_y])
            look_x += delta_x
            look_y += delta_y
        if Pos(new_board, look_x, look_y) == player and len(flip_list) > 0:
                        # there's a continuous line of our opponents
                        # pieces between our own pieces at
                        # [look_x,look_y] and the newly placed one at
                        # [x,y], making it a legal move.
            SetPos(new_board, x, y, player)
            for flip_move in flip_list:
                flip_x = flip_move[0]
                flip_y = flip_move[1]
                SetPos(new_board, flip_x, flip_y, player)
            return True
        return False

    # Takes a move dict and return the new Game state after that move.
    # Returns None if the move itself is invalid.
    def NextBoardPosition(self, move):
        x = move["Where"][0]
        y = move["Where"][1]
        if self.Pos(x, y) != 0:
                        # x,y is already occupied.
                        return None
        new_board = copy.deepcopy(self._board)
        pieces = new_board["Pieces"]

        if not (self.__UpdateBoardDirection(pieces, x, y, 1, 0)
                        | self.__UpdateBoardDirection(pieces, x, y, 0, 1)
                | self.__UpdateBoardDirection(pieces, x, y, -1, 0)
                | self.__UpdateBoardDirection(pieces, x, y, 0, -1)
                | self.__UpdateBoardDirection(pieces, x, y, 1, 1)
                | self.__UpdateBoardDirection(pieces, x, y, -1, 1)
                | self.__UpdateBoardDirection(pieces, x, y, 1, -1)
                | self.__UpdateBoardDirection(pieces, x, y, -1, -1)):
                        # Nothing was captured. Move is invalid.
                return None
                
                # Something was captured. Move is valid.
        new_board["Next"] = 3 - self.Next()
        return Game(board=new_board)

# Returns piece on the board.
# 0 for no pieces, 1 for player 1, 2 for player 2.
# None for coordinate out of scope.
#
# Pos and SetPos takes care of converting coordinate from 1-indexed to
# 0-indexed that is actually used in the underlying arrays.
def Pos(board, x, y):
    if 1 <= x and x <= 8 and 1 <= y and y <= 8:
        return board[y-1][x-1]
    return None

# Set piece on the board at (x,y) coordinate
def SetPos(board, x, y, piece):
    if x < 1 or 8 < x or y < 1 or 8 < y or piece not in [0,1,2]:
        return False
    board[y-1][x-1] = piece

# Debug function to pretty print the array representation of board.
def PrettyPrint(board, nl="<br>"):
    s = ""
    for row in board:
        for piece in row:
            s += str(piece)
        s += nl
    return s

def PrettyMove(move):
    m = move["Where"]
    return '%s%d' % (chr(ord('A') + m[0] - 1), m[1])

class MainHandler(webapp2.RequestHandler):
    # Handling GET request, just for debugging purposes.
    # If you open this handler directly, it will show you the
    # HTML form here and let you copy-paste some game's JSON
    # here for testing.
    def get(self):
        if not self.request.get('json'):
          self.response.write("""
<body><form method=get>
Paste JSON here:<p/><textarea name=json cols=80 rows=24></textarea>
<p/><input type=submit>
</form>
</body>
""")
          return
        else:
          g = Game(self.request.get('json'))
          self.pickMove(g)

    def post(self):
        # Reads JSON representation of the board and store as the object.
        g = Game(self.request.body)
        # Do the picking of a move and print the result.
        self.pickMove(g)


    def pickMove(self, g):
        # Gets all valid moves.
        valid_moves = g.ValidMoves()
        if len(valid_moves) == 0:
            # Passes if no valid moves.
            self.response.write("PASS")
        else:
            # Chooses a valid move randomly if available.
                # TO STEP STUDENTS:
                # You'll probably want to change how this works, to do something
                # more clever than just picking a random move.

            #move = random.choice(valid_moves)
            countOfPiece = 0
            for i in xrange(1,9):
                for j in xrange(1,9):
                    if g.Pos(i, j) != 0:
                        countOfPiece = countOfPiece + 1
            begin = time.time()
            (score, move) = MainHandler.maxmin(self, 4, g, g, countOfPiece, g.Next(), begin)
            self.response.write(PrettyMove(move))


    def maxmin(self, depth, g, prev_g, countOfPiece, player, begin):
        move = {"Where":[0,0]}
        return MainHandler.alphabeta(self, depth, g, prev_g, -100000000, 1000000000, countOfPiece, True, player,move, begin)


    def alphabeta(self, depth, g, prev_g, alpha, beta, countOfPiece, isMe, player, move, begin):

        end = time.time()

        #if countOfPiece <= 12 and depth == 0:
            #return MainHandler.earlyStageScore(self, g, prev_g, player), move


        if end - begin > 12.5:
            #if countOfPiece <= 18:
                #return MainHandler.earlyStageScore(self, g, prev_g, player), move
            #if countOfPiece < 55:
            if countOfPiece < 53:
                return MainHandler.middleStageScore(self,g, player), move
            else:
                return MainHandler.lateStageScore(self, g, player), move

        if isMe:
            moves = g.ValidMoves()
            for move in moves:
                gameBoard = g.NextBoardPosition(move)
                (alpha0, move0)  = MainHandler.alphabeta(self, depth-1, gameBoard, g, alpha, beta, countOfPiece, False, player, move, begin)
                alpha = max(alpha, alpha0)
                if alpha >= beta:
                    break
            return alpha, move

        else:
            moves = g.ValidMoves()
            for move in moves:
                gameBoard = g.NextBoardPosition(move)
                (beta0, move0) = MainHandler.alphabeta(self, depth-1, gameBoard, g, alpha, beta,countOfPiece, True, player, move, begin)
                beta = min(beta, beta0)
                if alpha >= beta:
                    break
            return beta, move

    def earlyStageScore(self, g, prev_g, player):

        turnOverPieces = []
        degreeOfFreedom = 0
        angle = 0

        print('pos')
        print(g.Pos(1,8))
        if player == 1:

            if g.Pos(1,1) == 1:
                angle = angle + 100
            if g.Pos(1,8) == 1:
                print('1, 8')
                angle = angle + 100
                print(angle)
            if g.Pos(8,1) == 1:
                print('8, 1')
                angle = angle + 100
            if g.Pos(8,8) == 1:
                angle = angle + 100

            if g.Pos(1,1) == 2:
                angle = angle - 100
            if g.Pos(1,8) == 2:
                angle = angle - 100
            if g.Pos(8,1) == 2:
                angle = angle - 100
            if g.Pos(8,8) == 2:
               angle = angle - 100


            for i in xrange(1,9):
                for j in xrange(1,9):
                    if prev_g.Pos(i,j) == 1 and g.Pos(i,j) == 2:
                        piece = {"Where":[j,i]}
                        turnOverPieces.append(piece)

        if player == 2:

            if g.Pos(1,1) == 2:
                angle = angle + 100
            if g.Pos(1,8) == 2:
                angle = angle + 100
            if g.Pos(8,1) == 2:
                angle = angle + 100
            if g.Pos(8,8) == 2:
                angle = angle + 100

            if g.Pos(1,1) == 1:
                angle = angle - 100
            if g.Pos(1,8) == 1:
                angle = angle - 100
            if g.Pos(8,1) == 1:
                angle = angle - 100
            if g.Pos(8,8) == 1:
                angle = angle - 100


            for i in xrange(1,9):
                for j in xrange(1,9):
                    if prev_g.Pos(i,j) == 2 and g.Pos(i,j) == 1:
                        piece = {"Where":[j,i]}
                        turnOverPieces.append(piece)


        for piece in turnOverPieces:

            x = piece["Where"][0]
            y = piece["Where"][1]

            if g.Pos(x+1,y) == 0:
                degreeOfFreedom = degreeOfFreedom + 1

            if g.Pos(x,y+1) == 0:
                degreeOfFreedom = degreeOfFreedom + 1

            if g.Pos(x-1,y) == 0:
                degreeOfFreedom = degreeOfFreedom + 1

            if g.Pos(x,y-1) == 0:
                degreeOfFreedom = degreeOfFreedom + 1

            if g.Pos(x+1,y+1) == 0:
                degreeOfFreedom = degreeOfFreedom + 1

            if g.Pos(x-1,y+1) == 0:
                degreeOfFreedom = degreeOfFreedom + 1

            if g.Pos(x+1,y-1) == 0:
                degreeOfFreedom = degreeOfFreedom + 1

            if g.Pos(x-1,y-1) == 0:
                degreeOfFreedom = degreeOfFreedom + 1

        print(angle)

        return degreeOfFreedom + angle


    def middleStageScore(self,g, player):

        pieceScore = MainHandler.calcPieceScore(self, g, player)
        numOfmoves = len(g.ValidMoves())
        return pieceScore + numOfmoves*2


    #def pattern(self, g, player):


    def calcPieceScore(self, g, player):

        black = 0 
        white = 0
                      #1                            #2                                          #3                                #4                                  #5                                  #6                              #7
        scores = [500,-100,50,50,50,50,-100,500],[-100, -100, -50, -50, -50, -50, -100, -100],[50, -50, 0, 10, 10, 0, -50, 50],[50, -50, 10, 15, 15, 10, -50, 50],[50, -50, 10, 15, 15, 10, -50, 50],[50, -50, 0, 10, 10, 0, -50, 50],[-100, -100, -50, -50, -50, -50, -100, -100],[500,-100,60,60,60,60,-100,500]
        for i in range(8):
            for j in range(8):
                if g.Pos(i, j) == 1:
                    black = black + scores[i][j]
                elif g.Pos(i, j) == 2:
                    white = white + scores[i][j]

        if player == 1:
            return black - white

        return white - black




    def lateStageScore(self, g, player):

        black = 0
        white = 0
        for i in range(8):
            for j in range(8):
                if g.Pos(i,j) == 1:
                    black = black + 1
                if g.Pos(i,j) == 2:
                    white = white + 1

        if player == 1:
            return black - white

        return white - black

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
