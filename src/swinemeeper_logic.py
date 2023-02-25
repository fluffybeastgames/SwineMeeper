### SWINEMEEPER!!!

import random as rand
import tkinter as tk # currently only used in this script to grab const values tk.NORMAL and tk.DISABLED

GAME_STATUS_INIT = 'Initializing'
GAME_STATUS_READY = 'Ready'
GAME_STATUS_IN_PROGRESS = 'In Progress'
GAME_STATUS_GAME_OVER = 'Game Over'

CELL_STATUS_HIDDEN = 0 # available
CELL_STATUS_EXPOSED = 1
CELL_STATUS_FLAG = 2
CELL_STATUS_FLAG_MAYBE = 3
CELL_STATUS_BOOM = 4
CELL_STATUS_BOMB_EXPOSED = 5 
CELL_STATUS_FLAG_WAS_WRONG = 6


class MinesweeperCell:
    def __init__(self, row, col):
#        print(f'Initializing cell [{row}][{col}]')
        self.row = row 
        self.col = col
        self.contains_bomb = False
        self.neighbors = 0
        self.status = CELL_STATUS_HIDDEN
    
    def enabled(self):
        return self.status in (CELL_STATUS_HIDDEN, CELL_STATUS_FLAG, CELL_STATUS_FLAG_MAYBE)
    
    def get_img_key(self):
        if self.status == CELL_STATUS_EXPOSED:
            return f'img_{self.neighbors}'
        elif self.status == CELL_STATUS_FLAG:
            return 'img_flag'
        elif self.status == CELL_STATUS_FLAG_MAYBE: # TODO add logic and image
            return 'img_flag_maybe'
        elif self.status == CELL_STATUS_BOOM:
            return 'img_boom'
        elif self.status == CELL_STATUS_BOMB_EXPOSED: # TODO add logic and image
            return 'img_bomb'
        elif self.status == CELL_STATUS_FLAG_WAS_WRONG: # TODO add logic and image
            return 'img_bad_flag'
        else: # hidden should be the only remaining option
            return 'img_hidden'
        

