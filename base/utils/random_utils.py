import random
import string

letters = string.ascii_letters + string.digits


def random_str(length: 16):
    return ''.join(random.choice(letters) for _ in range(length))


if __name__ == '__main__':
    print(random_str(128))