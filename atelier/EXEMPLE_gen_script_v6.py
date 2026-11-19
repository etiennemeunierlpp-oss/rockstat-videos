import json, subprocess
def dur(n): return float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f'rush_v2/b_{n}.mp4'],capture_output=True,text=True).stdout)
def pool(ns, k=34, step=1.4):
    D={n:dur(n) for n in ns}; pos={n:0.0 for n in ns}; out=[]; i=0
    while len(out)<k:
        n=ns[i%len(ns)]; i+=1
        if pos[n] > D[n]-1.0: pos[n]=0.35
        out.append(f"b_{n}@{pos[n]:.2f}"); pos[n]+=step
    return out
S=[
 {"id":"hook","text":"Dans GTA 6, la police peut maintenant te mettre 6 étoiles. Et c'est même pas le détail le plus fou caché dans la vidéo de 26 minutes de Rockstar.",
  "clips":pool(["109","155","156","121","148"]),"fx":[{"type":"logo","at":0.0,"dur":1.5,"y":640,"width":640},{"type":"sticker","text":"26 MIN DE GAMEPLAY","word":"Rockstar","dur":1.5,"y":700}]},
 {"id":"abo","text":"Abonne-toi pour rien rater de GTA 6.","clips":pool(["130","002","219"]),
  "fx":[{"type":"subscribe","at":0.0,"dur":2.6,"y":700,"handle":"@rockstat433","logo":"assets/logo_rs.png"}]},
 {"id":"1","text":"À la 14e minute, Jason tire depuis une voiture en fuite, avec la police et un hélico aux trousses. Regarde en haut de l'écran : 6 étoiles de recherche. Dans GTA 5, le maximum, c'était 5. Et dans GTA 4, la 6e étoile, c'était carrément les forces spéciales.",
  "clips":pool(["109","111","121"]),"fx":[{"type":"counter","to":6,"label":"ÉTOILES DE RECHERCHE","word":"étoiles","dur":2.0,"y":640},{"type":"label","text":"GTA 5 : 5 MAXIMUM","word":"maximum","dur":1.5,"y":700}]},
 {"id":"2","text":"Voler une voiture, ça change aussi. Dans GTA 5, Franklin appuyait sur un seul bouton. Là, c'est fini : Jason glisse une tige en métal dans la portière, et tu dois garder une jauge dans la bonne zone. Et selon Rockstar, les voitures de luxe à verrou électronique demandent un cloneur de clés.",
  "clips":pool(["039","057","124","058"]),"fx":[{"type":"sticker","text":"🔧 CROCHETAGE","word":"tige","dur":1.6,"y":640},{"type":"label","text":"CLONEUR DE CLÉS","word":"cloneur","dur":1.6,"y":700}]},
 {"id":"3","text":"Il y a aussi un profil criminel. Le jeu ne juge pas tous tes crimes pareil : te défendre contre un mec agressif, c'est moins grave qu'un massacre gratuit. Et des petits gestes, comme jeter un déchet à la poubelle ou nourrir un animal, améliorent ton profil.",
  "clips":pool(["149","065","130","086","140"]),"fx":[{"type":"big","text":"KARMA","word":"profil","dur":1.5,"y":640},{"type":"sticker","text":"🗑️ + RESPECT","word":"poubelle","dur":1.6,"y":700}]},
 {"id":"4","text":"Pendant une fuite, Lucia peut lancer un live, façon réseau social, avec les commentaires qui défilent. Un peu comme Lifeinvader dans GTA 5, mais en direct. Le pire ? Elle fait ça avec un otage dans le coffre.",
  "clips":pool(["150","097","148","146"]),"fx":[{"type":"alert","text":"🔴 EN DIRECT","word":"live","dur":1.6,"y":640},{"type":"sticker","text":"OTAGE DANS LE COFFRE 😱","word":"otage","dur":1.6,"y":700}]},
 {"id":"5","text":"Et les activités, c'est un délire : du catch dans un jardin avec des vraies prises de catch, de la plongée, du kayak, du motocross, et même Lucia qui pousse de la fonte au développé couché.",
  "clips":["b_067@0.3","b_067@1.5","b_067@2.6","b_136@0.2","b_136@1.3","b_141@0.2","b_141@1.1","b_153@0.3","b_153@1.6","b_153@2.9","b_137@0.2","b_137@1.4","b_137@2.5","b_139@0.2","b_156@0.5","b_156@2.0","b_156@3.5","b_156@5.0","b_139@1.0","b_067@0.8","b_153@0.9"],
  "fx":[{"type":"label","text":"🤼 CATCH","word":"catch","dur":1.4,"y":640},{"type":"label","text":"🏍️ MOTOCROSS","word":"motocross","dur":1.4,"y":700}]},
 {"id":"6","text":"Le plus fou, c'est à la fin. Jason récupère le ralenti de Michael dans GTA 5, avec des killcams à la Max Payne 3. Et des marqueurs semblent apparaître sur le corps des ennemis, pour viser un point vital, ou juste les désarmer.",
  "clips":pool(["203","193","202"],step=2.2),"fx":[{"type":"big","text":"RALENTI","word":"ralenti","dur":1.5,"y":640},{"type":"label","text":"🎯 POINTS VITAUX","word":"vital","dur":1.6,"y":700}]},
 {"id":"outro","text":"GTA 6 sort demain, le 19 novembre. Et toi, c'est quel détail qui t'a le plus choqué ? Dis-le en commentaire, et abonne-toi.",
  "clips":pool(["126","218","174","072","206","219"]),"fx":[{"type":"sticker","text":"📅 19 NOVEMBRE","word":"demain","dur":1.6,"y":640}]},
]
cfg={"title":"6 détails de GTA 6 que t'as ratés","style":"v2","max_shot":0.85,"music":"music_pack/m1_1114.mp3","music_offset":0.0,"music_volume":0.13,
 "logo":"assets/logo_gta6.webp","handle":"@rockstat433",
 "caption":"6 détails de GTA 6 que t'as sûrement ratés dans la vidéo de 26 minutes 👀 Lequel t'a le plus choqué ? #gta6 #gtavi #gta #gta6news #lucia",
 "remap_de":"https://www.tiktok.com/@clubgtavi/video/7633634514064968978 (8,5 M vues)",
 "sources":["Engadget - 20+ things you may have missed in the GTA 6 extended look","eGamers.io - GTA 6 extended look: 20+ details that slipped past most viewers","Rob Nelson (Rockstar North) cité par IGN via Engadget : cloneurs de clés, profil criminel"],
 "sections":S}
json.dump(cfg,open('scripts/details_extended.json','w'),ensure_ascii=False,indent=1)
print(sum(len(s['text'].split()) for s in S),'mots')
