import os, math, time
import pygame
import numpy


#******Updated: 2020-03-11******
#
#Game functionality:
#Pawns?
#   Moves? Good
#   En-passant? No
#       *Bug* en-passant still works if positional condition works, needs to work when pawn hasn't moved before 
#   Pawn move twice from start, 1 thereafter? Yes
#
#Knights?
#   Moving? Yes
#   Taking? Yes
#   Invalid move handling? Yes
#
#Bishops?
#   Moving? Yes
#   Taking? Yes
#   Invalid move handling? Yes
#   
#Queens?
#   Moves? Yes
#   Taking? Yes
#   Invalid move handling? Yes
#Rooks?
#   Moves? Yes
#   Taking? Yesimport os, math, time
import pygame
import numpy


#******Updated: 2020-03-11******
#
#Game functionality:
#Pawns?
#   Moves? Good
#   En-passant? No
#       *Bug* en-passant still works if positional condition works, needs to work when pawn hasn't moved before 
#   Pawn move twice from start, 1 thereafter? Yes
#
#Knights?
#   Moving? Yes
#   Taking? Yes
#   Invalid move handling? Yes
#
#Bishops?
#   Moving? Yes
#   Taking? Yes
#   Invalid move handling? Yes
#   
#Queens?
#   Moves? Yes
#   Taking? Yes
#   Invalid move handling? Yes
#Rooks?
#   Moves? Yes
#   Taking? Yes
#   Invalid move handling? Yes
#Kings?
#   Moves?
#   Taking?
#   Invalid move handling?
#   
#Can't take king? Yep
#Kings not next to eachother?
#Castle? Yep
#Check? 
#Checkmate? 
#Time control? 
#Winning condition?
#

pygame.init()

screen_width=800
screen_height=800
BLACK = 0,0,0
RED = 255,0,0
GREEN = 0,255,0
BLUE = 0,0,255
WHITE = 255,255,255

white_pieces = {}
black_pieces = {}

types = ['P', 'B', 'K', 'R', 'Q', 'KG']
for type in types:
    white_pieces[type] = os.getcwd() +  '/images/' + type + 'w.png'
    black_pieces[type] = os.getcwd() + '/images/' + type + 'b.png'

####BOARD SQUARE SIZE is 85x85####

"""def create_board(xstart, ystart):
    #Long way of drawing the chess board#
    width, height = 50,50
    y = ystart
    count = 0

    while (count < 8):
        for i in range(count, count+8):
            if i % 2 == 0:
                white = pygame.draw.rect(screen, (WHITE), (xstart,y,width,height))
            else:
                black = pygame.draw.rect(screen, (BLUE), (xstart,y,width,height))

            y += 50

        count, xstart, y = count+1, xstart+50, ystart
"""
start_fract = 3 / 40
center_fract = 17 / 160


start_x = round(start_fract * screen_width)
incr_x = round(center_fract * screen_width)
start_x += round(incr_x / 2)

start_y = round(start_fract * screen_height)
incr_y = round(center_fract * screen_height)
start_y += round(incr_y / 2)

piece_size = (round(0.9*incr_x), round(0.9*incr_y))
delta = round(0.8*piece_size[0]) #tuneable

board_area = pygame.Rect((0.5*start_y, 0.5*start_x), (start_y+7*incr_y, start_x+7*incr_x))

##########################EACH SQUARE IS 85x85, TOP LEFT SQUARE = (100,100)##########
coords = numpy.array([[[x,y] for y in range(start_x,start_x+8*incr_x,incr_x)] for x in range(start_y,start_y+8*incr_y,incr_y)])
#####################################################################################

def create_board(xstart, ystart):

    board_canvas = pygame.draw.rect(screen, (BLACK), ((xstart, ystart), (screen_width, screen_height)))
    board = pygame.image.load(os.getcwd() + '/images/chess_board.png').convert()
    board = pygame.transform.scale(board, (screen_width, screen_height))

    return board_canvas, board

