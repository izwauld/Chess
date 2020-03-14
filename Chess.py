"""A Chess program -- created by Isaac Twelves"""

# Import dependencies
import os, math, time
import sys
import pygame
import numpy
from helpers import generate_moves, update_movelist, process_moves, return_indices, return_closest_indices, get_pieces
# Initialise pygame
pygame.init()

# Define constants/dependencies (screen dimensions, RGB values of colours,
# and chess square area threshold, and image locations of pieces)
screen_width=800
screen_height=800
Black = 0,0,0 
RED = 255,0,0
GREEN = 0,255,0
BLUE = 0,0,255
White = 255,255,255

types = ['P', 'B', 'K', 'R', 'Q', 'KG']
White_pieces = {}
Black_pieces = {}

for p in types:
    White_pieces[p] = os.getcwd() +  '/images/' + p + 'w.png'
    Black_pieces[p] = os.getcwd() + '/images/' + p + 'b.png'

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
delta = round(0.9*piece_size[0]) #tuneable: threhold for determining which square a piece is placed in

#The dimensions of our board in the image
board_area = pygame.Rect((0.5*start_y, 0.5*start_x), (start_y+7*incr_y, start_x+7*incr_x))

##########################EACH SQUARE IS 85x85, TOP LEFT SQUARE = (100,100)####################################################
coords = numpy.array([[[x,y] for y in range(start_x,start_x+8*incr_x,incr_x)] for x in range(start_y,start_y+8*incr_y,incr_y)])
###############################################################################################################################

# Create pieces, White/Black pieces (done)
class Piece(pygame.sprite.Sprite):
    """Defines a chess piece which inherits from the Sprite class.

    Attributes:
        type: str, the type of the piece (pawn, rooks, queen, etc.)
        colour: str, the colour of the piece (Black or White)
        takeable: bool, describes the takeable state of the piece
        clicked: bool, describes if the piece has been taken or not
        hasBeenClickedCount: int, counts how many times the piece has been moved/clicked
        image: pygame.Surface, how the piece looks
        rect: pygame.Rect, the rect object of the image - used for moving the piece - has it's own attributes
        such as rect.center, rect.x, rect.y, etc.

    Methods:
        move: displaces the rect x/y componenets of the Sprite object - rect move to the 
        center of the mouse position and move along with it

    """

    def __init__(self, piece, colour, position, takeable=False):
        super(Piece, self).__init__()
        self.type = piece
        self.colour = colour
        self.takeable = takeable
        self.clicked = False
        self.hasBeenClickedCount = 0
        self.moves = []

        #If piece is a king, have a check attribute for seeing if in check or not
        if self.type == 'KG':
            self.check = False

        if self.colour == 'White':
            # Since images are transparent, convert_alpha() needs to be called
            self.image = pygame.image.load(White_pieces[piece]).convert_alpha()
            self.image = pygame.transform.scale(self.image, piece_size)
        else:
            self.image = pygame.image.load(Black_pieces[piece]).convert_alpha()
            self.image = pygame.transform.scale(self.image, piece_size)


        self.rect = self.image.get_rect()
        self.rect.center = position

    # Define method to move the Sprite, so sprite center moves with mouse
    def move(self):
        pos = pygame.mouse.get_pos()
        self.rect.x = pos[0] - self.rect.width / 2
        self.rect.y = pos[1] - self.rect.height / 2
    # Define method to draw the Sprite - useful for drawing individual sprites
    def draw(self, screen):
        screen.blit(self.image, self.rect)

def populate_board():
    """Creates a Group() object to hold all the pieces. The pieces
    are then drawn in later in the main loop"""

    pieces = pygame.sprite.Group()

    #Pawns
    for i in range(8):
        pieces.add(Piece('P', 'Black', coords[i,1]))
        pieces.add(Piece('P', 'White', coords[i,6]))
    #Rooks
    pieces.add(Piece('R', 'Black', coords[0,0]))
    pieces.add(Piece('R', 'Black', coords[7,0]))
    pieces.add(Piece('R', 'White', coords[0,7]))
    pieces.add(Piece('R', 'White', coords[7,7]))
    #Knights
    pieces.add(Piece('K', 'Black', coords[1,0]))
    pieces.add(Piece('K', 'Black', coords[6,0]))
    pieces.add(Piece('K', 'White', coords[1,7]))
    pieces.add(Piece('K', 'White', coords[6,7]))
    #Bishops
    pieces.add(Piece('B', 'Black', coords[2,0]))
    pieces.add(Piece('B', 'Black', coords[5,0]))
    pieces.add(Piece('B', 'White', coords[2,7]))
    pieces.add(Piece('B', 'White', coords[5,7]))
    #Queens
    pieces.add(Piece('Q', 'Black', coords[3,0]))
    pieces.add(Piece('Q', 'White', coords[3,7]))
    #Kings
    pieces.add(Piece('KG', 'Black', coords[4,0]))
    pieces.add(Piece('KG', 'White', coords[4,7]))

    return pieces
    
