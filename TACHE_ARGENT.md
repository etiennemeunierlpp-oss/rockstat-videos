# Tâche « Vidéo argent GTA 6 » (10 h et 18 h) — procédure complète

Thème unique : **comment se faire de l'argent facilement dans GTA 6** (glitchs, planques, braquages rentables, voitures à revendre, coffres, astuces chapitre par chapitre). Pas de news générales.
Compte TikTok @rockstat433, en français, tutoiement. Le rendu se fait sur GitHub Actions : cette session n'encode RIEN.

## 0. Préparer (2 min)
```
mkdir -p ~/gta && cd ~/gta
curl -sSL -o .tg_token "https://drive.usercontent.google.com/download?id=10dqt-uGTmtvOztO4KxMxFmrBWeAlUjOb&export=download&confirm=t"
cp /home/claude/rockstat-videos/atelier/tg.py . && python3 tg.py read   # messages d'Etienne (idées, consignes)
```
Lire `sujets_faits.txt` (racine du dépôt) : ne JAMAIS refaire un sujet déjà fait. Lire aussi `idees_etienne.txt` s'il existe (idées prioritaires).

## ÉCONOMIE DE TOKENS (Etienne, 22/11)
- Attentes : UNIQUEMENT `bash atelier/attendre.sh <branche>` (timeout Bash 540000 ms) ; elle n'affiche qu'une ligne. Relancer seulement si PAS_ENCORE. Jamais de petites boucles ls-remote/sleep à la main, jamais de `gh run view --log`.
- Pas de veille web quand la vidéo source (transcription) donne déjà le lieu, les étapes et les montants. Au plus 1 recherche si un montant est flou.
- Planches : lire la transcription d'abord, puis n'ouvrir que les planches des passages utiles (1 planche = 60 s de vidéo). Pas de re-lecture de fichiers déjà lus.
- Pas de narration entre les étapes ; sorties de commandes courtes (`-q`, `| tail -3`).

## 1. Veille (seulement si pas de vidéo source exploitable ; 3 recherches web max)
Chercher les méthodes d'argent GTA 6 du moment : `GTA 6 money glitch`, `GTA 6 make money fast`, `GTA 6 hidden cash stash`, `GTA 6 best heist payout`, guides Game Rant / Vice / Dexerto / PowerPyx / GTA Base, + comptes TikTok GTA qui buzzent.
Choisir LE sujet le plus « argent facile » pas encore fait. Vérifier les faits sur 2 sources si possible ; sinon « selon <source> ».
Écrire avec des étapes concrètes (lieu, chapitre, code, montant). Montants en chiffres.

## 1b. FORMAT GAMEPLAY — OBLIGATOIRE pour toutes les vidéos (Etienne, 22/11)
La vidéo qui a percé (Wish List de Randy, 21/11) + le test gameplay du 22/11 : on garde hook/abo/animations et on monte les parties sur le **vrai gameplay** d'une vidéo qui a bien marché.
1. Trouver la vidéo source : `cd /home/claude/rockstat-videos && python3 atelier/veille_youtube.py` → vidéos **YouTube de la semaine, 30 s à 3 min, « GTA 6 money »**, triées par vues (Apify, 1 recherche/jour gardée dans `veille/youtube_<date>.json`, déjà utilisées écartées). Prendre la plus vue dont le sujet n'est pas dans `sujets_faits.txt` et dont on voit le gameplay (titre/miniature = tuto, pas une réaction). Lien envoyé par Etienne (Telegram / `idees_etienne.txt`) = prioritaire. Sinon TikTok (WebSearch `site:tiktok.com gta 6 money`). Le sujet de la vidéo = le sujet du jour : la veille web (§1) sert à vérifier les montants.
   Noter l'id choisi en fin de `veille/gameplay_utilises.txt` (« <videoId> <date> <slug> »).
