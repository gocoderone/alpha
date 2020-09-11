'''
MULTIPLAYER ENVIRONMENT
'''

from time import sleep
import math
import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2

IMAGE_DIR = 'img/'

def convert_to_rgba(img):
    if img.shape[2] == 3:
        # convert img from RGB to RGBA
        b_channel, g_channel, r_channel = cv2.split(img)
        alpha_channel = np.ones(b_channel.shape, dtype=b_channel.dtype)
        img = cv2.merge((b_channel, g_channel, r_channel, alpha_channel))
        #cvtColor(img, cv2.COLOR_BGRA2BGR)
    return img

# load images
img_empty = convert_to_rgba(mpimg.imread(IMAGE_DIR + 'empty.png'))
img_p1 = convert_to_rgba(mpimg.imread(IMAGE_DIR + 'p1.png'))
img_p2 = convert_to_rgba(mpimg.imread(IMAGE_DIR + 'p2.png'))
img_bomb = convert_to_rgba(mpimg.imread(IMAGE_DIR + 'bomb.png'))
img_exploding_bomb = convert_to_rgba(mpimg.imread(IMAGE_DIR + 'exploding_bomb.png'))
img_hard_block = convert_to_rgba(mpimg.imread(IMAGE_DIR + 'hard_block.png'))
img_soft_block = convert_to_rgba(mpimg.imread(IMAGE_DIR + 'soft_block.png'))
img_exploding_tile = convert_to_rgba(mpimg.imread(IMAGE_DIR + 'exploding_tile.png'))

# map labels to images
dict_img = {
    0: img_empty,
    1: img_p1,
    2: img_p2,
    3: img_soft_block,
    4: img_hard_block,
    5: img_bomb,
    6: img_bomb,
    7: img_bomb,
    8: img_exploding_bomb,
    9: img_exploding_tile
}

# map rewards
d_rewards = {
    'DESTROY_BLOCK': 1,
    'INVALID_MOVE': -10,
    'LOSE_GAME': -100,
    'WIN_GAME': 100,
}

class bcolors:
    RED= '\u001b[31m'
    GREEN= '\u001b[32m'
    YELLOW= '\u001b[33m'
    BLUE='\u001b[34m'
    MAGENTA= '\u001b[35m'
    CYAN= '\u001b[36m'
    RESET= '\u001b[0m'

class actions:
    NONE = 0
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4
    BOMB = 5

# stores bomb's timer & position
class Bomb():

    def __init__(self, position, tiles_in_range, player=0, max_timer=5):
        self.timer = max_timer
        self.position = position
        self.owned_by = player
        self.recently_exploded = False
        self.tiles_in_range = tiles_in_range

    def update_timer(self):
        self.timer -= 1

    def explode(self):
        self.recently_exploded = True

    def clear(self):
        self.recently_exploded = False

# define behavior of player e.g. powerups, score
class Player():

    def __init__(self, number, starting_position, max_bombs):
        self.number = number
        self.position = starting_position
        self.prev_position = starting_position
        self.bombs = []
        self.num_bombs = max_bombs
        self.score = 0

    def update_score(self, reward):
        '''
        reward system:
        +1 destroy block
        -10 invalid move
        -1000 lose game
        +100 win game
        '''
        self.score += reward

