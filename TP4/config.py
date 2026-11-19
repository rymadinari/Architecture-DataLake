"""Réglages du TP4 : où sont les données du TP3, où enregistrer les résultats, et comment démarrer Spark.

Le notebook lit ce fichier. Si un chemin change, on le change seulement ici.
"""
import os
from pathlib import Path

RACINE = Path(__file__).resolve().parent

# Les données du TP3 (lues seulement, jamais modifiées)
TP3 = Path.home() / "TP3"
SILVER = TP3 / "data" / "silver"
GOLD = TP3 / "data" / "gold"

# Où le TP4 enregistre ses résultats
OUTPUTS = RACINE / "resultats"
VISUALISATIONS = RACINE / "graphiques"

# Java 17, installé au TP2 dans ~/opt (nécessaire pour Spark)
JAVA_HOME = Path.home() / "opt" / "jdk-17"

# Texte écrit en bas de chaque graphique
SOURCE_GRAPHIQUE = "Source : TPCx-BB (données inventées), fichiers Silver/Gold du TP3 – calculs Spark du TP4"


def creer_session(nom="TP4-Retail-Intelligence"):
    """Démarre Spark sur mon PC (ou reprend celui déjà démarré), comme au TP3."""
    os.environ.setdefault("JAVA_HOME", str(JAVA_HOME))
    from pyspark.sql import SparkSession

    spark = (
        SparkSession.builder
        .appName(nom)
        .master("local[*]")
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "8")
        .config("spark.sql.session.timeZone", "Europe/Paris")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    return spark
