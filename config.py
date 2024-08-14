from typing import Final

# Uses PostgreSQL date/time formatting patterns for 'to_char(timestamp, text)'
DATE_FORMAT : Final[str] = "DD.MM.YYYY klo HH24:MI"
