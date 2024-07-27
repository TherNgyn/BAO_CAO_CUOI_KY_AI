import streamlit as st
import math
from search import *
from PIL import Image, ImageTk
import cv2
from matplotlib.animation import FuncAnimation
import numpy as np
import matplotlib.pyplot as plt
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
MAP = """
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
MAP = MAP.split("\n")

x_start = st.slider("x_start", 1, 28, 2)
y_start = st.slider("y_start", 2, 9, 2)
x_end = st.slider("x_end", 1, 28, 24)
y_end = st.slider("y_end", 2, 9, 7)

MAP[y_start] = MAP[y_start][:x_start] + "o" + MAP[y_start][x_start+1:]
MAP[y_end] = MAP[y_end][:x_end] + "x" + MAP[y_end][x_end+1:]
MAP = "\n".join(MAP)
MAP = [list(x) for x in MAP.split("\n") if x]
M = 10
N = 30
W = 21
mau_xanh = np.zeros((W, W, 3), np.uint8) + (np.uint8(0), np.uint8(0), np.uint8(255))
mau_trang = np.zeros((W, W, 3), np.uint8) + (np.uint8(255), np.uint8(255), np.uint8(255))
image = np.ones((M*W, N*W, 3), np.uint8)*255
st.title("Maze Solver")
for x in range (0, M):
    for y in range (0,N):
        if MAP[x][y] == "#":
            image[x*W:(x+1)*W, y*W:(y+1)*W] = mau_xanh
        elif MAP[x][y] == ' ':
            image[x*W:(x+1)*W, y*W:(y+1)*W] = mau_trang
        elif MAP[x][y].lower() == 'o':
            center_coordinates = (y*W + W//2, x*W + W//2)
            radius = W//2
            color = (255, 0, 0)  
            thickness = -1 
            image = cv2.circle(image, center_coordinates, radius, color, thickness)
        elif MAP[x][y].lower() == 'x':
            center_coordinates = (y*W + W//2, x*W + W//2)
            radius = W//2
            color = (0, 0, 255)  
            thickness = -1 
            image = cv2.rectangle(image, (y*W, x*W), (y*W + W, x*W + W), (255,0,0), -1)
pil_image = Image.fromarray(image)
st.image(pil_image)
def ve_mui_ten(b, a, tx, ty):
    p_mui_ten = [(0,0,1), (-20,10,1), (-15,0,1), (-20,-10,1)]
    p_mui_ten_ma_tran = [np.array([[0],[0],[1]],np.float32),
                            np.array([[-20],[10],[1]],np.float32),
                            np.array([[-15],[0],[1]],np.float32),
                            np.array([[-20],[-10],[1]],np.float32)]

    # Tạo ma trận dời (tịnh tiến) - translate
    M1 = np.array([[1, 0, tx], 
                    [0, 1, ty], 
                    [0, 0, 1]], np.float32)

    # Tạo ma trận quay - rotation
    theta = np.arctan2(b, a)
    M2 = np.array([[np.cos(theta), -np.sin(theta), 0],
                    [np.sin(theta),  np.cos(theta), 0],
                    [     0,             0,        1]], np.float32)

    M = np.matmul(M1, M2)

    q_mui_ten = []

    for p in p_mui_ten_ma_tran:
        q = np.matmul(M, p)
        q_mui_ten.append([q[0,0], q[1,0]])
    return q_mui_ten 
class MazeSolver(Problem):
    def __init__(self, board):
        self.board = board
        self.goal = (0, 0)
        for y in range(len(self.board)):
            for x in range(len(self.board[y])):
                if self.board[y][x].lower() == "o":
                    self.initial = (x, y)
                elif self.board[y][x].lower() == "x":
                    self.goal = (x, y)
    def actions(self, state):
        actions = []
        for action in COSTS.keys():
            newx, newy = self.result(state, action)
            if self.board[newy][newx] != "#":
                actions.append(action)
        return actions
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
    def is_goal(self, state):
        return state == self.goal
    def path_cost(self, c, state1, action, state2):
        return c + COSTS[action]
    def h(self, node):
        (x, y) = node.state
        (gx, gy) = self.goal
        return math.sqrt((x - gx) ** 2 + (y - gy) ** 2)
if st.button("Run"):
    problem = MazeSolver(MAP)
    result = astar_search(problem)
    path = [x.state for x in result.path()]
    for i in range(0, len(path) - 1):
        pt1 = (path[i][0]*W + W//2, path[i][1]*W + W//2)
        pt2 = (path[i+1][0]*W + W//2, path[i+1][1]*W + W//2)
        image = cv2.line(image, pt1, pt2, (255, 0, 0), 2) 
    pil_image = Image.fromarray(image)
    for y in range(len(MAP)):
        for x in range(len(MAP[y])):
            if (x, y) == problem.initial:
                print('o', end='')
            elif (x, y) == problem.goal:
                print('x', end='')
            elif (x, y) in path:
                print('.', end='')
            else:
                print(MAP[y][x], end='')
        print()
    fig, ax = plt.subplots()
    ax.imshow(image)
    L = len(path)
    lst_vi_tri = []
    for i in range(0, L - 1):
        x1, y1 = path[i]
        x2, y2 = path[i + 1]
        q = ve_mui_ten(y2-y1, x2-x1, x2*W+W//2, y2*W+W//2)
        lst_vi_tri.append(q)
    red_polygon, = ax.fill([],[], 'r')
    FRAME = len(lst_vi_tri)
    def init():
        ax.axis([0, N*W, M*W, 0])
        return red_polygon, 
    def animate(i):
        red_polygon.set_xy(lst_vi_tri[i])
        return red_polygon,
    anim = FuncAnimation(fig, animate, frames= FRAME, interval=50, init_func=init, repeat=False) 
    anim.save('animation.gif', writer='imagemagick')
    st.image('animation.gif')
    


    

    
