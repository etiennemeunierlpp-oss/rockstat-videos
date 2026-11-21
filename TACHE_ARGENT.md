# Tâche « Vidéo argent GTA 6 » (10 h et 18 h) — procédure complète

Thème unique : **comment se faire de l'argent facilement dans GTA 6** (glitchs, planques, braquages rentables, voitures à revendre, coffres, astuces chapitre par chapitre). Pas de news générales.
Compte TikTok @rockstat433, en français, tutoiement. Le rendu se fait sur GitHub Actions : cette session n'encode RIEN.

## 0. Préparer (2 min)
```
mkdir -p ~/gta && cd ~/gta
curl -sSL -o .tg_token "https://drive.usercontent.google.com/download?id=10dqt-uGTmtvOztO4KxMxFmrBWeAlUjOb&export=download&confirm=t"
cp /home/claude/rockstat-videos/atelier/tg.py . && python3 tg.py read   # messages d'Etienne (idées, consignes)
```
Lire `sujets_faits.txt` (racine du dépôt) : ne JAMAIS refaire un sujet déjà fait.

## 1. Veille (3-5 recherches web max)
Chercher les méthodes d'argent GTA 6 du moment : `GTA 6 money glitch`, `GTA 6 make money fast`, `GTA 6 hidden cash stash`, `GTA 6 best heist payout`, guides Game Rant / Vice / Dexerto / PowerPyx / GTA Base, + comptes TikTok GTA qui buzzent.
Choisir LE sujet le plus « argent facile » pas encore fait. Vérifier les faits sur 2 sources si possible ; sinon « selon <source> ».
Écrire avec des étapes concrètes (lieu, chapitre, code, montant). Montants en chiffres.

## 2. Script → fichier de file d'attente
Slug : `AAAA-MM-JJ_10h_<sujet-court>` ou `_18h_`. Fichier `queue/<slug>.json` :
```json
{"slug":"<slug>",
 "thumb":["rush_v2/b_146.mp4",3,"LIGNE ROSE","LIGNE 2","LIGNE 3"],
 "tg_msg":"🎬 <titre> — publication auto à 10 h sur les 4 réseaux. Réponds « stop » pour bloquer.",
 "cfg":{"title":"…","style":"v2","max_shot":1.1,"music":"music_pack/flower.mp3","music_offset":80,"music_volume":0.12,
  "logo":"assets/logo_gta6.webp","handle":"@rockstat433",
  "caption":"<phrase> <question> #gta6 #gtavi #gta #gta6news #lucia",
  "sources":["…"],
  "sections":[
   {"id":"hook","text":"Dans GTA 6, …","kws":["braquage","sac"],"n":9,"fx":[{"type":"logo","at":0.0,"dur":1.5,"y":640,"width":640},{"type":"counter","to":8000,"suffix":" $","label":"…","word":"…","dur":2.2,"y":700}]},
   {"id":"abo","text":"Abonne-toi pour avoir toutes les astuces argent facile sur GTA 6.","kws":["vice city","nuit"],"n":4,"fx":[{"type":"subscribe","at":0.0,"dur":2.6,"y":700}]},
   {"id":"1","text":"…","kws":["…"],"n":12,"fx":[…]},
   {"id":"outro","text":"… question … Dis-le en commentaire, et abonne-toi.","kws":["…"],"n":10,"fx":[…]}
 ]}}
```
Règles :
- 230-280 mots (≈ 60-70 s). Hook : « Dans GTA 6, … » + promesse chiffrée. 4 à 6 parties. Outro : question + abonne-toi.
- **Varier le format** d'une vidéo à l'autre (tuto pas à pas, top 3 méthodes, « arrête de faire ça », comparatif rentabilité, défi « 0 à 100 000 $ »), le max_shot (0,9 à 1,3) et les fx.
- `kws` = mots-clés des plans (tags de la banque : braquage, bijouterie, superette, labo, drogue, sac, fusillade, conduite, decapotable, van, berline, fuite, poursuite, police, moto, bateau, jet ski, hydravion, marais, plage, vice city, nuit, neon, soiree, bar, fete, appart, garage, parking, telephone, jumelles, skyline, coucher soleil…). `n` ≈ durée de la partie (mots/3,9) / max_shot + 2. Le choix des plans (jamais deux fois le même) est fait par `montage.py` sur GitHub.
- fx 1-2 par partie : sticker, label, big, alert, counter (tout montant cité), stars, source, image (`assets/map_gta6.png` pour un lieu), emoji. `"word"` = mot du texte qui déclenche l'effet. y 640/700 alternés. Jamais de layout card, aucune numérotation.
- Faits sourcés ; rumeur/méthode non vérifiée = « selon <source> ».

## 3. Envoyer au rendu
```
cd /home/claude/rockstat-videos && git pull -q --depth 1 origin main
# écrire queue/<slug>.json, ajouter le sujet en fin de sujets_faits.txt
git add -A && git commit -qm "<slug>" && git -c push.negotiate=true push -q origin HEAD:main
```
Le push sur `queue/` lance GitHub Actions (~20-30 min) : voix, montage, miniature, MP4 sur la branche `v-<slug>`, aperçu Telegram.

## 4. Attendre le MP4 (max 90 min)
Boucle (commandes Bash de ≤ 9 min, `sleep 120` entre deux essais) :
`git ls-remote --exit-code --heads origin v-<slug>` → présent = prêt.
Si `log-<slug>` apparaît ou rien après 90 min : `python3 tg.py send "❌ …"` et s'arrêter.
URL : `https://raw.githubusercontent.com/etiennemeunierlpp-oss/rockstat-videos/v-<slug>/<slug>.mp4`

## 5. Publier (Metricool)
Juste avant : `python3 tg.py read` ; si Etienne a écrit « stop » → ne rien publier, répondre « OK, bloquée » sur Telegram.
Sinon `createScheduledPost` : blogId `7690282`, date = créneau (10:00 ou 18:00 Europe/Paris ; si passé : maintenant + 5 min), autoPublish true,
providers tiktok, instagram, youtube, facebook ; media = [URL] ; `videoCoverMilliseconds: 100` ;
tiktokData.title = accroche ; instagramData.type REEL ; youtubeData {title: accroche + " #shorts", type "short", privacy "public", category "GAMING", madeForKids false} ; facebookData.type REEL ; text = caption.
Puis `python3 tg.py send "✅ <titre> programmée à <heure>"`.

## 6. Projet propre
Metricool garde sa propre copie du MP4 : la branche `v-<slug>` et `queue/<slug>.json` sont supprimées automatiquement par le workflow « Ménage » (chaque nuit, tout ce qui a plus de 6 h). Ne rien créer d'autre (pas de doc, pas de fichier dans le Drive ni dans le projet Claude). Seul `sujets_faits.txt` grossit.

## Interdits
Ne pas recréer de tâche programmée. Ne pas toucher au Drive (quota plein). Pas de Drive partagé 0AKiz…, pas d'Atelier 1bTQ…, pas de « GTA VI DATA ».
