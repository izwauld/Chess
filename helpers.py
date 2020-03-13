
"""HELPER FUNCTIONS FOR CHESS GAME"""

import os, math, time
import pygame
import numpy

screen_width=800
screen_height=800
BLACK = 0,0,0 
RED = 255,0,0
GREEN = 0,255,0
BLUE = 0,0,255
WHITE = 255,255,255
delta = 60 #if placing piece within delta pixels of a square, place in that square

types = ['P', 'B', 'K', 'R', 'Q', 'KG']
white_pieces = {}
black_pieces = {}

for p in types:
    white_pieces[p] = os.getcwd() +  '/images/' + p + 'w.png'
    black_pieces[p] = os.getcwd() + '/images/' + p + 'b.png'

#Pre-determined ratios between square screen dimensions and the top left of the board image
start_fract = 3 / 40
center_fract = 17 / 160

#Using above, we determine the locations where the pieces will be blitted
start_x = round(start_fract * screen_width)
incr_x = round(center_fract * screen_width)
start_x += round(incr_x / 2)

start_y = round(start_fract * screen_height)
incr_y = round(center_fract * screen_height)
start_y += round(incr_y / 2)

piece_size = (round(0.9*incr_x), round(0.9*incr_y))
delta = round(0.8*piece_size[0]) #tuneable: threhold for determining which square a piece is placed in

#The dimensions of our board in the image
board_area = pygame.Rect((0.5*start_y, 0.5*start_x), (start_y+7*incr_y, start_x+7*incr_x))

##########################EACH SQUARE IS 85x85, TOP LEFT SQUARE = (100,100)####################################################
coords = numpy.array([[[x,y] for y in range(start_x,start_x+8*incr_x,incr_x)] for x in range(start_y,start_y+8*incr_y,incr_y)])
###############################################################################################################################

def generate_moves(piece, pieces, coords):
    #Pawns: can move up by at most 2 at starts, then by 1
    moves = []
    x, y = return_indices(piece.rect.center, coords)

    #Pawns
    if piece.type == 'P':
        if piece.colour == 'white':
            #if at start of game, pawn can move up twice
            if piece.hasBeenClickedCount == 0:
                moves.append((x, y-2))

            update_movelist(moves, x, y-1, x>=0 and x<8, y-1>=0)

            #Append take moves
            update_movelist(moves, x-1, y-1, x-1>=0, y-1>=0)
            update_movelist(moves, x+1, y-1, x+1<8, y-1>=0)


            moves = process_moves(piece, pieces, moves)

            piece.hasBeenClickedCount += 1

        elif piece.colour == 'black':
            if piece.hasBeenClickedCount == 0:
                moves.append((x, y+2))

            update_movelist(moves, x, y+1, True, y+1<8)

            #Append take moves
            update_movelist(moves, x-1, y+1, x-1>=0, y+1<8)
            update_movelist(moves, x+1, y+1, x+1<8, y+1<8)

            moves = process_moves(piece, pieces, moves)

            piece.hasBeenClickedCount += 1
            
    #Knights
    elif piece.type == 'K':
        update_movelist(moves, x+1, y+2, x+1<8, y+2<8)
        update_movelist(moves, x+1, y-2, x+1<8, y-2>=0)
        update_movelist(moves, x-1, y+2, x-1>=0, y+2<8)
        update_movelist(moves, x-1, y-2, x-1>=0, y-2>=0)
        update_movelist(moves, x+2, y+1, x+2<8, y+1<8)
        update_movelist(moves, x+2, y-1, x+2<8, y-1>=0)
        update_movelist(moves, x-2, y+1, x-2>=0, y+1<8)
        update_movelist(moves, x-2, y-1, x-2>=0, y-1>=0)

        moves = process_moves(piece, pieces, moves)

        piece.hasBeenClickedCount += 1

    #Bishops
    elif piece.type == 'B':
        for c in range(1,8):
            update_movelist(moves, x+c, y+c, x+c<8, y+c<8)
            update_movelist(moves, x-c, y-c, x-c>=0, y-c>=0)
            update_movelist(moves, x+c, y-c, x+c<8, y-c>=0)
            update_movelist(moves, x-c, y+c, x-c>=0, y+c<8)

        moves = process_moves(piece, pieces, moves)

        piece.hasBeenClickedCount += 1

    #Rooks
    elif piece.type == 'R':
        for c in range(1,8):
            update_movelist(moves, x, y+c, True, y+c<8)
            update_movelist(moves, x, y-c, True, y-c>=0)
            update_movelist(moves, x+c, y, x+c<8, True)
            update_movelist(moves, x-c, y, x-c>=0, True)

        moves = process_moves(piece, pieces, moves)

        piece.hasBeenClickedCount += 1

    #Queens [x+c, x, x-c, y+c, y, y-c]
    elif piece.type == 'Q':
        #moves = list(combinations([x+c, x, x-c, y+c, y, y-c] for c in range(1,8)))
        for c in range(1,8):
            update_movelist(moves, x+c, y+c, x+c<8, y+c<8)
            update_movelist(moves, x, y+c, True, y+c<8)
            update_movelist(moves, x-c, y+c, x-c>=0, y+c<8)
            update_movelist(moves, x+c, y, x+c<8, True)
            update_movelist(moves, x-c, y, x-c>=0, True)
            update_movelist(moves, x+c, y-c, x+c<8, y-c>=0)
            update_movelist(moves, x, y-c, True, y-c>=0)
            update_movelist(moves, x-c, y-c, x-c>=0, y-c>=0)

        moves = process_moves(piece, pieces, moves)

        piece.hasBeenClickedCount += 1

    #Kings
    elif piece.type == 'KG':
        update_movelist(moves, x+1, y+1, x+1<8, y+1<8)
        update_movelist(moves, x, y+1, True, y+1<8)
        update_movelist(moves, x-1, y+1, x-1>=0, y+1<8)
        update_movelist(moves, x+1, y, x+1<8, True)
        update_movelist(moves, x-1, y, x-1>=0, True)
        update_movelist(moves, x+1, y-1, x+1<8, y-1>=0)
        update_movelist(moves, x, y-1, True, y-1>=0)
        update_movelist(moves, x-1, y-1, x-1>=0, y-1>=0)

        #Castling
        if piece.colour == 'white' and piece.hasBeenClickedCount == 0:
            update_movelist(moves, x+2, y, piece.hasBeenClickedCount == 0, y==7)
            update_movelist(moves, x-3, y, piece.hasBeenClickedCount == 0, y==7)
        elif piece.colour == 'black' and piece.hasBeenClickedCount == 0:
            update_movelist(moves, x+2, y, piece.hasBeenClickedCount == 0, y==0)
            update_movelist(moves, x-3, y, piece.hasBeenClickedCount == 0, y==0)

        moves = process_moves(piece, pieces, moves)

        piece.hasBeenClickedCount += 1

    return moves