class SwinemeeperBoard:
    def __init__(self, num_rows, num_cols, num_bombs):

        print('Initializing board object')
        print(f'Parameters: {num_rows} rows x {num_cols} with {num_bombs} bombs')
        
        if num_bombs >= num_rows*num_cols:
            raise ValueError('Too many bombs!')

        self.num_rows = num_rows
        self.num_cols = num_cols
        self.num_bombs = num_bombs
        self.turn_count = 0 # will be incremented every time a valid click event is encountered #TODO HERE!!!!! REMOVE THIS AND REPLACE WITH FUNC

        self.board = [[MinesweeperCell(i, j) for j in range(num_cols)] for i in range(num_rows)]

        self.add_bombs(num_bombs)
        self.calculate_neighbors()

        self.game_status = GAME_STATUS_READY

    def add_bombs(self, num_bombs_to_add):
        num_attempts = 0
        num_added = 0

        while (num_added < num_bombs_to_add):
            num_attempts = num_attempts + 1       
            target_row = rand.randrange(self.num_rows)
            target_col = rand.randrange(self.num_cols)
            
            if not self.board[target_row][target_col].contains_bomb:
                self.board[target_row][target_col].contains_bomb = True
                num_added = num_added + 1
        
        print(f'Added {num_bombs_to_add} bombs in {num_attempts} attempts.')

    
    def remove_bomb(self, cell_coords): # eg if encountered on first move
        self.board[cell_coords[0]][cell_coords[1]].contains_bomb = False


    def calculate_neighbors(self):
    # Record how many bombs are adjacent to each cell. 
    # In cells containing bombs, the number of neighbors is irrelevant 
    
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                num_adjacent_bombs = 0

                #check above
                if row > 0: 
                    if self.board[row - 1][col].contains_bomb: num_adjacent_bombs += 1
                    
                    if col > 0: # top left
                        if self.board[row - 1][col - 1].contains_bomb: num_adjacent_bombs += 1

                    if (self.num_cols - col > 1): # top right
                        if self.board[row - 1][col + 1].contains_bomb: num_adjacent_bombs += 1

                #check below
                if self.num_rows - row > 1: 
                    if self.board[row + 1][col].contains_bomb: num_adjacent_bombs += 1
                    
                    if col > 0: # top left
                        if self.board[row + 1][col - 1].contains_bomb: num_adjacent_bombs += 1

                    if (self.num_cols - col > 1): # top right
                        if self.board[row + 1][col + 1].contains_bomb: num_adjacent_bombs += 1

                #check left/right
                if col > 0: # left
                    if self.board[row][col - 1].contains_bomb: num_adjacent_bombs += 1

                if (self.num_cols - col > 1): # right
                    if self.board[row][col + 1].contains_bomb: num_adjacent_bombs += 1

                self.board[row][col].neighbors = num_adjacent_bombs
        

    def print_display_grid(self):
        print(f'\nGame Status: {self.game_status}')
        str_output = ''
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                if self.board[row][col].visible:
                    if self.board[row][col].flag:
                        char_cell = 'F'
                    elif self.board[row][col].contains_bomb:
                        char_cell = '*'
                    elif self.board[row][col].neighbors == 0:
                        char_cell = ' '
                    else:
                        char_cell = str(self.board[row][col].neighbors)

                else:
                    char_cell = '-'
                
                str_output = f'{str_output}\t{char_cell}'

            str_output = f'{str_output}\n'    
        
        print(str_output)        


    def get_dict_of_cell_images(self): # returns a dict where they keys are cell coords and the values are the current image that should be associated with the corresponding cell
        dict_out = {}

        for row in range(self.num_rows):
            for col in range(self.num_cols):
                if self.board[row][col].flag:
                    dict_out[(row,col)] = 'img_flag'

                elif self.board[row][col].visible:
                    if self.board[row][col].contains_bomb:
                        dict_out[(row,col)] = 'img_boom'

                    else:
                        dict_out[(row,col)] = f'img_{self.board[row][col].neighbors}'
                        
                else:
                    dict_out[(row,col)] = 'img_hidden'
                
        return dict_out


    def get_dict_of_cell_states(self): # returns a dict where they keys are cell coords and the values are tk.NORMAL or tk.DISABLED
        dict_out = {}

        for row in range(self.num_rows):
            for col in range(self.num_cols):
                if self.board[row][col].enabled:
                    dict_out[(row,col)] = tk.NORMAL
                else:
                    dict_out[(row,col)] = tk.DISABLED
                
        return dict_out


    def induce_game_over(self, losing_coords):
        # Call this method when the game state is switched to game over. Disables all cells
        self.game_status = GAME_STATUS_GAME_OVER
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                self.board[row][col].enabled = False
                    

    def toggle_flag(self, cell_coords):  # aka right click
        row = cell_coords[0]
        col = cell_coords[1]
        
        MAYBE_FLAG_ENABLED = True # TODO turn into a user option

        if self.game_status in (GAME_STATUS_READY, GAME_STATUS_IN_PROGRESS):
            cell_status = self.board[row][col].status

            if cell_status == CELL_STATUS_HIDDEN:
                self.board[row][col].status = CELL_STATUS_FLAG
            elif cell_status == CELL_STATUS_FLAG:

                if MAYBE_FLAG_ENABLED:
                    self.board[row][col].status = CELL_STATUS_FLAG_MAYBE
                else:
                    self.board[row][col].status = CELL_STATUS_HIDDEN

            elif cell_status == CELL_STATUS_FLAG_MAYBE:
                self.board[row][col].status = CELL_STATUS_HIDDEN


    def valid_target(self, row, col):
    # Check if a row/column is a) in bounds and b) is 'exposable'
        if row >= 0 and row < self.num_rows and col >= 0 and col < self.num_cols:
            return (self.board[row][col].status == CELL_STATUS_HIDDEN)
        else:
            return False


    def expose_cell(self, cell_coords, was_clicked=True): # aka left click. If was_clicked=False then this cell was exposed by a neighbor recursively or through middle clicking
        # print(f'expose cell {cell_coords}')
        row = cell_coords[0]
        col = cell_coords[1]

        cell_status = self.board[row][col].status

        if self.game_status in (GAME_STATUS_READY, GAME_STATUS_IN_PROGRESS) and cell_status == CELL_STATUS_HIDDEN: # proceed

            if was_clicked:
                self.game_status = GAME_STATUS_IN_PROGRESS
                self.turn_count += 1

            if self.board[row][col].contains_bomb:
                if self.turn_count <= 1: # move bomb to a new location, recalculate neighbor counts, and reveal newly empty cell                        
                    print('OH NO a bomb on the first move') # HMMMM what about an option to implement 'suicide minesweeper' where you're guaranteed 0 neighbors on 1st move and then have to left click on bombs to expose more territory?
                    self.add_bombs(1)
                    self.remove_bomb(cell_coords)
                    self.calculate_neighbors()
                    # self.print_bomb_grid()

                else:
                    self.board[row][col].status = CELL_STATUS_BOOM
                    self.induce_game_over(cell_coords)
            else:
                self.board[row][col].status = CELL_STATUS_EXPOSED

            # start search for newly exposed "0 neighbors" cells if cell value = 0
            if self.board[row][col].neighbors == 0:
                if self.valid_target(row - 1, col - 1): self.expose_cell((row - 1, col - 1))
                if self.valid_target(row - 1, col): self.expose_cell((row - 1, col))
                if self.valid_target(row - 1, col + 1): self.expose_cell((row - 1, col + 1))
                
                if self.valid_target(row, col - 1): self.expose_cell((row, col - 1))
                if self.valid_target(row, col + 1): self.expose_cell((row, col + 1))

                if self.valid_target(row + 1, col - 1): self.expose_cell((row + 1, col - 1))
                if self.valid_target(row + 1, col): self.expose_cell((row + 1, col))
                if self.valid_target(row + 1, col + 1): self.expose_cell((row + 1, col + 1))


    def expand_solution(self, cell_coords): # aka middle click
        row = cell_coords[0]
        col = cell_coords[1]

        if self.game_status in (GAME_STATUS_IN_PROGRESS):
            if self.board[row][col].status == CELL_STATUS_EXPOSED: # can't expand if we can't see the neighboring bomb count
                print('to do expand')
                # check if number of adjacent flags is the same as num_neighbors
                

                # if not self.board[row][col].flag: # can't expose if a flag is covering the cell - remove the flag first with toggle_flag()

                #     self.board[row][col].visible = True

                #     if self.board[row][col].contains_bomb:
                #         #print('Game over man')
                #         self.game_status = GAME_STATUS_GAME_OVER
                    
                #     else:
                #         self.game_status = GAME_STATUS_IN_PROGRESS
                #         # TODO start search for newly exposed "0 neighbors" cells'


    def print_bomb_grid(self): # for debug purposes
        print('\nBomb grid:')
        str_output = ''
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                str_output = f'{str_output}\t{self.board[row][col].contains_bomb}'

            str_output = f'{str_output}\n'    
        
        print(str_output)


    def print_neighbor_grid(self): # for debug purposes
        print('\nNeighbor grid:')
        str_output = ''
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                str_output = f'{str_output}\t{self.board[row][col].neighbors}'

            str_output = f'{str_output}\n'    
        
        print(str_output)


if __name__ == '__main__':
    print('Don\'t run me! Run swinemeeper_gui.py instead!')