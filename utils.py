import re
import unicodedata

def is_printable(char : str):
    return not unicodedata.category(char).startswith(("Z", "C"))

def nonprintable_chars_to_whitespace(string : str):
    repl = "".join(char if is_printable(char) else " " for char in string)
    return re.sub(" +", " ", repl)
