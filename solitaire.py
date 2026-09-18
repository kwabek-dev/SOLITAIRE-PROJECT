class SolitaireBoard:
    def __init__(self, marbles=32):
        self.marbles = marbles

    def remove_marble(self):
        if self.marbles > 0:
            self.marbles -= 1

    def get_marble_count(self):
        return self.marbles