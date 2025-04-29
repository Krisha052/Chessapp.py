import pygame
import sys
import os
import json
import random
import time

# Initialize Pygame
pygame.init()

# --- Constants ---
# Colors
BLACK_BOARD_COLOR = (125, 193, 235)  # #7dc1eb
WHITE_BOARD_COLOR = (255, 255, 255)  # white
WHITE_PIECE_COLOR = (240, 176, 241)  # #f0b0f1
BLACK_PIECE_COLOR = (64, 56, 159)    # #40389f
SELECTED_COLOR = (255, 255, 0, 128)  # Highlight for selected piece (yellow with alpha)
LEGAL_MOVE_COLOR = (0, 255, 0, 128)  # Highlight for legal moves (green with alpha)
LAST_MOVE_COLOR = (255, 128, 0, 128) # Highlight for the last move. (orange with alpha)
CHECK_COLOR = (255, 0, 0, 128) # Highlight for the king in check (red with alpha)

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BOARD_SIZE = 8
SQUARE_SIZE = SCREEN_WIDTH // BOARD_SIZE
MENU_WIDTH = 200  # Width of the menu on the right side

# Font
FONT = pygame.font.Font(None, 36)
BUTTON_FONT = pygame.font.Font(None, 24)  # Smaller font for buttons

# Paths
# ASSETS_DIR = "assets"  # Directory for images and other data # Commented out to use current directory
SAVES_DIR = "saves"  # Directory for saved games
if not os.path.exists(SAVES_DIR):
    os.makedirs(SAVES_DIR)

# --- Helper Functions ---

def load_image(name):
    """Loads an image from the current directory."""
    # path = os.path.join(ASSETS_DIR, name) # Commented out to use current directory
    path = name
    try:
        return pygame.image.load(path).convert_alpha()
    except pygame.error as e:
        print(f"Error loading image {name}: {e}")
        # Create a dummy surface if the image fails to load.  This allows the
        # game to continue to run, albeit with missing images.
        surface = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        surface.fill((255, 0, 255, 0))  # Make it transparent pink (for debugging)
        return surface
    #return pygame.image.load(path).convert_alpha() #commented out to handle missing images

def scale_image(image, factor):
    """Scales an image by a given factor."""
    return pygame.transform.scale(image, (int(image.get_width() * factor), int(image.get_height() * factor)))

def get_piece_images(piece_size):
    """Loads and scales all chess piece images."""
    pieces = {
        'wR': scale_image(load_image("wR.png"), piece_size),
        'wN': scale_image(load_image("wN.png"), piece_size),
        'wB': scale_image(load_image("wB.png"), piece_size),
        'wQ': scale_image(load_image("wQ.png"), piece_size),
        'wK': scale_image(load_image("wK.png"), piece_size),
        'wP': scale_image(load_image("wp.png"), piece_size), # Changed wP.png
        'bR': scale_image(load_image("bR.png"), piece_size),
        'bN': scale_image(load_image("bN.png"), piece_size),
        'bB': scale_image(load_image("bB.png"), piece_size),
        'bQ': scale_image(load_image("bQ.png"), piece_size),
        'bK': scale_image(load_image("wK.png"), piece_size), # Corrected typo: changed bK to wK.
        'bP': scale_image(load_image("bp.png"), piece_size), # Changed bP.png
    }
    return pieces

def get_square_rect(row, col):
    """Gets the rectangle for a square on the board."""
    return pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)

def draw_board(screen, board, selected_square, legal_moves, last_move, check_square):
    """Draws the chessboard and pieces."""
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            rect = get_square_rect(row, col)
            color = WHITE_BOARD_COLOR if (row + col) % 2 == 0 else BLACK_BOARD_COLOR
            pygame.draw.rect(screen, color, rect)

            # Highlight selected square
            if selected_square and selected_square == (row, col):
                pygame.draw.rect(screen, SELECTED_COLOR, rect)

            # Highlight legal moves
            if legal_moves and (row, col) in legal_moves:
                pygame.draw.rect(screen, LEGAL_MOVE_COLOR, rect)
            
            #Highlight last move
            if last_move and ((last_move[0] == (row,col)) or (last_move[1] == (row,col))):
                pygame.draw.rect(screen, LAST_MOVE_COLOR, rect)
            
            # Highlight the king if in check.
            if check_square and check_square == (row, col):
                pygame.draw.rect(screen, CHECK_COLOR, rect)

            piece = board[row][col]
            if piece:
                screen.blit(PIECE_IMAGES[piece], rect.topleft)
                