# Draw chess board, interchanging Black/White squares (done)
def create_board(xstart, ystart, screen):

    board_canvas = pygame.draw.rect(screen, (Black), ((xstart, ystart), (screen_width, screen_height)))
    board = pygame.image.load(os.getcwd() + '/images/chess_board.png').convert()
    board = pygame.transform.scale(board, (screen_width, screen_height))

    return board_canvas, board

def putInCheck(piece, king):
    x, y = return_indices(king.rect.center, coords)
    for move in piece.moves:
        if x == move[0] and y == move[1]:
            king.check = True
        else:
            king.check = False

    return king.check

def make_move(piece, pieces, curr_pos, moves, screen):
    """Takes a piece and makes the appropriate action

    Inputs:
    Outputs:

    """
    global moveIsValid
    mouse_pos = numpy.array(pygame.mouse.get_pos())
    king = list(filter(lambda x: x.type == 'KG' and x.colour == piece.colour, pieces))[0]


    # Define the board region - if dropping a piece outside this region, the move is invalid, so move back.
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
            if numpy.array_equal(other.rect.center, coords[i,j]):
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
                if piece.colour == 'White':
                    cond1 = i == l-1 and j == m-1
                    cond2 = i == l+1 and j == m-1
                    
                    if cond1 and i == a and j == b-1:
                        pieces.remove(other)
                        x, y = return_closest_indices(mouse_pos, coords)
                        piece.rect.center = coords[x,y]
                        piece.clicked = False
                        moveIsValid = True

                    elif cond2 and i == a and j == b-1:
                        pieces.remove(other)
                        x, y = return_closest_indices(mouse_pos, coords)
                        piece.rect.center = coords[x,y]
                        piece.clicked = False
                        moveIsValid = True

                    else:
                        count+=1

                elif piece.colour == 'Black':
                    cond1 = i == l-1 and j == m+1
                    cond2 = i == l+1 and j == m+1

                    if cond1 and i == a and j == b+1:
                        pieces.remove(other)
                        piece.rect.center = coords[i,j]
                        piece.clicked = False
                        moveIsValid = True
                        
                    elif cond2 and i == a and j == b+1:
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
            #P=Q
            elif piece.type == 'P':
                if piece.colour == 'White' and m == 1 and j == 0:
                    dead = list(filter(lambda x: numpy.array_equal(x.rect.center, coords[i,j]), pieces))
                    for other_piece in dead:
                        pieces.remove(other_piece) 
                    pieces.remove(piece)
                    queen = Piece('Q', piece.colour, coords[i,j])
                    pieces.add(queen)
                    piece = queen
                    piece.clicked = False
                    moveIsValid = False
                    return
                elif piece.colour == 'Black' and m == 6 and j == 7:
                    dead = list(filter(lambda x: numpy.array_equal(x.rect.center, coords[i,j]), pieces))
                    for other_piece in dead:
                        pieces.remove(other_piece) 
                    pieces.remove(piece)
                    queen = Piece('Q', piece.colour, coords[i,j])
                    pieces.add(queen)
                    piece = queen
                    piece.clicked = False
                    moveIsValid = True
                    return

                else:
                    count+=1

            else:
                count+=1
                king.check = False

    if count == num_pieces - 1:#if none of the other pieces occupy the square, and its a valid move, go there!
        if piece.type == 'P' and (i == l+1 or i == l-1) and (j == m-1 or j == m+1):
            if piece.hasBeenClickedCount > 1:
                piece.hasBeenClickedCount -= 1
            elif piece.hasBeenClickedCount == 1:
                piece.hasBeenClickedCount = 0 
            piece.rect.center = coords[l,m]
            piece.clicked = False
            moveIsValid = False
            return

        #Castling for both pieces
        if piece.type == 'KG' and piece.hasBeenClickedCount == 1:
            rook = list(filter(lambda x: x.type == 'R' and x.hasBeenClickedCount == 0 and x.colour == piece.colour and \
                (numpy.array_equal(x.rect.center,coords[i+1,j]) or numpy.array_equal(x.rect.center,coords[i-1,j])), pieces))
            if len(rook) != 0:
                rook = rook[0]
                if numpy.array_equal(rook.rect.center,coords[i-1,j]):
                    rook.rect.center = coords[i+1,j]
                elif numpy.array_equal(rook.rect.center,coords[i+1,j]):
                    rook.rect.center = coords[i-1,j]

        piece.rect.center = coords[i,j]
        piece.clicked = False
        #The move is only a valid one if moving to a different empty square,
        #not the one you're currently in! Prevents moving back to your original square as a turn
        moveIsValid = False if numpy.array_equal(coords[i,j], curr_pos) else True
        

        #If King has made a valid move, he's not in check
        #if piece.type == 'KG':
        #    piece.check = False

