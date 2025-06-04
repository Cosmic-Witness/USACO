read = open('max.in','r')

n = int(read.readline())
x = list(map(int,read.readline().split()))
y = list(map(int,read.readline().split()))
max = 0

for i in range(n):
    for j in range(i+1,n):
        dx =  x[i] - x[j]
        dy = y[i] - y[j]

        euclid = dx * dx + dy * dy
        if euclid > max:
            max = euclid

out = open('max.out','w')
out.write(str(max))