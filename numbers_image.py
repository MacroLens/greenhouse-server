g = (0, 255, 0)
w = (255, 255, 255)
b = (0, 0, 0)

def combine_numbers(n1, n2):
    list_len = 4
    n1_split = [n1[i:i + list_len] for i in range(0, len(n1), list_len)] 
    n2_split = [n2[i:i + list_len] for i in range(0, len(n2), list_len)]
    ret = list(zip(n1_split, n2_split))
    ret = [item for sublist in ret for item in sublist]
    ret = [item for sublist in ret for item in sublist]
    return ret

numbers = [[
    b, w, b, b,
    w, w, b, b,
    b, w, b, b,
    b, w, b, b,
    b, w, b, b,
    b, w, b, b,
    b, w, b, b,
    w, w, w, b,
],

[
    b, w, w, b,
    w, b, b, w,
    b, b, b, w,
    b, b, w, b,
    b, w, b, b,
    w, b, b, b,
    w, b, b, b,
    w, w, w, w,  
],

[
    b, w, w, w,
    b, b, b, w,
    b, b, b, w,
    b, w, w, w,
    b, b, b, w,
    b, b, b, w,
    b, b, b, w,
    b, w, w, w,
],

[
    w, b, w, b,
    w, b, w, b,
    w, b, w, b,
    w, b, w, b,
    w, w, w, w,
    b, b, w, b,
    b, b, w, b,
    b, b, w, b,
],

[
    w, w, w, w,
    w, b, b, b,
    w, b, b, b,
    w, w, w, w,
    b, b, b, w,
    b, b, b, w,
    w, b, b, w,
    b, w, w, w,
],

[
    b, w, w, b,
    w, w, b, w,
    w, b, b, b,
    w, w, w, b,
    w, b, b, w,
    w, b, b, w,
    w, b, b, w,
    b, w, w, b,
],

[
    w, w, w, w,
    b, b, b, w,
    b, b, w, b,
    b, w, b, b,
    b, w, b, b,
    b, w, b, b,
    b, w, b, b,
    b, w, b, b,
],

[
    b, w, w, b,
    w, b, b, w,
    w, b, b, w,
    b, w, w, b,
    w, b, b, w,
    w, b, b, w,
    w, b, b, w,
    b, w, w, b,
],

[
    b, w, w, b,
    w, b, b, w,
    w, b, b, w,
    w, w, w, b,
    b, b, b, w,
    b, b, b, w,
    w, b, b, w,
    b, w, w, b,
]]

print(len(combine_numbers(numbers[0], numbers[2])))