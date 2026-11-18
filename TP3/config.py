"""Paramètres communs du TP3 : chemins, colonnes des sources, session Spark.

Tous les notebooks font `from config import *` : si un chemin change,
on ne le modifie qu'ici.
"""
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Chemins
# ---------------------------------------------------------------------------
RACINE = Path(__file__).resolve().parent

# Données brutes (zone Raw/Bronze) : le kit TPCx-BB du Jour 1, déjà déposé
# dans HDFS au Jour 2. On lit la copie locale (solution documentée dans le README).
SOURCE = Path.home() / "TP1" / "retail_project" / "data"

DATA = RACINE / "data"
SILVER = DATA / "silver"
GOLD = DATA / "gold"
QUARANTAINE = DATA / "quarantine"   # lignes mises à l'écart, jamais supprimées
TEST = DATA / "test"
PREUVES = RACINE / "preuves"

# Java 17 installé au Jour 2 dans ~/opt (pas de droits sudo)
JAVA_HOME = Path.home() / "opt" / "jdk-17"


def chemin_source(table):
    """Chemin du fichier brut d'une table, ex. .../data/store_sales/store_sales.dat"""
    return SOURCE / table / f"{table}.dat"


# ---------------------------------------------------------------------------
# Colonnes des 4 sources retenues : (nom, type cible en Silver)
# Les fichiers n'ont pas d'en-tête : les noms viennent du schéma TPCx-BB
# repris au Jour 1 (TP1/scripts/schema_tpcxbb.py). Les types sont NOS choix,
# vérifiés dans le notebook 01 (on n'utilise pas inferSchema).
# ---------------------------------------------------------------------------
COLONNES = {
    "store_sales": [
        ("ss_sold_date_sk", "bigint"), ("ss_sold_time_sk", "bigint"),
        ("ss_item_sk", "bigint"), ("ss_customer_sk", "bigint"),
        ("ss_cdemo_sk", "bigint"), ("ss_hdemo_sk", "bigint"),
        ("ss_addr_sk", "bigint"), ("ss_store_sk", "bigint"),
        ("ss_promo_sk", "bigint"), ("ss_ticket_number", "bigint"),
        ("ss_quantity", "int"),
        ("ss_wholesale_cost", "decimal(7,2)"), ("ss_list_price", "decimal(7,2)"),
        ("ss_sales_price", "decimal(7,2)"), ("ss_ext_discount_amt", "decimal(7,2)"),
        ("ss_ext_sales_price", "decimal(7,2)"), ("ss_ext_wholesale_cost", "decimal(7,2)"),
        ("ss_ext_list_price", "decimal(7,2)"), ("ss_ext_tax", "decimal(7,2)"),
        ("ss_coupon_amt", "decimal(7,2)"), ("ss_net_paid", "decimal(7,2)"),
        ("ss_net_paid_inc_tax", "decimal(7,2)"), ("ss_net_profit", "decimal(7,2)"),
    ],
    "item": [
        ("i_item_sk", "bigint"), ("i_item_id", "string"),
        ("i_rec_start_date", "date"), ("i_rec_end_date", "date"),
        ("i_item_desc", "string"), ("i_current_price", "decimal(7,2)"),
        ("i_wholesale_cost", "decimal(7,2)"), ("i_brand_id", "int"),
        ("i_brand", "string"), ("i_class_id", "int"), ("i_class", "string"),
        ("i_category_id", "int"), ("i_category", "string"),
        ("i_manufact_id", "int"), ("i_manufact", "string"), ("i_size", "string"),
        ("i_formulation", "string"), ("i_color", "string"), ("i_units", "string"),
        ("i_container", "string"), ("i_manager_id", "int"),
        ("i_product_name", "string"),
    ],
    "store": [
        ("s_store_sk", "bigint"), ("s_store_id", "string"),
        ("s_rec_start_date", "date"), ("s_rec_end_date", "date"),
        ("s_closed_date_sk", "bigint"), ("s_store_name", "string"),
        ("s_number_employees", "int"), ("s_floor_space", "int"),
        ("s_hours", "string"), ("s_manager", "string"), ("s_market_id", "int"),
        ("s_geography_class", "string"), ("s_market_desc", "string"),
        ("s_market_manager", "string"), ("s_division_id", "int"),
        ("s_division_name", "string"), ("s_company_id", "int"),
        ("s_company_name", "string"), ("s_street_number", "string"),
        ("s_street_name", "string"), ("s_street_type", "string"),
        ("s_suite_number", "string"), ("s_city", "string"), ("s_county", "string"),
        ("s_state", "string"), ("s_zip", "string"), ("s_country", "string"),
        ("s_gmt_offset", "decimal(5,2)"), ("s_tax_precentage", "decimal(5,2)"),
    ],
    "date_dim": [
        ("d_date_sk", "bigint"), ("d_date_id", "string"), ("d_date", "date"),
        ("d_month_seq", "int"), ("d_week_seq", "int"), ("d_quarter_seq", "int"),
        ("d_year", "int"), ("d_dow", "int"), ("d_moy", "int"), ("d_dom", "int"),
        ("d_qoy", "int"), ("d_fy_year", "int"), ("d_fy_quarter_seq", "int"),
        ("d_fy_week_seq", "int"), ("d_day_name", "string"),
        ("d_quarter_name", "string"), ("d_holiday", "string"),
        ("d_weekend", "string"), ("d_following_holiday", "string"),
        ("d_first_dom", "int"), ("d_last_dom", "int"), ("d_same_day_ly", "int"),
        ("d_same_day_lq", "int"), ("d_current_day", "string"),
        ("d_current_week", "string"), ("d_current_month", "string"),
        ("d_current_quarter", "string"), ("d_current_year", "string"),
    ],
}


# ---------------------------------------------------------------------------
# Spark
# ---------------------------------------------------------------------------
def creer_session(nom="TP3-Retail-Intelligence"):
    """Crée (ou réutilise) la session Spark en mode local.

    Mémoire volontairement limitée : le poste n'a que 15 Go de RAM.
    """
    os.environ.setdefault("JAVA_HOME", str(JAVA_HOME))
    from pyspark.sql import SparkSession

    spark = (
        SparkSession.builder
        .appName(nom)
        .master("local[*]")
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "8")   # petit volume : 8 suffisent
        .config("spark.sql.session.timeZone", "Europe/Paris")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    return spark


def lire_brut(spark, table):
    """Lit un fichier brut TEL QU'IL EST : toutes les colonnes en texte.

    - sep="|" : séparateur des fichiers TPCx-BB
    - header=False : pas de ligne d'en-tête, on donne les noms nous-mêmes
    - tout en string : on ne laisse pas Spark deviner les types ;
      la conversion se fait ensuite, de façon contrôlée, dans le notebook 02.
    """
    from pyspark.sql.types import StructType, StructField, StringType

    schema = StructType([StructField(nom, StringType()) for nom, _ in COLONNES[table]])
    return (
        spark.read
        .option("header", False)
        .option("sep", "|")
        .schema(schema)
        .csv(str(chemin_source(table)))
    )
