from flask import Flask, render_template, request, jsonify
import chess
import random

app = Flask(__name__)

# Initialize the chess board and turn tracker
board = chess.Board()
turn = "White"  # Starting turn (White goes first)

# Track players' names
players = {"White": None, "Black": None}


# Function to render the chessboard
def render_board():
    board_rows = []
    for row in range(7, -1, -1):  # Ranks 8 to 1
        row_pieces = []
        for col in range(8):  # Files a to h
            piece = board.piece_at(row * 8 + col)
            if piece:
                piece_color = 'white-piece' if piece.color == chess.WHITE else 'black-piece'
                piece_symbol = piece.symbol().upper()
                row_pieces.append(f'<span class="{piece_color}">{piece_symbol}</span>')
            else:
                row_pieces.append('<span class="empty-square">.</span>')
        board_rows.append(" ".join(row_pieces))
    return "<br>".join(board_rows)


@app.route('/')
def index():
    global turn
    board_str = render_board()
    return render_template('index.html', board_str=board_str, error_message=None, turn=turn, players=players)


@app.route('/set_name', methods=['POST'])
def set_name():
    global players
    name = request.form.get('name')
    random_color = random.choice(["White", "Black"])

    players[random_color] = name  # Assign the name to the random color
    if random_color == "White":
        players["Black"] = "Opponent"  # You can modify this to let the opponent choose as well

    return jsonify({"name": name, "color": random_color})


@app.route('/move', methods=['POST'])
def move():
    global turn
    move = request.form.get('move')
    error_message = None

    try:
        if chess.Move.from_uci(move) in board.legal_moves:
            board.push(chess.Move.from_uci(move))
            turn = "Black" if turn == "White" else "White"  # Toggle turn
        else:
            error_message = "Invalid move! Please try again."
    except Exception as e:
        error_message = f"Error: {str(e)}"

    board_str = render_board()
    return render_template('index.html', board_str=board_str, error_message=error_message, turn=turn, players=players)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
