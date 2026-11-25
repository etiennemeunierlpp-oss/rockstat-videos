#!/usr/bin/env python3
"""tg.py send "texte" | tg.py video fichier.mp4 "légende" | tg.py read  (affiche les nouveaux messages d'Etienne et les acquitte)"""
import sys,json,urllib.request,os,subprocess
T=open(os.path.expanduser("~/gta/.tg_token")).read().strip(); C=1101390069; U=f"https://api.telegram.org/bot{T}/"
def call(m,d): return json.load(urllib.request.urlopen(urllib.request.Request(U+m,json.dumps(d).encode(),{"Content-Type":"application/json"}),timeout=30))
a=sys.argv[1]
if a=="send": print(call("sendMessage",{"chat_id":C,"text":sys.argv[2]})["ok"])
elif a=="video":
    r=subprocess.run(["curl","-sS","-m","120","-F",f"chat_id={C}","-F",f"caption={sys.argv[3]}","-F","supports_streaming=true","-F",f"video=@{sys.argv[2]}",U+"sendVideo"],capture_output=True,text=True)
    print(json.loads(r.stdout).get("ok"),json.loads(r.stdout).get("description",""))
elif a=="read":
    r=call("getUpdates",{"timeout":0}); last=None
    for u in r["result"]:
        last=u["update_id"]; m=u.get("message",{})
        if m.get("chat",{}).get("id")==C: print(m.get("text"))
    if last: call("getUpdates",{"offset":last+1})
