# Pente 
# 2 players
# take turns placing 1 pip on a grid
# ways to win:
# - place 5 pips in a row
# - make 5 captures
#   - a capture is placing a pip
#     to enclose exactly 2 pips in a row
#     of the other player's pips
#   - the captured pips are removed from the grid

import copy
import random
import MiniMax as mm
import math

NUM_GAMES = 1          # number of games the program will play
NUM_PLAYERS = 2        # number of players (ONLY 2 for now)
NUM_IN_A_ROW = 5       # number of pips in a row needed for a win
NUM_CAPTURES = 5       # number of captures needed for a win
DIMENSIONS = 8         # square length of the board (D x D sized board)
AI_BREADTH = 30        # max number of moves the minimax will consider (0=all available)
AI_DEDTH = 4           # max number of moves in the future the minimax will consider

X_DIRS = [0 , 1,1,1,0,-1,-1,-1]
Y_DIRS = [-1,-1,0,1,1, 1, 0,-1]

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
class Grid:
    def __init__(self, dim:int):
        self.dim = dim
        self.empty_spaces = dim * dim
        self.pips = [0 for i in range(self.empty_spaces)]
    def __str__(self) -> str:
        s = ""
        for i in range(len(self.pips)):
            colored = ""
            if self.pips[i] == 0: colored += "O "
            elif self.pips[i] == 1: colored += f"{(bcolors.FAIL)}0{(bcolors.ENDC)} "
            else: colored += f"{(bcolors.OKBLUE)}0{(bcolors.ENDC)} "
            s += f"{colored}"
            if (i+1) % self.dim == 0: s += "\n"
        return s
    def __str_last_move__(self, last_move) -> str:
        s = ""
        for i in range(len(self.pips)):
            colored = ""
            pip_type = "X" if last_move[0] + last_move[1]*self.dim == i else "0"
            if self.pips[i] == 0: colored += "O "
            elif self.pips[i] == 1: colored += f"{(bcolors.FAIL)}{pip_type}{(bcolors.ENDC)} "
            else: colored += f"{(bcolors.OKBLUE)}{pip_type}{(bcolors.ENDC)} "
            s += f"{colored}"
            if (i+1) % self.dim == 0: s += "\n"
        return s
    def __deepcopy__(self, memo):
        copied = Grid(self.dim)
        copied.pips = copy.deepcopy(self.pips)
        return copied
    def InGrid(self, x, y) -> bool:
        return y >= 0 and y < self.dim and x >= 0 and x < self.dim
    def Pip(self, x, y) -> int:
        return self.pips[y * self.dim + x]
    def AddPip(self, row, col, player):
        if self.InGrid(row, col) < 0:
            print(f"cannot place pip at ({row}, {col}): outside range")
            return False
        if self.pips[col * self.dim + row] > 0:
            print(f"cannot place pip at ({row}, {col}): pip here already")
            return False
        self.empty_spaces -= 1
        self.pips[col * self.dim + row] = player
        return True
    def RemovePip(self, row, col):
        self.empty_spaces += 1
        self.pips[col * self.dim + row] = 0
        return (row, col)
    
class Player:
    def __init__(self, style=0):
        self.captures = 0
        self.style = style
        
# from iMalc from https://cboard.cprogramming.com/c-programming/119173-connect-5-algorithm-c.html
def CheckDirections(grid:Grid, amount:int, player:int, start_x:int, start_y:int, check_function, check_all_dirs:bool):
    result = []
    distance = amount if amount > 0 else DIMENSIONS 
    for i in range(8):
        x = start_x
        y = start_y 
        sequence = []
        for j in range(distance):
            if not grid.InGrid(x, y):
                break   
            pip_here = grid.Pip(x, y)        
            if not check_function(pip_here, player, len(sequence)):
                break
            tup = (x, y)
            sequence.append(tup)
            x += X_DIRS[i]        
            y += Y_DIRS[i]     
        if len(sequence) >= amount:
            if not check_all_dirs:
                return (player, sequence)
            else: 
                tup = (player, sequence)
                result.append(tup)
    return result

