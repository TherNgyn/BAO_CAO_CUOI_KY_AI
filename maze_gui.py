import math
from simpleai.search import SearchProblem, astar
import numpy as np
import cv2
import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image, ImageTk
import time
from tkinter import messagebox
from matplotlib.animation import FuncAnimation
# Define cost of moving around the map
cost_regular = 1.0
cost_diagonal = 1.7

# Create the cost dictionary
COSTS = {
    "up": cost_regular,
    "down": cost_regular,
    "left": cost_regular,
    "right": cost_regular,
    "up left": cost_diagonal,
    "up right": cost_diagonal,
    "down left": cost_diagonal,
    "down right": cost_diagonal,
}
# Define the map
MAP =  """
##############################
#         #              #   #
# ####    ########       #   #
#    #    #              #   #
#    ###     #####  ######   #
#      #   ###   #           #
#      #     #   #  #  #   ###
#     #####    #    #  #     #
#              #       #     #
##############################

"""

MAP = [list(x) for x in MAP.split("\n") if x]
M = 10
N = 30
W = 21
mau_xanh = np.zeros((W, W, 3), np.uint8) + (np.uint8(255), np.uint8(0), np.uint8(0))
mau_trang = np.zeros((W, W, 3), np.uint8) + (np.uint8(255), np.uint8(255), np.uint8(255))
image = np.ones((M*W, N*W, 3), np.uint8)*255

for x in range (0, M):
    for y in range (0,N):
        if MAP[x][y] == "#":
            image[x*W:(x+1)*W, y*W:(y+1)*W] = mau_xanh
        elif MAP[x][y] == ' ':
            image[x*W:(x+1)*W, y*W:(y+1)*W] = mau_trang
color_coverted = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
pil_image = Image.fromarray(color_coverted)

