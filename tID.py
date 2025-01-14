import random
import string

def generate_id_digits(i=None,l=None):
    if l is None:
        if i is None:
            l = 3
        else:
            l = 2
            max = 240*240
            while i>max:
                l += 1
                max *= 240

    n=[24,10]*l

    if isinstance(i,int):
        digits = []
        for j in range(len(n)):
            digits = digits + [i % n[-j]]  
            i = i // n[-j]          
    else:
        digits = [random.randint(0, _ -1 ) for _ in n] 
    checksum = sum((digits[_]+1)*(_+1) for _ in range(len(n))) % 24
    digits.append(checksum)
    return digits

def n_to_tID(i=None,l=None):
    return digits_to_string(generate_id_digits(i,l))

def digits_to_string(id):
    res = "" 
    for i in range(len(id)):
        if i % 2 == 0:
            res += "ABCDEFGHJKLMNPQRSTUVWXYZ"[id[i]]
        else:
            res += string.digits[id[i]]
    return res

def str_to_digits(s):
    s = s.upper().replace("O",'0').replace('I','1')
    res = []
    for i in range(len(s)):
        if i % 2 == 0:
            res.append("ABCDEFGHJKLMNPQRSTUVWXYZ".index(s[i]))
        else:
            res.append(int(s[i]))
    return res

def is_valid_tID(s):
    if len(s) != 7 and len(s) != 5:
        return False
    try:
        id = str_to_digits(s)
    except ValueError:
        return False 
    checksum = sum((id[_]+1)*(_+1) for _ in range(len(s)-1)) % 24 
    return checksum == id[-1]

def main():
    for _ in range(1,20):
        id = generate_id_digits()
        id_str = digits_to_string(id)
        id_test= str_to_digits(id_str)
        print(id_str, id,id_test == id, is_valid_tID(id_str))


    for _ in range(0,20):
        id = generate_id_digits(_)
        id_str = digits_to_string(id)
        id_test= str_to_digits(id_str)
        print(id_str, id,id_test == id, is_valid_tID(id_str))

if __name__ == "__main__":
    main()
