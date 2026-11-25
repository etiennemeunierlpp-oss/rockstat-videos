#!/usr/bin/env bash
# Attend sans bruit qu'une branche existe : bash atelier/attendre.sh <branche> [minutes, 8 max par appel]
# Affiche une seule ligne : PRET <branche> | ECHEC log-… | PAS_ENCORE (relancer la commande)
B=$1; M=${2:-8}; [ "$M" -gt 8 ] && M=8; end=$(( $(date +%s) + M*60 ))
while [ $(date +%s) -lt $end ]; do
  timeout 30 git ls-remote --exit-code --heads origin "$B" >/dev/null 2>&1 && { echo "PRET $B"; exit 0; }
  timeout 30 git ls-remote --exit-code --heads origin "log-$B" >/dev/null 2>&1 && { echo "ECHEC log-$B"; exit 2; }
  case "$B" in v-*) git ls-remote --exit-code --heads origin "log-${B#v-}" >/dev/null 2>&1 && { echo "ECHEC log-${B#v-}"; exit 2; };; esac
  sleep 45
done
echo "PAS_ENCORE $B"; exit 1
