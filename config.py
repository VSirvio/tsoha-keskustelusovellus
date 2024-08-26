# Uses PostgreSQL date/time formatting patterns for 'to_char(timestamp, text)'
DATE_FORMAT = "DD.MM.YYYY klo HH24:MI"

# Possible values are "newest", "oldest", "most_liked", and "most_disliked"
DEFAULT_ORDER = "newest"

INVALID_USERNAME_MSG = "Tunnus ei saa sisältää muita merkkejä kuin isot ja " \
                       "pienet kirjaimet A:sta Ö:hön, numerot (0-9) " \
                       "ja alaviiva (_)"
USERNAME_ALLOWED_CHARS = "abcdefghijklmnopqrstuvwxyzåäö" \
                         "ABCDEFGHIJKLMNOPQRSTUVWXYZÅÄÖ" \
                         "0123456789_"
