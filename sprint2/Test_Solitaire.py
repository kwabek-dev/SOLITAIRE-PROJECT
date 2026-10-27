import random
import unittest
from Solitaire import (SolitaireGame, create_board, EnglishBoard,
                       DiamondBoard, HexagonBoard)

class TestChooseBoard(unittest.TestCase):

    def test_ac_1_1_board_type(self):
        self.assertIsInstance(create_board("English", 7), EnglishBoard)
        self.assertIsInstance(create_board("Hexagon", 7), HexagonBoard)
        self.assertIsInstance(create_board("Diamond", 7), DiamondBoard)

    def test_ac_1_1_unknown_type(self):
        with self.assertRaises(ValueError):
            create_board("Triangle", 7)

    def test_ac_1_2_board_size(self):
        for size in (5, 7, 9, 11, 13):
            self.assertEqual(create_board("English", size).size, size)

    def test_ac_1_3_bad_sizes(self):
        for size in (4, 6, 8, 15, -7, "7", 7.5):
            with self.assertRaises(ValueError):
                create_board("English", size)

    def test_ac_1_4_defaults(self):
        game = SolitaireGame()
        self.assertEqual(game.board_type, "English")
        self.assertEqual(game.size, 7)

class TestNewGame(unittest.TestCase):

    def test_ac_2_1_uses_chosen_type_and_size(self):
        game = SolitaireGame()
        game.new_game("Hexagon", 9)
        self.assertIsInstance(game.board, HexagonBoard)
        self.assertEqual(game.size, 9)

    def test_ac_2_1_bad_choice_keeps_old_game(self):
        game = SolitaireGame()
        game.make_move((3, 1), (3, 3))
        with self.assertRaises(ValueError):
            game.new_game("English", 8)
        self.assertEqual(game.board.marble_count, 31)

    def test_ac_2_2_center_empty_rest_full(self):
        for board_type in ("English", "Hexagon", "Diamond"):
            board = create_board(board_type, 7)
            self.assertTrue(board.is_empty_hole(board.center))
            self.assertEqual(board.marble_count, len(board.cells) - 1)

    def test_ac_2_2_number_of_holes(self):
        self.assertEqual(len(create_board("English", 7).cells), 33)
        self.assertEqual(len(create_board("Diamond", 7).cells), 25)
        self.assertEqual(len(create_board("Hexagon", 7).cells), 37)

    def test_ac_2_3_new_game_replaces_old_game(self):
        game = SolitaireGame()
        game.make_move((3, 1), (3, 3))
        game.new_game()
        self.assertEqual(game.moves_made, 0)
        self.assertEqual(game.board.marble_count, 32)

class TestMove(unittest.TestCase):

    def test_ac_3_1_straight_move(self):
        board = create_board("English", 7)
        self.assertTrue(board.make_move((3, 1), (3, 3)))
        self.assertTrue(board.has_marble((3, 3)))
        
    def test_ac_3_1_diagonal_move(self):
        board = create_board("English", 7)
        board.set_marbles({(2, 2), (3, 3)})
        self.assertTrue(board.make_move((2, 2), (4, 4)))
        
    def test_ac_3_1_hexagon_move(self):
        board = create_board("Hexagon", 7)
        self.assertTrue(board.make_move((2, -2), (0, 0)))

    def test_ac_3_2_jumped_marble_removed(self):
        board = create_board("English", 7)
        board.make_move((3, 1), (3, 3))
        self.assertTrue(board.is_empty_hole((3, 2)))
        self.assertEqual(board.marble_count, 31)

    def test_ac_3_3_invalid_moves(self):
        board = create_board("English", 7)
        board.make_move((3, 1), (3, 3))
        before = set(board.marbles)
        bad_moves =[((3, 5), (3, 3)),   # hole is not empty
                    ((3, 2), (3, 4)),   # nothing to move
                    ((3, 0), (3, 2)),   # nothing to jump over
                    ((3, 0), (3, 1)),   # only one step
                    ((1, 3), (3, 2)),   # not in a line
                    ((3, 5), (3, 7))]   # off the board
        for start, end in bad_moves:
            self.assertFalse(board.make_move(start, end))
            self.assertEqual(board.marbles, before)

    def test_ac_3_3_game_counts_only_good_moves(self):
        game = SolitaireGame()
        self.assertFalse(game.make_move((3, 2), (3, 4)))
        self.assertTrue(game.make_move((3, 1), (3, 3)))
        self.assertEqual(game.moves_made, 1)

    def test_ac_3_4_moves_from(self):
        board = create_board("English", 7)
        self.assertEqual(board.moves_from((3, 1)), [(3, 3)])
        self.assertEqual(board.moves_from((0, 2)), [])

class TestGameOver(unittest.TestCase):

    def test_ac_4_1_game_can_continue(self):
        for board_type in ("English", "Hexagon", "Diamond"):
            game = SolitaireGame(board_type, 7)
            self.assertFalse(game.is_game_over())

    def test_ac_4_2_game_over_no_moves(self):
        game = SolitaireGame()
        game.board.set_marbles({(2, 2), (4, 4)})
        self.assertTrue(game.is_game_over())
        self.assertFalse(game.is_won())
    
    def test_ac_4_2_no_moves_after_game_over(self):
        game = SolitaireGame()
        game.board.set_marbles({(2, 2), (4, 4)})
        self.assertFalse(game.make_move((2, 2), (2, 4)))

    def test_ac_4_3_one_marble_is_a_win(self):
        game = SolitaireGame()
        game.board.set_marbles({(3, 3)})
        self.assertTrue(game.is_won())

    def test_ac_4_3_random_play_ends(self):
        for board_type in ("English", "Hexagon", "Diamond"):
            rng = random.Random(1)
            game = SolitaireGame(board_type, 7)
            while not game.is_game_over():
                start, end = rng.choice(game.board.valid_moves())
                game.make_move(start, end)
            self.assertEqual(game.board.valid_moves(), [])

class TestExtra(unittest.TestCase):

    def test_marble_outside_board(self):
        board = create_board("English", 7)
        with self.assertRaises(ValueError):
            board.set_marbles({(0, 0)})

    def test_reset(self):
        board = create_board("Hexagon", 7)
        board.make_move((2, 9), (0, 0))
        board.reset()
        self.assertEqual(board.marble_count, 36)

if __name__ == "__main__":
    unittest.main()


    



        


    
        
        


