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