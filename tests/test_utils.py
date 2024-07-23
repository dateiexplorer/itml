import unittest

from itml.utils import get_leading_space


class TestUtils(unittest.TestCase):
    def test_get_leading_space(self):
        test_cases = {
            "    Hello, world!": 4,
            "    Hello, world!  ": 4,
            "\tHello, world!": 1,
            "\t Hello, world!": 2,
            "Hello, world!": 0,
            "\n": 1,
            "": 0,
        }
        for input, expected in test_cases.items():
            with self.subTest():
                actual = get_leading_space(input)
                self.assertEqual(actual, expected)