def Capture(grid:Grid, place_x:int, place_y:int):
    def Check(pip, matching, current_sequence) -> bool:
        if pip == 0:
            return False
        if current_sequence == 0:
            return pip == matching
        elif current_sequence < 3:
            return pip != matching
        else: return pip == matching
            
    player = grid.Pip(place_x, place_y)
    results = CheckDirections(grid, 4, player, place_x, place_y, Check, True)
    pips_to_remove = []
    if len(results) == 0: 
        return pips_to_remove
    sequences = []
    # print(results)
    for result in results:
        # print (result)
        for seq in result[1]:
            sequences.append(seq)
    if len(sequences) == 0:
        return pips_to_remove
    for pip in sequences:
        x = pip[0]
        y = pip[1]
        here = grid.Pip(x, y)
        if here != player:
            p = (here, (x, y))
            pips_to_remove.append(p)
    return pips_to_remove
    
def MaxCountVertical(grid:Grid, player_index:int):
    max_count = 0
    for xx in range(grid.dim):
        count = 0
        for yy in range(grid.dim):
            if grid.pips[yy * grid.dim + xx] == player_index+1:
                count += 1
                max_count = max(count, max_count)
            else: 
                count = 0
                if grid.dim - yy < max_count: break
    return max_count

def MaxCountHorizontal(grid:Grid, player_index:int):
    max_count = 0
    for yy in range(grid.dim):
        count = 0
        for xx in range(grid.dim):
            if grid.pips[yy * grid.dim + xx] == player_index+1:
                count += 1
                max_count = max(count, max_count)
            else: 
                count = 0
                if grid.dim - xx < max_count: break
    return max_count

def MaxCountUpRightDiagonal(grid:Grid, player_index:int):
    max_count = 0
    limit = 0
    for i in range((grid.dim * 2) - 1):
        count = 0
        limit = limit + (1 if i < grid.dim else -1)
        row = min(i, grid.dim - 1)
        col = max(i - grid.dim + 1, 0)
        for j in range(limit):
            if grid.pips[row * grid.dim + col] == player_index+1:
                count += 1
                max_count = max(count, max_count)
            else: 
                count = 0
                if limit - j < max_count: break
            row -= 1
            col += 1
    return max_count

def MaxCountDownRightDiagonal(grid:Grid, player_index:int):
    max_count = 0
    limit = 0
    size = (grid.dim * 2) - 1
    for i in range(size):
        count = 0
        limit = limit + (1 if i < grid.dim else -1)
        row = max(0, i - grid.dim + 1)
        col = max(grid.dim - i - 1, 0)
        for j in range(limit):
            if grid.pips[row * grid.dim + col] == player_index+1:
                count += 1
                max_count = max(count, max_count)
            else: 
                count = 0
                if limit - j < max_count: break
            row += 1
            col += 1
    return max_count

def MaxLengthOfPlayer(grid:Grid, player_index:int):
    return max(MaxCountVertical(grid, player_index), MaxCountHorizontal(grid, player_index), MaxCountUpRightDiagonal(grid, player_index), MaxCountDownRightDiagonal(grid, player_index))

