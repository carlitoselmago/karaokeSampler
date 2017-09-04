import numpy as np
def find_nearest(array,value):
    return min(range(len(array)), key=lambda i: abs(array[i]-value))

array = [29.43,9.97,1.44,5.13,6.30,7.0,6.60]

# [ 0.21069679  0.61290182  0.63425412  0.84635244  0.91599191  0.00213826
#   0.17104965  0.56874386  0.57319379  0.28719469]

value = 6.5

print(find_nearest(array, value))
# 0.568743859261