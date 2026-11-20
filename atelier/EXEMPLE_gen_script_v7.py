import json, sys
import os; sys.path.insert(0, os.path.expanduser('~/gta'))
from montage import Picker, check
LOGO={"type":"logo","at":0.0,"dur":1.5,"y":640,"width":640}
def ABO(P): return {"id":"abo","text":"Abonne-toi pour rien rater de GTA 6.","clips":P.take(["vice city","nuit","neon"],4),
  "fx":[{"type":"subscribe","at":0.0,"dur":2.6,"y":700,"handle":"@rockstat433","logo":"assets/logo_rs.png"}]}
TAGS="#gta6 #gtavi #gta #gta6news #lucia"

# ---------- 1) ARGENT : tuto glitch
P=Picker(seed="glitch-argent-grange")
S=[
 {"id":"hook","text":"Dans GTA 6, il y a un glitch qui te rapporte 8000 dollars toutes les 5 minutes. Fais-le vite, avant que Rockstar le corrige.",
  "clips":P.take(["braquage","sac","labo"],10),"fx":[LOGO,{"type":"counter","to":8000,"suffix":" $","label":"TOUTES LES 5 MIN","word":"dollars","dur":2.2,"y":700}]},
 ABO(P),
 {"id":"1","text":"Prends ta voiture perso, celle avec un coffre, et va dans le comté de South Vice-Dale, juste au nord de Key Lento, à l'est de Hamlet. Tu cherches une grange rouge.",
  "clips":P.take(["conduite","route","marais","jour"],11),"fx":[{"type":"sticker","text":"🚗 TA VOITURE PERSO","word":"voiture","dur":1.6,"y":640},{"type":"image","src":"assets/map_gta6.png","word":"Key","dur":2.2,"y":760},{"type":"label","text":"📍 GRANGE ROUGE","word":"grange","dur":1.6,"y":700}]},
 {"id":"2","text":"Entre, et va dans le bureau du fond. Il y a de la cocaïne sur la table, et un coffre-fort qui en cache encore plus. Remplis ton sac de butin, puis range-le dans le coffre de ta voiture.",
  "clips":P.take(["labo","drogue","sac","fumee"],12),"fx":[{"type":"label","text":"🔐 COFFRE-FORT","word":"coffre-fort","dur":1.5,"y":640},{"type":"sticker","text":"🎒 SAC DE BUTIN","word":"sac","dur":1.5,"y":700}]},
 {"id":"3","text":"Retourne au milieu de la grange. Dans le van ouvert, il y a un 2e sac, déjà plein de cash. Complète-le avec la cocaïne du van, et celle du van garé dehors. Avec ces 2 sacs, t'as environ 8640 dollars.",
  "clips":P.take(["van","parking","sac","fuite"],13),"fx":[{"type":"label","text":"💵 SAC DE CASH","word":"cash","dur":1.5,"y":640},{"type":"counter","to":8640,"suffix":" $","label":"AVEC 2 SACS","word":"8640","dur":2.0,"y":700}]},
 {"id":"4","text":"Et maintenant, le glitch. Sauvegarde, puis recharge ta partie. Tu réapparais chez Jason, avec les sacs toujours dans ta voiture. Et dans la grange, tout le butin est revenu. Tu recommences jusqu'à 4 sacs.",
  "clips":P.take(["jason","appart","fusillade","gameplay"],13),"fx":[{"type":"big","text":"GLITCH","word":"glitch","dur":1.5,"y":640},{"type":"alert","text":"BUTIN REVENU","word":"revenu","dur":1.6,"y":700}]},
 {"id":"5","text":"Ensuite, file au Brian's Lockup, au sud-ouest de Key Lento. Tape le code 7700, dépose les 4 sacs, et l'argent tombe en quelques minutes. Attention : chez certains joueurs, le butin met quelques jours dans le jeu à revenir.",
  "clips":P.take(["garage","nuit","berline","rue"],14),"fx":[{"type":"big","text":"7700","word":"code","dur":1.8,"y":640},{"type":"sticker","text":"⚠️ PARFOIS QUELQUES JOURS","word":"Attention","dur":1.8,"y":700}]},
 {"id":"outro","text":"Et quand t'auras débloqué les gros coffres de banque, à la fin du chapitre 4, c'est jusqu'à 205000 dollars le coup. Tu veux que je t'explique comment ? Dis-le en commentaire, et abonne-toi.",
  "clips":P.take(["braquage","bijouterie","soiree","vice city"],12),"fx":[{"type":"counter","to":205000,"suffix":" $","label":"COFFRE DE BANQUE","word":"205000","dur":2.2,"y":640}]},
]
cfg={"title":"Glitch argent infini GTA 6","style":"v2","max_shot":1.25,"music":"music_pack/m1_1114.mp3","music_offset":12.0,"music_volume":0.12,
 "logo":"assets/logo_gta6.webp","handle":"@rockstat433",
 "caption":"Le glitch qui rapporte 8000 $ toutes les 5 minutes dans GTA 6 💸 Tu l'as déjà testé ? "+TAGS,
 "sources":["Game Rant - Use This Infinite Money Glitch in GTA 6 Before It's Patched (19/11/2026)","xboxplay.games - GTA 6 Money Glitch","timesaver.gg / boostingfactory - coffres de banque jusqu'à 205 000 $, fin du chapitre 4"],
 "sections":S}