def draw_menu(screen, game_state, current_player, selected_square, game_over_text):
    """Draws the menu on the right side of the screen."""
    menu_x = SCREEN_WIDTH - MENU_WIDTH
    pygame.draw.rect(screen, (220, 220, 220), (menu_x, 0, MENU_WIDTH, SCREEN_HEIGHT))  # Light gray background

    # Title
    title_text = FONT.render("Chess Game", True, (0, 0, 0))
    title_rect = title_text.get_rect(center=(menu_x + MENU_WIDTH // 2, 30))
    screen.blit(title_text, title_rect)

    # Game State Display
    state_text = FONT.render(f"State: {game_state}", True, (0, 0, 0))
    state_rect = state_text.get_rect(center=(menu_x + MENU_WIDTH // 2, 80))
    screen.blit(state_text, state_rect)
    
    # Current Player Display
    player_text = FONT.render(f"Player: {current_player}", True, (0, 0, 0))
    player_rect = player_text.get_rect(center=(menu_x + MENU_WIDTH // 2, 110))
    screen.blit(player_text, player_rect)
    
     # Selected Square Display
    selected_text = FONT.render(f"Selected: {selected_square}", True, (0, 0, 0))
    selected_rect = selected_text.get_rect(center=(menu_x + MENU_WIDTH // 2, 140))
    screen.blit(selected_text, selected_rect)
    
    # Game Over Text Display
    if game_over_text:
        game_over_display_text = FONT.render(game_over_text, True, (255, 0, 0))  # Red text for game over
        game_over_rect = game_over_display_text.get_rect(center=(menu_x + MENU_WIDTH // 2, 170))
        screen.blit(game_over_display_text, game_over_rect)

    # Buttons
    button_y_start = 250
    button_spacing = 50
    button_width = MENU_WIDTH - 20
    button_height = 40

    def draw_button(text, y_offset, action=None): # Added action parameter
        """Draws a button and handles clicks."""
        rect = pygame.Rect(menu_x + 10, button_y_start + y_offset, button_width, button_height)
        pygame.draw.rect(screen, (100, 100, 100), rect)  # Darker gray
        pygame.draw.rect(screen, (200, 200, 200), rect, 2)  # White border
        text_surface = BUTTON_FONT.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)
        return rect # Return the rect

    # Create buttons.  Store the rect *and* the action.
    button_actions = [
        ("New Game", lambda: init_board()),
        ("Save Game", lambda: save_game(board, current_player, game_state, selected_square, last_move)),
        ("Load Game", lambda: load_game()),
        ("Play vs AI", lambda: play_vs_ai()),
        ("Undo Move", lambda: undo_move()),
        ("Exit", lambda: sys.exit()),
    ]
    
    button_rects = []
    for i, (text, action) in enumerate(button_actions):
        button_rects.append((draw_button(text, i * button_spacing), action))  # Store rect and action
        
    return button_rects # Return list of button rects and actions.

def display_message(screen, message):
    """Displays a message in a popup box."""
    # Dimensions of the message box
    box_width = 400
    box_height = 200
    box_x = (SCREEN_WIDTH - box_width) // 2
    box_y = (SCREEN_HEIGHT - box_height) // 2

    # Background of the message box
    pygame.draw.rect(screen, (200, 200, 200), (box_x, box_y, box_width, box_height))
    pygame.draw.rect(screen, (100, 100, 100), (box_x, box_y, box_width, box_height), 2)  # Border

    # Font for the message
    message_font = pygame.font.Font(None, 24)
    lines = message.splitlines()  # Handle multi-line messages
    y_offset = 0
    for line in lines:
        text_surface = message_font.render(line, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(box_x + box_width // 2, box_y + 50 + y_offset))
        screen.blit(text_surface, text_rect)
        y_offset += 30  # Space between lines

    # OK button
    ok_button_rect = pygame.Rect(box_x + box_width // 4, box_y + box_height - 50, box_width // 2, 30)
    pygame.draw.rect(screen, (100, 100, 100), ok_button_rect)
    pygame.draw.rect(screen, (200, 200, 200), ok_button_rect, 2)
    ok_text = message_font.render("OK", True, (255, 255, 255))
    ok_rect = ok_text.get_rect(center=ok_button_rect.center)
    screen.blit(ok_text, ok_rect)

    pygame.display.update()  # Update the entire screen to show the message box

    # Event loop to wait for the OK button click
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if ok_button_rect.collidepoint(event.pos):
                    return  # Return when the OK button is clicked

# --- Game Logic ---

def init_board():
    """Initializes the chessboard."""
    board = [
        ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
        ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
        ['', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', ''],
        ['', '', '', '', '', '', '', ''],
        ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
        ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR'],
    ]
    return board

def get_legal_moves(board, row, col, current_player):
    """Gets all legal moves for the piece at the given square."""
    moves = []
    piece = board[row][col]
    if not piece or piece[0] != current_player:
        return moves

    def is_valid_move(r, c):
        """Checks if a move is within the board bounds."""
        return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

    def is_empty_or_opponent(r, c, player):
        """Checks if a square is empty or occupied by the opponent."""
        target_piece = board[r][c]
        return not target_piece or target_piece[0] != player

    if piece[1] == 'P':  # Pawn
        direction = -1 if current_player == 'w' else 1
        # One step forward
        new_row = row + direction
        if is_valid_move(new_row, col) and not board[new_row][col]:
            moves.append((new_row, col))
            # Two steps forward from initial position
            if (row == 6 and current_player == 'w') or (row == 1 and current_player == 'b'):
                new_row_2 = row + 2 * direction
                if not board[new_row_2][col] and not board[new_row][col]:
                    moves.append((new_row_2, col))
        # Capture left
        new_row = row + direction
        new_col_left = col - 1
        if is_valid_move(new_row, new_col_left) and board[new_row][new_col_left] and board[new_row][new_col_left][0] != current_player:
            moves.append((new_row, new_col_left))
        # Capture right
        new_col_right = col + 1
        if is_valid_move(new_row, new_col_right) and board[new_row][new_col_right] and board[new_row][new_col_right][0] != current_player:
            moves.append((new_row, new_col_right))
        # En passant (simplified)
        if last_move and last_move[0][1] != last_move[1][1]: #different columns
            en_passant_row = last_move[1][0]
            en_passant_col = last_move[1][1]
            if row == en_passant_row - direction and (col - 1 == en_passant_col or col + 1 == en_passant_col):
                moves.append((en_passant_row + direction, en_passant_col))

    elif piece[1] == 'R':  # Rook
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        for dr, dc in directions:
            for i in range(1, BOARD_SIZE):
                new_row, new_col = row + i * dr, col + i * dc
                if not is_valid_move(new_row, new_col):
                    break
                if is_empty_or_opponent(new_row, new_col, current_player):
                    moves.append((new_row, new_col))
                if board[new_row][new_col]:
                    break

    elif piece[1] == 'N':  # Knight
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1),
        ]
        for dr, dc in knight_moves:
            new_row, new_col = row + dr, col + dc
            if is_valid_move(new_row, new_col) and is_empty_or_opponent(new_row, new_col, current_player):
                moves.append((new_row, new_col))

    elif piece[1] == 'B':  # Bishop
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in directions:
            for i in range(1, BOARD_SIZE):
                new_row, new_col = row + i * dr, col + i * dc
                if not is_valid_move(new_row, new_col):
                    break
                if is_empty_or_opponent(new_row, new_col, current_player):
                    moves.append((new_row, new_col))
                if board[new_row][new_col]:
                    break

    elif piece[1] == 'Q':  # Queen
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for dr, dc in directions:
            for i in range(1, BOARD_SIZE):
                new_row, new_col = row + i * dr, col + i * dc
                if not is_valid_move(new_row, new_col):
                    break
                if is_empty_or_opponent(new_row, new_col, current_player):
                    moves.append((new_row, new_col))
                if board[new_row][new_col]:
                    break

    elif piece[1] == 'K':  # King
        king_moves = [
            (0, 1), (0, -1), (1, 0), (-1, 0),
            (1, 1), (1, -1), (-1, 1), (-1, -1),
        ]
        for dr, dc in king_moves:
            new_row, new_col = row + dr, col + dc
            if is_valid_move(new_row, new_col) and is_empty_or_opponent(new_row, new_col, current_player):
                moves.append((new_row, new_col))
        # Castling (simplified)
        if piece[0] == 'w' and row == 7:
            if board[7][4] == 'wK':
                if board[7][0] == 'wR' and board[7][1] == '' and board[7][2] == '' and board[7][3] == '':
                    moves.append((7, 2))
                if board[7][7] == 'wR' and board[7][5] == '' and board[7][6] == '':
                    moves.append((7, 6))
        elif piece[0] == 'b' and row == 0:
            if board[0][4] == 'bK':
                if board[0][0] == 'bR' and board[0][1] == '' and board[0][2] == '' and board[0][3] == '':
                    moves.append((0, 2))
                if board[0][7] == 'bR' and board[0][5] == '' and board[0][6] == '':
                    moves.append((0, 6))

    return moves

def move_piece(board, start_row, start_col, end_row, end_col, current_player):
    """Moves a piece on the board. Returns True if the move was valid, False otherwise."""
    legal_moves = get_legal_moves(board, start_row, start_col, current_player)
    if (end_row, end_col) in legal_moves:
        piece = board[start_row][start_col]
        board[start_row][start_col] = ''
        board[end_row][end_col] = piece
        
        #handle castling
        if piece[1] == 'K':
            if start_col - end_col == 2: #kingside
                board[start_row][start_col-1] = board[start_row][0]
                board[start_row][0] = ''
            elif start_col - end_col == -2: #queenside
                board[start_row][start_col+1] = board[start_row][7]
                board[start_row][7] = ''
        
        #handle en passant
        if piece[1] == 'P':
            if end_col != start_col and board[end_row][end_col] == '':
                board[start_row][end_col] = '' #remove the captured pawn
        
        return True
    else:
        return False

def is_check(board, player):
    """Checks if the given player's king is in check."""
    king_pos = None
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] and board[r][c][0] == player and board[r][c][1] == 'K':
                king_pos = (r, c)
                break
        if king_pos:
            break

    if not king_pos:
        return False  # King not found (shouldn't happen, but handle it)

    opponent = 'b' if player == 'w' else 'w'
    # Check if any opponent piece can attack the king
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] and board[r][c][0] == opponent:
                opponent_moves = get_legal_moves(board, r, c, opponent)
                if king_pos in opponent_moves:
                    return True
    return False

def is_checkmate(board, player):
    """Checks if the given player is checkmated."""
    if not is_check(board, player):
        return False

    # Check if there are any legal moves to escape check
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] and board[r][c][0] == player:
                if get_legal_moves(board, r, c, player):
                    return False  # Found a legal move, not checkmate
    return True

def is_stalemate(board, player):
    """Checks if the given player is stalemated."""
    if is_check(board, player):
        return False  # Can't be stalemate if in check

    # Check if there are any legal moves
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] and board[r][c][0] == player:
                if get_legal_moves(board, r, c, player):
                    return False  # Found a legal move, not stalemate
    return True

def save_game(board, current_player, game_state, selected_square, last_move):
    """Saves the current game state to a file."""
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = os.path.join(SAVES_DIR, f"save_{timestamp}.json")
    game_data = {
        "board": board,
        "current_player": current_player,
        "game_state": game_state,
        "selected_square": selected_square,
        "last_move": last_move,
    }
    try:
        with open(filename, "w") as f:
            json.dump(game_data, f)
        print(f"Game saved to {filename}")
        return "Game Saved!"
    except Exception as e:
        print(f"Error saving game: {e}")
        return f"Error saving game: {e}"

def load_game():
    """Loads a game from a file."""
    # Get a list of save files
    save_files = [f for f in os.listdir(SAVES_DIR) if f.startswith("save_") and f.endswith(".json")]
    if not save_files:
        print("No saved games found.")
        return None, None, None, None, None  # Return Nones to indicate no game loaded

    # For simplicity, load the most recent save file
    save_files.sort(key=lambda x: os.path.getmtime(os.path.join(SAVES_DIR, x)), reverse=True)
    latest_save = save_files[0]
    filename = os.path.join(SAVES_DIR, latest_save)

    try:
        with open(filename, "r") as f:
            game_data = json.load(f)
        print(f"Game loaded from {filename}")
        board = game_data["board"]
        current_player = game_data["current_player"]
        game_state = game_data["game_state"]
        selected_square = tuple(game_data["selected_square"]) if game_data["selected_square"] else None
        last_move = game_data["last_move"]
        return board, current_player, game_state, selected_square, last_move
    except Exception as e:
        print(f"Error loading game: {e}")
        return None, None, None, None, None

# --- AI ---
def get_ai_move(board, player):
    """Gets the AI's move using the minimax algorithm."""
    def minimax(board, depth, maximizing_player, alpha, beta):
        """Minimax algorithm with alpha-beta pruning."""
        if depth == 0 or is_game_over(board):
            return evaluate_board(board), None, None

        if maximizing_player:
            best_move = None
            max_eval = -float('inf')
            for r in range(BOARD_SIZE):
                for c in range(BOARD_SIZE):
                    if board[r][c] and board[r][c][0] == player:
                        possible_moves = get_legal_moves(board, r, c, player)
                        for move in possible_moves:
                            new_board = [row[:] for row in board]
                            move_piece(new_board, r, c, move[0], move[1], player)
                            evaluation, _, _ = minimax(new_board, depth - 1, False, alpha, beta)
                            if evaluation > max_eval:
                                max_eval = evaluation
                                best_move = (r, c, move[0], move[1])
                            alpha = max(alpha, evaluation)
                            if beta <= alpha:
                                break
                        if beta <= alpha:
                            break
            return max_eval, best_move[0], best_move[1], best_move[2], best_move[3]
        else:
            min_eval = float('inf')
            best_move = None
            for r in range(BOARD_SIZE):
                for c in range(BOARD_SIZE):
                    if board[r][c] and board[r][c][0] != player:
                        possible_moves = get_legal_moves(board, r, c, player)
                        for move in possible_moves:
                            new_board = [row[:] for row in board]
                            move_piece(new_board, r, c, move[0], move[1], player)
                            evaluation, _, _ = minimax(new_board, depth - 1, True, alpha, beta)
                            if evaluation < min_eval:
                                min_eval = evaluation
                                best_move = (r, c, move[0], move[1])
                            beta = min(beta, evaluation)
                            if beta <= alpha:
                                break
                        if beta <= alpha:
                            break
            return min_eval, best_move[0], best_move[1], best_move[2], best_move[3]

    def evaluate_board(board):
        """Evaluates the board from the perspective of the maximizing player (white)."""
        evaluation = 0
        piece_values = {
            'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 100,
        }
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = board[r][c]
                if piece:
                    value = piece_values[piece[1]]
                    if piece[0] == 'w':
                        evaluation += value
                    else:
                        evaluation -= value
        return evaluation

    def is_game_over(board):
        """Checks if the game is over (checkmate or stalemate)."""
        return is_checkmate(board, 'w') or is_checkmate(board, 'b') or is_stalemate(board, 'w') or is_stalemate(board, 'b')

    # Main AI logic:
    depth = 2  # Search depth for minimax
    alpha = -float('inf')
    beta = float('inf')
    _, start_row, start_col, end_row, end_col = minimax(board, depth, True, alpha, beta)
    return start_row, start_col, end_row, end_col

# --- Game Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chess Game")
PIECE_SIZE_FACTOR = 0.7  # Adjust as needed
PIECE_IMAGES = get_piece_images(SQUARE_SIZE * PIECE_SIZE_FACTOR)
board = init_board()
current_player = 'w'
selected_square = None
game_state = "Playing"  # "Playing", "Game Over"
game_over_text = None
last_move = None # Store the last move as a tuple of (start_row, start_col), (end_row, end_col)
play_ai = False #boolean to indicate if we are playing against the AI.
undo_stack = [] # Stack to store game states for undo functionality

def switch_player():
    """Switches the current player."""
    global current_player
    current_player = 'b' if current_player == 'w' else 'w'
    
def undo_move():
    """Undoes the last move, if possible."""
    global board, current_player, selected_square, game_state, last_move
    if undo_stack:
        board, current_player, selected_square, last_move = undo_stack.pop()
        game_state = "Playing" #set the game state to playing when we undo.
        game_over_text = None #clear the game over text

def play_vs_ai():
    """Sets the game mode to play against the AI."""
    global play_ai
    play_ai = True
    global board, current_player, selected_square, game_state, last_move
    board = init_board() #reset the board.
    current_player = 'w' #always start with white.
    selected_square = None
    game_state = "Playing"
    last_move = None

# --- Main Game Loop ---
running = True
button_rects = [] #store the button rects and actions

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            
            #handle button clicks.
            for button_rect, button_action in button_rects: #iterate through the button actions.
                if button_rect.collidepoint(x, y):
                    result = button_action() # Execute the action
                    if isinstance(result, tuple): #if the action returns a tuple, it's the game state.
                        board, current_player, game_state, selected_square, last_move = result
                        if board is None: #if board is none, then no game was loaded.
                            board = init_board() # Reset the board
                            current_player = 'w'
                            game_state = "Playing"
                            selected_square = None
                            last_move = None
                    elif isinstance(result, str):
                        display_message(screen, result)
                    break # Only handle one button click per event
            
            if 0 <= x < SCREEN_WIDTH- MENU_WIDTH and 0 <= y < SCREEN_HEIGHT: #make sure it is on the board.
                col = x // SQUARE_SIZE
                row = y // SQUARE_SIZE

                if selected_square:
                    start_row, start_col = selected_square
                    
                    # Store the currentstate for undo
                    undo_stack.append(( [row[:] for row in board], current_player, selected_square, last_move))
                    if move_piece(board, start_row, start_col, row, col, current_player):
                        last_move = ( (start_row, start_col), (row, col) ) #store the last move
                        
                        if is_checkmate(board, 'w' if current_player == 'b' else 'b'):
                            game_state = "Game Over"
                            game_over_text = f"{current_player.upper()} wins by checkmate!"
                        elif is_stalemate(board, 'w' if current_player == 'b' else 'b'):
                            game_state = "Game Over"
                            game_over_text = "Stalemate!"
                        else:
                            switch_player()
                        selected_square = None
                    else:
                        selected_square = row, col
                else:
                    selected_square = row, col
                    
    # Draw everything
    draw_board(screen, board, selected_square, get_legal_moves(board, selected_square[0], selected_square[1], current_player) if selected_square else [], last_move, (find_king(board, 'w') if is_check(board, 'w') else find_king(board, 'b') if is_check(board, 'b') else None))
    button_rects = draw_menu(screen, game_state, current_player, selected_square, game_over_text) #get the button rects.
    pygame.display.flip()
    
    # AI move
    if play_ai and current_player == 'b' and game_state == 'Playing':
        pygame.time.delay(500)  # Add a delay for a more "human-like" response
        
        # Store the current state for undo
        undo_stack.append(( [row[:] for row in board], current_player, selected_square, last_move))
        
        ai_start_row, ai_start_col, ai_end_row, ai_end_col = get_ai_move(board, 'b')
        if move_piece(board, ai_start_row, ai_start_col, ai_end_row, ai_end_col, 'b'):
            last_move = ( (ai_start_row, ai_start_col), (ai_end_row, ai_end_col) )
            if is_checkmate(board, 'w'):
                game_state = "Game Over"
                game_over_text = "AI wins by checkmate!"
            elif is_stalemate(board, 'w'):
                game_state = "Game Over"
                game_over_text = "Stalemate!"
            else:
                switch_player()
        selected_square = None

def find_king(board, player):
    """Finds the coordinates of the king for the given player."""
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] and board[r][c][0] == player and board[r][c][1] == 'K':
                return r, c
    return None

pygame.quit()
sys.exit()