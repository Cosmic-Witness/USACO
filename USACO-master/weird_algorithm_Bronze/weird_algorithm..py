n = int(input())
n_s = [n]

while n!= 1:
    if n % 2 == 0:
        n = n//2
        n_s.append(n)
    else:
        n = 3*n +1
        n_s.append(n)

print(*n_s)
    