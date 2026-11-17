#!/usr/bin/env bash
# UC-03 : création de l'arborescence du Data Lake et dépôt manuel des fichiers TPCx-BB
# Utilisation : bash ingestion/scripts/depot_hdfs.sh
# Les fichiers sources ne sont jamais modifiés : on fait seulement des copies vers HDFS.

set -u
cd "$(dirname "$0")/../.."
source ingestion/scripts/env-j2.sh

KIT=$HOME/TP1/retail_project
LOG=${LOG:-preuves/j2/hdfs/depot_hdfs.log}

{
echo "=== Dépôt HDFS du $(date '+%d/%m/%Y %H:%M:%S') par $(whoami) ==="

echo; echo "--- 1. Arborescence du Data Lake ---"
for d in raw/tpcxbb/initial raw/tpcxbb/refresh raw/nifi bronze/tpcxbb silver gold quality logs; do
  echo "\$ hdfs dfs -mkdir -p /retail-lake/$d"
  hdfs dfs -mkdir -p /retail-lake/$d
done

echo; echo "--- 2. Dépôt des fichiers (un dossier par table) ---"
for lot in data:initial data_refresh:refresh; do
  src=${lot%%:*}; dst=${lot##*:}
  for f in "$KIT"/$src/*/*.dat; do
    table=$(basename "$(dirname "$f")")
    cible=/retail-lake/raw/tpcxbb/$dst/$table
    hdfs dfs -mkdir -p "$cible"
    if hdfs dfs -test -e "$cible/$(basename "$f")"; then
      echo "DEJA PRESENT (pas d'écrasement) : $cible/$(basename "$f")"
    else
      echo "\$ hdfs dfs -put $f $cible/"
      hdfs dfs -put "$f" "$cible/" && echo "  OK"
    fi
  done
done

echo; echo "--- 3. Résultat ---"
echo "\$ hdfs dfs -ls -R /retail-lake | head"
hdfs dfs -ls -R /retail-lake | head -20
echo "\$ hdfs dfs -du -h /retail-lake/raw/tpcxbb"
hdfs dfs -du -h /retail-lake/raw/tpcxbb
echo "=== Fin $(date '+%H:%M:%S') ==="
} 2>&1 | tee "$LOG"
