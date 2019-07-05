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
            
            initBoard = [[0]*9]*9
            for i in xrange(1,9):
                for j in xrange(1,9):
                    initBoard[i][j] = 0

            initBoard[4][4] = 2
            initBoard[4][5] = 1
            initBoard[5][4] = 1
            initBoard[5][5] = 2

            #initBoard = MainHandler.makeInitBoard(self)
            #initBoard[4][4] = 100

            (score, move) = MainHandler.maxmin(self, 2, g, countOfPiece, initBoard, g.Next())
            self.response.write(PrettyMove(move))

    def makeInitBoard(self):

        initBoard = [[0]*9]*9

        for y in xrange(1,9):
            for x in xrange(1,9):
                if  x == 4 and y == 4:
                    initBoard[y][x] = 2

                elif x == 4 and y == 5:
                    initBoard[y][x] == 1

                elif x == 5 and y == 4:
                    initBoard[y][x] = 1

                elif x == 5 and y == 5:
                    initBoard[y][x] = 2

                else:
                    initBoard[y][x] = 0
        return initBoard

    def maxmin(self, depth, g, countOfPiece, initBoard, player):
        move = {"Where":[0,0]}
        return MainHandler.alphabeta(self, depth, g, -100000000, 1000000000, countOfPiece, True, initBoard, player,move)


    def alphabeta(self, depth, g, alpha, beta, countOfPiece, isMe, board, player, move):

        if depth == 0:
            if countOfPiece >= 58 :
                return MainHandler.lastPos(self, g,board, player), move
            return MainHandler.calcScore(self,g,board, player), move

        #nextBoard →　moves (nextValidMoves)
        #moves　→　move
        #move →　nextBoard
        #alphabeta()

        
        if isMe:
            moves = MainHandler.myValidMoves(self, board, player)
            print('len')
            print(len(moves))
            for move in moves:
                newBoard = MainHandler.makeNewBoard(self, board, move, player)
                (alpha0, move0)  = MainHandler.alphabeta(self, depth-1, g, alpha, beta, countOfPiece, False, newBoard, 3-player, move)
                alpha = max(alpha, alpha0)
                if alpha >= beta:
                    break
            return alpha, move

        else:
            #print('Board★')
            #print(board[4][4])
            moves = MainHandler.myValidMoves(self, board, player)
            print('LEN')
            print(len(moves))
            for move in moves:
                newBoard = MainHandler.makeNewBoard(self, board, move, player)
                (beta0, move0) = MainHandler.alphabeta(self, depth-1, g, alpha, beta,countOfPiece, True, newBoard, 3-player, move)
                beta = min(beta, beta0)
                if alpha >= beta:
                    break
            return beta, move



    def myValidMoves(self, board, player):
        moves = []
        for y in xrange(1,9):
            for x in xrange(1,9):
                move = {"Where":[x,y]}
                if MainHandler.makeNewBoard(self,board,move,player) is not None:
                    moves.append(move)
        print('move s len')
        print(len(moves))
        return moves


    #use myUpdataBoardDirection
    #return newBoard
    def makeNewBoard(self, currentBoard, move, player):
        board = [[0]*9]*9
        x = move["Where"][0]
        y = move["Where"][1]
        
        board = MainHandler.myUpdateBoardDirection(self, currentBoard, x, y, 1, 0, player)
        if board != currentBoard:
            print('changed!')
        board = MainHandler.myUpdateBoardDirection(self, board, x, y, 0, 1, player)
        if board != currentBoard:
            print('changed!')
        board = MainHandler.myUpdateBoardDirection(self, board, x, y, -1, 0, player)
        if board != currentBoard:
            print('changed!')
        board = MainHandler.myUpdateBoardDirection(self, board, x, y, 0, -1, player)
        if board != currentBoard:
            print('changed!')
        board = MainHandler.myUpdateBoardDirection(self, board, x, y, 1, 1, player)
        if board != currentBoard:
            print('changed!')
        board = MainHandler.myUpdateBoardDirection(self, board, x, y, 1, -1, player)
        if board != currentBoard:
            print('changed!')
        board = MainHandler.myUpdateBoardDirection(self, board, x, y, -1, 1, player)
        if board != currentBoard:
            print('changed!')
        board = MainHandler.myUpdateBoardDirection(self, board, x, y, -1, -1, player)

        if board == currentBoard:
            return None
        #isChanged = False
        #for i in

        print('changed')
        return board



    #use myPos and mySetPos
    #return newBoard
    def myUpdateBoardDirection(self, board, x, y, delta_x, delta_y, player):
        opponent = 3 - player
        look_x = x + delta_x
        look_y = y + delta_y
        flip_list = []


        newBoard =[[0]*9]*9

        for i in xrange(1,9):
            for j in xrange(1,9):
                newBoard[i][j] = board[i][j]


        while MainHandler.myPos(self, board, look_x, look_y) == opponent:
            flip_list.append([look_x, look_y])
            look_x += delta_x
            look_y += delta_y
        if MainHandler.myPos(self, board, look_x, look_y) == player and len(flip_list) > 0:
                        # there's a continuous line of our opponents
                        # pieces between our own pieces at
                        # [look_x,look_y] and the newly placed one at
                        # [x,y], making it a legal move.
            #print('if')
            #print(board[y][x])
            newBoard = MainHandler.mySetPos(self, board, x, y, player)
            #print('new')
            #print(newBoard[y][x])
            for flip_move in flip_list:
                #print('flip_move')
                flip_x = flip_move[0]
                flip_y = flip_move[1]
                newBoard = MainHandler.mySetPos(self, newBoard, flip_x, flip_y, player)
    
            print('return newBoard')

            return newBoard

        return board



    def myPos(self, board, x, y):
        #print('board')
        #print(board[y-1][x-1])
        if 1 <= x and x <= 8 and 1 <= y and y <= 8:
            #return board[y-1][x-1]
            return board[y][x]
        return -1


    def mySetPos(self, board, x, y, player):
        if x < 1 or 8 < x or y < 1 or 8 < y:
            return False
        #board[y-1][x-1] = player
        #print('mySetPos board')
        #print(board[y][x])
        board[y][x] = player
        #print(board[y][x])
        return board



    def calcScore(self,g,nextBoard, player):

        #numOfValiedMoves = len(g.ValidMoves()) * 5
        pieceScore = MainHandler.calcPieceScore(self, g, nextBoard, player)
        #score = numOfValiedMoves + pieceScore
        #return score
        return pieceScore


    def calcPieceScore(self, g, nextBoard, player):

        black = 0 
        white = 0
                      #1                            #2                                          #3                                #4                                  #5                                  #6                              #7
        scores = [300,-100,50,50,50,50,-100,300],[-100, -100, -50, -50, -50, -50, -100, -100],[50, -50, 0, 10, 10, 0, -50, 50],[50, -50, 10, 15, 15, 10, -50, 50],[50, -50, 10, 15, 15, 10, -50, 50],[50, -50, 0, 10, 10, 0, -50, 50],[-100, -100, -50, -50, -50, -50, -100, -100],[300,-100,60,60,60,60,-100,300]
        for i in range(8):
            for j in range(8):
                if g.Pos(i, j) == 1:
                    black = black + scores[i][j]
                elif g.Pos(i, j) == 2:
                    white = white + scores[i][j]

        if player == 1:
            return black - white

        return white - black

   
    def lastPos(self, g, nextBoard, player):

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
