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
    root.img_hidden = tk.PhotoImage(file=f'{dir_img}cell_hidden.gif')    
    root.img_flag   = tk.PhotoImage(file=f'{dir_img}cell_flag.gif')    
    root.img_boom   = tk.PhotoImage(file=f'{dir_img}cell_boom.gif') 
    root.img_bomb   = tk.PhotoImage(file=f'{dir_img}cell_bomb.gif') 
    root.img_0      = tk.PhotoImage(file=f'{dir_img}cell_0.gif') 
    root.img_1      = tk.PhotoImage(file=f'{dir_img}cell_1.gif') 
    root.img_2      = tk.PhotoImage(file=f'{dir_img}cell_2.gif') 
    root.img_3      = tk.PhotoImage(file=f'{dir_img}cell_3.gif') 
    root.img_4      = tk.PhotoImage(file=f'{dir_img}cell_4.gif') 
    root.img_5      = tk.PhotoImage(file=f'{dir_img}cell_5.gif') 
    root.img_6      = tk.PhotoImage(file=f'{dir_img}cell_6.gif') 
    root.img_7      = tk.PhotoImage(file=f'{dir_img}cell_7.gif') 
    root.img_8      = tk.PhotoImage(file=f'{dir_img}cell_8.gif') 

    MAGIC_NUM_TO_FIX_CELL_HEIGHT = 5 # tk.Button seems to add 5 px to the height and width
    cell_width.set(root.img_0.width() + MAGIC_NUM_TO_FIX_CELL_HEIGHT)
    cell_height.set(root.img_0.height() + MAGIC_NUM_TO_FIX_CELL_HEIGHT)
   


def ButtonReleaseHandler(btn_coords, event):

    
    # First check to see if the user tried to cancel the click by moving the cursor out of the cell
    if not(event.x < 0 or event.y < 0 or event.x > cell_width.get() or event.y > cell_height.get()):
        if board.cell_enabled(btn_coords):
            #print(f'Button {event.num} release on btn {btn_coords}')

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
    # print('render_gui')
    # board.print_display_grid()



#get_num_flags_placed

    # update game grid:
    dict_curr_images = board.get_dict_of_cell_images()
    dict_curr_btn_states = board.get_dict_of_cell_states()

    for i in range(board.num_rows): # basic approach: change the image and TODO state of each cell after every user input
        for j in range(board.num_cols):
            dict_buttons[(i,j)].config(image=getattr(root, dict_curr_images[(i,j)]))##, state=state)
            dict_buttons[(i, j)]['state'] = dict_curr_btn_states[(i,j)]
           
    # update top frame
    varClock.set(str(board.turn_count).zfill(3))
    
    if board.game_status == meep.GAME_STATUS_GAME_OVER:
        varStartBtnTxt.set(':(')
    else:
        varStartBtnTxt.set(':)')
       

            

    # TODO more sophisticated than redrawing every cell's image every move: look only at the dictionary items where keys don't match, and redraw/configure them
    # shared_items = {k: x[k] for k in x if k in y and x[k] == y[k]}
    # print(len(shared_items))


def restart_game():
    print('Restarting game...')

    # global board
    # global dict_buttons

    # #board.new

    # dir_img =  r'C:\Users\thema\Documents\Python Scripts\swinemeeper\img\\'
    # rows = 6
    # cols = 12
    # bombs = int(rows*cols*.25)

    # dict_buttons.clear() # repopulate the dict of buttons. Don't just overwrite key value pairs ( in case the board has shrunk)
    # board = meep.SwinemeeperBoard(rows, cols, bombs)
    # board.print_bomb_grid()

    # # list = root.grid_slaves()
    # # for l in list:
    # #     l.destroy()

    # frame_cell_grid = create_frame_cell_grid()
    # frame_cell_grid.grid(row=1, column=0, pady=5)
    # # board.print_neighbor_grid()
    # # board.print_display_grid()


    # #create_gui(dir_img)

def create_frame_cell_grid():
    frame_out = tk.Frame(master=root)
    
    for i in range(board.num_rows):
        for j in range(board.num_cols):
            dict_buttons[(i, j)] = tk.Button(master=frame_out, image=root.img_hidden) # add cell to the dictionary and establish default behavior
            #dict_buttons[(i, j)].grid(row=i, column=j, pady=Y_PAD_ON_CELLS) # place the cell in the frame
            dict_buttons[(i, j)].grid(row=i, column=j) # place the cell in the frame
            dict_buttons[(i, j)].bind('<ButtonRelease>', partial(ButtonReleaseHandler,(i , j))) # add a mouse handler to deal with user input
            
    return frame_out


def create_menu_bar():
    menubar = tk.Menu(root)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="About", command=open_about_window)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=filemenu)

    game_menu = tk.Menu(menubar, tearoff=0)
    game_menu.add_command(label="Settings", command=open_game_settings_window)
    game_menu.add_command(label="Help", command=open_help_window)
    menubar.add_cascade(label="Game", menu=game_menu)

    root.config(menu=menubar)

def open_game_settings_window():
   top= tk.Toplevel(root)
   top.geometry("500x250")
   top.title("Game Settings")
   tk.Label(top, text= "Settings go here", font=('Helvetica 14 bold')).place(x=150,y=80)

def open_help_window():
   top= tk.Toplevel(root)
   top.geometry("500x250")
   top.title("Help")
   tk.Label(top, text= "Here's how to play SwineMeeper", font=('Helvetica 14 bold')).place(x=150,y=80)

def open_about_window():
   top= tk.Toplevel(root)
   top.geometry("500x250")
   top.title("About SwineMeeper")
   tk.Label(top, text= "All About SwineMeeper", font=('Helvetica 14 bold')).place(x=150,y=80)


def create_gui(dir_img):

    import_assets(root, dir_img)

    # Menu 
    create_menu_bar()
    
    
    # Top Frame - contains the start button and timer/flags remaining counter
    frame_top = tk.Frame(master=root) 
    varStartBtnTxt.set(':)')
    varClock.set('0'.zfill(3))
    varBombCounter.set(str(board.num_bombs).zfill(3))

    btn_start = tk.Button(master=frame_top, textvariable=varStartBtnTxt, command=restart_game)
    lbl_clock = tk.Label(master=frame_top, textvariable=varClock)
    lbl_bomb_counter = tk.Label(master=frame_top, textvariable=varBombCounter)
    
    lbl_clock.grid(row=0, column=0)
    btn_start.grid(row=0, column=1)
    lbl_bomb_counter.grid(row=0, column=2)

    # Game Frame - a 2D array of buttons representing the game cells
    frame_cell_grid = create_frame_cell_grid() #
    

    frame_top.grid(row=0, column=0, pady=5)
    frame_cell_grid.grid(row=1, column=0, pady=5)



if __name__ == '__main__':


    dir_img =  r'C:\Users\thema\Documents\Python Scripts\swinemeeper\img\\'
    # rows = 7
    # cols = 12
    # bombs = int(rows*cols*.25)


    rows = 10
    cols = 14
    bombs = 6
    
    board = meep.SwinemeeperBoard(rows, cols, bombs)
    board.print_bomb_grid()
    # board.print_neighbor_grid()
    # board.print_display_grid()


    create_gui(dir_img)
    
    # varClock.set('001')
    # varBombCounter.set('998')

    root.mainloop()

