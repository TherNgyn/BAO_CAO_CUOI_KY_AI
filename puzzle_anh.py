import tkinter as tk
from PIL import Image, ImageTk
import cv2
import numpy as np
import os.path
import random
import time
from functools import partial
from tkinter import *
from tkinter import ttk
import tkinter as tk
from PIL import Image, ImageTk

from search import astar_search, EightPuzzle
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
state = [1, 2, 3, 4, 5, 6, 7, 8, 0]
puzzle = EightPuzzle(tuple(state))
solution = None

b = [None] * 9
image = cv2.imread('stray-2.jpg')

image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
pil_image = Image.fromarray(image)

piece_width = pil_image.width // 3
piece_height = pil_image.height // 3

pieces = []
state_pieces = {}
white = Image.new('RGB', (piece_width, piece_height), (255, 255, 255))
piece_number = 0

for j in range(3):
    for i in range(3):
        left = i * piece_width
        upper = j * piece_height
        right = left + piece_width
        lower = upper + piece_height
        if i==2 and j==2:
            break
        piece = pil_image.crop((left, upper, right, lower))
        pieces.append(piece)
        state_pieces[piece_number] = piece
        piece_number += 1

pieces.append(white)
pieces = pieces[1:] + [pieces[0]]
root = tk.Tk()

root.title('8 Puzzle')

def scramble():
    global state
    global state_pieces
    global pieces
    global puzzle
    possible_actions = ['UP', 'DOWN', 'LEFT', 'RIGHT']
    scramble = []
    for _ in range(60):
        scramble.append(random.choice(possible_actions))
    for move in scramble:
        if move in puzzle.actions(state):
            state = list(puzzle.result(state, move))
            puzzle = EightPuzzle(tuple(state))
            state_pieces = {state[i]: pieces[i] for i in range(9)}
            create_buttons()
    print(state)
    for i, piece in state_pieces.items():
        print(i, piece)
def solve():
    return astar_search(puzzle).solution()
def solve_steps():
    global puzzle
    global solution
    global state
    global state_pieces
    global pieces
    solution = solve()
    print(solution)
    for move in solution:
        state = list(puzzle.result(state, move))
        puzzle = EightPuzzle(tuple(state))
        state_pieces = {state[i]: pieces[i] for i in range(9)}
        create_buttons()
        root.update()
        root.after(0, time.sleep(0.75))

def exchange(index):
    global state
    global solution
    global puzzle
    global state_pieces
    global pieces
    zero_ix = list(state).index(0)
    actions= puzzle.actions(state)
    current_action = ''

    i_diff = index // 3 - zero_ix // 3
    j_diff = index % 3 - zero_ix % 3
    if i_diff == 1:
        current_action += 'DOWN'
    elif i_diff == -1:
        current_action += 'UP'
    if j_diff == 1:
        current_action += 'RIGHT'
    elif j_diff == -1:
        current_action += 'LEFT'
    if abs(i_diff) + abs(j_diff) != 1:
        current_action = ''
    if current_action in actions:
        b[zero_ix].grid_forget()
        b[zero_ix] = tk.Button(root, image=state_pieces[index], width=150, command=partial(exchange, zero_ix))
        state_pieces[zero_ix], state_pieces[index] = state_pieces[index], state_pieces[zero_ix]
        puzzle = EightPuzzle(tuple(state_pieces.keys()))
        
    
def create_buttons():
    new_size = (150, 150)
    for i, piece in state_pieces.items():
        h = piece.thumbnail(new_size)
        tk_piece = ImageTk.PhotoImage(piece)
        b[i] = tk.Button(root, image=tk_piece, width= h, command=partial(exchange, i))
        b[i].grid(row=i // 3, column=i % 3)
        b[i].image = tk_piece
    

def create_static_buttons():
    scramble_btn = ttk.Button(root, text='Scramble', width=8, command=partial(scramble))
    scramble_btn.grid(row=3, column=0, ipady=10, sticky=tk.EW)
    run_btn = ttk.Button(root, text='Run', width=8, command=partial(solve_steps))
    run_btn.grid(row=3, column=2, ipady=10, sticky=tk.EW)

def init():
    global state
    global solution
    global puzzle
    global pieces
    global state_pieces
    state = [1, 2, 3, 4, 5, 6, 7, 8, 0]
    scramble()
    create_buttons()
    create_static_buttons()
init()
root.mainloop()
