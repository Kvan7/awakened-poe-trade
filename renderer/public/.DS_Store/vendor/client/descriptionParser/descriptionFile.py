from pprint import pprint

from descriptionParser.description import Description


class DescriptionFile:
    def __init__(self, filePath):
        self.filePath = filePath
        self.fileLines = self.load(self.filePath)
        self.blocks = self.split_into_description_blocks(self.fileLines)
        pprint(self.blocks)
        self.descriptions = [Description(block) for block in self.blocks]
        self.descriptions_lookup = {d.id: d for d in self.descriptions}

    def load(self, filePath: str) -> list[str]:
        with open(filePath, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return lines

    def split_into_description_blocks(self, lines: list[str]) -> list[list[str]]:
        blocks = [[]]

        for i in range(len(lines)):
            if lines[i].startswith("description"):
                if blocks[-1][-1] == "":
                    # remove last empty line
                    blocks[-1].pop()
                blocks.append([])
            blocks[-1].append(lines[i])

        return blocks
