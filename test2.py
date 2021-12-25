x1, y1, w1, h1 = [int(i) for i in input().split()]
x2, y2, w2, h2 = [int(i) for i in input().split()]

xw1 = set(range(x1, x1 + w1 + 1))
yh1 = set(range(y1, y1 + h1 + 1))
xw2 = set(range(x2, x2 + w2 + 1))
yh2 = set(range(y2, y2 + h2 + 1))

if xw1.intersection(xw2) and yh1.intersection(yh2):
    print('YES')