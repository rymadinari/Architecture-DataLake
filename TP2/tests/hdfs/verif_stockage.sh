#!/usr/bin/env bash
# UC-03 étape 5 : vérification du stockage HDFS
# Pour chaque fichier : présence, taille, empreinte SHA-256 locale = empreinte du fichier relu depuis HDFS
# Utilisation : bash tests/hdfs/verif_stockage.sh

set -u
cd "$(dirname "$0")/../.."
source ingestion/scripts/env-j2.sh

KIT=$HOME/TP1/retail_project
OUT=preuves/j2/hdfs/verif_stockage.csv
LOG=preuves/j2/hdfs/verif_stockage.log
ok=0; ko=0

echo "lot;table;taille_locale;taille_hdfs;sha256_local;sha256_hdfs;resultat" > "$OUT"
{
echo "=== Vérification du stockage du $(date '+%d/%m/%Y %H:%M:%S') ==="
for lot in data:initial data_refresh:refresh; do
  src=${lot%%:*}; dst=${lot##*:}
  for f in "$KIT"/$src/*/*.dat; do
    table=$(basename "$(dirname "$f")")
    h=/retail-lake/raw/tpcxbb/$dst/$table/$(basename "$f")
    tl=$(stat -c %s "$f")
    th=$(hdfs dfs -stat %b "$h" 2>/dev/null || echo ABSENT)
    sl=$(sha256sum "$f" | cut -d' ' -f1)
    sh=$(hdfs dfs -cat "$h" 2>/dev/null | sha256sum | cut -d' ' -f1)
    if [ "$tl" = "$th" ] && [ "$sl" = "$sh" ]; then r=OK; ok=$((ok+1)); else r=ECART; ko=$((ko+1)); fi
    echo "$dst;$table;$tl;$th;$sl;$sh;$r" >> "$OUT"
    echo "$r  $dst/$table  ($tl octets)"
  done
done
echo
echo "Fichiers identiques : $ok   Écarts : $ko"
echo "Détail : $OUT"
} 2>&1 | tee "$LOG"