class Game:
    def __init__(self, grid_size, players) -> None:
        self.grid = Grid(grid_size)
        self.players = []
        for i in range(players):
            self.players.append(Player())
        self.current_turn = 0
        self.current_player = 0
        self.last_move = (-1,-1)
        self.history = {} # history => { turn:[player, placement, result, winning]}
    def __deepcopy__(self, memo):
        copied = Game(0,0)
        copied.grid = copy.deepcopy(self.grid)
        copied.players = copy.deepcopy(self.players)
        copied.current_turn = copy.deepcopy(self.current_turn)
        copied.current_player = copy.deepcopy(self.current_player)
        copied.last_move =  copy.deepcopy(self.last_move)
        copied.history =  copy.deepcopy(self.history)
        return copied
    def AvailableMoves(self, ordered=False, shuffled=False, maximum=0, consider_only_adj=False):
        result = [(idx - int(idx/self.grid.dim)*self.grid.dim, int(idx/self.grid.dim)) for idx, z in enumerate(self.grid.pips) if z == 0]
        if ordered or consider_only_adj:
            # order by distance to other non-0's
            distance = {}
            for point in result:
                distance[point] = 0
                for xx in range(-1,2):
                    for yy in range(-1,2):
                        if not self.grid.InGrid(point[0]+xx, point[1]+yy): continue
                        distance[point] += 1 if self.grid.Pip(point[0]+xx,point[1]+yy) > 0 else 0
            if ordered:
                sorted_by_distance = dict(sorted(list(distance.items()), key=lambda item: item[1], reverse=True))
                result = list(sorted_by_distance.keys())
            if consider_only_adj:
                result = [x for x in result if distance[x] > 0]
        if maximum >= 1:
            result = result[0:min(maximum, len(result))]
        if shuffled:
            random.shuffle(result)
        return result
    def PlacePip(self, placement):
        if placement == None:
            return False
        player = self.current_player+1
        added = self.grid.AddPip(placement[0], placement[1], player)
        if added: 
            self.last_move = placement
            self.history[self.current_turn] = [player, placement, None, False]
            # check for captures
            total_captures = Capture(self.grid, self.last_move[0], self.last_move[1])
            if len(total_captures) > 0:
                # print("CAPTURE!!!")
                self.history[self.current_turn][2] = total_captures
                for cap in total_captures:
                    self.grid.RemovePip(cap[1][0], cap[1][1])
                self.players[self.current_player].captures += round(len(total_captures) / 2)
            # print(game.grid)
            self.NextTurn() # INCREMENT CURRENT TURN AND PLAYER HERE
        return added
    def GameOver(self):
        # check for captures
        for i in range(len(self.players)):
            if self.players[i].captures >= NUM_CAPTURES:
                self.history[self.current_turn-1][3] = True
                return True
        # check for winning line
        max_line = max([MaxLengthOfPlayer(self.grid, player_index) for player_index in range(len(self.players))])
        # if WinningLine(self.grid, NUM_IN_A_ROW) != 0:
        if max_line >= NUM_IN_A_ROW:
            self.history[self.current_turn-1][3] = True
            return True
        if self.grid.empty_spaces == 0:
            return True
        return False
    def NextTurn(self):
        self.current_turn += 1
        self.current_player = self.current_turn % NUM_PLAYERS
    def IsWinning(self, player_index):
        if len(self.history) == 0: return False
        # return self.players[player_index].captures >= NUM_CAPTURES or WinningLine(self.grid, NUM_IN_A_ROW) == player_index+1
        max_line = MaxLengthOfPlayer(self.grid, player_index)
        return self.players[player_index].captures >= NUM_CAPTURES or max_line >= NUM_IN_A_ROW
    def LastAction(self):
        if len(self.history) == 0:
            return [-1, (-1,-1), None, False]
        return self.history[len(self.history)-1]
    def Results(self):
        result = ""
        for i in range(len(self.players)):
            result += f"Player {i+1} -- captures: {self.players[i].captures}\n"         
        return result
    def UndoTurn(self):
        if self.current_turn <= 0:
            return
        
        move = self.history[self.current_turn-1] # [player, placement, result, winning?]
        del self.history[self.current_turn-1]
        
        # remove piece here
        self.grid.RemovePip(move[1][0], move[1][1])

        # put pieces back
        if move[2] is not None:
            for pip in move[2]:
                self.grid.AddPip(pip[1][0], pip[1][1], pip[0])
            self.players[move[0]-1].captures -= round(len(move[2]) / 2)
        self.current_turn -= 1
        self.current_player = self.current_turn % NUM_PLAYERS
        
