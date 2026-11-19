import json, os, sys, numpy as np
sys.argv=[sys.argv[0]]
import analyze_rushes as A
idx=json.load(open('rush_index.json')); have={c['name'] for c in idx}
for f in sorted(os.listdir('rush_v2')):
    n=os.path.splitext(f)[0]
    if not n.startswith('b_') or n in have: continue
    xs=[];hits=0;tot=0
    for ts,fr in A.frames('rush_v2/'+f,step=0.5):
        tot+=1; b=A.detect(fr)
        if b:
            hits+=1; faces=[x for x in b if x[0]=='face'] or b; xs+= [x[1] for x in faces]
    fx=round(float(np.median(xs)),3) if xs else 0.5
    idx.append({"name":n,"format":"horizontal","tags":[],"subject":bool(xs),"focus_x":fx,"spread":0,"start_ok":0,"coverage":round(hits/max(tot,1),2)})
    print(n,fx,hits,tot)
json.dump(idx,open('rush_index.json','w'),ensure_ascii=False,indent=1)
