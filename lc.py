def isAnagram(s, t):
    """
    :type s: str
    :type t: str
    :rtype: bool
    """
    s_table = {}
    t_table = {}
    for char in s:
        s_table[char] = True
    for char in t:
        t_table[char] = True

    temp = s_table.copy()
    # print(s_table)
    # print(t_table)
    for char in temp.keys():
        print("char " + char)
        if char in s_table and char in t_table:
            del s_table[char]
            del t_table[char]
            print(s_table)
            print(t_table)
        else:
            return False
    if len(t_table) or len(s_table):
        return False
    else:
        return True
    


print(isAnagram("anagram", "nagaram"))