class GameEvaluator:
    def PlayerPower(game:Game, player_index):
        player = player_index+1
        pip_amount = len([p for p in game.grid.pips if p == player])
        pip_factor = 1
        pip_power = pip_amount * pip_factor
        capture_amount = game.players[player_index].captures
        capture_factor = 10
        capture_power = capture_amount * capture_factor
        line_amount = MaxLengthOfPlayer(game.grid, player_index)
        line_factor = 5
        line_power = line_amount * line_factor
        winning_power = 1000 if line_amount >= NUM_IN_A_ROW or capture_amount >= NUM_CAPTURES else 0
        return round(pip_power + capture_power + line_power + winning_power)

def RandomMoveChoice(game):
    moves = game.AvailableMoves()
    return random.choice(moves)

def MinimaxMoveChoice(game:Game):
    game_copy = copy.deepcopy(game)
    maximize = game.current_player == 0
    breadth = int(AI_BREADTH * min((game.current_turn+1)/ 8, 1))
    move_evaluation = mm.Minimax(game_copy, AI_DEDTH, breadth, float('-inf'), float('inf'), maximize, True)
    print(f"\nmove evaluation = {move_evaluation[0]} (score={move_evaluation[1]})")
    move_choice = move_evaluation[0]
    del game_copy
    if move_choice == None:
        moves = game.AvailableMoves()
        move_choice = random.choice(moves)
    return move_choice

def PlayerMoveChoice(game:Game):
    while True:
        action = input("input move \"x y\" : ")
        action = action.strip().split(" ")
        if len(action) != 2: continue
        try:
            action = [int(a) for a in action]
        except: continue
        if not game.grid.InGrid(action[0], action[1]): continue
        return (action[0], action[1])
    
def GetPlayStyle(player):
    if player.style == 1: return PlayerMoveChoice
    elif player.style == 2: return MinimaxMoveChoice
    return RandomMoveChoice

def RunGames(player_1_style, player_2_style, pause_after_moves):
    current_num_games = 0
    while current_num_games < NUM_GAMES:
        # start new game
        game = Game(DIMENSIONS, NUM_PLAYERS)
        game.players[0].style = player_1_style
        game.players[1].style = player_2_style
        # take turns until game over
        while True:
            if game.grid.empty_spaces == 0:
                print("NO MOVES AVAILBLE! ending the game")
                break
            move_choice = None
            print(f"Player {game.current_player+1}'s Turn")
            # current player making a choice
            choice_function = GetPlayStyle(game.players[game.current_player])
            move_choice = choice_function(game)
            
            print("======================================")
            print(f"playing on {move_choice}\n")
            # trying to add that choice to the board
            choice_result = game.PlacePip(move_choice)
            if not choice_result:
                continue
            print(game.grid.__str_last_move__(move_choice))
            # check for captures and x-in-a-row
            if game.GameOver():
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                if game.IsWinning(0): print(f"{bcolors.FAIL}PLAYER 1 WINS!!{bcolors.ENDC} ")
                else: print(f"{bcolors.OKBLUE}PLAYER 2 WINS!!{bcolors.ENDC}")
                print(game.grid)
                print(game.Results())  
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~")
                break
            # check for continue
            if pause_after_moves:
                action = input("continue? ('q' to quit) ")
                if action == "q": break
        # end the game  
        current_num_games += 1
        if (current_num_games >= NUM_GAMES): break
        action = input("press Return/Enter to continue (q to quit) ")
        if action == "q": break
    # finish
    print("Goodbye!~")
    
if __name__ == "__main__":
    print("===============")
    print("=====PENTE=====")
    print("===============")
    p1 = input(f"{bcolors.FAIL}Player 1{bcolors.ENDC} (0-random, 1-player, 2-minimax): ")
    p2 = input(f"{bcolors.OKBLUE}Player 2{bcolors.ENDC} (0-random, 1-player, 2-minimax): ")
    pause = input("Pause after each move? (y/n): ")
    RunGames(int(p1), int(p2), pause[:1].lower() == 'y')