class Piece(pygame.sprite.Sprite):
    def __init__(self, piece, colour, position):
        super(Piece, self).__init__()
        self.type = piece
        self.colour = colour
        self.takeable = False
        self.clicked = False
        self.hasBeenClickedCount = 0 #Useful for pawns off start/en-passant
        if self.colour == 'white':
            self.image = pygame.image.load(white_pieces[piece]).convert_alpha()
            self.image = pygame.transform.scale(self.image, piece_size)#good size
        else:
            self.image = pygame.image.load(black_pieces[piece]).convert_alpha()
            self.image = pygame.transform.scale(self.image, piece_size)#good size


        self.rect = self.image.get_rect()
        self.rect.center = position

    def move(self):
        pos = pygame.mouse.get_pos()
        self.rect.x = pos[0] - self.rect.width / 2
        self.rect.y = pos[1] - self.rect.height / 2


def update_movelist(list, a, b, acondition=True, bcondition=True):
    #Note: while condition causes program to crash (4 of these are performed in
    # validate moves). Need to work on speedier alternative.
    if acondition and bcondition:
        list.append((a,b))
    

def process_moves(piece, pieces, moves):
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


def generate_moves(piece, pieces, coords):
    global canCastle
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

            moves = list(filter(lambda x: x != [], moves))
            moves = list(dict.fromkeys(moves))
            moves = process_moves(piece, pieces, moves)

            piece.hasBeenClickedCount += 1

        elif piece.colour == 'black':
            if piece.hasBeenClickedCount == 0:
                moves.append((x, y+2))

            update_movelist(moves, x, y+1, True, y+1<8)

            #Append take moves
            update_movelist(moves, x-1, y+1, x-1>=0, y+1<8)
            update_movelist(moves, x+1, y+1, x+1<8, y+1<8)

            moves = list(filter(lambda x: x != [], moves))
            moves = list(dict.fromkeys(moves))
            moves = process_moves(piece, pieces, moves)

            piece.hasBeenClickedCount += 1
            
    #Knights
    elif piece.type == 'K':
        update_movelist(moves, x+1, y+2, x+1<8, y+2<8)
        update_movelist(moves, x+1, y-2, x+1<8, y-2>=0)
        update_movelist(moves, x-1, y+2, x-1>=0, y+2<8)
        update_movelist(moves, x-1, y-2, x-1>=0, y-2>=0)
        update_movelist(moves, x+2, y+1, x+2<8, y+1<8)
        update_movelist(moves, x+2, y-1, x+2<8, y-1<8)
        update_movelist(moves, x-2, y+1, x-2>=0, y+1<8)
        update_movelist(moves, x-2, y-1, x-2>=0, y-1>=0)

        moves = list(filter(lambda x: x != [], moves))
        moves = list(dict.fromkeys(moves))
        moves = process_moves(piece, pieces, moves)

        piece.hasBeenClickedCount += 1

    #Bishops
    elif piece.type == 'B':
        for c in range(1,8):
            update_movelist(moves, x+c, y+c, x+c<8, y+c<8)
            update_movelist(moves, x-c, y-c, x-c>=0, y-c>=0)
            update_movelist(moves, x+c, y-c, x+c<8, y-c>=0)
            update_movelist(moves, x-c, y+c, x-c>=0, y+c<8)

        moves = list(filter(lambda x: x != [], moves))
        moves = list(dict.fromkeys(moves))
        moves = process_moves(piece, pieces, moves)

        piece.hasBeenClickedCount += 1

    #Rooks
    elif piece.type == 'R':
        for c in range(1,8):
            update_movelist(moves, x, y+c, True, y+c<8)
            update_movelist(moves, x, y-c, True, y-c>=0)
            update_movelist(moves, x+c, y, x+c<8, True)
            update_movelist(moves, x-c, y, x-c>=0, True)

        moves = list(filter(lambda x: x != [], moves))
        moves = list(dict.fromkeys(moves))
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

        moves = list(filter(lambda x: x != [], moves))
        moves = list(dict.fromkeys(moves))
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
            canCastle = True
        elif piece.colour == 'black' and piece.hasBeenClickedCount == 0:
            update_movelist(moves, x+2, y, piece.hasBeenClickedCount == 0, y==0)
            update_movelist(moves, x-3, y, piece.hasBeenClickedCount == 0, y==0)
            canCastle = True

        moves = list(filter(lambda x: x != [], moves))
        moves = list(dict.fromkeys(moves))
        moves = process_moves(piece, pieces, moves)

        piece.hasBeenClickedCount += 1

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

def get_pieces(type, pieces):
    mylist =[]
    for piece in pieces:
        if type == 'R':
            mylist.append(piece)

    return mylist