class MazeSolver(SearchProblem):
    # Initialize the class 
    def __init__(self, board):
        self.board = board
        self.goal = (0, 0)

        for y in range(len(self.board)):
            for x in range(len(self.board[y])):
                if self.board[y][x].lower() == "o":
                    self.initial = (x, y)
                elif self.board[y][x].lower() == "x":
                    self.goal = (x, y)
        super(MazeSolver, self).__init__(initial_state=self.initial)
    def actions(self, state):
        actions = []
        for action in COSTS.keys():
            newx, newy = self.result(state, action)
            if self.board[newy][newx] != "#":
                actions.append(action)
        return actions

    # Update the state based on the action
    def result(self, state, action):
        x, y = state

        if action.count("up"):
            y -= 1
        if action.count("down"):
            y += 1
        if action.count("left"):
            x -= 1
        if action.count("right"):
            x += 1

        new_state = (x, y)

        return new_state

    # Check if we have reached the goal
    def is_goal(self, state):
        return state == self.goal

    # Compute the cost of taking an action
    def cost(self, state, action, state2):
        return COSTS[action]

    # Heuristic that we use to arrive at the solution
    def heuristic(self, state):
        x, y = state
        gx, gy = self.goal
        return math.sqrt((x - gx) ** 2 + (y - gy) ** 2)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.dem = 0
        self.title("Maze Solver")
        self.cvs_me_cung = tk.Canvas(self, width=N*W, height=M*W, relief = tk.SUNKEN, border = 1)
        self.image_tk = ImageTk.PhotoImage(pil_image)
        self.cvs_me_cung.create_image(0, 0, anchor = tk.NW, image = self.image_tk)
        self.cvs_me_cung.bind("<Button-1>", self.xu_ly_mouse)
        btn_start  = tk.Button(self, text = "Start", width = 7, command = self.btn_start_click)
        btn_restart = tk.Button(self, text = "Restart", width = 7, command = self.btn_restart_click)
        self.cvs_me_cung.grid(row = 0, column = 0, padx = 5, pady = 5)
        btn_start.grid(row = 0, column = 1, padx = 5, pady = 6, sticky = tk.N) #pady la khoang cach giua 2 button
        btn_restart.grid(row = 0, column = 1, padx = 5, pady = 6)
    
    def btn_start_click(self):
        # Create a map
        problem = MazeSolver(MAP)
        # Run the search
        result = astar(problem, graph_search=True) 
        # Extract the path
        if result is not None:
            path = [x[1] for x in result.path()]
        else:
            print("No path found.")
            messagebox.showinfo("Thông báo", "Không tìm thấy đường đi")
            path = []
        # Print the result
        print()
        for y in range(len(MAP)):
            for x in range(len(MAP[y])):
                if (x, y) == problem.initial:
                    print('o', end='')
                elif (x, y) == problem.goal:
                    print('x', end='')
                elif (x, y) in path:
                    print('·', end='')
                else:
                    print(MAP[y][x], end='')

            print()
        print(path)
        L = len(path)
        bg_color = self.cvs_me_cung['background']  # Define the variable "bg_color"
        for i in range(1, L):
            x1, y1 = path[i-1]
            x2, y2 = path[i]
            line = self.cvs_me_cung.create_line(x1*W+W//2, y1*W+W//2, x2*W+W//2, y2*W+W//2, fill='red', width=2)
            arrow = self.ve_mui_ten(y2-y1, x2-x1, x2*W+W//2, y2*W+W//2, 'red')
            self.cvs_me_cung.update()
            time.sleep(0.1)
            self.cvs_me_cung.delete(arrow)
            self.cvs_me_cung.update()

        self.ve_mui_ten(y2-y1, x2-x1, x2*W+W//2, y2*W+W//2, 'red')
        
    def ve_mui_ten(self, b, a, tx, ty, color):
        p_mui_ten = [(0,0,1), (-20,10,1), (-15,0,1), (-20,-10,1)]
        p_mui_ten_ma_tran = [np.array([[0],[0],[1]],np.float32),
                                np.array([[-20],[10],[1]],np.float32),
                                np.array([[-15],[0],[1]],np.float32),
                                np.array([[-20],[-10],[1]],np.float32)]

        M1 = np.array([[1, 0, tx], 
                        [0, 1, ty], 
                        [0, 0, 1]], np.float32)

        theta = np.arctan2(b, a)
        M2 = np.array([[np.cos(theta), -np.sin(theta), 0],
                        [np.sin(theta),  np.cos(theta), 0],
                        [     0,             0,        1]], np.float32)

        M = np.matmul(M1, M2)

        q_mui_ten = []
        for p in p_mui_ten_ma_tran:
            q = np.matmul(M, p)
            q_mui_ten.append((q[0,0], q[1,0]))
        arrow = self.cvs_me_cung.create_polygon(q_mui_ten, fill = color, outline = color)
        return arrow
    def btn_restart_click(self):
        # Delete all items from the canvas
        self.cvs_me_cung.delete('all')
        # Redraw the initial image
        self.cvs_me_cung.create_image(0, 0, anchor = tk.NW, image = self.image_tk)
        
        self.dem = 0
        self.cvs_me_cung.update()
        for y in range(len(MAP)):
            for x in range(len(MAP[y])):
                if MAP[y][x] == 'o':
                    MAP[y][x] = ' '
                elif MAP[y][x] == 'x':
                    MAP[y][x] = ' '
        self.cvs_me_cung.bind("<Button-1>", self.xu_ly_mouse)
    def xu_ly_mouse(self, event):
        if self.dem == 0:
            px = event.x 
            py = event.y
            x = px//W
            y = py//W
            MAP[y][x] = 'o'
            self.cvs_me_cung.create_oval(x*W+2, y*W+2, (x+1)*W-2,(y+1)*W-2, outline = '#FF0000', fill = '#FF0000', width = 2)
            self.dem += 1
        elif self.dem == 1:
            px = event.x 
            py = event.y
            x = px//W
            y = py//W
            MAP[y][x] = 'x'
            self.cvs_me_cung.create_rectangle(x*W+2, y*W+2, (x+1)*W-2,(y+1)*W-2, outline = '#FF0000', fill = '#FF0000', width = 2)
            self.dem += 1

if __name__ == "__main__":
    app = App()
    app.mainloop()