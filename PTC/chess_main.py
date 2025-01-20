from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import chess
import random

app = Flask(__name__)
socketio = SocketIO(app)

# Initialize the chess board
board = chess.Board()
players = {"White": None, "Black": None}  # Track players
turn = "White"  # Track whose turn it is

# Define piece symbols for white and black pieces
piece_symbols = {
    'P': 'P', 'R': 'R', 'N': 'N', 'B': 'B', 'Q': 'Q', 'K': 'K',  # Black pieces (lowercase)
    'p': 'p', 'r': 'r', 'n': 'n', 'b': 'b', 'q': 'q', 'k': 'k',  # White pieces (uppercase)
    None: '.'  # Empty squares are represented by a dot
}

# Function to render the chessboard in a plain text format using custom font symbols
def render_board():
    board_rows = []
    for row in range(7, -1, -1):  # Ranks 8 to 1
        row_pieces = []
        for col in range(8):  # Files a to h
            piece = board.piece_at(row * 8 + col)
            if piece:
                # Determine if the piece is white or black
                piece_color = 'white-piece' if piece.color == chess.WHITE else 'black-piece'
                # Convert all piece symbols to uppercase
                piece_symbol = piece.symbol().upper()
                row_pieces.append(f'<span class="{piece_color}">{piece_symbol}</span>')
            else:
                # Empty square
                row_pieces.append('<span class="empty-square">.</span>')
        board_rows.append(" ".join(row_pieces))
    return "<br>".join(board_rows)  # Use <br> for newlines in HTML

@app.route('/')
def index():
    board_str = render_board()
    return render_template('index.html', board_str=board_str, error_message=None, players=players, turn=turn)

@app.route('/set_name', methods=['POST'])
def set_name():
    name = request.form.get('name')
    global players, turn

    # Assign the player randomly to white or black
    if players['White'] is None:
        players['White'] = name
        turn = "White"  # The first person plays as White, the second one plays as Black
        return {"color": 'White'}

    elif players['Black'] is None:
        players['Black'] = name
        return {"color": 'Black'}

    return {"color": 'None'}

# WebSocket event: Listen for a move from a client
@socketio.on('move')
def handle_move(move):
    global turn
    error_message = None

    try:
        chess_move = chess.Move.from_uci(move)
        if chess_move in board.legal_moves:
            board.push(chess_move)
            turn = "Black" if turn == "White" else "White"  # Toggle turn
        else:
            error_message = "Invalid move! Please try again."
    except Exception as e:
        error_message = f"Error: {str(e)}"

    board_str = render_board()
    emit('update_board', {'board_str': board_str, 'error_message': error_message, 'turn': turn}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5500, debug=True,allow_unsafe_werkzeug=True)
