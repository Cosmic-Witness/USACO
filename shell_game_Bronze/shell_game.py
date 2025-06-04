#not novel solution, partly read the solution doc
read = open('shell.in','r')

n = int(read.readline())

shell_positions = [i for i in range(3)]

counter = [0]*3

for _ in range(n):
    a,b,g = [int(i)-1 for i in read.readline().split()]
    
    shell_positions[a], shell_positions[b] = shell_positions[b], shell_positions[a]

    counter[shell_positions[g]] += 1


print(max(counter),file = open('shell.out','w'))
    