def take_action(piece, curr_pos, pieces, moves):
    global moveIsValid, canCastle
    mouse_pos = numpy.array(pygame.mouse.get_pos())

    #Note: pretty messy, improve this!
    if not board_area.collidepoint((mouse_pos[0], mouse_pos[1])):
        piece.rect.center = curr_pos
        piece.clicked = False
        moveIsValid = False
        return

    else:
        i, j = return_closest_indices(mouse_pos, coords) #coords[i,j] is candidate square
        l, m = return_indices(curr_pos, coords) 

    num_pieces = len(pieces)

    if len(moves) == 0 or (i,j) not in moves:
        piece.rect.center = curr_pos
        piece.clicked = False
        moveIsValid = False
        if piece.type == 'P' and not moveIsValid and piece.hasBeenClickedCount == 1:
            piece.hasBeenClickedCount = 0
        return

    count = 0
    for other in pieces:
        if other != piece:
            a, b = return_indices(other.rect.center, coords)
            #If there is a piece in candidate square, consider if it is takeable or not
            if numpy.array_equal(coords[a,b], coords[i,j]):
                if not other.takeable or other.type == 'KG':
                    #Can't take piece, move back
                    piece.rect.center = coords[l,m]
                    piece.clicked = False
                    moveIsValid = False

                else:
                    #Remove piece and put your piece there, which will be
                    #closest piece to the mouse position
                    pieces.remove(other)
                    piece.rect.center = coords[i,j]
                    piece.clicked = False
                    moveIsValid = True
            
            #En-passant
            elif piece.type == 'P' and other.type == 'P' and piece.colour != other.colour and other.hasBeenClickedCount == 1:
                if piece.colour == 'white':
                    cond1 = i == l-1 and j == m-1
                    cond2 = i == l+1 and j == m-1
                    
                    if cond1 and i == a and j == b-1:
                        pieces.remove(other)
                        x, y = return_closest_indices(mouse_pos, coords)
                        piece.rect.center = coords[x,y]
                        piece.clicked = False
                        moveIsValid = True
                    if cond2 and i == a and j == b-1:
                        pieces.remove(other)
                        x, y = return_closest_indices(mouse_pos, coords)
                        piece.rect.center = coords[x,y]
                        piece.clicked = False
                        moveIsValid = True

                    else:
                        count+=1

                elif piece.colour == 'black':
                    cond1 = i == l-1 and j == m+1
                    cond2 = i == l+1 and j == m+1

                    if cond1 and i == a and j == b+1:
                        pieces.remove(other)
                        piece.rect.center = coords[i,j]
                        piece.clicked = False
                        moveIsValid = True
                    if cond2 and i == a and j == b+1:
                        pieces.remove(other)
                        piece.rect.center = coords[i,j]
                        piece.clicked = False
                        moveIsValid = True

                    else:
                        count+=1

            #Can't have kings next to eachother
            elif piece.type == 'KG' and other.type == 'KG':
                if numpy.linalg.norm(numpy.array((a,b)) - numpy.array((i,j))) in [1, math.sqrt(2)]:
                    piece.rect.center = coords[l,m]
                    piece.clicked = False
                    moveIsValid = False
                    return
                else:
                    count+=1

            else:
                count+=1

    if count == num_pieces - 1: #if none of the other pieces occupy the square, and its a valid move, go there!
        if piece.type == 'P' and (i == l+1 or i == l-1) and (j == m-1 or j == m+1):
            if piece.hasBeenClickedCount == 1:
                piece.hasBeenClickedCount = 0
            piece.rect.center = coords[l,m]
            piece.clicked = False
            moveIsValid = False
            return

        #Castling for both pieces
        if piece.type == 'KG' and canCastle == True:
            rook = list(filter(lambda x: x.type == 'R' and x.hasBeenClickedCount == 0 and x.colour == piece.colour and \
                (numpy.array_equal(x.rect.center,coords[i+1,j]) or numpy.array_equal(x.rect.center,coords[i-1,j])), pieces))
            
            if len(rook) != 0:
                rook = rook[0]
                if numpy.array_equal(rook.rect.center,coords[i-1,j]):
                    rook.rect.center = coords[i+1,j]
                elif numpy.array_equal(rook.rect.center,coords[i+1,j]):
                    rook.rect.center = coords[i-1,j]

            canCastle = False

        piece.rect.center = coords[i,j]
        piece.clicked = False
        #The move is only a valid one if moving to a different empty square,
        #not the one you're currently in! Prevents moving back to your original square as a turn
        moveIsValid = False if numpy.array_equal(coords[i,j], curr_pos) else True

