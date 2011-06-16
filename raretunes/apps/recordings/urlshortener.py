# Generate a [0-9a-zA-Z] string
ALPHABET = map(str,range(0, 10)) + map(chr, range(97, 123) + range(65, 91))

def encode_id(id_number, alphabet=ALPHABET):
    """Convert an integer to a string."""
    if id_number == 0:
        return alphabet[0]

    alphabet_len = len(alphabet) # Cache

    result = ''
    while id_number > 0:
        id_number, mod = divmod(id_number, alphabet_len)
        result = alphabet[mod] + result

    return result

def decode_id(id_string, alphabet=ALPHABET):
    """Convert a string to an integer."""
    alphabet_len = len(alphabet) # Cache
    return sum([alphabet.index(char) * pow(alphabet_len, power) for power, char in enumerate(reversed(id_string))])
