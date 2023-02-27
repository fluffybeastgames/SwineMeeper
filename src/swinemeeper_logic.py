### SWINEMEEPER!!!

import random as rand
import tkinter as tk 
import time
from functools import partial
import os.path

GAME_STATUS_READY = 'Ready'
GAME_STATUS_IN_PROGRESS = 'In Progress'
GAME_STATUS_GAME_OVER = 'Game Over'
GAME_STATUS_WON = 'Won'

CELL_STATUS_HIDDEN = 0 # available
CELL_STATUS_EXPOSED = 1
CELL_STATUS_FLAG = 2
CELL_STATUS_FLAG_MAYBE = 3
CELL_STATUS_BOOM = 4
CELL_STATUS_BOMB_EXPOSED = 5 
CELL_STATUS_FLAG_WAS_WRONG = 6

RECURSION_LIMIT = 1000 # 1000 by default, but can be expanded at user risk w/ sys.setrecursionlimit(num)
    # Added maximum size for grid (for general performance reasons but more specifically to avoid breaching the recursion depth limit. When implementing custom game dimensions we could offer users exceeding the default max of 1000 cells the ability to increase the sys. max recursion depth option (up to a reasonable option like, 2000?)
 
DEBUG_MODE = True # no proper logging exists yet, but this will increase the number of print() statements executed
if DEBUG_MODE: print('DEBUG_MODE active')




def test_classes():
    print('testing class rewrite')
    game_manager = SwineMeeperGameManager()

    game_manager.timer.start_timer()
    print(f'Game status: {game_manager.game_status}')
    print(f'Game turn: {game_manager.turn_count}')
    print(f'Game params: {game_manager.num_bombs}x{game_manager.num_bombs} cells with {game_manager.num_bombs} bombs')

    print(f'Time elapsed: {game_manager.timer.get_elapsed_time()}')

    game_manager.timer.pause_timer()
    print(f'Time elapsed: {game_manager.timer.get_elapsed_time()}')
    game_manager.timer.add_time_to_timer(10)
    print(f'Time elapsed: {game_manager.timer.get_elapsed_time()}')
    
    game_manager.timer.pause_timer()
    print(f'Time elapsed: {game_manager.timer.get_elapsed_time()}')
    game_manager.timer.add_time_to_timer(-50)
    print(f'Time elapsed: {game_manager.timer.get_elapsed_time()}')

    # game_manager.expose_cell((0,0))

    print(f'Game turn: {game_manager.turn_count}')

    game_manager.gui.root.mainloop()






################################################################################

# root = tk.Tk()
# root.title("SwineMeeper")

# board = None # will become a meep.SwinemeeperBoard object

# dict_buttons = {} # contains all the main button objects (cells in the game grid). The key is the tuple of (x, y)
# dict_cell_images = {} # contains an entry of (x, y) for every cell in the board - theoretically saves the images from garbage collection

# btn_start = None # the start / restart button
# varStartBtnTxt = tk.StringVar() # :) :(
# varClock = tk.StringVar() # number of seconds (or clicks?) elapsed since first cell was exposed
# varBombCounter = tk.StringVar() # Number of bombs - number of placed flags

# cell_width = tk.IntVar() # based on the size of cell_0.gif (assuming all are same dimensions) - do we need to add padding?
# cell_height = tk.IntVar()
    



# def render_gui():
#     dict_curr_btn_states = board.get_dict_of_cell_states()

#     for i in range(board.num_rows): # basic approach: change the image and TODO state of each cell after every user input
#         for j in range(board.num_cols):
#             dict_buttons[(i,j)].config(image=getattr(root, board.board[i][j].get_img_key()))##, state=state)
#             dict_buttons[(i, j)]['state'] = dict_curr_btn_states[(i,j)]
#             ####dict_buttons[(i, j)]['state'] = dict_curr_btn_states[(i,j)]
           
#     # update top frame
#     varClock.set(str(board.timer.get_elapsed_time()).zfill(3))
#     varBombCounter.set(str(board.num_bombs - board.get_num_flags_placed()).zfill(3))
    
#     if board.game_status == meep.GAME_STATUS_GAME_OVER:
#         print('game over button')
#         #dict_buttons[(i,j)].config(image=getattr(root, board.board[i][j].get_img_key()))##, state=state)

#         ###dict_buttons[(i,j)].config(image=getattr(root, board.board[i][j].get_img_key()))##, state=state)
            
#     else:
#         print('happy buttton')



# def create_frame_cell_grid():
#     frame_out = tk.Frame(master=root)
    
