from typing import Final, Literal

# Uses PostgreSQL date/time formatting patterns for 'to_char(timestamp, text)'
DATE_FORMAT : Final[str] = "DD.MM.YYYY klo HH24:MI"

type OrderBy = Literal["newest", "oldest", "most_liked", "most_disliked"]
DEFAULT_ORDER : Final[OrderBy] = "newest"
