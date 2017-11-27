# Profile
RE_EMAIL = "(\w+\.)*\w+@(\w+\.)+[A-Za-z]+"
RE_KOR_ID_NUMBER = "(\d{6}-?\d{7})"
RE_KOR_PHONE = "(0\d{1,3}-\d{3,4}-\d{4})"

# Network Address
RE_IP4 = "(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
RE_IP6 = ""

# HTML
RE_HTML_URL = "href='([^']*?)'"
RE_HTML_SCRIPT = "<\s*script*?>(.?)</\s*script\s*>"

# Miscellaneous
RE_LINE_COMMENT = "(//.*)"
RE_BLOCK_COMMENT = "(?:\/\*(?:[^*]|(?:\*+[^*\/]))*\*+\/)"