# defines the game environment
class Game():

    # environment attributes
    MAX_BOMBS = 1
    MAX_TIMER = 5 # number of steps before bomb explodes

    # dictionary of board labels
    BOARD_DICT = {'empty':0,'player1':1, 'player2':2,'soft_block':3,'hard_block':4,
    'bomb':5,'p1_on_bomb':6, 'p2_on_bomb':7, 'exploding_bomb':8, 'exploding_tile':9}

    # dictionary of rewards
    REWARDS_DICT = {'destroy_blocks':1, 'invalid_move':-10, 'lose':-1000}

    PLAYER_LIST = ['player1','player2']
    ON_BOMB_LIST = ['p1_on_bomb','p2_on_bomb']

    # define movement patterns for each action
    ACTIONS_DICT = {0:(0,0),5:(0,0),1:(0,-1),2:(0,1),3:(-1,0),4:(1,0)}

    def __init__(self,rows=11,cols=13):
        self.rows=rows
        self.cols=cols

    def step(self, player_actions):

        rewards = np.zeros((len(self.players),1)) # rewards assigned this turn
        bomb_list = [] # populate list of bombs to return to players

        # get player's new positions
        for player in self.players:
            # store current position before next move
            player.prev_position = player.position 

            # clear any recent bombs
            for bomb in player.bombs:
                if bomb.recently_exploded == True:
                    self.clear_bomb(bomb)
                    del bomb 
                    player.bombs = [] 

            # get player's action
            action = player_actions[player.number]
            # get player's new position if action is taken
            new_position = tuple([sum(x) for x in zip(self.ACTIONS_DICT[player_actions[player.number]],player.prev_position)])

            if self.check_if_valid(action, player.prev_position, new_position):
                player.position = new_position # valid move, so update player's position
                if action == actions.BOMB:
                    if player.num_bombs > 0:
                        player.bombs.append(Bomb(player.position, self.get_tiles_in_range(player.position), player.number, self.MAX_TIMER)) # create a bomb instance
                        player.num_bombs -= 1 # one less bomb available for the player
                        self.board[player.position] = self.BOARD_DICT[self.ON_BOMB_LIST[player.number]] # place bomb on map
                elif action == actions.NONE:
                    pass
                else:
                    # move
                    self.board[player.position] = self.BOARD_DICT[self.PLAYER_LIST[player.number]]

                    if not self.board[player.prev_position] == self.BOARD_DICT[self.ON_BOMB_LIST[player.number]]:
                        # clear previous position only if it wasn't a just-placed bomb
                        self.board[player.prev_position] = self.BOARD_DICT['empty']
                    else:
                        # player has left behind a bomb
                        self.board[player.prev_position] = self.BOARD_DICT['bomb']
            else:
                # return some invalid move penalty
                player.score += self.get_reward('invalid_move')

            # update timer of any bombs
            for bomb in player.bombs:
                bomb_list.append(bomb)
                bomb.update_timer()                               
                if bomb.timer == 0: # bomb explodes
                    # check if any player is in range of the bomb
                    is_game_over, player_hit = self.check_if_game_over(bomb.tiles_in_range)
                    if is_game_over:
                        self.done = True
                        self.players[player_hit].score += self.get_reward('lose')
                    num_blocks = self.explode_bomb(bomb) # update bomb objects and map
                    player.score += self.get_reward('destroy_blocks', num_blocks)
                    player.num_bombs += 1 # return bomb to the player

        return self.board, self.done, self.players, bomb_list

    def check_if_valid(self, action, curr_pos, new_pos):

        if (action == actions.NONE) or (action == actions.BOMB):
            is_valid = True
        elif (new_pos[0] < 0 or new_pos[1] < 0):
            # trying to move through left or top boundary
            is_valid = False
        elif new_pos[0] >= self.rows or new_pos[1] >= self.cols:
            # trying to move through right or bottom boundary
            is_valid = False
        elif (self.board[tuple(new_pos)] == self.BOARD_DICT['empty']) or (self.board[tuple(new_pos)] == self.BOARD_DICT['exploding_tile']):
            is_valid = True
        else:
            is_valid = False

        return is_valid

    def check_if_game_over(self,tiles):

        is_game_over = False # did a player get hit
        player_hit = None # which player

        for tile in tiles:
            if (self.board[tile] == self.BOARD_DICT['player1']) or (self.board[tile] == self.BOARD_DICT['p1_on_bomb']):
                is_game_over = True
                player_hit = 0

            if (self.board[tile] == self.BOARD_DICT['player2']) or (self.board[tile] == self.BOARD_DICT['p2_on_bomb']):
                is_game_over = True
                player_hit = 1

        return is_game_over, player_hit

    ###################################            
    ###### BOMB HELPER FUNCTIONS ######
    ###################################

    def get_tiles_in_range(self, position):
        '''
        get surrounding 4 tiles impacted near bomb
        '''

        tile_up = (position[0]-1,position[1])
        tile_down = (position[0]+1,position[1])
        tile_left = (position[0],position[1]-1)
        tile_right = (position[0],position[1]+1)
        
        bomb_range = [tile_up, tile_down, tile_left, tile_right, position]
        tiles_to_remove = []

        for tile in bomb_range:
            if (tile[0] < 0 or tile[1] < 0 or tile[0] >= self.rows or tile[1] >= self.cols or 
                self.board[tile] == self.BOARD_DICT['hard_block']):
                # exclude tiles that cross the border of the board
                # or contain indestructible object
                tiles_to_remove.append(tile)

        for tile in tiles_to_remove:
            bomb_range.remove(tile)

        return bomb_range

    def explode_bomb(self, bomb):
        '''
        reset bomb parameters and return number of blocks destroyed
        '''

        num_blocks = 0

        # update tiles that have been impacted
        for tile in bomb.tiles_in_range:
            if self.board[tile] == self.BOARD_DICT['soft_block']:
                num_blocks+=1
            self.board[tile] = self.BOARD_DICT['exploding_tile']

        self.board[bomb.position] = self.BOARD_DICT['exploding_bomb']

        bomb.explode()

        return num_blocks

    def clear_bomb(self, bomb):
        '''
        clear map after recent bomb
        '''

        self.board[bomb.position] = self.BOARD_DICT['empty'] 
        for tile in bomb.tiles_in_range:
            if (self.board[tile] != self.BOARD_DICT['player1']) and (self.board[tile] != self.BOARD_DICT['player2']):
                self.board[tile] = self.BOARD_DICT['empty']

        bomb.clear()
        
    def get_reward(self, item, num_blocks=0):
        '''
        reward system:
        +1 destroy block
        -10 invalid move
        -1000 lose game
        +100 win game
        '''
        if item == 'destroy_blocks':
            return num_blocks * self.REWARDS_DICT[item]
        else:
            return self.REWARDS_DICT[item]

    def reset(self,num_players=2):
        '''
        Initializes a starting board
        '''

        ### move num_players to environment level

        # initalize board
        self.board = np.zeros((self.rows,self.cols)).astype(int)
        self.players = [] # stores player objects
        self.tiles_in_range = [] # stores position of surrounding spaces near a bomb --> should beowned by bomb?
        self.done = False # checks if game over

        # number of soft blocks to place
        num_soft_blocks = int(math.floor(0.3*self.cols*self.rows))

        # initialize players
        assert num_players <= 4
        starting_positions = [(0,0), (self.rows-1, self.cols-1), (0, self.cols-1), (self.rows-1, 0)]
        for i in range(num_players):
            self.players.append(Player(i, starting_positions[i], self.MAX_BOMBS))

        # update map with player locations
        player_list = ['player1', 'player2', 'player3', 'player4']
        for player in range(len(self.players)):
            self.board[self.players[player].position] = self.BOARD_DICT[player_list[player]]

        # place hard blocks
        self.board[1::2,1::2] = self.BOARD_DICT['hard_block']

        ## place soft blocks (random)
        # flatten array
        flat_board = np.reshape(self.board,-1)
        # get positions that can be filled
        open_pos = [i for i in range(len(flat_board)) if flat_board[i] == 0]
        # spots immediately to the right and bottom of player1 can't be filled
        open_pos.remove(1)
        open_pos.remove(2)
        open_pos.remove(self.cols)
        open_pos.remove(self.cols*2)
        # spots immediately to the left and top of player2 can't be filled
        open_pos.remove(self.cols * self.rows - 2)
        open_pos.remove(self.cols * self.rows - 3)
        open_pos.remove(self.cols * self.rows - self.cols*2 - 1)
        open_pos.remove(self.cols * self.rows - self.cols - 1)
        # choose a random subset from open spots
        rand_pos = random.sample(open_pos,num_soft_blocks)
        flat_board[rand_pos] = self.BOARD_DICT['soft_block']
        self.board = np.reshape(flat_board,(self.rows,self.cols))

        return self.board, self.players

    def render(self, graphical=True):
        # renders bomberman environment

        # render with graphics
        if graphical:
            flattened_map = np.reshape(self.board,-1)
            # get rows
            map_rows=[]
            for row in range(self.rows):
                map_rows.append(np.concatenate(([dict_img[i] for i in self.board[row]]),axis=1))

            full_map = np.concatenate(([i for i in map_rows]),axis=0)

            plt.clf()
            plt.imshow(full_map)
            plt.axis('off')
            plt.ion()
            plt.show()
            plt.pause(0.05)
        # render text-based environment
        else:
            print(self)

    def __str__(self):
        # return visualized board
        '''
        Displays board with icons instead of number values
        Player = P
        Bomb = *
        Soft block = O
        Hard block = X
        '''
        #initialize row & col
        row=0
        col=0

        # map icons to board
        d = {0: '     ', 1:f'{bcolors.MAGENTA}  P1 {bcolors.RESET}', 2:f'{bcolors.BLUE}  P2 {bcolors.RESET}', 3:f'{bcolors.YELLOW}  O  {bcolors.RESET}',
         4:'  X  ', 5:f'{bcolors.RED}  *  {bcolors.RESET}', 6:f'{bcolors.MAGENTA} P1* {bcolors.RESET}', 7:f'{bcolors.BLUE} P2* {bcolors.RESET}',
          8:f'{bcolors.RED}  !  {bcolors.RESET}', 9:f'{bcolors.RED} === {bcolors.RESET}'}
        #d = {0: '     ', 1:'  P1 ', 2:'  O  ', 3:'  X  ', 4:'  *  ', 5:'  P* ', 6:'  !  ', 7:' === '}
        flat_board = np.reshape(self.board,-1)
        mapped_board=[d[i] for i in flat_board]
        mapped_board = np.reshape(mapped_board,self.board.shape)

        board_str=""
        for row in range(self.rows):
            row_str = ""
            board_str += "-"*self.cols*6 + "\n"
            for col in range(self.cols):
                row_str += f"|{mapped_board[row,col]}"
            board_str += row_str + "|" + "\n"
        board_str += "-"*self.cols*6
        
        return board_str

if __name__ == '__main__':
    board = Bomberman(5,7)
    board.render()