#!/usr/bin/env bash
# UC-04 étape 9 : vérifie que les fichiers déposés par NiFi sont identiques aux originaux du kit
# Utilisation : bash tests/ingestion/verif_depot_nifi.sh <fichier_original_local> [<autre> ...]

set -u
cd "$(dirname "$0")/../.."
source ingestion/scripts/env-j2.sh

echo "=== Vérification du dépôt NiFi du $(date '+%d/%m/%Y %H:%M:%S') ==="
echo "\$ hdfs dfs -ls -h /retail-lake/raw/nifi"
hdfs dfs -ls -h /retail-lake/raw/nifi
echo "\$ hdfs dfs -du -h /retail-lake/raw/nifi"
hdfs dfs -du -h /retail-lake/raw/nifi
echo
for f in "$@"; do
  h=/retail-lake/raw/nifi/$(basename "$f")
  sl=$(sha256sum "$f" | cut -d' ' -f1)
  sh=$(hdfs dfs -cat "$h" 2>/dev/null | sha256sum | cut -d' ' -f1)
  tl=$(stat -c %s "$f"); th=$(hdfs dfs -stat %b "$h" 2>/dev/null || echo ABSENT)
  [ "$sl" = "$sh" ] && [ "$tl" = "$th" ] && r=IDENTIQUE || r=DIFFERENT
  echo "$r : $(basename "$f")  local=$tl o / hdfs=$th o"
  echo "   sha256 local = $sl"
  echo "   sha256 hdfs  = $sh"
done
echo
echo "Fichier original toujours présent dans le kit :"
for f in "$@"; do ls -l "$f"; done
