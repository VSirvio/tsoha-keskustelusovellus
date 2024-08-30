# Uses PostgreSQL date/time formatting patterns for 'to_char(timestamp, text)'
DATE_FORMAT = "DD.MM.YYYY klo HH24:MI"

# Possible values are "newest", "oldest", "most_liked", and "most_disliked"
DEFAULT_ORDER = "newest"

ALLOWED_USERNAME_PATTERN = "[a-zåäöA-ZÅÄÖ0-9_]*"

LOGIN_REQUIRED_MSG = "Toiminto vaatii kirjautumisen"

ADMIN_USER_REQUIRED_MSG = "Kyseinen toiminto on sallittu vain ylläpitäjille"
