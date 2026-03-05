import string
import random
MINIMUM = 6

#TODO: добавить проверку что такого кода еще нет
def generate_short_code(length=MINIMUM):
    if length < MINIMUM: 
        raise ValueError(f"Length must be greater than {MINIMUM}")
    c = list(string.ascii_letters + string.digits)
    return ''.join(random.choices(c, k=length))