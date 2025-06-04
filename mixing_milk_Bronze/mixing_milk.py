#not novel solution, partly read the solution doc
with open('milk.in') as read:
    line = [line.split() for line in read]

milk_holding = [int(i[1]) for i in line]
max_cap = [int(i[0]) for i in line]
positions = [0,1,2]

#mix?
n = 100

#cyclical loop through the list of length of 3
for i in range(n):
    bucket1_indx = i % 3
    bucket2_indx = (i+1)% 3

    resid = min(milk_holding[bucket1_indx],max_cap[bucket2_indx] - milk_holding[bucket2_indx])

    milk_holding[bucket1_indx] -= resid
    milk_holding[bucket2_indx] += resid


print(max_cap)
print(milk_holding)

