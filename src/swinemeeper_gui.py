import tkinter as tk
from functools import partial

import swinemeeper_logic as meep

root = tk.Tk()
root.title("SwineMeeper")

board = None # will become a meep.SwinemeeperBoard object

dict_buttons = {} # contains all the main button objects (cells in the game grid). The key is the tuple of (x, y)
dict_cell_images = {} # contains an entry of (x, y) for every cell in the board - theoretically saves the images from garbage collection

btn_start = None # the start / restart button
varStartBtnTxt = tk.StringVar() # :) :(
varClock = tk.StringVar() # number of seconds (or clicks?) elapsed since first cell was exposed
varBombCounter = tk.StringVar() # Number of bombs - number of placed flags

cell_width = tk.IntVar() # based on the size of cell_0.gif (assuming all are same dimensions) - do we need to add padding?
cell_height = tk.IntVar()
    
def import_assets(root, dir_img):
    # Tile graphics:
    root.img_hidden     = tk.PhotoImage(file=f'{dir_img}hidden.gif')    
    root.img_flag       = tk.PhotoImage(file=f'{dir_img}flag.gif')    
    root.img_flag_maybe = tk.PhotoImage(file=f'{dir_img}flag_maybe.gif')        
    root.img_boom       = tk.PhotoImage(file=f'{dir_img}boom.gif') 
    root.img_bomb       = tk.PhotoImage(file=f'{dir_img}bomb.gif') 
    root.img_0          = tk.PhotoImage(file=f'{dir_img}0.gif') 
    root.img_1          = tk.PhotoImage(file=f'{dir_img}1.gif') 
    root.img_2          = tk.PhotoImage(file=f'{dir_img}2.gif') 
    root.img_3          = tk.PhotoImage(file=f'{dir_img}3.gif') 
    root.img_4          = tk.PhotoImage(file=f'{dir_img}4.gif') 
    root.img_5          = tk.PhotoImage(file=f'{dir_img}5.gif') 
    root.img_6          = tk.PhotoImage(file=f'{dir_img}6.gif') 
    root.img_7          = tk.PhotoImage(file=f'{dir_img}7.gif') 
    root.img_8          = tk.PhotoImage(file=f'{dir_img}8.gif') 
    
    # Start button graphics:
    root.img_happy      = tk.PhotoImage(file=f'{dir_img}happy.gif') 
    root.img_unhappy    = tk.PhotoImage(file=f'{dir_img}unhappy.gif') 
#    root.img_unsure    = tk.PhotoImage(file=f'{dir_img}TODO.gif') 

    MAGIC_NUM_TO_FIX_CELL_HEIGHT = 5 # tk.Button seems to add 5 px to the height and width 
    cell_width.set(root.img_0.width() + MAGIC_NUM_TO_FIX_CELL_HEIGHT) # TODO THIS SEEMS LIKE BAD PRACTICE!
    cell_height.set(root.img_0.height() + MAGIC_NUM_TO_FIX_CELL_HEIGHT) # TODO THIS SEEMS LIKE BAD PRACTICE!
   
   
def ButtonReleaseHandler(btn_coords, event):
    if board.game_status in(meep.GAME_STATUS_READY, meep.GAME_STATUS_IN_PROGRESS):

        # First check to see if the user tried to cancel the click by moving the cursor out of the cell
        if not(event.x < 0 or event.y < 0 or event.x > cell_width.get() or event.y > cell_height.get()):
            #print(f'Button {event.num} release on btn {btn_coords}')        
            
            if board.board[btn_coords[0]][btn_coords[1]].enabled():
                if event.num == 1: # Left click
                    board.expose_cell(btn_coords)

                elif event.num == 2: # middle click
                    board.expand_solution(btn_coords)

                elif event.num == 3: # right click
                    board.toggle_flag(btn_coords)

                else:
                    raise ValueError('Unexpected button click on game cell')

                render_gui()

            # else:
                # print(f'Disabled button clicked - {btn_coords}')
        # else: 
            # print(event)


def render_gui():
    dict_curr_btn_states = board.get_dict_of_cell_states()

    for i in range(board.num_rows): # basic approach: change the image and TODO state of each cell after every user input
        for j in range(board.num_cols):
            dict_buttons[(i,j)].config(image=getattr(root, board.board[i][j].get_img_key()))##, state=state)
            dict_buttons[(i, j)]['state'] = dict_curr_btn_states[(i,j)]
            ####dict_buttons[(i, j)]['state'] = dict_curr_btn_states[(i,j)]
           
    # update top frame
    varClock.set(str(board.timer.get_elapsed_time()).zfill(3))
    varBombCounter.set(str(board.num_bombs - board.get_num_flags_placed()).zfill(3))
    
    if board.game_status == meep.GAME_STATUS_GAME_OVER:
        print('game over button')
        #dict_buttons[(i,j)].config(image=getattr(root, board.board[i][j].get_img_key()))##, state=state)

        ###dict_buttons[(i,j)].config(image=getattr(root, board.board[i][j].get_img_key()))##, state=state)
            
    else:
        print('happy buttton')


def restart_game():
    print('Restarting game...')
    print('(todo)')




if __name__ == '__main__':
    dir_img =  r'C:\Users\thema\Documents\Python Scripts\swinemeeper\img\\'
   
    rows = 10
    cols = 15
    bombs = 5
    
    board = meep.SwinemeeperBoard(rows, cols, bombs)
    
    board.print_bomb_grid()    
    # board.print_neighbor_grid()
    # board.print_display_grid()

    create_gui(dir_img)

    root.mainloop()


