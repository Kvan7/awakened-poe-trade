import re


def convert_stat_name(stat: str) -> str:
    stat = stat.strip()
    open_square_bracket = stat.find("[")
    close_square_bracket = stat.find("]")

    while open_square_bracket >= 0 and close_square_bracket > 0:
        # resolve brackets, this can be either the plain text or a key|value pair
        key = stat[open_square_bracket + 1 : close_square_bracket]

        if "|" in key:  # key|value pair
            key = key.split("|")[1]  # use value
        stat = stat[:open_square_bracket] + key + stat[close_square_bracket + 1 :]

        open_square_bracket = stat.find("[")
        close_square_bracket = stat.find("]")

    pattern = re.compile(r"{\d+}")
    for match in pattern.findall(stat):
        stat = stat.replace(match, "#")

    stat = stat.replace("{0:+d}", "+#")

    if len(stat) == 0:
        return None

    if stat[0] == "{" and stat[1] == "}":
        stat = "#" + stat[2:]

    return stat