2. Demander la préparation : `gameplay_req/<id>.json` = `{"id":"<id court>","url":"<lien>"}` → commit + push sur main, puis attendre la branche : `bash atelier/attendre.sh g-<id>` (relancer une fois si PAS_ENCORE). Le workflow « Préparation gameplay » (~3-5 min) crée la branche `g-<id>` : `src.mp4` (sans son), `transcript.txt` (timecodes mm:ss), `info.txt`, `sheet_00.jpg…` (1 image toutes les 2 s, temps en secondes écrit en jaune). YouTube est téléchargé via Apify (epctex/youtube-video-downloader, 1080p, ~0,10 $ la vidéo) car YouTube bloque GitHub ; transcription Whisper (anglais). Échec → branche `log-g-<id>` + Telegram → essayer la vidéo suivante de la liste (jusqu'à 3). Toujours rien → `python3 tg.py send "❌ Pas de gameplay exploitable pour <créneau>"` et s'arrêter : **plus jamais de vidéo sur la banque du Drive** (Etienne, 23/11).
3. Lire : `git fetch -q --depth 1 origin g-<id> && git show FETCH_HEAD:transcript.txt` ; puis extraire SEULEMENT les planches utiles (`git show FETCH_HEAD:sheet_00.jpg > /tmp/s0.jpg`, sheet_NN = secondes NN*60 à NN*60+60) et les REGARDER (Read) pour repérer les moments clés : carte/lieu, trajet, arrivée, action (fouille, coffre, braquage…), argent gagné, revente.
4. Écrire le script FR (même règles que §2) en suivant les étapes de la vidéo source, puis les plans, **au niveau racine du fichier (pas dans `cfg`)** : `"gameplay":{"src":"g-<id>","cuts":[["gp_map1",20.5,0],["gp_corps1",46,1],["gp_x",12,0,0.3],…]}` = [nom gp_…, début en s, sombre 0/1, (option) cadrage horizontal 0-1 si la source est en 16:9]. 5e valeur optionnelle = zoom 1-1,6 (gros plan sur x). Chaque plan découpé dure 2,5 s mais n'est montré que ~1 s (`max_shot`). Prévoir **~1 plan par seconde de voix (≈ mots/2,7)** + 2 plans de marge par partie, tous à des moments différents de la source. Contrôle du rendu : un même plan (nom@offset) jamais deux fois dans la vidéo, un même gp_ jamais deux fois dans une partie → découper la source en plans de 1 s (`gp_t00`, `gp_t01`… = seconde de départ) et attribuer chaque seconde à la phrase qu'elle illustre (modèle validé par Etienne le 23/11 : `atelier/modele_montage_v8.json`, 66 s de source pour 62 s de vidéo).
5. Dans les parties : `"clips":["gp_map1","gp_route1",…]` au lieu de kws/n (un même gp_ jamais deux fois dans une partie ; pour le réutiliser ailleurs : `"gp_route1@0.8"`). **Hook, abo et outro aussi sur le gameplay** (`clips` gp_ partout ; `kws`/`n` interdits, le rendu refuse le fichier sinon). Miniature : `"thumb":["rush_tv/gp_<plan parlant>.mp4",1.0,"MONTANT","LIGNE 2","LIGNE 3"]`.
6. Ne pas créditer le créateur dans la description (consigne d'Etienne). Couper son son (fait automatiquement).

### Montage (modèle : reel koumaoff « Urus doré cheaté », Etienne 23/11)
- **Un plan par idée, cut sur le mot** : chaque plan montre littéralement ce que dit la voix à cet instant (« ouvre ta map » → carte ; « discret » → perso accroupi ; « barre-toi » → fuite en voiture ; montant → écran d'argent du jeu). Les `clips` d'une partie sont dans l'ordre exact du texte.
- **Aucun effet par-dessus le logo** (0-1,5 s) : le rendu décale automatiquement le counter après le logo.
- **Rythme** : `max_shot` 1,0 (0,8-1,2), jamais un plan de plus de 1,5 s, jamais d'image fixe (zoom lent automatique).
- **Hook = ARGENT d'entrée** (Etienne 23/11) : la 1re phrase parle tout de suite d'argent facile avec le montant (« Dans GTA 6, tu peux te faire 4 000 dollars toutes les 2 minutes sans rien faire. »), puis le comment. Jamais d'intro sur un lieu ou un bâtiment. 1er plan = l'argent ou le résultat promis en pleine action (voiture qui drifte, sac d'argent, compteur), logo GTA VI en pop à 0 s ; la phrase du hook dit le sujet en moins de 1,5 s. Miniature (1re frame) = ce même plan.
- **Recadrage** : fait par `gameplay_cut.py` (bande centrale 1080x1600, sous-titres du créateur coupés, fond flouté). Choisir x pour garder le sujet (perso, voiture) au centre ; zoom 1,2-1,4 pour un gros plan. HUD du jeu (minimap, argent, « mission réussie ») = bonus, il prouve que c'est du vrai jeu.
- **Son** : musique m1_1114 présente tout le long sous la voix (`music_volume` 0,16) ; whoosh seulement aux changements de partie (les coupes rapides restent sans son, retour d'Etienne).
- **Fin** : l'outro boucle sur un plan du hook et finit par « Envoie ça à un pote qui joue à GTA 6, et abonne-toi. »

## 2. Script → fichier de file d'attente
Slug : `AAAA-MM-JJ_10h_<sujet-court>` ou `_18h_`. Fichier `queue/<slug>.json` :
```json
{"slug":"<slug>","preset":"v4",
 "gameplay":{"src":"g-<id>","cuts":[["gp_hook1",12.0,0,0.5,1.3],["gp_map1",20.5,0],…]},
 "thumb":["rush_tv/gp_hook1.mp4",1.0,"LIGNE ROSE","LIGNE 2","LIGNE 3"],
 "tg_msg":"🎬 <titre> — publication auto à 10 h sur les 4 réseaux. Réponds « stop » pour bloquer.",
 "cfg":{"title":"…","style":"v2","max_shot":1.0,"music":"music_pack/m1_1114.mp3","music_offset":22,"music_volume":0.16,
  "logo":"assets/logo_gta6.webp","handle":"@rockstat433",
  "caption":"<phrase> <question> #gta6 #gtavi #gta #gta6news #lucia #argentgta6",
  "sources":["…"],
  "sections":[
   {"id":"hook","text":"Dans GTA 6, …","clips":["gp_hook1","gp_hook2",…],"fx":[{"type":"logo","at":0.0,"dur":1.5,"y":640,"width":640},{"type":"counter","to":8000,"suffix":" $","label":"…","word":"…","dur":2.2,"y":700}]},
   {"id":"abo","text":"Abonne-toi et enregistre cette vidéo si tu veux connaître toutes les astuces argent facile dans GTA 6.","clips":["gp_x1","gp_x2","gp_x3","gp_x4"],"fx":[{"type":"subscribe","at":0.0,"dur":2.6,"y":700}]},
   {"id":"1","text":"…","clips":["gp_…"],"fx":[…]},
   {"id":"outro","text":"… question … Envoie ça à un pote qui joue à GTA 6, et abonne-toi.","clips":["gp_…","gp_hook1@0.5"],"fx":[…]}
 ]}}
```
Règles :
- abo = TOUJOURS exactement « Abonne-toi et enregistre cette vidéo si tu veux connaître toutes les astuces argent facile dans GTA 6. » (Etienne, 22/11).
- **TOUJOURS `"preset":"v4"` + musique `m1_1114.mp3` offset 22** (musique, voix Fenrir énergique et SFX de la vidéo Randy qui a percé ; la voix Achird est abandonnée). max_shot 1,0 (0,8-1,2) ; music_volume 0,16.
- Format gameplay (§1b) TOUJOURS : la banque du Drive (`kws`/`n`) n'est plus utilisée (Etienne, 23/11).
- 230-280 mots (≈ 60-70 s). Hook : « Dans GTA 6, tu peux te faire <montant> … » (l'argent dans la 1re phrase). 4 à 6 parties. Outro : question + « Envoie ça à un pote qui joue à GTA 6, et abonne-toi. »
- **Varier le format** d'une vidéo à l'autre (tuto pas à pas, top 3 méthodes, « arrête de faire ça », comparatif rentabilité, défi « 0 à 100 000 $ »), et les fx.
- fx 1-2 par partie : sticker, label, big, alert, counter (tout montant cité), stars, source, emoji. **Jamais l'image de carte `assets/map_gta6.png`** (Etienne 23/11, elle cache le montage ; le rendu la retire) : pour un lieu, on montre la carte du jeu dans le gameplay (plans gp_ de la map). `"word"` = mot du texte qui déclenche l'effet. y 640/700 alternés. Jamais de layout card, aucune numérotation.
- Faits sourcés ; rumeur/méthode non vérifiée = « selon <source> ».

## 3. Envoyer au rendu
```
cd /home/claude/rockstat-videos && git pull -q --depth 1 origin main
# écrire queue/<slug>.json, ajouter le sujet en fin de sujets_faits.txt
git add -A && git commit -qm "<slug>" && git -c push.negotiate=true push -q origin HEAD:main
```
Le push sur `queue/` lance GitHub Actions (~20-30 min) : voix, montage, miniature, MP4 sur la branche `v-<slug>`, aperçu Telegram.

## 4. FIN de la tâche « Création » (économie de tokens, 22/11)
Après le push du §3 : S'ARRÊTER. Ne pas attendre le rendu (chaque attente relit tout le contexte, images comprises). La publication est faite par la tâche « Publication GTA 6 » (9 h 23 pour 10 h, 17 h 23 pour 18 h), qui suit le §5.
Le slug DOIT contenir `_10h_` ou `_18h_` : c'est ainsi que la tâche Publication retrouve `queue/<slug>.json`.

## 5. Publier (tâche « Publication GTA 6 », légère)
1. `cd /home/claude/rockstat-videos` ; créneau = 10h si l'heure Paris < 12 h, sinon 18h. Fichier = `ls queue/<AAAA-MM-JJ>_<créneau>_*.json` (sans suffixe -v2…). Aucun fichier → s'arrêter sans rien envoyer (la tâche Création a déjà signalé son échec).
2. Si le slug est dans `bloquees.txt` → ne rien publier, s'arrêter.
3. Attendre `bash atelier/attendre.sh v-<slug>` (timeout 540000 ms) ; relancer tant que PAS_ENCORE et que l'heure < créneau + 60 min. ECHEC ou trop tard → `python3 tg.py send "❌ …"` et s'arrêter.
4. Lire seulement `cfg.title` et `cfg.caption` du JSON (`python3 -c` ou `jq`), rien d'autre. URL : `https://raw.githubusercontent.com/etiennemeunierlpp-oss/rockstat-videos/v-<slug>/<slug>.mp4`
Juste avant : `python3 tg.py read` ; si Etienne a écrit « stop » → ne rien publier, répondre « OK, bloquée » sur Telegram. (Autres messages : les ajouter à `idees_etienne.txt` et le dire en une ligne sur Telegram.)
Anti-doublon : `getScheduledPosts` (blogId 7690282, journée du jour, Europe/Paris) ; si un post a déjà ce texte/titre → ne rien republier, s'arrêter.
Toute commande bloquée plus de 10 min = échec : `python3 tg.py send "❌ …"` et s'arrêter (jamais d'attente au-delà de créneau + 60 min).
Sinon `createScheduledPost` : blogId `7690282`, date = créneau (10:00 ou 18:00 Europe/Paris ; si passé : maintenant + 5 min), autoPublish true,
providers tiktok, instagram, youtube, facebook ; media = [URL] ; `videoCoverMilliseconds: 100` ;
tiktokData.title = accroche ; instagramData.type REEL ; youtubeData {title: accroche + " #shorts", type "short", privacy "public", category "GAMING", madeForKids false} ; facebookData.type REEL ; text = caption.
Puis `python3 tg.py send "✅ <titre> programmée à <heure>"`.

## 6. Projet propre
Metricool garde sa propre copie du MP4 : la branche `v-<slug>` et `queue/<slug>.json` sont supprimées automatiquement par le workflow « Ménage » (chaque nuit, tout ce qui a plus de 6 h). Ne rien créer d'autre (pas de doc, pas de fichier dans le Drive ni dans le projet Claude). Seul `sujets_faits.txt` grossit.

## Interdits
Ne pas recréer de tâche programmée. Ne pas toucher au Drive (quota plein). Pas de Drive partagé 0AKiz…, pas d'Atelier 1bTQ…, pas de « GTA VI DATA ».

## 7. Retours d'Etienne sur Telegram (tâche « Retours Telegram GTA 6 », toutes les 2 h, Sonnet)
1. Préparer comme au §0, puis `python3 tg.py read` (attention : lire VIDE la file, donc tout traiter ici). Aucun message → s'arrêter sans rien envoyer.
2. « stop » → `getScheduledPosts` (blogId 7690282, aujourd'hui → demain) : passer le prochain post GTA en `draft: true`, répondre « OK, bloquée » Si le post n'est pas encore créé (rendu en cours) : ajouter le slug du prochain créneau en fin de `bloquees.txt`, push sur main.
3. Retour sur une vidéo (anim, son, texte, CTA…) = la dernière programmée/publiée sauf précision :
   - `python3 tg.py send "👍 Bien reçu : <résumé>. V2 en rendu, aperçu dans ~25 min."`
   - Copier `queue/<slug>.json` en `queue/<slug>-v2.json` (v3…), slug mis à jour, appliquer les retours (texte, fx, compteur…). Si le retour vaut pour toutes les vidéos (son, DA, CTA), corriger aussi `atelier/` ou ce fichier.
   - Push, attendre `v-<slug>-v2` (§4) : l'aperçu part tout seul sur Telegram.
   - Si le post n'est pas encore publié : `updateScheduledPost` avec le nouveau media (URL raw de la v2), même date. S'il est déjà publié : ne rien republier, envoyer la v2 et demander « go » pour la reposter.
   - `python3 tg.py send "✅ V2 en place pour <heure>"`.
4. Idée de sujet / consigne générale → l'ajouter en fin de `idees_etienne.txt` (lu par la veille) et répondre « 📝 Noté ».
