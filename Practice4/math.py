import math

degree = float(input("Input degree: "))
radian = degree * 3.142 / 180
print("Output radian:", round(radian, 6))


#area of a trapezoid
h = float(input())
b1 = float(input())
b2 = float(input())
area = ((b1 + b2) / 2) * h
print(area)

#area of regular poligon
n = int(input())
a = float(input())
area = (n * a ** 2) / (4 * math.tan(math.pi / n))
print(round(area))

#area of a parallelogram
b = float(input())
h = float(input())
area = b * h
print(area)