#Find intersecting moves of two pieces
def common_moves(piece1, piece2):
    moves = [value for value in piece1.moves if value in piece2.moves]
    return moves

#Main loop
def main():
    screen = pygame.display.set_mode([screen_width,screen_height])

    pieces = populate_board()

    turn = 0
    check_piece = None

    while True:
        mouse_pos = pygame.mouse.get_pos()
        #White starts, then Black
        if turn % 2 == 0:
            turn_colour = 'White'
        else:
            turn_colour = 'Black'

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                print("Exiting...")
                os.sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                clicked_piece = None
                clicked = [piece for piece in pieces if piece.clicked]

                king = list(filter(lambda x: x.type == 'KG' and x.colour == turn_colour, pieces))[0]

                if king.check:
                    if event.button == 1 and king.rect.collidepoint(mouse_pos):
                       king.clicked = True
                       clicked_piece = king
                       position = numpy.array(king.rect.center)
                else:
                    for piece in pieces:
                        if event.button == 1 and piece.rect.collidepoint(mouse_pos):
                            if piece.colour == turn_colour:
                                piece.clicked = True
                                clicked_piece = piece
                                position = numpy.array(piece.rect.center)
                                clicked_piece.moves = generate_moves(piece, pieces, coords, turn_colour)

            if event.type == pygame.MOUSEBUTTONUP:
                if clicked_piece != None:
                    make_move(clicked_piece, pieces, position, clicked_piece.moves, screen) #should have update isMoveValid and piece.clicked
                    if moveIsValid:
                        turn += 1
                    else:
                        if clicked_piece.hasBeenClickedCount >= 1:
                            clicked_piece.hasBeenClickedCount -= 1

                    if clicked_piece == king and king.check:
                        continue
                    #Update moveset if the clicked_piece is not in check
                    clicked_piece.moves = generate_moves(clicked_piece, pieces, coords, turn_colour)
                    clicked_piece.hasBeenClickedCount -= 1 #since we increase moves by 1 in the above step - too many!

                    enemy_king = list(filter(lambda x: x.type == 'KG' and x.colour != clicked_piece.colour, pieces))[0]
                    enemies = list(filter(lambda x: x.colour != enemy_king.colour, pieces))
                    enemies_moves = [enemy.moves for enemy in enemies]

                    while len(enemies_moves) != 0:
                        moves = enemies_moves.pop()
                        invalid_moves = [move for move in enemy_king.moves if move in moves]

                        #Kings cannot check other kings (by design!), so we check if the piece is not a king first
                        if clicked_piece != 'KG':
                            enemy_king.check = putInCheck(clicked_piece, enemy_king)
                            if enemy_king.check:
                                #It will then be opposite turns go, and so enemy_king will be only one you can move
                                if len(enemy_king.moves) == 0:
                                    #Checkmate!
                                    print(turn_colour + " wins!")
                                    os.sys.exit()
                                print("Check!")

                        for move in invalid_moves:
                            enemy_king.moves.remove(move)

     
        for piece in pieces:
            if piece.clicked == True and piece.colour == turn_colour:
                piece.move()

        board_canvas, board = create_board(0,0,screen)
        screen.fill(Black)
        screen.blit(board, board_canvas)
        pieces.draw(screen)
        pygame.display.flip()

if __name__ == '__main__':
    main()