assert not check(cfg), check(cfg); P.save("glitch-argent")
json.dump(cfg,open(os.path.expanduser('~/gta/scripts/')+'glitch-argent.json','w'),ensure_ascii=False,indent=1)
print("argent",sum(len(s['text'].split()) for s in S),'mots')

# ---------- 2) NEWS : flash 4 news
P=Picker(seed="news-20-11")
S=[
 {"id":"hook","text":"Dans GTA 6, il se passe déjà des trucs de fou, 2 jours après la sortie. Voilà les 4 news que t'as ratées aujourd'hui.",
  "clips":P.take(["vice city","fete","soiree","foule"],9),"fx":[LOGO,{"type":"alert","text":"FLASH INFO","word":"news","dur":1.6,"y":700}]},
 ABO(P),
 {"id":"1","text":"D'abord, le leaker Cyberleek a remis ça. Selon PC Gamer, il a balancé en ligne ce qu'il présente comme une version Xbox presque complète du jeu. Environ 200 gigas, d'après des commentaires sur Reddit.",
  "clips":P.take(["telephone","ordinateur","fenetre","silhouette","jumelles"],13),"fx":[{"type":"source","name":"PC Gamer","sub":"20 novembre","word":"PC","dur":1.8,"y":640},{"type":"counter","to":200,"suffix":" Go","label":"VERSION XBOX","word":"200","dur":2.0,"y":700}]},
 {"id":"2","text":"Ensuite, les 6 étoiles. Les testeurs de PC Gamer ont galéré pour les avoir. La seule façon qu'ils ont trouvée : voler un tank dans une base militaire, et faire sauter d'autres tanks. Dans GTA 5, ça s'arrêtait à 5.",
  "clips":P.take(["poursuite","police","fuite","emeute","feu"],13),"fx":[{"type":"stars","n":6,"word":"étoiles","dur":1.8,"y":640},{"type":"sticker","text":"🪖 VOLE UN TANK","word":"tank","dur":1.6,"y":700}]},
 {"id":"3","text":"Mauvaise nouvelle pour les fans de vue à la première personne : il n'y a pas de vrai mode. Rob Nelson, de Rockstar North, l'avait confirmé. Tu passes en première personne seulement en visant, avec certaines armes.",
  "clips":P.take(["vue interieur","conduit","fusil","arme","gros plan"],13),"fx":[{"type":"label","text":"❌ PAS DE MODE FPS","word":"mode","dur":1.6,"y":640},{"type":"label","text":"🎯 EN VISANT","word":"visant","dur":1.5,"y":700}]},
 {"id":"4","text":"Et si t'as acheté la boîte en magasin, tu pourras pas la revendre. Il n'y a pas de disque dedans, juste un code de téléchargement. Résultat : des magasins ont carrément refusé de vendre le jeu.",
  "clips":P.take(["superette","caissier","boutique","bar","galerie"],12),"fx":[{"type":"big","text":"0 DISQUE","word":"disque","dur":1.5,"y":640},{"type":"sticker","text":"🚫 REVENTE IMPOSSIBLE","word":"revendre","dur":1.6,"y":700}]},
 {"id":"outro","text":"Et toi, laquelle de ces 4 news t'a le plus choqué ? Dis-le en commentaire, et abonne-toi pour la suite.",
  "clips":P.take(["skyline","coucher soleil","mer","jet ski"],7),"fx":[{"type":"emoji","word":"commentaire","dur":1.6,"y":700}]},
]
cfg={"title":"4 news GTA 6 du 20 novembre","style":"v2","max_shot":0.95,"music":"music_pack/m1_1114.mp3","music_offset":40.0,"music_volume":0.13,
 "logo":"assets/logo_gta6.webp","handle":"@rockstat433",
 "caption":"Les 4 news GTA 6 du jour : leak Xbox, 6 étoiles, vue FPS et revente 📰 Laquelle t'a choqué ? "+TAGS,
 "sources":["PC Gamer - Cyberleek drops what they claim is a near-complete GTA 6 Xbox build online","PC Gamer - How to reach 6 stars in GTA 6","Vice / Beebom - pas de mode première personne (Rob Nelson)","SVG / Kotaku - édition physique = code, pas de revente"],
 "sections":S}
assert not check(cfg), check(cfg); P.save("news-20-11")
json.dump(cfg,open(os.path.expanduser('~/gta/scripts/')+'news-20-11.json','w'),ensure_ascii=False,indent=1)
print("news",sum(len(s['text'].split()) for s in S),'mots')
