from pathlib import Path
from typing import Any, TypeAlias

import jinja2

from itml import utils


class Token(tuple):
    pass


def tokenize(s: str) -> list[Token]:
    tokenizer = _Tokenizer(s)
    return tokenizer.tokenize()


class _Tokenizer:

    def __init__(self, s: str) -> None:
        self._s = s

    def tokenize(self) -> list[Token]:
        lines: list[str] = self._s.splitlines()
        tokens: list[Token] = []
        for line in lines:
            tokens.extend(self._tokenize_line(line))

        return tokens

    def _tokenize_line(self, line: str) -> list[Token]:
        leading_space = utils.get_leading_space(line)
        if leading_space == 0 and len(line) == 0:
            # Empty line
            return [Token(("NEWLINE",))]
        elif line.strip().startswith("#"):
            # Comment
            return [Token(("COMMENT",))]
        elif line.startswith("import"):
            # Import statement
            path = line.removeprefix("import").strip()
            return [Token(("FUNCTION", "IMPORT", path))]
        elif leading_space == 0:
            # Identifier
            id, type = line.split(":", 2)
            return [Token(("NAME", id.strip(), type.strip()))]
        else:
            # String
            return [
                Token(("INDENT", leading_space)),
                Token(("STRING", line.strip())),
            ]


TextTemplates: TypeAlias = dict[str, str | list[str]]


def parse(s: str | Path, **kwargs) -> TextTemplates:
    parser = _Parser(s, **kwargs)
    return parser.parse()


class _Parser:

    def __init__(self, s: str | Path, **kwargs) -> None:
        self._index = 0
        if isinstance(s, Path) and s.is_file():
            content = s.read_text("utf-8")
            self._anchor: Path = s.parent
        else:
            content = s
            self._anchor = Path()

        self._anchor = kwargs.get("anchor", self._anchor)
        self._tokens: list[Token] = tokenize(content)

    def parse(self) -> TextTemplates:
        data: TextTemplates = {}
        while True:
            token = self._get_next_token()
            if token is None:  # Reached end of tokens
                break
            match token[0]:
                case "NAME":
                    id, type = token[1], token[2]
                    if type == "str":
                        data[id] = self._parse_str()
                    elif type == "list":
                        data[id] = self._parse_list()
                case "NEWLINE" | "COMMENT":
                    continue
                case "FUNCTION":
                    match token[1]:
                        case "IMPORT":
                            path: str = token[2]
                            data.update(self._import(path))

        return data

    def _get_next_token(self) -> Token | None:
        if 0 <= self._index < len(self._tokens):
            value = self._tokens[self._index]
        else:
            value = None

        self._index += 1
        return value

    def _decrease_index(self) -> None:
        self._index -= 1

    def _parse_str(self) -> str:
        strings: list[str] = []
        while True:
            token = self._get_next_token()
            if token is None:  # Reached end of tokens
                self._decrease_index()
                return self._join_str(strings)
            elif token[0] == "INDENT":
                continue
            elif token[0] == "STRING":
                strings.append(token[1])
            elif token[0] == "COMMENT":
                continue
            else:
                self._decrease_index()
                return self._join_str(strings)

    def _parse_list(self) -> list[str]:
        paragraphs: list[str] = []
        while True:
            token = self._get_next_token()
            if token is None or token[0] == "NAME":
                self._decrease_index()
                return paragraphs
            elif token[0] == "INDENT":
                self._decrease_index()
                string = self._parse_str()
                paragraphs.append(string)
            elif token[0] == "NEWLINE":
                continue
            elif token[0] == "COMMENT":
                continue

    def _join_str(self, strings: list[str]) -> str:
        return " ".join(strings)

    def _import(self, path: str) -> TextTemplates:
        path: Path = self._anchor.joinpath(path).resolve()
        parser = _Parser(path)
        data = parser.parse()
        return data


def compile(
    templates: TextTemplates,
    context: dict[str, Any] = dict(),
) -> TextTemplates:
    compiler = _Compiler(templates, context)
    return compiler.compile()


class _Compiler:

    def __init__(
        self,
        templates: TextTemplates,
        context: dict[str, Any] = dict(),
    ) -> None:
        self._templates = templates
        self._context = context

    def compile(self) -> TextTemplates:
        texts = {
            key: self._compile_templates(value)
            for key, value in self._templates.items()
        }
        return texts

    def _compile_templates(self, template: str | list[str]) -> str | list[str]:
        if type(template) == list:
            return [self._compile_str(s) for s in template]
        else:
            return self._compile_str(template)

    def _compile_str(self, s: str) -> str:
        text = jinja2.Template(s).render(self._context)
        return text