#     for i in range(board.num_rows):
#         for j in range(board.num_cols):
#             dict_buttons[(i, j)] = tk.Button(master=frame_out, image=root.img_hidden) # add cell to the dictionary and establish default behavior
#             #dict_buttons[(i, j)].grid(row=i, column=j, pady=Y_PAD_ON_CELLS) # place the cell in the frame
#             dict_buttons[(i, j)].grid(row=i, column=j) # place the cell in the frame
#             dict_buttons[(i, j)].bind('<ButtonRelease>', partial(ButtonReleaseHandler,(i , j))) # add a mouse handler to deal with user input
            
#     return frame_out



# if __name__ == '__main__':
#     dir_img =  r'C:\Users\thema\Documents\Python Scripts\swinemeeper\img\\'
   
#     rows = 10
#     cols = 15
#     bombs = 5
    
#     board = meep.SwinemeeperBoard(rows, cols, bombs)
    
#     board.print_bomb_grid()    
#     # board.print_neighbor_grid()
#     # board.print_display_grid()

#     create_gui(dir_img)

#     root.mainloop()


################################################################################



class SwineMeeperGameManager:
    def __init__(self):
        print('SwineMeeperGameManager init')

        self.DEFAULT_NUM_ROWS = 8
        self.DEFAULT_NUM_COLS = 12
        self.DEFAULT_NUM_BOMBS = 5


        self.game_status = GAME_STATUS_READY
        self.turn_count = 0
        self.num_rows = self.DEFAULT_NUM_ROWS  
        self.num_cols = self.DEFAULT_NUM_COLS 
        self.num_bombs = self.DEFAULT_NUM_BOMBS 
        
        if DEBUG_MODE: print(f'Starting Parameters: {self.num_rows} rows x {self.num_cols} with {self.num_bombs} bombs')
        
        self.timer = SwineTimer()
        #self.board = SwinemeeperBoard() # defaults to 10x10 grid w/ 10 bombs
        self.gui = self.SwineMeeperGUI(self.num_rows, self.num_cols)

        
        if self.num_rows*self.num_cols >= RECURSION_LIMIT:
            raise ValueError('Too many cells!')
        
        elif self.num_bombs >= self.num_rows*self.num_cols:
            raise ValueError('Too many bombs!')

        self.board = [[self.SwineMeeperCell(i, j) for j in range(self.num_cols)] for i in range(self.num_rows)]
                
        self.add_bombs(self.num_bombs)
        self.calculate_neighbors()        
        # self.timer = SwineTimer()

      
    def add_bombs(self, num_bombs_to_add):
        num_attempts = 0
        num_added = 0
        if DEBUG_MODE: attempt_start_time = time.time()

        while (num_added < num_bombs_to_add):
            num_attempts = num_attempts + 1       
            target_row = rand.randrange(self.num_rows)
            target_col = rand.randrange(self.num_cols)
            
            if not self.board[target_row][target_col].contains_bomb:
                self.board[target_row][target_col].contains_bomb = True
                num_added = num_added + 1
        
        if DEBUG_MODE: print(f'Added {num_bombs_to_add} bombs in {num_attempts} attempts in {time.time() - attempt_start_time} seconds')

    
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
        
    def get_remaining_cell_count(self): # How many more cells must be exposed before only bombs are left?
        total_cells = self.num_rows * self.num_cols
        cells_occupied = 0
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                if self.board[row - 1][col].status == CELL_STATUS_EXPOSED:
                    cells_occupied +=1
                    
        #if DEBUG_MODE: print(f'cells occupied: {cells_occupied}, bombs_left: {total_cells - cells_occupied - self.num_bombs}')
        return total_cells - cells_occupied - self.num_bombs


    def get_num_flags_placed(self):
        num_flags = 0
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                if self.board[row - 1][col].status == CELL_STATUS_FLAG:
                    num_flags +=1        
        return num_flags


    def get_dict_of_cell_images(self): # returns a dict where they keys are cell coords and the values are the current image that should be associated with the corresponding cell
        # TODO this can probably be refactored away..
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
        # TODO this can probably be refactored away..
        
        dict_out = {}

        for row in range(self.num_rows):
            for col in range(self.num_cols):
                if self.board[row][col].enabled:
                    dict_out[(row,col)] = tk.NORMAL
                else:
                    dict_out[(row,col)] = tk.DISABLED
                
        return dict_out


    def end_game(self, victory=False):
        self.timer.pause_timer()

        for row in range(self.num_rows):
            for col in range(self.num_cols):
                self.board[row][col].enabled = False # all cells should be disabled, regardless of status
                
                cell_status = self.board[row][col].status
                cell_has_bomb = self.board[row][col].contains_bomb

                if cell_has_bomb and cell_status in (CELL_STATUS_HIDDEN, CELL_STATUS_FLAG_MAYBE):
                    if victory:
                        self.board[row][col].status = CELL_STATUS_FLAG
                    else:
                        self.board[row][col].status = CELL_STATUS_BOMB_EXPOSED
                    
        if victory:
            self.game_status = GAME_STATUS_WON
            print('YOU WIN')

        else:
            self.game_status = GAME_STATUS_GAME_OVER
            print('YOU LOSE')


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

        if self.master.game_status in (GAME_STATUS_READY, GAME_STATUS_IN_PROGRESS) and cell_status in (CELL_STATUS_HIDDEN, CELL_STATUS_FLAG_MAYBE): # proceed
            if self.master.game_status == GAME_STATUS_READY:
                self.timer.start_timer()
                self.master.game_status = GAME_STATUS_IN_PROGRESS

            if was_clicked:
                self.master.turn_count += 1

            if self.board[row][col].contains_bomb:
                if self.master.turn_count <= 1: # move bomb to a new location, recalculate neighbor counts, and reveal newly empty cell                        
                    # TODO perhaps we should make this functionality optional? Add a checkbox to the options..

                    print('OH NO a bomb on the first move') # HMMMM what about an option to implement 'suicide minesweeper' where you're guaranteed 0 neighbors on 1st move and then have to left click on bombs to expose more territory?
                    self.add_bombs(1)
                    self.remove_bomb(cell_coords)
                    self.calculate_neighbors()
                    # self.print_bomb_grid()
                    self.board[row][col].status = CELL_STATUS_EXPOSED

                else:
                    self.board[row][col].status = CELL_STATUS_BOOM
                    self.end_game(victory=False)
            else:
                self.board[row][col].status = CELL_STATUS_EXPOSED

            # If the cell contains no neighbors, recursively 'click' on all adjacent cells until a wall of numbers is fully exposed
            
            if self.board[row][col].neighbors == 0:
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
        print('expaaaand')
        row = cell_coords[0]
        col = cell_coords[1]
    
        if self.master.game_status in (GAME_STATUS_READY, GAME_STATUS_IN_PROGRESS):
            print('wt')
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



    class SwineMeeperCell:
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
            elif self.status == CELL_STATUS_FLAG_MAYBE:
                return 'img_flag_maybe'
            elif self.status == CELL_STATUS_BOOM:
                return 'img_boom'
            elif self.status == CELL_STATUS_BOMB_EXPOSED:
                return 'img_bomb'
            elif self.status == CELL_STATUS_FLAG_WAS_WRONG: # TODO add logic and image
                return 'img_bad_flag'
            else: # hidden should be the only remaining option
                return 'img_hidden'
            

    class SwineMeeperGUI:
        def __init__(self, default_rows, default_cols):
            print('SwineMeeperGUI init')
            
            self.root = tk.Tk()
            
            self.assets = self.SM_Assets(r'C:\Users\thema\Documents\Python Scripts\swinemeeper\assets\\') # TODO TEMP! 
            
            self.root.title("SwineMeeper")
            self.root.config(menu=self.create_menu_bar(self.root))
            
            self.varClockText = tk.StringVar() # number of seconds elapsed since first cell was clicked
            self.varBombCounter = tk.StringVar() # Number of bombs - number of placed flags

            self.varClockText.set('19')
            self.varBombCounter.set('11')
            
            self.btn_start = tk.Button(master=self.root, image=self.assets.img_happy, command=self.restart_game)
            self.lbl_clock = tk.Label(master=self.root, textvariable=self.varClockText, font=('Stencil 24'))
            self.lbl_bomb_counter = tk.Label(master=self.root, textvariable=self.varBombCounter, font=('Stencil 24'))
            # self.frame_cell_grid = self.create_frame_cell_grid() #

            self.frame_cell_grid = tk.Frame(master=self.root)
            self.dict_buttons = {}

            for i in range(default_rows):
                for j in range(default_cols):
                    self.dict_buttons[(i, j)] = tk.Button(master=self.frame_cell_grid, image=self.assets.img_hidden) # add cell to the dictionary and establish default behavior
                    self.dict_buttons[(i, j)].grid(row=i, column=j) # place the cell in the frame
                    self.dict_buttons[(i, j)].bind('<ButtonRelease>', partial(self.ButtonReleaseHandler,(i , j))) # add a mouse handler to deal with user input

            self.lbl_clock.grid(row=0, column=0) #, sticky = tk.W)
            self.btn_start.grid(row=0, column=1)
            self.lbl_bomb_counter.grid(row=0, column=2)
            self.frame_cell_grid.grid(row=1, column=0, columnspan=3, pady=5)


        class SM_Assets: # yay inner class!
            def __init__(self, dir_img):
                # print(f'{os.path.dirname(__file__)}../test')
                # print(os.getcwd())
                
                self.img_hidden     = tk.PhotoImage(file=f'{dir_img}hidden.gif')    
                self.img_flag       = tk.PhotoImage(file=f'{dir_img}flag.gif')    
                self.img_flag_maybe = tk.PhotoImage(file=f'{dir_img}flag_maybe.gif')        
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
                self.img_happy      = tk.PhotoImage(file=f'{dir_img}happy.gif') 
                self.img_unhappy    = tk.PhotoImage(file=f'{dir_img}unhappy.gif') 
                # self.img_unsure    = tk.PhotoImage(file=f'{dir_img}TODO.gif') 

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



        def create_gui():
            #self.create_menu_bar()
            
            # Top Frame - contains the start button and timer/flags remaining counter
            frame_top = tk.Frame(master=root) 
            varStartBtnTxt.set(':)')
            varClock.set('0'.zfill(3))
            varBombCounter.set(str(board.num_bombs).zfill(3))

            btn_start = tk.Button(master=frame_top, image=root.img_happy, command=restart_game)
            lbl_clock = tk.Label(master=frame_top, textvariable=varClock, font=('Stencil 24'))
            #lbl_clock = tk.Label(master=frame_top, textvariable=board.timer.udate_timer_label , font=('Stencil 24'))
            lbl_bomb_counter = tk.Label(master=frame_top, textvariable=varBombCounter, font=('Stencil 24'))
            
            lbl_clock.grid(row=0, column=0) #, sticky = tk.W)
            btn_start.grid(row=0, column=1)
            lbl_bomb_counter.grid(row=0, column=2)

            # Game Frame - a 2D array of buttons representing the game cells
            frame_cell_grid = create_frame_cell_grid() #
            
            frame_top.grid(row=0, column=0, pady=5)
            frame_cell_grid.grid(row=1, column=0, pady=5)

        
        def ButtonReleaseHandler(self, btn_coords, event):
            print('CLICK')
            # if board.game_status in(meep.GAME_STATUS_READY, meep.GAME_STATUS_IN_PROGRESS):

            #     # First check to see if the user tried to cancel the click by moving the cursor out of the cell
            #     if not(event.x < 0 or event.y < 0 or event.x > cell_width.get() or event.y > cell_height.get()):
            #         #print(f'Button {event.num} release on btn {btn_coords}')        
                    
            #         if board.board[btn_coords[0]][btn_coords[1]].enabled():
            #             if event.num == 1: # Left click
            #                 board.expose_cell(btn_coords)

            #             elif event.num == 2: # middle click
            #                 board.expand_solution(btn_coords)

            #             elif event.num == 3: # right click
            #                 board.toggle_flag(btn_coords)

            #             else:
            #                 raise ValueError('Unexpected button click on game cell')

            #             render_gui()

            #         # else:
            #             # print(f'Disabled button clicked - {btn_coords}')
            #     # else: 
            #         # print(event)



        # def create_frame_cell_grid(self):
        #     frame_out = tk.Frame(master=root)
            
        #     for i in range(self board.num_rows):
        #         for j in range(board.num_cols):
        #             dict_buttons[(i, j)] = tk.Button(master=frame_out, image=root.img_hidden) # add cell to the dictionary and establish default behavior
        #             #dict_buttons[(i, j)].grid(row=i, column=j, pady=Y_PAD_ON_CELLS) # place the cell in the frame
        #             dict_buttons[(i, j)].grid(row=i, column=j) # place the cell in the frame
        #             dict_buttons[(i, j)].bind('<ButtonRelease>', partial(ButtonReleaseHandler,(i , j))) # add a mouse handler to deal with user input
                    
        #     return frame_out
        

            
        def restart_game():
            print('Restarting game...')
            print('(todo)')



class SwineTimer:
    def __init__(self):
        self.time_started = 0
        self.time_stopped = 0
        self.is_running = False

    def start_timer(self):
        if not self.is_running:
            if DEBUG_MODE: print(f'Starting timer')
            self.is_running = True
            self.time_started = time.time()
            self.time_stopped = 0

    def pause_timer(self):
        if self.is_running:
            if DEBUG_MODE: print(f'Stopping timer')
            self.is_running = False
            self.time_stopped = time.time()

    def restart_timer(self):
        if self.is_running:
            if DEBUG_MODE: print(f'Resetting timer')
            self.time_started = 0
            self.time_stopped = 0

    def resume_timer(self):
        if not self.is_running:
            if DEBUG_MODE: print(f'Resuming timer')
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
    # print('Don\'t run me! Run swinemeeper_gui.py instead!')
    test_classes()