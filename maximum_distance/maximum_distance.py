n = int(input())
x = list(map(int, input().split()))
y = list(map(int, input().split()))

max_dist = 0

for i in range(n):
    for j in range(i + 1, n):
        dx = x[i] - x[j]
        dy = y[i] - y[j]
        euclid = dx * dx + dy * dy
        if euclid > max_dist:
            max_dist = euclid

print(max_dist)
