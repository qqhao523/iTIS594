import commands
import sys
import time

total=0
times=10

Str=commands.getoutput('iostat -c 10 -n cpu')
lines=Str.split('\n')

for i in range(2,times+1):
    user=lines[i][0:3]
    sys=lines[i][3:6]
    total=total+float(user)+float(sys)

#print total
#print times
print total/times
