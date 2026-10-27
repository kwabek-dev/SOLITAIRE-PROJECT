import tkinter as tk
from Solitaire import (BOARD_TYPES, DEFAULT_SIZE, DEFAULT_TYPE,
                       MAX_SIZE, MIN_SIZE, SolitaireGame)

CANVAS_SIZE = 520
MARGIN = 40

class SolitaireGUI:

    def __init__(self, root):
        self.root = root
        self.game = SolitaireGame()
        self.selected = None
        self.positions = {}
        self.radius = 10

        root.title("Solitaire")
        self.build_controls()
        self.canvas = tk.Canvas(root, width=CANVAS_SIZE, height=CANVAS_SIZE,
                                bg="white")
        self.status = tk.Label(root, text="Welcome to Solitaire")
        self.canvas.pack(padx=10)
        self.canvas.bind("<Button-1>", self.on_click)
        self.status = tk.Label(root, text="", font=("Arial", 12))
        self.status.pack(pady=10)

        self.draw_board()
        self.status.config(text="Ready to play. Click a marble, then a hole.")

    def build_controls(self):
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10, fill="x")

        tk.Label(frame, text="Board size").grid(row=1, column=0, sticky="w")
        self.size_var = tk.StringVar(value=str(DEFAULT_SIZE))
        tk.Spinbox(frame, from_=MIN_SIZE, to=MAX_SIZE, increment=2,
                   textvariable=self.size_var, width=5).grid(row=0, column=1)
        
        tk.Label(frame, text="Board Type").grid(row=1, column=0, sticky="w")
        self.type_var = tk.StringVar(value=DEFAULT_TYPE)
        column = 1
        for name in BOARD_TYPES:
            tk.Radiobutton(frame, text=name, variable=self.type_var,
                           value=name).grid(row=1, column=column)
            column += 1

        tk.Button(frame, text="New Game",
                  command=self.on_new_game).grid(row=0, column=3, padx=10)
        
    def find_positions(self):
        board = self.game.board
        points = {pos: board.lattice_xy(pos) for pos in board.cells}
        xs = [p[0] for p in points.values()]
        ys = [p[1] for p in points.values()]
        width = max(xs) - min(xs)
        height = max(ys) - min(ys)
        scale = (CANVAS_SIZE - 2 * MARGIN) / max(width, height, 1)
        left = (CANVAS_SIZE - width * scale) / 2
        top = (CANVAS_SIZE - height * scale) / 2
        self.radius = scale * 0.4
        self.positions = {}
        for pos, (x, y) in points.items():
            self.positions[pos] = (left + (x - min(xs)) * scale,
                                   top + (y - min(ys)) * scale)
            
    def draw_board(self):
        board = self.game.board
        self.find_positions()
        self.canvas.delete("all")
        targets = []
        if self.selected is not None:
            targets = board.moves_from(self.selected)
        r = self.radius
        for pos, (x, y) in self.positions.items():
            outline = "green" if pos in targets else "gray"
            width = 3 if pos in targets else 1
            self.canvas.create_oval(x - r, y - r, x + r, y + r,
                                    fill="#d9d9d9", outline=outline,
                                    width=width)
            if board.has_marble(pos):
                color = "orange" if pos == self.selected else "blue"
                m = r * 0.8
                self.canvas.create_oval(x - m, y - m, x + m, y + m,
                                        fill=color, outline="black")
                
    def on_new_game(self):
        try:
            size = int(self.size_var.get())
            self.game.new_game(self.type_var.get(), size)
        except ValueError:
            self.status.config(
                text="Invalid size. Enter an odd number from %d to %d."
                % (MIN_SIZE, MAX_SIZE), fg="red")
            return
        self.selected = None
        self.draw_board()
        self.status.config(
            text="New %s game, size %d. Marbles: %d"
            % (self.game.board_type, self.game.size,
               self.game.board.marble_count), fg="black")
        
    def hole_at(self, x, y):
        for pos, (px, py) in self.positions.items():
            if (x - px) ** 2 + (y - py) ** 2 <= self.radius ** 2:
                return pos
        return None
    
    def on_click(self, event):
        if self.game.is_game_over():
            return
        board = self.game.board
        pos = self.hole_at(event.x, event.y)

        if pos is None:
            self.selected = None
        elif self.selected is None:
            if board.has_marble(pos):
                self.selected = pos
        elif pos == self.selected:
            self.selected = None
        elif self.game.make_move(self.selected, pos):
            self.selected = None
        elif board.has_marble(pos):
            self.selected = pos
        else:
            self.selected = None
            self.draw_board()
            self.status.config(
                text="Invalid move. Jump over a marble into an empty hole.",
                fg="red")
            return
        
        self.draw_board()
        self.update_status()

    def update_status(self):
        count = self.game.board.marble_count
        if self.game.is_won():
            self.status.config(text="Game over - you won! One marble left.",
                               fg="green")
        elif self.game.is_game_over():
            self.status.config(
                text="Game over - no more moves. %d marbles left." % count,
                fg="red")
        else:
            self.status.config(text="Marbles: %d" % count, fg="black")

if __name__ == "__main__":
    root = tk.Tk()
    app = SolitaireGUI(root)
    root.mainloop()
