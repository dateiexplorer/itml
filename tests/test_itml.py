import unittest
from pathlib import Path

from itml.itml import Token, _Parser, _Tokenizer, parse, tokenize


class TestTokenizer(unittest.TestCase):

    def test_tokenize_line_as_newline(self):
        input = ""
        actual = _Tokenizer(None)._tokenize_line(input)
        self.assertEqual(len(actual), 1)
        self.assertEqual(actual, [Token(("NEWLINE",))])

    def test_tokenize_line_as_name(self):
        input = "identifier: type"
        actual = _Tokenizer(None)._tokenize_line(input)
        self.assertEqual(len(actual), 1)
        self.assertEqual(actual, [Token(("NAME", "identifier", "type"))])

    def test_tokenize_line_as_string(self):
        input = "    Hello, world!"
        actual = _Tokenizer(None)._tokenize_line(input)
        self.assertEqual(len(actual), 2)
        self.assertEqual(actual[0], Token(("INDENT", 4)))
        self.assertEqual(actual[1], Token(("STRING", "Hello, world!")))

    def test_tokenize_line_as_comments(self):
        input = "# This is a comment"
        actual = _Tokenizer(None)._tokenize_line(input)
        self.assertEqual(len(actual), 1)
        self.assertEqual(actual, [Token(("COMMENT",))])

    def test_tokenize(self):
        with open(
            Path(__file__).parent.resolve().joinpath("files", "sample01.itml")
        ) as file:
            input = file.read()

        actual = tokenize(input)
        self.assertEqual(len(actual), 11)
        self.assertEqual(actual[0], Token(("NAME", "id1", "str")))
        self.assertEqual(actual[1], Token(("INDENT", 4)))
        self.assertEqual(actual[2], Token(("STRING", "Hello, world!")))
        self.assertEqual(actual[3], Token(("NEWLINE",)))
        self.assertEqual(actual[4], Token(("COMMENT",)))
        self.assertEqual(actual[5], Token(("NAME", "id2", "str")))
        self.assertEqual(actual[6], Token(("INDENT", 4)))
        self.assertEqual(actual[7], Token(("STRING", "Hello,")))
        self.assertEqual(actual[8], Token(("COMMENT",)))
        self.assertEqual(actual[9], Token(("INDENT", 4)))
        self.assertEqual(actual[10], Token(("STRING", "world!")))


class TestParser(unittest.TestCase):

    def test_init(self):
        path = Path(__file__).parent.joinpath("files", "sample01.itml")
        parser = _Parser(path)
        self.assertEqual(parser._anchor, path.parent)

    def test_parse(self):
        path = Path(__file__).parent.joinpath("files", "sample01.itml")
        actual = parse(path)
        self.assertDictEqual(
            actual,
            {
                "id1": "Hello, world!",
                "id2": "Hello, world!",
            },
        )

    def test_import(self):
        data = parse(
            "import sample02.itml",
            anchor=Path(__file__).parent.joinpath("files"),
        )

        self.assertDictEqual({"id1": "Hello, world!"}, data)

    def test_import_with_content(self):
        path = Path(__file__).parent.joinpath("files", "sample03.itml")
        data = parse(path)

        self.assertDictEqual(
            {
                "id1": "Hello, world!",
                "id2": "New identifier",
            },
            data,
        )
