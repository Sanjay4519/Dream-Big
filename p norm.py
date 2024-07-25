import math
import random

def pth_root(radiant,p):
    return radiant ** (1/p)
def norm(vector, p):
    radiant = 0
    for dim in vector:
        radiant += dim ** p
    return(pth_root(radiant,p))

vector = [2,2]
p=2
print(norm(vector,p))

def throw_dart():
    n1 = random.uniform(-1, 1)
    n2 = random.uniform(-1 ,1)
    return (n1,n2)
def approxpi(n):
    darts_inside_circle = []
    for i in range(0,n):
        dart = throw_dart()
        if norm(dart,2) <= 1:
            darts_inside_circle.append(dart)
    ratio = len(darts_inside_circle) / n
    return ratio * 4

print(approxpi(5))


