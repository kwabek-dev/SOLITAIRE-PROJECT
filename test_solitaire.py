import unittest
from solitaire import SolitaireBoard


class TestSolitaireBoard(unittest.TestCase):

    def test_initial_marble_count(self):
        board = SolitaireBoard()
        self.assertEqual(board.get_marble_count(), 32)

    def test_remove_marble(self):
        board = SolitaireBoard()
        board.remove_marble()
        self.assertEqual(board.get_marble_count(), 31)


if __name__ == "__main__":
    unittest.main()