def update_movelist(list, a, b, acondition=True, bcondition=True):
    if acondition and bcondition:
        list.append((a,b))

def process_moves(piece, pieces, moves):

    #Remove empty lists of moves and duplicates
    moves = list(filter(lambda x: x != [], moves))
    moves = list(dict.fromkeys(moves))

    x, y = return_indices(piece.rect.center, coords)
    for other in pieces:
        i, j = return_indices(other.rect.center, coords)

        for elem in moves[:]:
            #If another piece of same colour is there, it ain't a valid move
            if (i,j) == elem and piece.colour == other.colour:
                moves.remove(elem)

            #moving up/down on same file
            if x == i and elem[0] == i:
                if elem[1] < j and j < y:
                    moves.remove(elem)
                elif y < j and j < elem[1]:
                    moves.remove(elem)

            #moving left/right on same rank
            if y == j and elem[1] == j:
                if x < i and elem[0] > i:
                    moves.remove(elem) #moving right on same rank
                elif x > i and elem[0] < i:
                    moves.remove(elem) #moving left on same rank

            #moving along upper/lower-right diagonal
            if x < i and i < elem[0]:
                if j == y - (i-x) and elem[1] == j - (elem[0]-i):
                    moves.remove(elem)
                elif j == y + (i-x) and elem[1] == j + (elem[0]-i):
                    moves.remove(elem)

            #moving along upper/lower-left diagonal
            if elem[0] < i and i < x:
                if j == y + (i-x) and elem[1] == j + (elem[0]-i):
                    moves.remove(elem) #moving along upper/lower-left diagonal
                elif j == y - (i-x) and elem[1] == j - (elem[0]-i):
                    moves.remove(elem)

        #Loop through remaining moves: for any piece, if opposite piece is within reach and a valid move, it's takeable
        #Also, for pawns, make sure you can take where possible!
        if other != piece:
            for move in moves:
                if (i,j) == move and piece.colour != other.colour and piece.type != 'P':
                    other.takeable = True
                elif piece.type == 'P':
                    if (i,j) == move and i == x:
                        other.takeable = False
                    #white pieces
                    elif piece.colour == 'white' and (i == x-1 or i == x+1) and j == y-1:
                        other.takeable = True
                    #black pieces
                    elif piece.colour == 'black' and (i == x-1 or i == x+1) and j == y+1:
                        other.takeable = True

    return moves

def return_indices(value, coords):
    for i in range(8):
        for j in range(8):
            if numpy.array_equal(coords[i,j], value):
                x, y = i, j
    return x, y

def return_closest_indices(ref, coords):
    for (i,j,k), _ in numpy.ndenumerate(coords):
        if numpy.linalg.norm(ref - coords[i,j]) < delta:
            return i, j

def get_pieces(kind, pieces):
    mylist =[]
    for piece in pieces:
        if piece.type == kind:
            mylist.append(piece)

    return mylist