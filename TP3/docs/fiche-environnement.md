# Fiche d'environnement – Jour 3

Relevé le 18/11/2026 sur mon ordinateur portable. La preuve est la première cellule du notebook `01_exploration.ipynb`.

| Élément | Valeur |
|---|---|
| Système | Ubuntu 24.04.4 LTS, 12 cœurs, 15 Go de RAM |
| Python | 3.12.3, dans un environnement virtuel `~/TP3/.venv` |
| PySpark / Spark | 4.3.0 (installé avec `pip install pyspark`) |
| Java | OpenJDK 17.0.21 (Temurin), celui installé au jour 2 dans `~/opt/jdk-17` |
| JupyterLab | 4.6.6 |
| Mode d'exécution | Spark en local (`local[*]`), 12 cœurs, 2 Go de mémoire pour le driver |
| Données d'entrée | `~/TP1/retail_project/data/` (kit TPCx-BB, copie locale des fichiers déposés dans HDFS au jour 2) |
| Sorties | `~/TP3/data/silver/`, `~/TP3/data/gold/`, `~/TP3/data/quarantine/` (créé seulement s'il y a des lignes écartées) |
| Preuves | `~/TP3/preuves/` et les sorties des notebooks |

## Choix et écarts

- **Lecture en local et pas depuis HDFS.** HDFS fonctionne (jour 2), mais lire en local est plus simple et prend moins de mémoire sur mon PC. Ce sont exactement les mêmes fichiers (vérifiés identiques par SHA-256 au jour 2). Mes traitements ont donc tourné **en local sur mon PC, pas sur un cluster**.
- **Java 17 réutilisé.** Spark 4 a besoin de Java 17 ou plus, donc je n'ai rien réinstallé. `config.py` indique ce Java à Spark (`JAVA_HOME`).
- **Mémoire limitée à 2 Go** pour Spark, parce que mon PC a peu de mémoire libre quand d'autres applications sont ouvertes. Ça suffit pour ces volumes (88 Mo pour le plus gros fichier).
- **Pas de sudo** : tout est installé dans mon dossier personnel.
