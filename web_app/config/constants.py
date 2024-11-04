import re

PASSWORD_REGEX = re.compile(
    r"^"
    r"(?=.*[a-zA-Zа-яА-Я])"
    r"(?=.*[a-zа-я])"
    r"(?=.*[A-ZА-Я])"
    r"(?=.*\d)"
    r"(?=.*[^\w\s@\"'<>\-])"
    r".{8,24}$"
)
