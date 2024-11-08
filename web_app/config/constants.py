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
MIN_QUIZ_QUESTION_COUNT = 2
MIN_QUESTION_ANSWER_COUNT = 2
