import chess
import multiprocessing

# Bot Execution

def worker(bot_name, fen, queue):
    try:
        module = __import__(bot_name)
        move = module.next_move(fen)
        queue.put(move)
    except:
        queue.put(None)


def get_safe_move(bot_name, fen):
    queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=worker, args=(bot_name, fen, queue))

    p.start()
    p.join(4)  # 4 sec timeout

    if p.is_alive():
        print(f"{bot_name} timed out.")
        p.terminate()
        return None

    if not queue.empty():
        return queue.get()

    return None


# GAME LOOP

def main():
    move_count = 0
    MAX_MOVES = 200

    board = chess.Board()
    turn = 0

    bot1 = "bot_random"
    bot2 = "bot_smart"   # change here to test

    print(f"\nMatch: {bot1} vs {bot2}\n")

    while not board.is_game_over():

        fen = board.fen()

        current_bot = bot1 if turn == 0 else bot2
        move = get_safe_move(current_bot, fen)

        print(f"{current_bot} played:", move)

        # If Bot failed
        if move is None:
            print(f"{current_bot} failed to move.")
            break

        # If Invalid format
        try:
            move_obj = chess.Move.from_uci(move)
        except:
            print(f"{current_bot} gave invalid format:", move)
            break

        # If Illegal move
        if move_obj not in board.legal_moves:
            print(f"{current_bot} played illegal move:", move)
            break

        # Apply move
        board.push(move_obj)

        move_count += 1
        print(f"Move {move_count}: {move}\n")

        # For Move limit
        if move_count >= MAX_MOVES:
            print("Move limit reached → Draw")
            break

        turn = 1 - turn

    # RESULT

    print("\nGame Over")
    print("Result:", board.result())

    # Winner condition
    if board.result() == "1-0":
        print("Winner: White (Bot 1)")
    elif board.result() == "0-1":
        print("Winner: Black (Bot 2)")
    else:
        print("No Winner (Draw)")

    # Reasons for Game end
    if board.is_checkmate():
        print("Reason: Checkmate")

    elif board.is_stalemate():
        print("Reason: Stalemate")

    elif board.is_insufficient_material():
        print("Reason: Insufficient Material")

    elif board.can_claim_threefold_repetition():
        print("Reason: Threefold Repetition")

    elif board.can_claim_fifty_moves():
        print("Reason: 50-Move Rule")

    elif move_count >= MAX_MOVES:
        print("Reason: Move Limit Reached")

    else:
        print("Reason: Unknown")



if __name__ == "__main__":
    main()
