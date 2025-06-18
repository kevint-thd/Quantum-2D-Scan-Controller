
from typing import List , Dict
from collections import defaultdict
output = defaultdict(List)
def groupanagram(strs):
    for index,word in strs:
        key =''.join(sorted(word))
        output[key].append(word)
        omega = List(output.values)

    return List(output.values)    
    print(omega)
        




    