def create_pieces():
    pieces = pygame.sprite.Group()

    #Pawns
    for i in range(8):
        pieces.add(Piece('P', 'black', coords[i,1]))
        pieces.add(Piece('P', 'white', coords[i,6]))
    #Rooks
    pieces.add(Piece('R', 'black', coords[0,0]))
    pieces.add(Piece('R', 'black', coords[7,0]))
    pieces.add(Piece('R', 'white', coords[0,7]))
    pieces.add(Piece('R', 'white', coords[7,7]))
    #Knights
    pieces.add(Piece('K', 'black', coords[1,0]))
    pieces.add(Piece('K', 'black', coords[6,0]))
    pieces.add(Piece('K', 'white', coords[1,7]))
    pieces.add(Piece('K', 'white', coords[6,7]))
    #Bishops
    pieces.add(Piece('B', 'black', coords[2,0]))
    pieces.add(Piece('B', 'black', coords[5,0]))
    pieces.add(Piece('B', 'white', coords[2,7]))
    pieces.add(Piece('B', 'white', coords[5,7]))
    #Queens
    pieces.add(Piece('Q', 'black', coords[3,0]))
    pieces.add(Piece('Q', 'white', coords[3,7]))
    #Kings
    pieces.add(Piece('KG', 'black', coords[4,0]))
    pieces.add(Piece('KG', 'white', coords[4,7]))

    return pieces

screen=pygame.display.set_mode([screen_width,screen_height])

pieces = create_pieces()

global check
check = False
checked_king = None
cache = []
clicked_pieces = []
turn = 0

while True:
    #white starts, then black
    if turn % 2 == 0:
        turn_colour = 'white'
    else:
        turn_colour = 'black'

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            os.sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            clicked_piece = None
            clicked = [piece.clicked for piece in pieces]
            for piece in pieces:
                if event.button == 1 and piece.rect.collidepoint(mouse_pos) and not any(clicked):
                    if piece.colour == turn_colour:
                        piece.clicked = True
                        clicked_piece = piece
                        position = numpy.array(piece.rect.center)
                        valid_moves = generate_moves(piece, pieces, coords)
                    #elif piece.type == 'KG' and piece.colour == turn_colour and piece.takeable:
                    #    piece.clicked = True
                    #    clicked_piece = piece
                    #    position = numpy.array(piece.rect.center)
                    #    valid_moves = generate_moves(piece, pieces, coords)


        if event.type == pygame.MOUSEBUTTONUP:
            if clicked_piece != None and clicked_piece.colour == turn_colour:
                take_action(clicked_piece, position, pieces, valid_moves) #should have update isMoveValid
                if moveIsValid and check == False:
                    turn += 1
                #clicked_pieces.append(clicked_piece)
                #moves = generate_moves(clicked_piece, pieces, coords)
                ##moves = list(filter(lambda x: x != [], moves))
                #moves = list(dict.fromkeys(moves))
                #moves = process_moves(clicked_piece, pieces, moves)
                #cache.append(moves)

                # if turn >= 1:
                #     clicked_pieces.append(clicked_piece)
                #     moves = generate_moves(clicked_pieces[turn-1], pieces, coords)
                #     moves = list(filter(lambda x: x != [], cache[turn-1]))
                #     moves = list(dict.fromkeys(cache[turn-1]))
                #     moves = process_moves(clicked_pieces[turn-1], pieces, cache[turn-1])
                #     cache.append(moves)

                # kings = list(filter(lambda x: x.type == 'KG' and x.takeable == True, pieces))
                # print(kings)
                # #Check if king is in check
                # for king in kings:
                #     if king.takeable:
                #         check = True
                #         checked_king = king
                #     else:
                #         check = False

    for piece in pieces:
        if piece.clicked == True and piece.colour == turn_colour:
            piece.move()

    

    board_canvas, board = create_board(0,0)
    screen.fill(BLACK)
    screen.blit(board, board_canvas)
    pieces.draw(screen)
    pygame.display.flip()
