# Each test name starts with the acceptance criterion it checks.

import random
import unittest

from Solitaire import (create_board, create_game, EnglishBoard, DiamondBoard,
                       HexagonBoard, ManualGame, AutomatedGame)

BOARD_TYPES = ("English", "Hexagon", "Diamond")


class TestBoardChoice(unittest.TestCase):
    """Story 1: choose a board size and type"""

    def test_ac_1_1_board_type(self):
        self.assertIsInstance(create_board("English", 7), EnglishBoard)
        self.assertIsInstance(create_board("Hexagon", 7), HexagonBoard)
        self.assertIsInstance(create_board("Diamond", 7), DiamondBoard)

    def test_ac_1_2_board_size(self):
        self.assertEqual(create_board("English", 9).size, 9)
        for size in (4, 8, 15, "7"):
            with self.assertRaises(ValueError):
                create_board("English", size)


class TestModeChoice(unittest.TestCase):
    """Story 2: choose the game mode"""

    def test_ac_2_1_manual_and_automated(self):
        self.assertIsInstance(create_game("Manual"), ManualGame)
        self.assertIsInstance(create_game("Automated"), AutomatedGame)

    def test_ac_2_2_default_is_manual(self):
        self.assertEqual(create_game("Manual").board_type, "English")
        self.assertEqual(create_game("Manual").size, 7)


class TestNewGame(unittest.TestCase):
    """Story 3: start a new game"""

    def test_ac_3_1_uses_chosen_type_size_mode(self):
        game = create_game("Automated", "Hexagon", 9)
        self.assertIsInstance(game.board, HexagonBoard)
        self.assertEqual(game.size, 9)
        self.assertEqual(game.mode, "Automated")

    def test_ac_3_2_center_empty_rest_full(self):
        for board_type in BOARD_TYPES:
            board = create_game("Manual", board_type, 7).board
            self.assertTrue(board.is_empty_hole(board.center))
            self.assertEqual(board.marble_count, len(board.cells) - 1)


class TestManualMove(unittest.TestCase):
    """Story 4: make a move in a manual game"""

    def test_ac_4_1_straight_move(self):
        game = create_game("Manual")
        self.assertTrue(game.make_move((3, 1), (3, 3)))
        self.assertTrue(game.board.is_empty_hole((3, 2)))  # jumped marble
        self.assertEqual(game.marble_count, 31)

    def test_ac_4_1_diagonal_move(self):
        game = create_game("Manual")
        game.board.set_marbles({(2, 2), (3, 3)})
        self.assertTrue(game.make_move((2, 2), (4, 4)))

    def test_ac_4_2_invalid_moves(self):
        game = create_game("Manual")
        before = set(game.board.marbles)
        for start, end in [((3, 3), (3, 5)),    # start hole is empty
                           ((3, 1), (3, 2)),    # only one step
                           ((1, 3), (3, 2)),    # not in a line
                           ((3, 5), (3, 7))]:   # off the board
            self.assertFalse(game.make_move(start, end))
        self.assertEqual(game.board.marbles, before)


class TestManualGameOver(unittest.TestCase):
    """Story 5: a manual game is over"""

    def test_ac_5_1_game_over_when_no_moves(self):
        game = create_game("Manual")
        self.assertFalse(game.is_game_over())
        game.board.set_marbles({(2, 2), (4, 4)})
        self.assertTrue(game.is_game_over())
        self.assertFalse(game.make_move((2, 2), (2, 4)))

    def test_ac_5_1_play_a_whole_game(self):
        for board_type in BOARD_TYPES:
            rng = random.Random(3)
            game = create_game("Manual", board_type, 7)
            while not game.is_game_over():
                start, end = rng.choice(game.board.valid_moves())
                game.make_move(start, end)
            self.assertEqual(game.board.valid_moves(), [])

    def test_ac_5_2_rating(self):
        game = create_game("Manual")
        spread = [(0, 2), (2, 0), (2, 6), (6, 2)]   # too far apart to jump
        for count, rating in [(1, "Outstanding"), (2, "Very Good"),
                              (3, "Good"), (4, "Average")]:
            game.board.set_marbles(spread[:count])
            self.assertEqual(game.rating(), rating)


class TestAutoMove(unittest.TestCase):
    """Story 6: make a move in an automated game"""

    def test_ac_6_1_computer_moves_are_valid_and_random(self):
        def play(seed):
            game = create_game("Automated", "English", 7, random.Random(seed))
            moves = []
            while not game.is_game_over():
                valid = game.board.valid_moves()
                move = game.auto_move()
                self.assertIn(move, valid)
                moves.append(move)
            return moves
        self.assertNotEqual(play(1), play(2))

    def test_ac_6_2_player_moves_not_accepted(self):
        game = create_game("Automated")
        self.assertFalse(game.make_move((3, 1), (3, 3)))
        self.assertEqual(game.marble_count, 32)


class TestAutoGameOver(unittest.TestCase):
    """Story 7: an automated game is over"""

    def test_ac_7_1_autoplay_stops_when_no_moves(self):
        for board_type in BOARD_TYPES:
            game = create_game("Automated", board_type, 7, random.Random(4))
            game.play_to_end()
            self.assertTrue(game.is_game_over())
            self.assertIsNone(game.auto_move())

    def test_ac_7_2_rating_after_game(self):
        game = create_game("Automated", "English", 7, random.Random(4))
        self.assertEqual(game.rating(), "")
        game.play_to_end()
        self.assertNotEqual(game.rating(), "")


class TestRandomize(unittest.TestCase):
    """Story 8: randomize the board in a manual game"""

    def test_ac_8_1_same_number_of_marbles(self):
        game = create_game("Manual", "English", 7, random.Random(1))
        game.make_move((3, 1), (3, 3))
        before = game.board.marbles
        self.assertTrue(game.randomize())
        self.assertEqual(game.marble_count, 31)
        self.assertNotEqual(game.board.marbles, before)

    def test_ac_8_2_not_in_automated_or_after_game_over(self):
        self.assertFalse(create_game("Automated").randomize())
        game = create_game("Manual")
        game.board.set_marbles({(2, 2), (4, 4)})
        self.assertFalse(game.randomize())

    def test_ac_8_x_manual_game_with_randomize_until_over(self):
        rng = random.Random(7)
        game = create_game("Manual", "English", 7, rng)
        for _ in range(200):                      # safety limit
            if game.is_game_over():
                break
            for _ in range(3):                    # a few moves, then shuffle
                if not game.is_game_over():
                    start, end = rng.choice(game.board.valid_moves())
                    game.make_move(start, end)
            game.randomize()
        self.assertTrue(game.is_game_over())


class TestExtra(unittest.TestCase):
    """Other tests"""

    def test_marble_outside_board(self):
        with self.assertRaises(ValueError):
            create_board("English", 7).set_marbles({(0, 0)})


if __name__ == "__main__":
    unittest.main()