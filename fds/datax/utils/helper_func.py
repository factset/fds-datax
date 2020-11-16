import re


def __valid_cache_name__(cache_name):
    """
    This function is used to ensure the cache name meets the standard of NO spaces or special characters.
    """
    if len(re.findall(r"[^a-zA-Z0-9_-]", cache_name)) == 0:
        pass
    else:
        print("Cache Name cannot contain spaces or special characters. Try again.")
        raise IpyExit


def __chunker__(seq, size):
    """
    Breaks up the sequence based on a size limit.
    """
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))


def __insert_values__(list_of_ids):
    """
    This function is used to dynamically created insert statements
    into a SQL temp table.  The make length of 1000 per line is handled
    through this function as well as __chunker__ and
    """
    insert_string = ""
    for group in __chunker__(list_of_ids, 999):
        insert_string += "INSERT #listofIDS (id) VALUES {};\n".format(
            "('" + "'),('".join(i for i in group) + "')"
        )
    return insert_string
