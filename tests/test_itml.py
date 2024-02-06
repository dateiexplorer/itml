from pathlib import Path
import unittest
from itml.itml import Token, get_leading_space, _tokenize_line, tokenize


class TestITMLTokenizing(unittest.TestCase):
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

    def test_tokenize_line_as_newline(self):
        input = ""
        actual = _tokenize_line(input)
        self.assertEqual(len(actual), 1)
        self.assertEqual(actual, [Token(("NEWLINE",))])

    def test_tokenize_line_as_name(self):
        input = "identifier: type"
        actual = _tokenize_line(input)
        self.assertEqual(len(actual), 1)
        self.assertEqual(actual, [Token(("NAME", "identifier", "type"))])

    def test_tokenize_line_as_string(self):
        input = "    Hello, world!"
        actual = _tokenize_line(input)
        self.assertEqual(len(actual), 2)
        self.assertEqual(actual[0], Token(("INDENT", 4)))
        self.assertEqual(actual[1], Token(("STRING", "Hello, world!")))

    def test_tokenize(self):
        with open(
            Path(__file__).parent.resolve().joinpath("files", "test.itml")
        ) as file:
            input = file.read()

        actual = tokenize(input)
        self.assertEqual(len(actual), 9)
        self.assertEqual(actual[0], Token(("NAME", "id1", "str")))
        self.assertEqual(actual[1], Token(("INDENT", 4)))
        self.assertEqual(actual[2], Token(("STRING", "Hello, world!")))
        self.assertEqual(actual[3], Token(("NEWLINE",)))
        self.assertEqual(actual[4], Token(("NAME", "id2", "str")))
        self.assertEqual(actual[5], Token(("INDENT", 4)))
        self.assertEqual(actual[6], Token(("STRING", "Hello,")))
        self.assertEqual(actual[7], Token(("INDENT", 4)))
        self.assertEqual(actual[8], Token(("STRING", "world!")))


if __name__ == "__main__":
    unittest.main()
