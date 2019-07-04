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
            for i in range(8):
                for j in range(8):
                    if g.Pos(i, j) != 0:
                        countOfPiece = countOfPiece + 1

            move = {"Where": [1, 1]}
            nextBoard = g.NextBoardPosition(move)

            (score, move) = MainHandler.maxmin(self, g, 4, countOfPiece, move, nextBoard)
            self.response.write(PrettyMove(move))


    def maxmin(self, g, depth, countOfPiece, move, nextBoard):
        firstMove = {"Where":[0,0]}
        return MainHandler.alphabeta(self, depth, g, -100000000, 1000000000, countOfPiece, True, move, nextBoard)


    def alphabeta(self, depth, g, alpha, beta, countOfPiece, isBlack, move, nextBoard):


        if depth == 0:
        
            return MainHandler.calcScore(self, g, move, nextBoard), move

        if isBlack:
            for move in g.ValidMoves():
                nextBoard = g.NextBoardPosition(move)
                (alpha0, move0)  = MainHandler.alphabeta(self, depth-1, g, alpha, beta, countOfPiece, False, move, nextBoard)
                alpha = max(alpha, alpha0)
                if alpha >= beta:
                    break
            return alpha, move

        else:
            for move in g.ValidMoves():
                nextBoard = g.NextBoardPosition(move)
                (beta0, move0) = MainHandler.alphabeta(self, depth-1, g, alpha, beta,countOfPiece, True, move, nextBoard)
                beta = min(beta, beta0)
                if alpha >= beta:
                    break
            return beta, move


    def calcScore(self, g, move, nextBoard):

        if MainHandler.isAngle(self, move):
            return 7000000

        if MainHandler.ngPos(self, move, g):
            return -1000000

        if MainHandler.ngPos_2(self, move):
            return -100000

        if MainHandler.isEdge(self, move):
            return 20000

         
        numOfValiedMoves = len(g.ValidMoves()) * 5
        pieceScore = MainHandler.calcPieceScore(self, g, nextBoard)
        score = numOfValiedMoves + pieceScore
        return score+500


    def calcPieceScore(self, g, nextBoard):

        black = 0  #1                                 #2                                          #3                                #4                                  #5                                  #6                              #7
        scores = [200,-100,50,50,50,50,-100,200],[-100, -100, -50, -50, -50, -50, -100, -100],[50, -50, 0, 10, 10, 0, -50, 50],[50, -50, 10, 15, 15, 10, -50, 50],[50, -50, 10, 15, 15, 10, -50, 50],[50, -50, 0, 10, 10, 0, -50, 50],[-100, -100, -50, -50, -50, -50, -100, -100],[200,-100,60,60,60,60,-100,200]
        for i in range(8):
            for j in range(8):
                if Game.Pos(nextBoard,i, j) == 1:
                    black = black + scores[i][j]

        return black

    
    def isAngle(self,move):

        x = move["Where"][0]
        y = move["Where"][1]

        if x == 1 and y == 1:
            return True
        if x == 1 and y == 8:
            return True
        if x == 8 and y == 1:
            return True
        if x == 8 and y == 8:
            return True
        return False

    def isEdge(self, move):
        x = move["Where"][0]
        y = move["Where"][1]
        if x == 1 or x == 8 or y == 1 or y == 8:
            return True
        return False

    def ngPos(self, move, g):

        x = move["Where"][0]
        y = move["Where"][1]

        if x == 2 and y == 2:
            return True

        if x == 2 and y == 7:
            return True

        if x == 7 and y == 2:
             return True

        if x == 7 and y == 7:
            return True


        if MainHandler.isEdge(self, move):
            #○●
            if y == 1 or y == 8:
                #if g.Pos(x-1, y) != g.Pos(x, y) and g.Pos(x+1, y) == 0 and g.Pos(x-1, y) != 0:
                if g.Pos(x-1, y) == 2:
                    return True

                #if g.Pos(x+1, y) != g.Pos(x, y) and g.Pos( x-1, y) == 0 and g.Pos(x+1, y) != 0:
                if g.Pos(x+1, y) == 2:
                    return True

            if x == 1 or x == 8:
                #if g.Pos(x, y+1) != g.Pos(x, y) and g.Pos(x, y-1) == 0 and g.Pos(x, y+1) != 0:
                if g.Pos(x, y+1) == 2:
                    return True

                #if g.Pos(x, y-1) != g.Pos(x, y) and g.Pos(x, y+1) == 0 and g.Pos(x, y-1) != 0: 
                if g.Pos(x, y-1) == 2: 
                    return True

        return False

    def ngPos_2(self, move):

        x = move["Where"][0]
        y = move["Where"][1]

        if x == 1 and y == 2:
            return True

        if x == 1 and y == 7:
            return True

        if x == 2 and y == 1:
            return True

        if x == 2 and y == 8:
            return True

        if x == 7 and y == 1:
            return True

        if x == 7 and y == 8:
            return True

        if x == 8 and y == 2:
            return True

        if x == 8 and y == 7:
            return True

        return False


app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)
