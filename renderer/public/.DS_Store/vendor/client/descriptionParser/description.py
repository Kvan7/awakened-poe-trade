import os
from pprint import pprint

from services.statNameBuilder import convert_stat_name


class Description:
    english_ref = None

    def __init__(self, lines: list[str]):
        self.lines = lines
        if not lines[0].startswith("description"):
            raise ValueError("Invalid description block")
        self.id = self.parse_id(lines)

        # self.english_ref = self.get_ref(lines)

        self.data = self.parse_lines(self.lines, self.id)

    def parse_id(self, lines: list[str]) -> str:
        assert lines[0].startswith("description")
        line = lines[1].strip()
        return line.strip()[2:].replace('"', "")

    def parse_lines(self, lines: list[str], id: str) -> dict:
        assert lines[0].startswith("description")
        sanitized_lines = self.sanitize_lines(lines)

        blocks = self.parse_blocks(sanitized_lines)
        lang_blocks = [self.simplify_block(block) for block in blocks]
        lang_dict = {
            lang: self.get_matchers(mod_lines, lang == "English")
            for lang, mod_lines in lang_blocks
        }

        return lang_dict

    def sanitize_lines(self, lines: list[str]) -> list[str]:
        return [line.strip() for line in lines[1:]]

    def parse_blocks(self, lines: list[str]) -> list[list[str]]:
        blocks = [[]]

        for i in range(len(lines)):
            if lines[i].startswith("lang"):
                blocks.append([])
            blocks[-1].append(lines[i])

        return blocks

    def simplify_block(self, block: list[str]) -> tuple[str, list[str]]:
        lang = self.extract_lang(block[0])
        lines = block[2:]
        # TODO: Parse for more complex line sets
        pos_line = lines[0].strip()
        out_lines = [pos_line[pos_line.find('"') + 1 : pos_line.rfind('"')]]

        if len(lines) > 1:
            neg_line = lines[1].strip()
            if "lang" not in neg_line and "negate" in neg_line:
                # mod has a negated version
                end = neg_line.find("negate")
                neg_line = neg_line[neg_line.find('"') + 1 : end + len("negate")]
                out_lines.append(neg_line)

        return lang, out_lines

    def extract_lang(self, line: str) -> str:
        line = line.strip()
        if not line.startswith("lang"):
            return "English"
        return line[line.find('"') + 1 : line.rfind('"')]

    def get_matchers(
        self, lines: list[str], is_en: bool
    ) -> list[dict[str, str | bool]]:
        matchers = []
        for line in lines:
            stat_name = convert_stat_name(line)
            if stat_name is None:
                continue
            matcher = stat_name
            # remove prefixes
            if matcher[0] == "+":
                matcher = matcher[1:]
            has_negate = matcher.find("negate") > 0
            if has_negate:
                matcher = matcher[: matcher.find('"')].strip()
            matchers.append({"string": matcher, "negate": has_negate})
            if is_en and self.english_ref is None:
                self.english_ref = stat_name
        return matchers


if __name__ == "__main__":
    # Test functionality
    with open(
        f"{os.path.dirname(os.path.realpath(__file__))}/singleDesc.csd",
        "r",
        encoding="utf-8",
    ) as f:
        lines = f.readlines()
    print(lines)
    desc = Description(lines)

    print(desc.english)
