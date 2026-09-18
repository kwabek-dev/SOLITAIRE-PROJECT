import tkinter as tk

def start_game():
    status_label.config(text="New game started!")

window = tk.Tk()
window.title("Solitaire")
window.geometry("500x400")

# Text
title_label = tk.Label(
    window,
    text="Peg Solitaire",
    font=("Arial", 20)
)
title_label.pack(pady=10)

instruction_label = tk.Label(
    window,
    text="Choose a board type and start a new game."
)
instruction_label.pack()

# Radio buttons
board_type = tk.StringVar(value="English")

english_button = tk.Radiobutton(
    window,
    text="English",
    variable=board_type,
    value="English"
)
english_button.pack()

diamond_button = tk.Radiobutton(
    window,
    text="Diamond",
    variable=board_type,
    value="Diamond"
)
diamond_button.pack()

hexagon_button = tk.Radiobutton(
    window,
    text="Hexagon",
    variable=board_type,
    value="Hexagon"
)
hexagon_button.pack()

# Check box
record_game = tk.BooleanVar()

record_checkbox = tk.Checkbutton(
    window,
    text="Record game",
    variable=record_game
)
record_checkbox.pack(pady=10)

# Line
line = tk.Frame(window, height=2, bg="black")
line.pack(fill="x", padx=40, pady=10)

# Button
new_game_button = tk.Button(
    window,
    text="New Game",
    command=start_game
)
new_game_button.pack(pady=10)

# Status text
status_label = tk.Label(
    window,
    text="Ready to play."
)
status_label.pack(pady=10)

window.mainloop()