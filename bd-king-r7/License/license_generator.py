import random
import string


def gen_block(length=4):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def generate_license():
    return f"BD-KING-R7-{gen_block()}-{gen_block()}-{gen_block()}"


print("Tamanna System License Code:")
print(generate_license())
