import random
import Pente as p

def Minimax(game:p.Game, depth:int, breadth:int, alpha:int, beta:int, maximizing_player:bool, top=False):
    if depth == 0 or game.GameOver():
        maximizer_power = p.GameEvaluator.PlayerPower(game, 0)      
        minimizer_power = p.GameEvaluator.PlayerPower(game, 1)   
        # print(f"at depth {depth}: p{1 if maximizing_player else 2}: {maximizer_power} {minimizer_power}")
        return (maximizer_power - minimizer_power) * max(depth, 1)
    best_move = None
    available_moves = game.AvailableMoves(True, True, breadth, False)
    i = 0
    if top:
        print(f"considering: {len(available_moves)} moves...")
    if maximizing_player:
        max_eval = float('-inf')
        for move in available_moves:
            game.PlacePip(move)
            evaluate = Minimax(game, depth-1, breadth, alpha, beta, False)
            if max_eval < evaluate: best_move = move
            max_eval = max(max_eval, evaluate)
            if top: 
                i += 1
                PrintMoveEval(available_moves, move, evaluate, i)
            game.UndoTurn()
            alpha = max(evaluate, alpha)
            if beta <= alpha:
                break
        if top: return best_move, max_eval
        return max_eval
    else:
        min_eval = float('inf')
        for move in available_moves:
            game.PlacePip(move)
            evaluate = Minimax(game, depth-1, breadth, alpha, beta, True)
            if min_eval > evaluate: best_move = move
            min_eval = min(min_eval, evaluate)
            if top: 
                i += 1
                PrintMoveEval(available_moves, move, evaluate, i)
            game.UndoTurn()
            beta = min(evaluate, beta)
            if beta <= alpha:
                break
        if top: return best_move, min_eval
        return min_eval

debug = False
def PrintMoveEval(available_moves:list, move, evaluate, idx):
    if debug:
        print(f">> move {idx}/{len(available_moves)} == {move} ({evaluate:+})")
    else:
        print(".", end=" ")
    