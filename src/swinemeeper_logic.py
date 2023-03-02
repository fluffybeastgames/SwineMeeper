### SWINEMEEPER!!!

import random as rand
import tkinter as tk 
import time
from functools import partial
import os.path

GAME_STATUS_READY = 'Ready'
GAME_STATUS_IN_PROGRESS = 'In Progress'
GAME_STATUS_LOST = 'Game Over'
GAME_STATUS_WON = 'Won'
GAME_STATUS_INIT = 'INIT'

CELL_STATUS_HIDDEN = 0 # available
CELL_STATUS_EXPOSED = 1
CELL_STATUS_FLAG = 2
CELL_STATUS_FLAG_MAYBE = 3
CELL_STATUS_BOOM = 4
CELL_STATUS_BOMB_EXPOSED = 5 
CELL_STATUS_FLAG_WAS_WRONG = 6

RECURSION_LIMIT = 1000 # 1000 by default, but can be expanded at user risk w/ sys.setrecursionlimit(num)


class SwineMeeperGameManager:
    def __init__(self):
        
        self.debug_mode = False

        if self.debug_mode: print('SwineMeeperGameManager init')

        self.DEFAULT_NUM_ROWS = 15
        self.DEFAULT_NUM_COLS = 12
        self.DEFAULT_NUM_BOMBS = 6

        self.game_status = GAME_STATUS_INIT
        self.turn_count = 0
        self.num_rows = self.DEFAULT_NUM_ROWS  
        self.num_cols = self.DEFAULT_NUM_COLS 
        self.num_bombs = 0
        self.maybe_flag_enabled = True
        
        if self.debug_mode: print(f'Starting Parameters: {self.num_rows} rows x {self.num_cols} with {self.num_bombs} bombs')
                
        if self.num_rows*self.num_cols >= RECURSION_LIMIT:
            raise ValueError('Too many cells!')
        
        elif self.num_bombs >= self.num_rows*self.num_cols:
            raise ValueError('Too many bombs!')

        self.timer = SwineTimer(self)
        self.gui = self.SwineMeeperGUI(self)

        self.board = {} # a dictionary containing all the individual cell objects (logical units, not the gui buttons)
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                self.board[(i, j)] = self.SwineMeeperCell(self, i, j)
                
        self.add_bombs(self.DEFAULT_NUM_BOMBS)
        self.calculate_neighbors()        
        self.game_status = GAME_STATUS_READY

      
    def add_bombs(self, num_bombs_to_add):
        num_attempts = 0
        num_added = 0
        if self.debug_mode: attempt_start_time = time.time()

        while (num_added < num_bombs_to_add):
            num_attempts = num_attempts + 1       
            target_row = rand.randrange(self.num_rows)
            target_col = rand.randrange(self.num_cols)
            
            if not self.board[(target_row, target_col)].contains_bomb:
                self.board[(target_row, target_col)].contains_bomb = True
                self.num_bombs += 1
                num_added = num_added + 1
        
        if self.debug_mode: print(f'Added {num_bombs_to_add} bombs in {num_attempts} attempts in {time.time() - attempt_start_time} seconds')

    
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
                if self.board[row, col].status == CELL_STATUS_EXPOSED:
                    cells_occupied +=1
                    
        #if self.debug_mode: print(f'cells occupied: {cells_occupied}, bombs_left: {total_cells - cells_occupied - self.num_bombs}')
        return total_cells - cells_occupied - self.num_bombs


    def get_num_flags_placed(self):
        num_flags = 0
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                if self.board[(row, col)].status == CELL_STATUS_FLAG:
                    num_flags +=1        
        return num_flags

    def get_num_flags_remaining(self):
        return (self.num_bombs - self.get_num_flags_placed()) if self.game_status not in (GAME_STATUS_INIT, GAME_STATUS_WON) else 0


    def end_game(self, victory=False):
        self.timer.pause_timer()

        if victory:
            self.game_status = GAME_STATUS_WON
            if self.debug_mode: print('YOU WIN')

            
            #self.root.aftercancel(self.gui.loop)
            

        else:
            self.game_status = GAME_STATUS_LOST
            if self.debug_mode: print('YOU LOSE')


    def toggle_flag(self, cell_coords):  # aka right click
        row = cell_coords[0]
        col = cell_coords[1]
        
        old_status = self.board[cell_coords].status
        if self.game_status in (GAME_STATUS_READY, GAME_STATUS_IN_PROGRESS) and old_status in (CELL_STATUS_HIDDEN, CELL_STATUS_FLAG, CELL_STATUS_FLAG_MAYBE):
            self.turn_count += 1
            
            if old_status == CELL_STATUS_HIDDEN:
                new_status = CELL_STATUS_FLAG

            elif old_status == CELL_STATUS_FLAG:
                if self.maybe_flag_enabled:
                    new_status = CELL_STATUS_FLAG_MAYBE
                else:
                    new_status = CELL_STATUS_HIDDEN

            elif old_status == CELL_STATUS_FLAG_MAYBE:
                new_status = CELL_STATUS_HIDDEN
                        
            self.board[row, col].status = new_status


    def valid_target(self, row, col, maybe_flags_are_valid=False): 
    # TODO rework this to be a function inside of the Cell class..
    # Had to add a maybe_flags_are_valid for now, too, to deal w/ middle clicks

    # Check if a row/column is a) in bounds and b) is 'exposable'
        if row >= 0 and row < self.num_rows and col >= 0 and col < self.num_cols:
            if maybe_flags_are_valid:
                return (self.board[row, col].status in(CELL_STATUS_HIDDEN, CELL_STATUS_FLAG_MAYBE))
            else:
                return (self.board[row, col].status == CELL_STATUS_HIDDEN)
        else:
            return False


    def expose_cell(self, cell_coords, was_clicked=True): # aka left click. If was_clicked=False then this cell was exposed by a neighbor recursively or through middle clicking
        cell_status = self.board[cell_coords].status

        if self.game_status in (GAME_STATUS_READY, GAME_STATUS_IN_PROGRESS) and cell_status in (CELL_STATUS_HIDDEN, CELL_STATUS_FLAG_MAYBE): # proceed
            # if self.debug_mode: print(f'expose cell {cell_coords}')

            if self.game_status == GAME_STATUS_READY:
                self.timer.start_timer()
                self.game_status = GAME_STATUS_IN_PROGRESS

            if was_clicked:
                self.turn_count += 1

            if self.board[cell_coords].contains_bomb:
                if self.turn_count <= 1: # move bomb to a new location, recalculate neighbor counts, and reveal newly empty cell                        
                    # TODO perhaps we should make this functionality optional? Add a checkbox to the options..

                    self.add_bombs(1)
                    self.remove_bomb(cell_coords)
                    self.calculate_neighbors() # recalculate the neighbor account for all cells

                    if self.debug_mode: 
                        print('OH NO a bomb on the first move') # HMMMM what about an option to implement 'suicide minesweeper' where you're guaranteed 0 neighbors on 1st move and then have to left click on bombs to expose more territory?
                        # self.print_bomb_grid()

                    self.board[cell_coords].status = CELL_STATUS_EXPOSED

                else:
                    self.board[cell_coords].status = CELL_STATUS_BOOM
                    self.end_game(victory=False)
            else:
                self.board[cell_coords].status = CELL_STATUS_EXPOSED

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
                if self.board[row - 1, col].status == CELL_STATUS_FLAG: num_adjacent += 1
                
                if col > 0: # top left
                    if self.board[row - 1, col - 1].status == CELL_STATUS_FLAG: num_adjacent += 1

                if (self.num_cols - col > 1): # top right
                    if self.board[row - 1, col + 1].status == CELL_STATUS_FLAG: num_adjacent += 1

            #check below
            if self.num_rows - row > 1: 
                if self.board[row + 1, col].status == CELL_STATUS_FLAG: num_adjacent += 1
                
                if col > 0: # top left
                    if self.board[row + 1, col - 1].status == CELL_STATUS_FLAG: num_adjacent += 1

                if (self.num_cols - col > 1): # top right
                    if self.board[row + 1, col + 1].status == CELL_STATUS_FLAG: num_adjacent += 1

            #check left/right
            if col > 0: # left
                if self.board[row, col - 1].status == CELL_STATUS_FLAG: num_adjacent += 1

            if (self.num_cols - col > 1): # right
                if self.board[row, col + 1].status == CELL_STATUS_FLAG: num_adjacent += 1

            return num_adjacent
                    
        if self.game_status in (GAME_STATUS_IN_PROGRESS):
            cell = self.board[cell_coords]

            if cell.status == CELL_STATUS_EXPOSED: # can't expand if we can't see the neighboring bomb count
                
                if num_adjacent_flags(cell) == cell.neighbors:
                    if self.debug_mode: print('expaaaand')
                
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
        def __init__(self, parent, row, col):
    #        print(f'Initializing cell [{row}][{col}]')
            self.parent = parent
            self.row = row 
            self.col = col
            self.contains_bomb = False
            self.neighbors = 0
            self.status = CELL_STATUS_HIDDEN
        
        def enabled(self):
            if self.parent.game_status in (GAME_STATUS_LOST, GAME_STATUS_WON, GAME_STATUS_INIT):
                return False
            else:
                return self.status in (CELL_STATUS_HIDDEN, CELL_STATUS_FLAG, CELL_STATUS_FLAG_MAYBE)
        

        def get_cell_image_key(self):
            # Return the name of the image variable in SM_Assets that should be used to represent this cell
            game_status = self.parent.game_status
            
            # on game over, reveal undetected bombs and highlight any false flags            
            if game_status == GAME_STATUS_WON and self.contains_bomb:
                return 'img_flag'
            
            elif game_status == GAME_STATUS_LOST and self.contains_bomb and self.status in (CELL_STATUS_HIDDEN, CELL_STATUS_FLAG_MAYBE):
                return 'img_bomb'

            elif game_status == GAME_STATUS_LOST and self.status == CELL_STATUS_FLAG and not self.contains_bomb:
                    return 'img_flag_wrong'

            else:
                if self.status == CELL_STATUS_EXPOSED:
                    return f'img_{self.neighbors}'
                elif self.status == CELL_STATUS_FLAG:
                    return 'img_flag'
                elif self.status == CELL_STATUS_FLAG_MAYBE:
                    return 'img_flag_maybe'
                elif self.status == CELL_STATUS_BOOM:
                    return 'img_boom'
                elif self.status == CELL_STATUS_BOMB_EXPOSED:
                    return 'img_bomb'
                else: # hidden should be the only remaining valid option
                    return 'img_hidden'
                

    class SwineMeeperGUI:
        def __init__(self, parent):
            # print('SwineMeeperGUI init')
            
            self.root = tk.Tk()
            self.parent = parent
            
            self.assets = self.SM_Assets(r'C:\Users\thema\Documents\Python Scripts\swinemeeper\assets\\') # TODO TEMP! 
            
            self.root.title("SwineMeeper")
            self.root.config(menu=self.create_menu_bar(self.root))

            self.CYCLE_SPEED = 6 # desired delay in game loop (in ms)
            self.FPS_TARGET = 500 # desired frames per second
            
            self.render_timestamp = time.time() # time we last updated the gui
            self.refresh_check_timestamp = 0 # last time a cycle was initiated.. hoping to use for FPS improvement

            self.frames_elapsed = 0 # for measuring actual FPS
            self.refresh_checks_elapsed = 0 # for evaluating peformance
            
            self.refresh_checks_startup_time = time.time() # for evaluating peformance
            self.loop = None # not sure if this is implemented 'correctly' yet but it works so far.. used with the tk.after and tk.after_cancel logic for looping through the game loop cycle
            
            self.last_action = 'creation' # description of the last action to affect the game
           
            self.clock_label_text = tk.StringVar() # number of seconds elapsed since first cell was clicked
            self.bomb_counter_text = tk.StringVar() # Number of bombs - number of placed flags
            
            self.clock_label_text.set('000')
            self.bomb_counter_text.set('000')            
            
            self.btn_start = tk.Button(master=self.root, image=self.assets.img_happy, command=self.restart_game)
            self.lbl_clock = tk.Label(master=self.root, textvariable=self.clock_label_text, font=('Stencil 24'))
            self.lbl_bomb_counter = tk.Label(master=self.root, textvariable=self.bomb_counter_text, font=('Stencil 24'))

            #if self.parent.debug_mode:
            self.debug_label_text = tk.StringVar() # A label w/ performance stats used for debugging purposes
            self.debug_label_text.set('')
            self.lbl_debug = tk.Label(master=self.root, textvariable=self.debug_label_text, font=('Arial 12'), justify='left', anchor='w')


            self.frame_cell_grid = tk.Frame(master=self.root)
            self.board_cell_buttons = {}

            for i in range(self.parent.num_rows):
                for j in range(self.parent.num_cols):
                    self.board_cell_buttons[(i, j)] = tk.Button(master=self.frame_cell_grid, image=self.assets.img_hidden) # add cell to the dictionary and establish default behavior
                    self.board_cell_buttons[(i, j)].grid(row=i, column=j) # place the cell in the frame
                    self.board_cell_buttons[(i, j)].bind('<ButtonRelease>', partial(self.CellButtonReleaseHandler,(i , j))) # add a mouse handler to deal with user input

            self.lbl_clock.grid(row=0, column=0) #, sticky = tk.W)
            self.btn_start.grid(row=0, column=1)
            self.lbl_bomb_counter.grid(row=0, column=2)
            self.frame_cell_grid.grid(row=1, column=0, columnspan=3, pady=5)
            self.lbl_debug.grid(row=2, column=0, columnspan=3, pady=5)
             
            self.game_loop() # start the game cycle!


        def get_performance_stats(self):
            time_since_render =  time.time() - self.render_timestamp
            run_time = round(self.render_timestamp - self.refresh_checks_startup_time,3)
            fps_actual = round(self.frames_elapsed/run_time,3) if run_time > 0 else 0
            refresh_cycle_actual = round(run_time/self.refresh_checks_elapsed*1000,3) if run_time > 0 else 0
            
            str_out = (
                f'Game status: {self.parent.game_status}'+
                f'\nRun Time: {run_time:.3f} s' +
                f'\t\tTime since last frame: {time_since_render:.6f}' +
                f'\nFrames elapsed: {str(self.frames_elapsed).zfill(3)}' +
                f'\tCycles elapsed: {str(self.refresh_checks_elapsed).zfill(3)}' +
                f'\nFPS (Target): {self.FPS_TARGET}' +
                f'\t\tCycle speed (Target): {self.CYCLE_SPEED} ms' +
                f'\nFPS (Actual): {fps_actual:.3f}' +
                f'\tCycle speed (Actual): {refresh_cycle_actual:.3f} ms' +
                f'\nClicks processed {self.parent.turn_count}' +
                f'\t\tRemaining cells: {self.parent.get_remaining_cell_count()} out of {self.parent.num_rows*self.parent.num_cols - self.parent.num_bombs}'
                )
            
            return str_out

        def game_loop(self):
            self.refresh_check_timestamp = time.time()
            if not self.parent.game_status in (GAME_STATUS_WON, GAME_STATUS_LOST):
                if self.parent.game_status not in (GAME_STATUS_INIT):    
                    self.refresh_checks_elapsed += 1
                    time_since_render =  time.time() - self.render_timestamp
                    if time_since_render >= 1.0/self.FPS_TARGET:
                        self.render_gui()


                time_to_render = (time.time() - self.refresh_check_timestamp)*1000 # in ms
                next_cycle_time = max(int(self.CYCLE_SPEED - time_to_render),0)
            
                # after_time = 0 if int(time_to_render) >= self.CYCLE_SPEED else int(self.CYCLE_SPEED - time_to_render)
                # after_time = max(time_to_render,0)
                # #after_time = int(self.CYCLE_SPEED)
                

                self.loop = self.root.after(next_cycle_time, self.game_loop) #try again in (at least) X ms

                # else:
                #     if self.parent.debug_mode: print('game is still loading - not time to render yet')
            else:
                #self.root.after_cancel(self.game_loop)
                if self.parent.debug_mode: print('this is the end')
                self.render_gui()
            
            
                


        class SM_Assets: # yay inner class!
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

                MAGIC_NUM_TO_FIX_CELL_SIZE = 5 # tk.Button seems to add 5 px to the height and width 
                self.cell_width = self.img_0.width() + MAGIC_NUM_TO_FIX_CELL_SIZE # assumes all cell images are identically sized
                self.cell_height = self.img_0.height() + MAGIC_NUM_TO_FIX_CELL_SIZE
            

        def create_menu_bar(self, root):
            menubar = tk.Menu(root)
            filemenu = tk.Menu(menubar, tearoff=0)
            filemenu.add_command(label="About", command=partial(self.open_about_window, root))
            filemenu.add_separator()
            filemenu.add_command(label="Exit", command=self.root.quit)
            menubar.add_cascade(label="File", menu=filemenu)
            game_menu = tk.Menu(menubar, tearoff=0)
            game_menu.add_command(label="Settings", command=partial(self.open_game_settings_window, root))
            game_menu.add_command(label="Help", command=partial(self.open_help_window, root))
            menubar.add_cascade(label="Game", menu=game_menu)
            return menubar
        

        def open_game_settings_window(self, root):
            top= tk.Toplevel(root)
            top.geometry("500x250")
            top.title("Game Settings")
            tk.Label(top, text= "Settings go here", font=('Stencil 24')).place(x=150,y=80)

        def open_help_window(self, root):
            top= tk.Toplevel(root)
            top.geometry("500x250")
            top.title("Help")
            tk.Label(top, text= "Here's how to play SwineMeeper", font=('Helvetica 14 bold')).place(x=150,y=80)

        
        def open_about_window(self, root):
            top= tk.Toplevel(root)
            top.geometry("500x250")
            top.title("About SwineMeeper")
            tk.Label(top, text= "All About SwineMeeper", font=('Helvetica 14 bold')).place(x=150,y=80)

    
        def CellButtonReleaseHandler(self, btn_coords, event):
            if self.parent.game_status in(GAME_STATUS_READY, GAME_STATUS_IN_PROGRESS):
                # First check to see if the user tried to cancel the click by moving the cursor out of the cell
                if not(event.x < 0 or event.y < 0 or event.x > self.assets.cell_width or event.y > self.assets.cell_height):      
                    # if self.parent.debug_mode: print('CLICK')

                    if event.num == 1: # Left click
                        self.parent.expose_cell(btn_coords)
                    elif event.num == 2: # middle click
                        self.parent.expand_solution(btn_coords)
                    elif event.num == 3: # right click
                        self.parent.toggle_flag(btn_coords)
                    else:
                        raise ValueError('Unexpected button click on game cell')
                else:
                    if self.parent.debug_mode: print('unCLICK')
                
            self.render_gui()
       
    
        def render_gui(self):
            if self.parent.debug_mode: self.debug_label_text.set(self.get_performance_stats())
            
            self.frames_elapsed += 1
            self.render_timestamp = time.time()
            
            self.clock_label_text.set(str(int(self.parent.timer.get_elapsed_time())).zfill(3)) # there's probably a cleaner way to format this #
            self.bomb_counter_text.set(str(self.parent.get_num_flags_remaining()).zfill(3))

            btn_img = 'img_unhappy' if (self.parent.game_status==GAME_STATUS_LOST) else 'img_happy'
            self.btn_start.config(image=getattr(self.assets, btn_img))

            for i in range(self.parent.num_rows): # basic approach: change the image and TODO state of each cell after every user input
                for j in range(self.parent.num_cols):
                    cell = self.parent.board[(i,j)]
                    btn = self.board_cell_buttons[(i,j)]
                    state = tk.NORMAL if cell.enabled() else tk.DISABLED

                    btn.config(image=getattr(self.assets, cell.get_cell_image_key()), state=state)

            #self.render_timestamp = time.time()
            

        def restart_game(self):
            print('Restarting game...')
            print('(todo)')


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

    def restart_timer(self):
        if self.is_running:
            if self.parent.debug_mode: print(f'Resetting timer')
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



if __name__ == '__main__':
    SwineMeeperGameManager().gui.root.mainloop()

    # game_manager = SwineMeeperGameManager()
    # game_manager.gui.root.mainloop()
