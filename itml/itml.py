class Token(tuple):
    pass


def get_leading_space(line: str) -> int:
    """Get leading whitespace of a string."""

    return len(line[: len(line) - len(line.lstrip())])


def tokenize(s: str) -> list[Token]:
    lines: list[str] = s.splitlines()
    tokens: list[Token] = []
    for line in lines:
        tokens.extend(_tokenize_line(line))

    return tokens


def _tokenize_line(line: str) -> list[Token]:
    leading_space = get_leading_space(line)
    if leading_space == 0 and len(line) == 0:
        # Empty line
        return [Token(("NEWLINE",))]
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


class Parser:
    def __init__(self, s: str):
        self._index = 0
        self._tokens: list[Token] = tokenize(s)
        self._data: dict[str, str] = {}

    def _get_next_token(self) -> Token | None:
        if 0 <= self._index < len(self._tokens):
            value = self._tokens[self._index]
        else:
            value = None

        self._index += 1
        return value

    def _decrease_index(self):
        self._index -= 1

    def parse(self) -> dict[str, str]:
        data: dict[str, str] = {}
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
                case "NEWLINE":
                    continue

        return data

    def _parse_str(self):
        strings: list[str] = []
        while True:
            token = self._get_next_token()
            if token is None:  # Reached end of tokens
                self._decrease_index()
                return " ".join(strings)
            elif token[0] == "INDENT":
                continue
            elif token[0] == "STRING":
                strings.append(token[1])
            else:
                self._decrease_index()
                return " ".join(strings)

    def _parse_list(self):
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
