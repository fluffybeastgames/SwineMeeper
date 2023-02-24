### SWINEMEEPER!!!

import random as rand
import tkinter as tk # currently only used in this script to grab const values tk.NORMAL and tk.DISABLED

GAME_STATUS_INIT = 'Initializing'
GAME_STATUS_READY = 'Ready'
GAME_STATUS_IN_PROGRESS = 'In Progress'
GAME_STATUS_GAME_OVER = 'Game Over'


class MinesweeperCell:
    def __init__(self, row, col):
#        print(f'Initializing cell [{row}][{col}]')
        self.row = row 
        self.col = col
        self.bomb = False
        self.neighbors = 0
        self.visible = False
        self.enabled = True
        self.flag = False # for now let's only worry about basic flags and not maybe flags
    
    #TODO MOVE VALIDMOVE HERE?

class SwinemeeperBoard:
    def __init__(self, num_rows, num_cols, num_bombs):

        print('Initializing board object')
        print(f'Parameters: {num_rows} rows x {num_cols} with {num_bombs} bombs')
        

        if num_bombs >= num_rows*num_cols:
            raise ValueError('Too many bombs!')


        self.num_rows = num_rows
        self.num_cols = num_cols
        self.num_bombs = num_bombs
        self.turn_count = 0 # will be incremented every time a valid click event is encountered
        #self.game_status = GAME_STATUS_INIT

        self.board = [[MinesweeperCell(i, j) for j in range(num_cols)] for i in range(num_rows)]

        self.add_bombs(num_bombs)
        self.calculate_neighbors()

        self.game_status = GAME_STATUS_READY
        

    def remove_bomb(self, cell_coords): # eg if encountered on first move
        self.board[cell_coords[0]][cell_coords[1]].bomb = False


    def add_bombs(self, num_bombs_to_add):
        num_attempts = 0
        num_added = 0

        while (num_added < num_bombs_to_add):
            num_attempts = num_attempts + 1       
            target_row = rand.randrange(self.num_rows)
            target_col = rand.randrange(self.num_cols)
            
            if not self.board[target_row][target_col].bomb:
                self.board[target_row][target_col].bomb = True
                num_added = num_added + 1
        
        print(f'Added {num_bombs_to_add} bombs in {num_attempts} attempts.')


    def calculate_neighbors(self):
    # Record how many bombs are adjacent to each cell. 
    # In cells containing bombs, the number of neighbors is irrelevant 
    
        #Naive attempt: count neighbors for each cell
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                num_adjacent_bombs = 0


                #check above
                if row > 0: 
                    if self.board[row - 1][col].bomb: num_adjacent_bombs = num_adjacent_bombs + 1
                    
                    if col > 0: # top left
                        if self.board[row - 1][col - 1].bomb: num_adjacent_bombs = num_adjacent_bombs + 1

                    if (self.num_cols - col > 1): # top right
                        if self.board[row - 1][col + 1].bomb: num_adjacent_bombs = num_adjacent_bombs + 1

                #check below
                if self.num_rows - row > 1: 
                    if self.board[row + 1][col].bomb: num_adjacent_bombs = num_adjacent_bombs + 1
                    
                    if col > 0: # top left
                        if self.board[row + 1][col - 1].bomb: num_adjacent_bombs = num_adjacent_bombs + 1

                    if (self.num_cols - col > 1): # top right
                        if self.board[row + 1][col + 1].bomb: num_adjacent_bombs = num_adjacent_bombs + 1

                #check left/right
                if col > 0: # left
                    if self.board[row][col - 1].bomb: num_adjacent_bombs = num_adjacent_bombs + 1

                if (self.num_cols - col > 1): # right
                    if self.board[row][col + 1].bomb: num_adjacent_bombs = num_adjacent_bombs + 1


                self.board[row][col].neighbors = num_adjacent_bombs

            


    def print_bomb_grid(self):
        print('\nBomb grid:')
        str_output = ''
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                str_output = f'{str_output}\t{self.board[row][col].bomb}'

            str_output = f'{str_output}\n'    
        
        print(str_output)


    def print_neighbor_grid(self):
        print('\nNeighbor grid:')
        str_output = ''
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                str_output = f'{str_output}\t{self.board[row][col].neighbors}'

            str_output = f'{str_output}\n'    
        
        print(str_output)


    def cell_enabled(self, btn_coords):
        return self.board[btn_coords[0]][btn_coords[1]].enabled


    def print_display_grid(self):
        print(f'\nGame Status: {self.game_status}')
        str_output = ''
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                if self.board[row][col].visible:
                    if self.board[row][col].flag:
                        char_cell = 'F'
                    elif self.board[row][col].bomb:
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


    def get_num_flags_placed(self): # returns the number of cells currently holding a flag
        return 123


    def get_dict_of_cell_images(self): # returns a dict where they keys are cell coords and the values are the current image that should be associated with the corresponding cell
        dict_out = {}

        for row in range(self.num_rows):
            for col in range(self.num_cols):
                if self.board[row][col].flag:
                    dict_out[(row,col)] = 'img_flag'

                elif self.board[row][col].visible:
                    if self.board[row][col].bomb:
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
        
        if self.game_status in (GAME_STATUS_READY, GAME_STATUS_IN_PROGRESS):

            if not self.board[row][col].visible: # can't flag/unflag if it's already revealed
                self.board[row][col].flag = not self.board[row][col].flag 

            # self.game_status = GAME_STATUS_IN_PROGRESS # - maybe we don't need to start the game if they preemptively start flagging
    
    def valid_target(self, row, col):
    # Check if a row/column is a) in bounds and b) is 'exposable'
        if row >= 0 and row < self.num_rows and col >= 0 and col < self.num_cols:
            return (self.board[row][col].enabled and not self.board[row][col].visible and not self.board[row][col].flag)
            
        else:
            return False


    def expose_cell(self, cell_coords): # aka left click
        # print(f'expose cell {cell_coords}')
        row = cell_coords[0]
        col = cell_coords[1]

        if self.game_status in (GAME_STATUS_READY, GAME_STATUS_IN_PROGRESS):
            if self.board[row][col].enabled: # can't expose if it's disabled
                if not self.board[row][col].visible: # can't expose if it's already revealed
                    if not self.board[row][col].flag: # can't expose if a flag is covering the cell - remove the flag first with toggle_flag()
                        self.turn_count += 1 # this will be wrong if we implement recursion
                        self.game_status = GAME_STATUS_IN_PROGRESS
                        
                        if self.board[row][col].bomb:
                            if self.turn_count <= 1: # move bomb to a new location, recalculate neighbor counts, and reveal newly empty cell                        
                                print('OH NO a bomb on the first move')
                                self.add_bombs(1)
                                self.remove_bomb(cell_coords)
                                self.calculate_neighbors()
                                self.print_bomb_grid()

                            else:
                                self.induce_game_over(cell_coords)
                        
                        self.board[row][col].visible = True
                        self.board[row][col].enabled = False
        
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
            if self.board[row][col].visible: # can't expand if we can't see the neighboring bomb count
                print('to do expand')
                # check if number of adjacent flags is the same as num_neighbors
                

                # if not self.board[row][col].flag: # can't expose if a flag is covering the cell - remove the flag first with toggle_flag()

                #     self.board[row][col].visible = True

                #     if self.board[row][col].bomb:
                #         #print('Game over man')
                #         self.game_status = GAME_STATUS_GAME_OVER
                    
                #     else:
                #         self.game_status = GAME_STATUS_IN_PROGRESS
                #         # TODO start search for newly exposed "0 neighbors" cells'


if __name__ == '__main__':
    print('Don\'t run me! Run swinemeeper_gui.py insteasd!')
    # rows = 10
    # cols = 5
    # bombs = 3

    # board = SwinemeeperBoard(rows, cols, bombs)
    # board.print_bomb_grid()
    # board.print_neighbor_grid()
    # board.print_display_grid()


    # board.toggle_flag(3, 0)

    # board.print_display_grid()


    # for i in range (rows):
    #     board.expose_cell((i, 0))
    #     board.print_display_grid()

    # for i in range (rows):
    #     board.expose_cell((i, 1))
    #     board.print_display_grid()


    # board.expand_solution(1,1) # aka middle click
    # board.print_display_grid()
