def bad_strings():
    return [
        "%s",
        "%x",
        "{'why is a': 'json here?'}",
        "<h1>",
        "A"*(2**10+100), # overflow
    ]

def bad_integers():
    return [
        -1,
        -2**8+1,
        2**8+1
        -2**16+1,
        2**16+1,
        2**32+1,
        -2**32-1,
        2**64+1,
        -2**64-1,

    ]

def magic_numbers():
    return [
    #   (byte_size, byte)
        (1, 255),
        (1, 127),
        (1, 0),
        (2, 255),
        (2, 0),
        (4, 255),
        (4, 0),
        (4, 127),
        (4, 128),
        (4, 64)
    ]