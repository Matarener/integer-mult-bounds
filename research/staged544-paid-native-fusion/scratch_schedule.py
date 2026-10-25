"""Constructive eight-word schedule witnesses, not Python-storage measurements.

The witness harness owns its inputs/outputs outside the eight private slots.
An implementation loads/stores those values from/to caller arrays as specified.
Each schedule clears arbitrary initial private words and returns them zero.
"""
def check():
    checks=0
    for a,b,c,d in [(1,0,0,0),(0,1,0,0),(0,0,1,0),(0,0,0,1),(71,-29,13,5)]:
        for q in range(4):
            s=[31-j for j in range(8)]
            for j in range(8):s[j]=0
            s[0],s[1]=a,b;s[2],s[3]=c,d
            s[4],s[5]=-s[0],-s[1]
            # Pair entries are slot aliases, not additional scalar storage.
            route=((0,1),(5,0),(4,5),(1,4))
            materialized=(s[route[q][0]],s[route[q][1]])
            targets=[]
            for sign in (2,2,0):
                s[6],s[7]=11,-17
                i,j=route[(q+sign)%4]
                s[6]+=s[i];s[7]+=s[j]
                targets.append((s[6],s[7]))
            expected=((a,b),(-b,a),(-a,-b),(b,-a))[q]
            if materialized!=expected or targets!=[(11-expected[0],-17-expected[1])]*2+[(11+expected[0],-17+expected[1])]:raise ValueError('consumer register schedule')
            if s[2:4]!=[c,d]:raise ValueError('cycle following value lost')
            for j in range(8):s[j]=0
            if any(s):raise ValueError('private scratch return')
            checks+=1
        s=[31-j for j in range(8)]
        for j in range(8):s[j]=0
        s[0],s[1],s[2],s[3]=a,b,c,d
        s[4]=s[0]+s[2];s[5]=s[1]+s[3]
        s[6]=s[0]-s[2];s[7]=s[1]-s[3]
        s[0]=s[4]-s[7];s[1]=s[5]+s[6]
        s[2]=s[4]+s[7];s[3]=s[5]-s[6]
        if s[:4]!=[a+c-b+d,b+d+a-c,a+c+b-d,b+d-a+c]:raise ValueError('butterfly register schedule')
        for j in range(8):s[j]=0
        if any(s):raise ValueError('butterfly scratch return')
        checks+=1
    return dict(private_real_words_upper_bound=8,whole_program_initial_and_final_clears=16,schedule_witnesses=checks,kind='constructive register schedule; not measured Python memory')
