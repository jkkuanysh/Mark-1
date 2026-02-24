def square(x):
    for i in range(1, x+1):
        yield i**2

n = square(int(input()))
for i in n:
    print (i, end = " ")



def evens(x):
    for i in range(0, x+1):
        if i % 2 == 0:
            yield i

n = evens(int(input()))
for i in n:
    print(i, end = ", ")



def div(x):
    for i in range(0, x+1):
        if i % 3 == 0 and i % 4 == 0:
            yield i

print(", ".join(map(str, div(int(input())))))



def squares(a, b):
    for i in range(a, b+1):
        yield i**2

a = int(input())
b = int(input())

for value in squares(a, b):
    print(value)



def func(x):
    for i in range(x, -1, -1):
        yield i

n = int(input())
for i in func(n):
    print(i)