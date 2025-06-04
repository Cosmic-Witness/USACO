with open('speed.in') as read:
    n,m = map(int, read.readline().split())

    roads = []
    for _ in range(n):
        length, speed = map(int,read.readline().split())
        roads.extend([speed]*length)
   
    bessie = []
    for _ in range(m):
        length, speed = map(int, read.readline().split())
        bessie.extend([speed]*length)

maximum = 0
print(bessie)

for i in range(100):
    maximum = max(maximum, roads[i] - bessie[i])

with open("speed.out","w") as write:
    write.write(str(maximum))