### SWINEMEEPER!!!

import random as rand
import tkinter as tk 
from tkinter import messagebox
import time
from functools import partial
from settings import constants


class SwineMeeperGameManager:
    DEFAULT_NUM_ROWS = 10
    DEFAULT_NUM_COLS = 12
    DEFAULT_NUM_BOMBS = 10
    DEFAULT_INCL_MAYBE_FLAG = True
    DEFAULT_CONFIRM_ON_EXIT = False
    DEFAULT_TO_DEBUG_MODE = False
    RECURSION_LIMIT = 1000 # 1000 by default, but can be expanded at user risk w/ sys.setrecursionlimit(num). In practice, this is max number of cells we can process with recurisve checks that can conceivably touch every cell at least once

    def __init__(self):
        if self.DEFAULT_TO_DEBUG_MODE: print('SwineMeeperGameManager init')
        
        self.lang = 'en' # which language to display to users. Default to English for now. Add to persistent user settings later.
        
        self.debug_mode = self.DEFAULT_TO_DEBUG_MODE
        self.timer = self.SwineTimer(self)
        self.game = self.SwineMeeperGame(self, self.DEFAULT_NUM_ROWS, self.DEFAULT_NUM_COLS, self.DEFAULT_NUM_BOMBS) # create a default game to allow gui to connect to said elements
        self.gui = self.SwineMeeperGUI(self)
        self.confirm_on_exit = self.DEFAULT_CONFIRM_ON_EXIT # If true, a popup will ask you to confirm before destroying the tk application - TODO add toggle to gui and user settings
        self.maybe_flag_enabled = self.DEFAULT_INCL_MAYBE_FLAG # If true, right clicking a flag will turn it into a question mark, which can be left or right clicked on. Should be ok to dis/enable mid-game - TODO add toggle to gui and user settings        
        
    
    def start_or_restart_game(self, num_rows, num_cols, num_bombs_to_add):
        self.debug_mode: print('start_or_restart_game() called!')
        
        self.game = self.SwineMeeperGame(self, num_rows, num_cols, num_bombs_to_add)
        if self.debug_mode: self.gui.lbl_debug.grid(row=2, column=0, columnspan=3)

        self.timer.stop_and_reset_timer()

        self.gui.frame_cell_grid.destroy()
        self.gui.frame_cell_grid = self.gui.create_frame_cell_grid()
        self.gui.frame_cell_grid.grid(row=1, column=0, columnspan=3, pady=5)


    class SwineMeeperGame:
        GAME_STATUS_READY = 'Ready'
        GAME_STATUS_IN_PROGRESS = 'In Progress'
        GAME_STATUS_LOST = 'Game Over'
        GAME_STATUS_WON = 'Won'
        GAME_STATUS_INIT = 'INIT'

        def __init__(self, parent, num_rows, num_cols, num_bombs_to_add): 
            self.parent = parent

            if self.parent.debug_mode: 
                print(f'SwineMeeperGame game\nStarting Parameters: {num_rows} rows x {num_cols} with {num_bombs_to_add} bombs')
    
            if num_rows*num_cols >= self.parent.RECURSION_LIMIT:
                raise ValueError('Too many cells!')
            
            elif num_bombs_to_add >= num_rows*num_cols:
                raise ValueError('Too many bombs!')

            self.game_status = self.GAME_STATUS_INIT
            self.turn_count = 0
            self.num_rows = num_rows
            self.num_cols = num_cols
            self.num_bombs = 0 # this is the number of bombs that have been placed by the game, and not necessarily num_bombs_to_add
            self.board = {} # a dictionary containing all the individual cell objects (logical units, not the gui buttons)
            
            # Create a dictionary represneting a 2D array of blank cells that will contain pertinent info (address, bomb status, number of neighbor bombs, image that should be displayed)
            for i in range(self.num_rows):
                for j in range(self.num_cols):
                    self.board[(i, j)] = self.SwineMeeperCell(self, i, j)
                    
            self.add_bombs(num_bombs_to_add)
            self.calculate_neighbors()        
            self.game_status = self.GAME_STATUS_READY


        def add_bombs(self, num_bombs_to_add):
            num_attempts = 0
            num_added = 0
            if self.parent.debug_mode: attempt_start_time = time.time()

            while (num_added < num_bombs_to_add):
                num_attempts = num_attempts + 1       
                target_row = rand.randrange(self.num_rows)
                target_col = rand.randrange(self.num_cols)
                
                if not self.board[(target_row, target_col)].contains_bomb:
                    self.board[(target_row, target_col)].contains_bomb = True
                    self.num_bombs += 1
                    num_added += 1
            
            if self.parent.debug_mode: print(f'Added {num_bombs_to_add} bombs in {num_attempts} attempts in {time.time() - attempt_start_time} seconds')

        
        def remove_bomb(self, cell_coords): # eg if encountered on first move
            self.board[cell_coords].contains_bomb = False
            self.num_bombs -= 1
            

        def calculate_neighbors(self):
        # Record how many bombs are adjacent to each cell. 
        # In cells containing bombs, the number of neighbors is irrelevant 
        
            for row in range(self.num_rows):
                for col in range(self.num_cols):
                    num_adjacent_bombs = 0

                    #check above
                    if row > 0: 
                        if self.board[row - 1, col].contains_bomb: num_adjacent_bombs += 1
                        
                        if col > 0: # top left
                            if self.board[row - 1, col - 1].contains_bomb: num_adjacent_bombs += 1

                        if (self.num_cols - col > 1): # top right
                            if self.board[row - 1, col + 1].contains_bomb: num_adjacent_bombs += 1

                    #check below
                    if self.num_rows - row > 1: 
                        if self.board[row + 1, col].contains_bomb: num_adjacent_bombs += 1
                        
                        if col > 0: # top left
                            if self.board[row + 1, col - 1].contains_bomb: num_adjacent_bombs += 1

                        if (self.num_cols - col > 1): # top right
                            if self.board[row + 1, col + 1].contains_bomb: num_adjacent_bombs += 1

                    #check left/right
                    if col > 0: # left
                        if self.board[row, col - 1].contains_bomb: num_adjacent_bombs += 1

                    if (self.num_cols - col > 1): # right
                        if self.board[row, col + 1].contains_bomb: num_adjacent_bombs += 1

                    self.board[row, col].neighbors = num_adjacent_bombs
            

        def get_remaining_cell_count(self): # How many more cells must be exposed before only bombs are left?
            total_cells = self.num_rows * self.num_cols
            cells_occupied = 0
            for row in range(self.num_rows):
                for col in range(self.num_cols):
                    #if self.board[row - 1, col].status == CELL_STATUS_EXPOSED:
                    if self.board[row, col].status == self.SwineMeeperCell.CELL_STATUS_EXPOSED:
                        cells_occupied +=1
                        
            return total_cells - cells_occupied - self.num_bombs


        def get_num_flags_placed(self):
            num_flags = 0
            for row in range(self.num_rows):
                for col in range(self.num_cols):
                    if self.board[(row, col)].status == self.SwineMeeperCell.CELL_STATUS_FLAG:
                        num_flags +=1        
            return num_flags


        def get_num_flags_remaining(self):
            return (self.num_bombs - self.get_num_flags_placed()) if self.game_status not in (self.GAME_STATUS_INIT, self.GAME_STATUS_WON) else 0


        def end_game(self, victory=False):
            self.parent.timer.pause_timer()

            if victory:
                self.game_status = self.GAME_STATUS_WON
                if self.parent.debug_mode: print('YOU WIN!')

            else:
                self.game_status = self.GAME_STATUS_LOST
                if self.parent.debug_mode: print('YOU LOSE')


        def toggle_flag(self, cell_coords):  # aka right click
            row = cell_coords[0]
            col = cell_coords[1]
            
            old_status = self.board[cell_coords].status
            if self.game_status in (self.GAME_STATUS_READY, self.GAME_STATUS_IN_PROGRESS) and old_status in (self.SwineMeeperCell.CELL_STATUS_HIDDEN, self.SwineMeeperCell.CELL_STATUS_FLAG, self.SwineMeeperCell.CELL_STATUS_FLAG_MAYBE):
                self.turn_count += 1
                
                if old_status == self.SwineMeeperCell.CELL_STATUS_HIDDEN:
                    new_status = self.SwineMeeperCell.CELL_STATUS_FLAG

                elif old_status == self.SwineMeeperCell.CELL_STATUS_FLAG:
                    if self.parent.maybe_flag_enabled:
                        new_status = self.SwineMeeperCell.CELL_STATUS_FLAG_MAYBE
                    else:
                        new_status = self.SwineMeeperCell.CELL_STATUS_HIDDEN

                elif old_status == self.SwineMeeperCell.CELL_STATUS_FLAG_MAYBE: # check even if not maybe_flag_enabled, as the value may have changed mid-game
                    new_status = self.SwineMeeperCell.CELL_STATUS_HIDDEN
                            
                self.board[row, col].status = new_status


        def valid_target(self, row, col, maybe_flags_are_valid=False): 
        # TODO rework this to be a function inside of the Cell class..
        # Had to add a maybe_flags_are_valid for now, too, to deal w/ middle clicks

        # Check if a row/column is a) in bounds and b) is 'exposable'
            if row >= 0 and row < self.num_rows and col >= 0 and col < self.num_cols:
                if maybe_flags_are_valid:
                    return (self.board[row, col].status in(self.SwineMeeperCell.CELL_STATUS_HIDDEN, self.SwineMeeperCell.CELL_STATUS_FLAG_MAYBE))
                else:
                    return (self.board[row, col].status == self.SwineMeeperCell.CELL_STATUS_HIDDEN)
            else:
                return False


        def expose_cell(self, cell_coords, was_clicked=True): # aka left click. If was_clicked=False then this cell was exposed by a neighbor recursively or through middle clicking
            cell_status = self.board[cell_coords].status

            if self.game_status in (self.GAME_STATUS_READY, self.GAME_STATUS_IN_PROGRESS) and cell_status in (self.SwineMeeperCell.CELL_STATUS_HIDDEN, self.SwineMeeperCell.CELL_STATUS_FLAG_MAYBE): # proceed
                if self.game_status == self.GAME_STATUS_READY:
                    self.parent.timer.start_timer()
                    self.game_status = self.GAME_STATUS_IN_PROGRESS

                if was_clicked:
                    self.turn_count += 1

                if self.board[cell_coords].contains_bomb:
                    if self.turn_count <= 1: # move bomb to a new location, recalculate neighbor counts, and reveal newly empty cell                        
                        # TODO  make this a menubar activated option (default to true)
                        self.add_bombs(1)
                        self.remove_bomb(cell_coords)
                        self.calculate_neighbors() # recalculate the neighbor account for all cells

                        if self.parent.debug_mode: 
                            print('OH NO a bomb on the first move') # HMMMM what about an option to implement 'suicide minesweeper' where you're guaranteed 0 neighbors on 1st move and then have to left click on bombs to expose more territory?
                            # self.print_bomb_grid()

                        self.board[cell_coords].status = self.SwineMeeperCell.CELL_STATUS_EXPOSED

                    else:
                        self.board[cell_coords].status = self.SwineMeeperCell.CELL_STATUS_BOOM
                        self.end_game(victory=False)
                else:
                    self.board[cell_coords].status = self.SwineMeeperCell.CELL_STATUS_EXPOSED

                # If the cell contains no neighbors, recursively 'click' on all adjacent cells until a wall of numbers is fully exposed
                if self.board[cell_coords].neighbors == 0:
                    row = cell_coords[0]
                    col = cell_coords[1]

                    if self.valid_target(row + 1, col): self.expose_cell((row + 1, col), was_clicked=False) # down
                    if self.valid_target(row, col + 1): self.expose_cell((row, col + 1), was_clicked=False) # right
                    if self.valid_target(row - 1, col): self.expose_cell((row - 1, col), was_clicked=False) # up
                    if self.valid_target(row, col - 1): self.expose_cell((row, col - 1), was_clicked=False) # left
                    if self.valid_target(row + 1, col + 1): self.expose_cell((row + 1, col + 1), was_clicked=False) # bot right           
                    if self.valid_target(row + 1, col - 1): self.expose_cell((row + 1, col - 1), was_clicked=False) # bot left
                    if self.valid_target(row - 1, col + 1): self.expose_cell((row - 1, col + 1), was_clicked=False) # top right
                    if self.valid_target(row - 1, col - 1): self.expose_cell((row - 1, col - 1), was_clicked=False) # top left

                if self.get_remaining_cell_count() <= 0:
                    self.end_game(victory=True)


        def expand_solution(self, cell_coords): # aka middle click
            # If the clicked cell contains an exposed number, and the number of neighbors with flags == that number, expose all unexposed neighbors

            def num_adjacent_flags(cell):
                row = cell.row
                col = cell.col
                num_adjacent = 0

                if row > 0: 
                    if self.board[row - 1, col].status == self.SwineMeeperCell.CELL_STATUS_FLAG: num_adjacent += 1
                    
                    if col > 0: # top left
                        if self.board[row - 1, col - 1].status == self.SwineMeeperCell.CELL_STATUS_FLAG: num_adjacent += 1

                    if (self.num_cols - col > 1): # top right
                        if self.board[row - 1, col + 1].status == self.SwineMeeperCell.CELL_STATUS_FLAG: num_adjacent += 1

                #check below
                if self.num_rows - row > 1: 
                    if self.board[row + 1, col].status == self.SwineMeeperCell.CELL_STATUS_FLAG: num_adjacent += 1
                    
                    if col > 0: # top left
                        if self.board[row + 1, col - 1].status == self.SwineMeeperCell.CELL_STATUS_FLAG: num_adjacent += 1

                    if (self.num_cols - col > 1): # top right
                        if self.board[row + 1, col + 1].status == self.SwineMeeperCell.CELL_STATUS_FLAG: num_adjacent += 1

                #check left/right
                if col > 0: # left
                    if self.board[row, col - 1].status == self.SwineMeeperCell.CELL_STATUS_FLAG: num_adjacent += 1

                if (self.num_cols - col > 1): # right
                    if self.board[row, col + 1].status == self.SwineMeeperCell.CELL_STATUS_FLAG: num_adjacent += 1

                return num_adjacent
                        
            if self.game_status in (self.GAME_STATUS_IN_PROGRESS):
                cell = self.board[cell_coords]

                if cell.status == self.SwineMeeperCell.CELL_STATUS_EXPOSED: # can't expand if we can't see the neighboring bomb count
                    
                    if num_adjacent_flags(cell) == cell.neighbors:
                        if self.parent.debug_mode: print('expaaaand')
                    
                        self.turn_count += 1
                        if self.valid_target(cell.row + 1, cell.col, maybe_flags_are_valid=True): self.expose_cell((cell.row + 1, cell.col), was_clicked=False) # down
                        if self.valid_target(cell.row, cell.col + 1, maybe_flags_are_valid=True): self.expose_cell((cell.row, cell.col + 1), was_clicked=False) # right
                        if self.valid_target(cell.row - 1, cell.col, maybe_flags_are_valid=True): self.expose_cell((cell.row - 1, cell.col), was_clicked=False) # up
                        if self.valid_target(cell.row, cell.col - 1, maybe_flags_are_valid=True): self.expose_cell((cell.row, cell.col - 1), was_clicked=False) # left
                        if self.valid_target(cell.row + 1, cell.col + 1, maybe_flags_are_valid=True): self.expose_cell((cell.row + 1, cell.col + 1), was_clicked=False) # bot right           
                        if self.valid_target(cell.row + 1, cell.col - 1, maybe_flags_are_valid=True): self.expose_cell((cell.row + 1, cell.col - 1), was_clicked=False) # bot left
                        if self.valid_target(cell.row - 1, cell.col + 1, maybe_flags_are_valid=True): self.expose_cell((cell.row - 1, cell.col + 1), was_clicked=False) # top right
                        if self.valid_target(cell.row - 1, cell.col - 1, maybe_flags_are_valid=True): self.expose_cell((cell.row - 1, cell.col - 1), was_clicked=False) # top left

            
        def print_bomb_grid(self): # for debug purposes
            print('\nBomb grid:')
            str_output = ''
            for row in range(self.num_rows):
                for col in range(self.num_cols):
                    str_output = f'{str_output}\t{self.board[(row,col)].contains_bomb}'
                str_output = f'{str_output}\n'    
            
            print(str_output)

        def print_neighbor_grid(self): # for debug purposes
            print('\nNeighbor grid:')
            str_output = '' 
            for row in range(self.num_rows):
                for col in range(self.num_cols):
                    str_output = f'{str_output}\t{self.board[(row, col)].neighbors}'
                str_output = f'{str_output}\n'    
            
            print(str_output)

        def print_display_grid(self):  # for debug purposes
            print(f'\nGame Status: {self.game_status}')
            str_output = ''
            for row in range(self.num_rows):
                for col in range(self.num_cols):
                    if self.board[(row, col)].visible:
                        if self.board[(row, col)].flag:
                            char_cell = 'F'
                        elif self.board[(row, col)].contains_bomb:
                            char_cell = '*'
                        elif self.board[(row, col)].neighbors == 0:
                            char_cell = ' '
                        else:
                            char_cell = str(self.board[(row, col)].neighbors)

                    else:
                        char_cell = '-'
                    str_output = f'{str_output}\t{char_cell}'
                str_output = f'{str_output}\n'    
            
                print(str_output)        



        class SwineMeeperCell:
            
            CELL_STATUS_HIDDEN = 0 # available
            CELL_STATUS_EXPOSED = 1
            CELL_STATUS_FLAG = 2
            CELL_STATUS_FLAG_MAYBE = 3
            CELL_STATUS_BOOM = 4
            CELL_STATUS_BOMB_EXPOSED = 5 
            CELL_STATUS_FLAG_WAS_WRONG = 6

            def __init__(self, parent, row, col):
                # if parent.parent.debug_mode:   print(f'Initializing cell [{row}][{col}]')
                    
                self.parent = parent # parent will always be a SwineMeeperGame object
                self.row = row 
                self.col = col
                self.contains_bomb = False # can be modified later
                self.neighbors = 0 # will be calculate later
                self.status = self.CELL_STATUS_HIDDEN # all cells start unexposed
            

            def enabled(self):
                if self.parent.game_status in (self.parent.GAME_STATUS_LOST, self.parent.GAME_STATUS_WON, self.parent.GAME_STATUS_INIT):
                    return False
                else:
                    return self.status in (self.CELL_STATUS_HIDDEN, self.CELL_STATUS_FLAG, self.CELL_STATUS_FLAG_MAYBE)
            

            def get_cell_image_key(self):
                # Return the name of the image variable in SM_Assets that should be used to represent this cell
                game_status = self.parent.game_status
                
                # on game over, reveal undetected bombs and highlight any false flags            
                if game_status == self.parent.GAME_STATUS_WON and self.contains_bomb:
                    return 'img_flag'
                
                elif game_status == self.parent.GAME_STATUS_LOST and self.contains_bomb and self.status in (self.CELL_STATUS_HIDDEN, self.CELL_STATUS_FLAG_MAYBE):
                    return 'img_bomb'

                elif game_status == self.parent.GAME_STATUS_LOST and self.status == self.CELL_STATUS_FLAG and not self.contains_bomb:
                        return 'img_flag_wrong'

                else:
                    if self.status == self.CELL_STATUS_EXPOSED:
                        return f'img_{self.neighbors}'
                    elif self.status == self.CELL_STATUS_FLAG:
                        return 'img_flag'
                    elif self.status == self.CELL_STATUS_FLAG_MAYBE:
                        return 'img_flag_maybe'
                    elif self.status == self.CELL_STATUS_BOOM:
                        return 'img_boom'
                    elif self.status == self.CELL_STATUS_BOMB_EXPOSED:
                        return 'img_bomb'
                    else: # hidden should be the only remaining valid option
                        return 'img_hidden'
                    

    class SwineTimer:
        def __init__(self, parent):
            self.time_started = 0
            self.time_stopped = 0
            self.is_running = False
            self.parent = parent

        def start_timer(self):
            if not self.is_running:
                if self.parent.debug_mode: print(f'Starting timer')
                self.is_running = True
                self.time_started = time.time()
                self.time_stopped = 0

        def pause_timer(self):
            if self.is_running:
                if self.parent.debug_mode: print(f'Stopping timer')
                self.is_running = False
                self.time_stopped = time.time()

        def stop_and_reset_timer(self):
            if self.parent.debug_mode: print(f'Resetting timer')
            
            self.is_running = False
            self.time_started = 0
            self.time_stopped = 0

        def resume_timer(self):
            if not self.is_running:
                if self.parent.debug_mode: print(f'Resuming timer')
                self.is_running = True
                seconds_on_clock = self.time_stopped - self.time_started
                self.time_started = time.time() - seconds_on_clock

        def add_time_to_timer(self, seconds_to_add): # can be negative to decrease the time
            self.time_started = self.time_started - seconds_to_add

        def get_elapsed_time(self):
            if self.is_running:
                return time.time() - self.time_started
            else:
                return self.time_stopped - self.time_started



    class SwineMeeperGUI:
        def __init__(self, parent):
            # print('SwineMeeperGUI init')
            self.parent = parent

            self.root = tk.Tk()
            self.root.protocol('WM_DELETE_WINDOW', self.on_delete_window) # behavior when the window is closed (eg by clicking the X button)
            
            self.assets = self.SM_Assets(r'C:\Users\thema\Documents\Python Scripts\swinemeeper\assets\\') # TODO TEMP! 
            
            self.root.title(constants[self.parent.lang]['title'])
            self.root.config(menu=self.create_menu_bar(self.root))

            self.CYCLE_SPEED = 30 # desired delay in game loop (in ms)
            self.FPS_TARGET = 35 # desired frames per second
            
            self.render_timestamp = time.time() # time we last updated the gui
            self.refresh_check_timestamp = 0 # last time a cycle was initiated.. hoping to use for FPS improvement

            self.frames_elapsed = 0 # for measuring actual FPS
            self.refresh_checks_elapsed = 0 # for evaluating peformance
            
            self.refresh_checks_startup_time = time.time() # for evaluating peformance
            self.root.after_id = None # not sure if this is implemented 'correctly' yet but it works so far.. used with the tk.after and tk.after_cancel logic for looping through the game loop cycle
            
            self.last_action = 'creation' # description of the last action to affect the game
           
            self.clock_label_text = tk.StringVar() # number of seconds elapsed since first cell was clicked
            self.bomb_counter_text = tk.StringVar() # Number of bombs - number of placed flags
            
            self.clock_label_text.set('000')
            self.bomb_counter_text.set('000')            
            
            self.btn_start = tk.Button(master=self.root, image=self.assets.img_happy, command=self.restart_game) # clicking the smiley face will always start a new game with the same settings as the current game
            self.lbl_clock = tk.Label(master=self.root, textvariable=self.clock_label_text, font=('Stencil 24'))
            self.lbl_bomb_counter = tk.Label(master=self.root, textvariable=self.bomb_counter_text, font=('Stencil 24'))
            
            self.frame_cell_grid = self.create_frame_cell_grid()

            self.debug_label_text = tk.StringVar() # A label w/ performance stats used for debugging purposes
            self.debug_label_text.set('')
            self.lbl_debug = tk.Label(master=self.root, textvariable=self.debug_label_text, font=('Arial 14'), justify='left', anchor='w')
            
            self.lbl_clock.grid(row=0, column=0) #, sticky = tk.W)
            self.btn_start.grid(row=0, column=1)
            self.lbl_bomb_counter.grid(row=0, column=2)
            self.frame_cell_grid.grid(row=1, column=0, columnspan=3, pady=5)
            
            #if self.parent.debug_mode:
            self.lbl_debug.grid(row=2, column=0, columnspan=3)

            self.game_loop() # start the game cycle!
                    

        def on_delete_window(self):
            if self.parent.confirm_on_exit:
                if messagebox.askokcancel(constants[self.parent.lang]['prompt_confirm_exit_title'], constants[self.parent.lang]['prompt_confirm_exit_msg']):
                    self.root.after_cancel(self.root.after_id)
                    self.root.destroy()
            else:
                self.root.after_cancel(self.root.after_id)
                self.root.destroy()

        def create_frame_cell_grid(self):
            f_grid = tk.Frame(master=self.root)
            f_grid.board_cell_buttons = {}

            for i in range(self.parent.game.num_rows):
                for j in range(self.parent.game.num_cols)    :
                    f_grid.board_cell_buttons[(i, j)] = tk.Button(master=f_grid, image=self.assets.img_hidden) # add cell to the dictionary and establish default behavior
                    f_grid.board_cell_buttons[(i, j)].grid(row=i, column=j) # place the cell in the frame
                    f_grid.board_cell_buttons[(i, j)].bind('<ButtonRelease>', partial(self.CellButtonReleaseHandler,(i , j))) # add a mouse handler to deal with user input
            
            return f_grid
        
        def get_performance_stats(self):
            game = self.parent.game # convenience ref var

            time_since_render =  time.time() - self.render_timestamp
            run_time = round(self.render_timestamp - self.refresh_checks_startup_time,3)
            fps_actual = round(self.frames_elapsed/run_time,3) if run_time > 0 else 0
            refresh_cycle_actual = round(run_time/self.refresh_checks_elapsed*1000,3) if run_time > 0 else 0
            
            str_out = (
                f'Game status: {game.game_status}'+
                f'\nRun Time: {run_time:.3f} s' +
                f'\t\tTime since last frame: {time_since_render:.6f}' +
                f'\nFrames elapsed: {str(self.frames_elapsed).zfill(3)}' +
                f'\tCycles elapsed: {str(self.refresh_checks_elapsed).zfill(3)}' +
                f'\nFPS (Target): {self.FPS_TARGET}' +
                f'\t\tCycle speed (Target): {self.CYCLE_SPEED} ms' +
                f'\nFPS (Actual): {fps_actual:.3f}' +
                f'\tCycle speed (Actual): {refresh_cycle_actual:.3f} ms' +
                f'\nClicks processed {game.turn_count}' +
                f'\t\tRemaining cells: {game.get_remaining_cell_count()} out of {game.num_rows*game.num_cols - game.num_bombs}' + 
                f'\nLast action: {self.last_action}'
                )
            
            return str_out


        def game_loop(self):
            self.refresh_check_timestamp = time.time()
            #if not self.parent.game.game_status in (self.parent.game.GAME_STATUS_WON, self.parent.game.GAME_STATUS_LOST):
            if self.parent.game.game_status not in (self.parent.game.GAME_STATUS_INIT):    
                self.refresh_checks_elapsed += 1
                time_since_render =  time.time() - self.render_timestamp
                if time_since_render >= 1.0/self.FPS_TARGET:
                    self.render_gui()

                time_to_render = (time.time() - self.refresh_check_timestamp)*1000 # in ms
                next_cycle_time = max(int(self.CYCLE_SPEED - time_to_render),0)
                #print(f'render time took: {round(time_to_render,3 )} ms and next cycle will be in {next_cycle_time} ms, cuz the desired refresh time is {round(self.refresh_check_timestamp*1000,3) - self.CYCLE_SPEED} ')#and proof if is {}')
                
                self.root.after_id = self.root.after(next_cycle_time, self.game_loop) #try again in (at least) X ms

                # else:
                #     if self.parent.debug_mode: print('game is still loading - not time to render yet')
            # else:
            #     #self.root.after_cancel(self.game_loop)
            #     if self.parent.debug_mode: print('this is the end')
            #     self.render_gui()
                
            #     self.root.after_cancel(self.root.after_id)
            #     # tk.after_cancel(self.loop)

        class SettingsWindow: # an instance of a top level window showing user options.. upon 'ok' buttoning it, underlying gamemanager settings are updated (though game settings won't update until after a game restart)
            # TODO 1 - pick better default options.. 
            
            # TODO 1.1 maybe dropdown for 'size' and a separate tkk counter widget thingy for num bombs 
            # instead of 3 hard-coded scenarios, how about populating from a dict and adding dynamic labels, eg:
            # o   Scenario              Size        Bombs
            #   |----Dropdown:                        ----|
            #   - Small (Easy)          8x8         6
            #   - Small (Hard)          8x8         20
            #   - Medium (Easy)         14x14       40
            #   - etc --- 
            # 
            # o Custom
            #   Rows    Columns Bombs
            #   |____|  |____|  |____|
            #
            #       ApplyBtn    CancelBtn
            
            # TODO 2 error check custom values - must be positive integers, cols*rows must be less than self.parent.parent.RECURSION_LIMIT, numb_bombs must be less than rows*cols

            # TODO 3 GUI behavior:
            #   Whenever a custom Entry is activated or edited, the custom radio button must be selected
            #   the the custom Entry fields should be greyed out (but still active) when the custom radio button is not selected, 
            #   and un-greyed out whenever it is activated (wheter by click or by activating/editing 1 of the 3 Entries)


            DIFFICULTY_VAL_EASY = 1
            DIFFICULTY_VAL_MED  = 2
            DIFFICULTY_VAL_HARD = 3
            DIFFICULTY_VAL_CUST = 4
            
            def __init__(self, parent):
                self.parent = parent
                
                self.wind_settingsow = tk.Toplevel(self.parent.root)
                self.wind_settingsow.title(constants[self.parent.parent.lang]['wind_settings_title'])
                #self.wind_settingsow.geometry('500x250')

                self.frame_difficulty = tk.Frame(self.wind_settingsow)
                self.frame_diff_cust = tk.Frame(self.frame_difficulty) # the text Entries and corresponding labels for custom difficulty

                self.difficulty = tk.IntVar()
                self.difficulty.set(self.DIFFICULTY_VAL_EASY)

                self.diff_easy = tk.Radiobutton(self.frame_difficulty, variable=self.difficulty, justify=tk.LEFT, anchor='w', value=self.DIFFICULTY_VAL_EASY, text='Easy')
                self.diff_med  = tk.Radiobutton(self.frame_difficulty, variable=self.difficulty, justify=tk.LEFT, anchor='w', value=self.DIFFICULTY_VAL_MED, text='Medium')
                self.diff_hard = tk.Radiobutton(self.frame_difficulty, variable=self.difficulty, justify=tk.LEFT, anchor='w', value=self.DIFFICULTY_VAL_HARD, text='Hard')
                self.diff_cust = tk.Radiobutton(self.frame_difficulty, variable=self.difficulty, justify=tk.LEFT, anchor='w', value=self.DIFFICULTY_VAL_CUST, text='Custom')

                self.var_cust_rows = tk.StringVar()
                self.var_cust_cols = tk.StringVar()
                self.var_cust_bomb = tk.StringVar()
                
                self.lbl_cust_rows = tk.Label(self.frame_diff_cust, text=constants[self.parent.parent.lang]['wind_settings_rows'])
                self.lbl_cust_cols = tk.Label(self.frame_diff_cust, text=constants[self.parent.parent.lang]['wind_settings_cols'])
                self.lbl_cust_bomb = tk.Label(self.frame_diff_cust, text=constants[self.parent.parent.lang]['wind_settings_bombs'])
                self.diff_cust_rows = tk.Entry(self.frame_diff_cust, textvariable=self.var_cust_rows, width=5) #TODO look into exportselection - saw note that claims default is, copy value to clipboard when text is selected.. set exportselection=0 to prevent
                self.diff_cust_cols = tk.Entry(self.frame_diff_cust, textvariable=self.var_cust_cols, width=5)
                self.diff_cust_bomb = tk.Entry(self.frame_diff_cust, textvariable=self.var_cust_bomb, width=5)

                # Starting values for the custom option will mimic the game in progress
                self.var_cust_rows.set(self.parent.parent.game.num_rows)
                self.var_cust_cols.set(self.parent.parent.game.num_cols)
                self.var_cust_bomb.set(self.parent.parent.game.num_bombs)

                self.diff_easy.grid(row=0, column=0, sticky='w')
                self.diff_med.grid(row=1, column=0, sticky='w')
                self.diff_hard.grid(row=2, column=0, sticky='w')
                self.diff_cust.grid(row=3, column=0, sticky='w')

                self.lbl_cust_rows.grid(row=0, column=0, sticky='w')
                self.lbl_cust_cols.grid(row=0, column=1, sticky='w')
                self.lbl_cust_bomb.grid(row=0, column=2, sticky='w')
                self.diff_cust_rows.grid(row=1, column=0, padx=5, sticky='w')
                self.diff_cust_cols.grid(row=1, column=1, padx=5, sticky='w')
                self.diff_cust_bomb.grid(row=1, column=2, padx=5, sticky='w')
                
                self.frame_diff_cust.grid(row=4, column=0, sticky='w')
                
                self.frame_difficulty.grid(row=0, column=0, columnspan=3)
                                
                self.btn_apply_settings = tk.Button(master=self.wind_settingsow, text=constants[self.parent.parent.lang]['wind_settings_apply'], command=self.apply_settings)
                self.btn_apply_settings.grid(row=99, column=0, columnspan=2, pady=5)
                
                self.btn_cancel_settings = tk.Button(master=self.wind_settingsow, text=constants[self.parent.parent.lang]['wind_settings_cancel'], command=self.cancel_settings)
                self.btn_cancel_settings.grid(row=99, column=3, pady=5)


            def apply_settings(self):
                if self.parent.parent.debug_mode: print('apply_settings')

                # which radio button is selected
                # if custom, a) validate entries and b) pass on values

                # print(f'Difficulty: {self.difficulty.get()}\tCust values {self.var_cust_rows.get()}x{self.var_cust_cols.get()} cells with {self.var_cust_bomb.get()} bombs')

                if self.difficulty.get() == self.DIFFICULTY_VAL_EASY:
                    num_rows = 10
                    num_cols = 10
                    num_bombs = 10
                elif self.difficulty.get() == self.DIFFICULTY_VAL_MED:
                    num_rows = 15
                    num_cols = 18
                    num_bombs = 40
                elif self.difficulty.get() == self.DIFFICULTY_VAL_HARD:
                    num_rows = 18
                    num_cols = 24
                    num_bombs = 100
                elif self.difficulty.get() == self.DIFFICULTY_VAL_CUST:
                    num_rows = int(self.var_cust_rows.get())
                    num_cols = int(self.var_cust_cols.get())
                    num_bombs = int(self.var_cust_bomb.get())

                    #TODO HERE VALIDATION ON INPUT
                
                else:
                    raise ValueError('INVALID DIFFICULTY DETECTED')
                    
                #self.parent.restart_game()
                self.parent.parent.start_or_restart_game(num_rows, num_cols, num_bombs)
                self.wind_settingsow.destroy()

            
            def cancel_settings(self): # destroy the top level window without updating anything
                self.wind_settingsow.destroy()


        class SM_Assets: # yay inner inner inner class!
            MAGIC_NUM_TO_FIX_CELL_SIZE = 5 # tk.Button seems to add 5 px to the height and width 
            
            def __init__(self, dir_img):
                # print(f'{os.path.dirname(__file__)}../test')
                # print(os.getcwd())
                
                self.img_hidden     = tk.PhotoImage(file=f'{dir_img}hidden.gif')    
                self.img_flag       = tk.PhotoImage(file=f'{dir_img}flag.gif')    
                self.img_flag_maybe = tk.PhotoImage(file=f'{dir_img}flag_maybe.gif')        
                self.img_flag_wrong = tk.PhotoImage(file=f'{dir_img}flag_wrong.gif')        
                self.img_boom       = tk.PhotoImage(file=f'{dir_img}boom.gif') 
                self.img_bomb       = tk.PhotoImage(file=f'{dir_img}bomb.gif') 
                self.img_0          = tk.PhotoImage(file=f'{dir_img}0.gif') 
                self.img_1          = tk.PhotoImage(file=f'{dir_img}1.gif') 
                self.img_2          = tk.PhotoImage(file=f'{dir_img}2.gif') 
                self.img_3          = tk.PhotoImage(file=f'{dir_img}3.gif') 
                self.img_4          = tk.PhotoImage(file=f'{dir_img}4.gif') 
                self.img_5          = tk.PhotoImage(file=f'{dir_img}5.gif') 
                self.img_6          = tk.PhotoImage(file=f'{dir_img}6.gif') 
                self.img_7          = tk.PhotoImage(file=f'{dir_img}7.gif') 
                self.img_8          = tk.PhotoImage(file=f'{dir_img}8.gif') 

                # Start button graphics:
                self.img_happy      = tk.PhotoImage(file=f'{dir_img}happy_button.gif') 
                self.img_unhappy    = tk.PhotoImage(file=f'{dir_img}unhappy_button.gif') 
                self.extra_happy    = tk.PhotoImage(file=f'{dir_img}extra_happy_button.gif') 
                self.img_unsure     = tk.PhotoImage(file=f'{dir_img}unsure_button.gif') 

                self.cell_width = self.img_0.width() + self.MAGIC_NUM_TO_FIX_CELL_SIZE # assumes all cell images are identically sized
                self.cell_height = self.img_0.height() + self.MAGIC_NUM_TO_FIX_CELL_SIZE
            

        def create_menu_bar(self, root):            
            menubar = tk.Menu(root)
            
            filemenu = tk.Menu(menubar, tearoff=0)
            filemenu.add_command(label=constants[self.parent.lang]['menu_new_game'], command=self.restart_game)
            filemenu.add_separator()
            filemenu.add_command(label=constants[self.parent.lang]['menu_about'], command=partial(self.open_wind_aboutow, root))
            filemenu.add_separator()
            filemenu.add_command(label=constants[self.parent.lang]['menu_exit'], command=self.root.quit)
            
            game_menu = tk.Menu(menubar, tearoff=0)
            game_menu.add_command(label=constants[self.parent.lang]['menu_settings'], command=partial(self.open_game_wind_settingsow, root))
            game_menu.add_command(label=constants[self.parent.lang]['menu_help'], command=partial(self.open_help_window, root))
            game_menu.add_command(label=constants[self.parent.lang]['menu_toggle_debug'], command=self.toggle_debug_menu)
            game_menu.add_command(label=constants[self.parent.lang]['menu_toggle_debug'], command=self.toggle_debug_menu)
            
            lang_menu = tk.Menu(game_menu, tearoff=0)
            langs = ['en', 'es', 'fr', 'nl']
            for lang in langs:
                lang_menu.add_command(label=constants[self.parent.lang][f'menu_lang_{lang}'], command=partial(self.set_language, lang))

            game_menu.add_cascade(label=constants[self.parent.lang]['menu_cascade_language'], menu=lang_menu)


            menubar.add_cascade(label=constants[self.parent.lang]['menu_cascade_file'], menu=filemenu)
            menubar.add_cascade(label=constants[self.parent.lang]['menu_cascade_game'], menu=game_menu)

            
            return menubar
        
        def set_language(self, lang):
            self.parent.lang = lang
            print('TODO: self.parent.enforce_lang_change()')
            #self.parent.enforce_lang_change()
            

        def toggle_debug_menu(self):
            self.parent.debug_mode = not self.parent.debug_mode


        def open_game_wind_settingsow(self, root):
            self.SettingsWindow(self) #maybe not best practice - creates a top level window that will destroy itself upon closure (but we can't refer to it or see if one is already open)


        def open_help_window(self, root):
            top= tk.Toplevel(root)
            top.geometry('500x250')
            top.title(constants[self.parent.lang]['wind_help_title'])
            tk.Label(top, text= constants[self.parent.lang]['wind_help_text'], font=('Helvetica 14 bold')).place(x=150,y=80)

        
        def open_wind_aboutow(self, root):
            top= tk.Toplevel(root)
            top.geometry('500x250')
            top.title('About SwineMeeper')
            tk.Label(top, text= 'All About SwineMeeper', font=('Helvetica 14 bold')).place(x=150,y=80)

    
        def CellButtonReleaseHandler(self, btn_coords, event):
            if self.parent.game.game_status in(self.parent.game.GAME_STATUS_READY, self.parent.game.GAME_STATUS_IN_PROGRESS):
                # First check to see if the user tried to cancel the click by moving the cursor out of the cell
                if not(event.x < 0 or event.y < 0 or event.x > self.assets.cell_width or event.y > self.assets.cell_height):      
                    # if self.parent.debug_mode: print('CLICK')

                    if event.num == 1: # Left click
                        self.parent.game.expose_cell(btn_coords)
                    elif event.num == 2: # middle click
                        self.parent.game.expand_solution(btn_coords)
                    elif event.num == 3: # right click
                        self.parent.game.toggle_flag(btn_coords)
                    else:
                        raise ValueError('Unexpected button click on game cell')
                else:
                    #if self.parent.debug_mode: print('unCLICK')
                    self.last_action = 'unCLICK'
                
       
    
        def render_gui(self):
            
            if self.parent.debug_mode: 
                self.debug_label_text.set(self.get_performance_stats())
            else:
                self.debug_label_text.set('')
            
            self.frames_elapsed += 1
            self.render_timestamp = time.time()
            
            self.clock_label_text.set(str(int(self.parent.timer.get_elapsed_time())).zfill(3)) # there's probably a cleaner way to format this #
            self.bomb_counter_text.set(str(self.parent.game.get_num_flags_remaining()).zfill(3))

            btn_img = 'img_unhappy' if (self.parent.game.game_status==self.parent.game.GAME_STATUS_LOST) else 'img_happy'
            self.btn_start.config(image=getattr(self.assets, btn_img))

            for i in range(self.parent.game.num_rows): # basic approach: change the image and TODO state of each cell after every user input
                for j in range(self.parent.game.num_cols):
                    cell = self.parent.game.board[(i,j)]
                    btn = self.frame_cell_grid.board_cell_buttons[(i,j)]
                    state = tk.NORMAL if cell.enabled() else tk.DISABLED

                    btn.config(image=getattr(self.assets, cell.get_cell_image_key()), state=state)

            #self.render_timestamp = time.time()
            

        def restart_game(self):
            if self.parent.debug_mode: print('Restarting game')
            
            num_rows = self.parent.game.num_rows
            num_cols = self.parent.game.num_cols
            num_bombs_to_add = self.parent.game.num_bombs

            self.parent.start_or_restart_game(num_rows, num_cols, num_bombs_to_add)
            
            

if __name__ == '__main__':
    game_manager = SwineMeeperGameManager()
    game_manager.gui.root.mainloop()

#    SwineMeeperGameManager().gui.root.mainloop()


####### game idea: a) place pills in weekly reminder box thingies, etc. (and challenge mode once you know game meachnics: diagnose the condition given the medicine shedule a la papers please.. base mode satisfying w/ 1-player-mancala-like gameplay loop
# or is it '1' plaser? maybe a rival pharmacist or anti-caregiver [pet|butler|family member] that's trying to F with you?
