def is_even_last_digit(k):
    last_digit = str(k)[-1]
    return last_digit in ['0', '2', '4', '6', '8']
print(is_even_last_digit(12))

def minmax(data):
    min = data[0]
    max = data[0]
    for i in range(0,len(data)):
        if data[i]< min:
            min = data[i]
        elif data[i]>max:
            max = data[i]
    return (max,min)
print(minmax([1,-4,6,89,5]))
