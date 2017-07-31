recordings=[['55_20', 116], ['60_2', 102], ['55_19', 74], ['57_9', 72], ['54_4', 45], ['54_10', 33], ['58_0', 33], ['53_13', 22], ['61_7', 11], ['58_16', 10], ['53_5', 10], ['54_11', 7], ['61_17', 3], ['56_14', 1], ['58_18', 0], ['57_15', 0], ['102_12', 0], ['108_8', 0], ['62_6', 0], ['55_3', 0], ['109_1', 0]]

selectLimit=3
selected=[]

def findFarestNoteWithLongestDuration(index,recordings):
    
    bestScore=0
    bestIndex=index
    
    baseNote=int(recordings[index][0].split("_")[0])
    
    for i,rec in enumerate(recordings):
        note=int(rec[0].split("_")[0])
        duration=rec[1]
        noteDistance=abs(baseNote-note)
        score= (noteDistance)*(duration/5)
        if score>bestScore:
            bestScore=score
            bestIndex=i
            
    return bestIndex
    

while len(selected)<selectLimit:
    candidateIndex= findFarestNoteWithLongestDuration(0,recordings)
    selected.append(recordings[candidateIndex])
    del recordings[candidateIndex]
    
print selected