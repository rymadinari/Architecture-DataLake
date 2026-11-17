"""Génère UC01_dictionnaire_KPI.xlsx et UC01_inventaire_sources.xlsx.

Usage (après profilage.py) : .venv/bin/python J1_Retail_Intelligence/scripts/build_xlsx.py
"""
import csv
import sys
from pathlib import Path

import duckdb
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

sys.path.insert(0, str(Path(__file__).parent))
from schema_tpcxbb import SCHEMA  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "J1_Retail_Intelligence" / "01_UC01_besoin_exploration"
PREUVES = BASE / "preuves"
HEAD = PatternFill("solid", fgColor="17324D")
WRAP = Alignment(wrap_text=True, vertical="top")


def sheet(ws, header, rows, widths):
    ws.append(header)
    for r in rows:
        ws.append(list(r))
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = HEAD
        c.alignment = WRAP
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = WRAP
    ws.freeze_panes = "B2"
    ws.auto_filter.ref = ws.dimensions


def read_csv(name):
    with open(PREUVES / name, encoding="utf-8") as fh:
        return list(csv.reader(fh, delimiter=";"))


# ---------- Valeurs de contrôle calculées sur le kit (lot initial) ----------
con = duckdb.connect()
for t in ("store_sales", "web_sales", "store_returns", "web_returns", "inventory",
          "web_clickstreams", "store", "product_reviews", "date_dim"):
    names = "[" + ",".join(f"'{c}'" for c in SCHEMA[t]) + "]"
    con.execute(f"CREATE VIEW {t} AS SELECT * FROM read_csv('{ROOT}/retail_project/data/{t}/{t}.dat', "
                f"delim='|', header=false, names={names}, sample_size=-1, quote='', escape='')")
v = lambda sql: con.execute(sql).fetchone()  # noqa: E731
ss = v("SELECT sum(ss_net_paid), count(DISTINCT ss_ticket_number), sum(ss_quantity), "
       "sum(ss_ext_discount_amt)/sum(ss_ext_list_price), sum(ss_net_profit)/sum(ss_net_paid) FROM store_sales")
ws_ = v("SELECT sum(ws_net_paid), count(DISTINCT ws_order_number), sum(ws_quantity), "
        "sum(ws_ext_discount_amt)/sum(ws_ext_list_price), sum(ws_net_profit)/sum(ws_net_paid) FROM web_sales")
evo = v("SELECT sum(ss_net_paid) FILTER (WHERE d_year=2004) / sum(ss_net_paid) FILTER (WHERE d_year=2003) - 1 "
        "FROM store_sales JOIN date_dim ON ss_sold_date_sk=d_date_sk")
ret = (v("SELECT sum(sr_return_quantity) FROM store_returns")[0] / ss[2],
       v("SELECT sum(wr_return_quantity) FROM web_returns")[0] / ws_[2])
stk = v("SELECT sum(inv_quantity_on_hand), count(*) FILTER (WHERE inv_quantity_on_hand=0) FROM inventory "
        "WHERE inv_date_sk=(SELECT max(inv_date_sk) FROM inventory)")
conv = v("SELECT count(wcs_sales_sk)/count(*) FROM web_clickstreams")[0]
m2 = v("SELECT sum(ss_net_paid)/(SELECT sum(s_floor_space) FROM store), "
       "sum(ss_net_paid)/(SELECT sum(s_number_employees) FROM store) FROM store_sales")
rev = v("SELECT avg(pr_review_rating), count(*) FROM product_reviews")
fmt = lambda x: f"{x:,.0f}".replace(",", " ")  # noqa: E731

COLS = ["Code", "Nom", "Définition métier", "Formule", "Unité", "Périmètre", "Fréquence",
        "Sources nécessaires", "Données manquantes", "Limites d'interprétation", "Questions",
        "Statut", "Valeur de contrôle (lot data/, 2001-01-01 → 2005-12-13)"]
KPI = [
    ("K1", "Chiffre d'affaires net", "Montant encaissé sur les ventes, après remises et coupons, hors taxes et hors frais de port.",
     "SUM(ss_net_paid) + SUM(ws_net_paid)", "Unité monétaire (devise non précisée)",
     "Lignes de vente magasin et web ; avant déduction des retours ; ventilable par date, canal, magasin, produit, catégorie, client.",
     "Quotidienne (agrégats mensuels et annuels)", "store_sales, web_sales, date_dim, item, store",
     "Devise ; taxes et frais de port exclus volontairement.",
     "CA avant retours (voir K8). 2005 incomplète sans data_refresh. Valeurs synthétiques.",
     "Q1, Q3, Q5, Q7", "Couvert", f"Magasin {fmt(ss[0])} ; Web {fmt(ws_[0])}"),
    ("K2", "Nombre de transactions", "Nombre de tickets de caisse (magasin) ou de commandes (web) distincts.",
     "COUNT(DISTINCT ss_ticket_number) ; COUNT(DISTINCT ws_order_number)", "Nombre",
     "Par canal ; ne jamais additionner les numéros entre canaux sans préfixe (espaces de numérotation distincts).",
     "Quotidienne", "store_sales, web_sales", "—",
     "Une transaction n'est pas une ligne de vente (7,5 lignes par ticket en moyenne).",
     "Q5, Q7", "Couvert", f"Magasin {fmt(ss[1])} ; Web {fmt(ws_[1])}"),
    ("K3", "Panier moyen", "Montant moyen dépensé par transaction.",
     "K1 / K2 (par canal)", "Unité monétaire par transaction", "Par canal, magasin, période.",
     "Mensuelle", "store_sales, web_sales", "—",
     "Sensible aux tickets atypiques ; un panier web inclut éventuellement plusieurs livraisons.",
     "Q5", "Couvert", f"Magasin {ss[0]/ss[1]:,.2f} ; Web {ws_[0]/ws_[1]:,.2f}".replace(",", " ")),
    ("K4", "Quantités vendues", "Nombre d'unités vendues.", "SUM(ss_quantity) + SUM(ws_quantity)", "Unités",
     "Par produit, catégorie, canal, magasin, période.", "Quotidienne", "store_sales, web_sales, item",
     "Unité de vente du produit (i_units peu fiable).", "Additionner des unités de produits différents n'a de sens qu'au sein d'une même catégorie.",
     "Q3, Q6, Q7", "Couvert", f"Magasin {fmt(ss[2])} ; Web {fmt(ws_[2])}"),
    ("K5", "Taux de remise", "Part du prix catalogue accordée en remise.",
     "SUM(ext_discount_amt) / SUM(ext_list_price) ; part coupons = SUM(coupon_amt) / SUM(ext_sales_price)", "%",
     "Par canal, magasin, catégorie, promotion.", "Mensuelle", "store_sales, web_sales, promotion",
     "Lien fiable promotion ↔ période (dates de promotion aberrantes).",
     "Remise moyenne ~50 % : distribution artificielle. 99,98 % des lignes ont une promotion.",
     "Q4, Q8", "Couvert (réserve)", f"Magasin {ss[3]:.1%} ; Web {ws_[3]:.1%}"),
    ("K6", "Marge nette et taux de marge", "Différence entre le montant encaissé et le coût d'achat des produits vendus.",
     "SUM(net_profit) ; taux = SUM(net_profit) / SUM(net_paid)", "Unité monétaire ; %",
     "Par canal, produit, magasin.", "Mensuelle", "store_sales, web_sales",
     "Coûts logistiques et coûts fixes des magasins.",
     "74 % des lignes magasin à marge négative : indicateur non interprétable sur ce jeu synthétique.",
     "Q2, Q10", "Calculable, non fiable", f"Taux magasin {ss[4]:.1%} ; web {ws_[4]:.1%}"),
    ("K7", "Évolution du CA", "Variation relative du CA entre deux périodes comparables.",
     "(K1 période N − K1 période N−1) / K1 période N−1", "%",
     "À nombre de jours identique ; par canal, magasin, catégorie.", "Mensuelle et annuelle",
     "store_sales, web_sales, date_dim", "—",
     "2005 incomplète dans data/ ; saisonnalité quasi inexistante dans le jeu synthétique.",
     "Q1", "Couvert", f"Magasin 2004 vs 2003 : {evo[0]:+.2%}"),
    ("K8", "Taux de retour", "Part des unités vendues qui sont retournées.",
     "SUM(return_quantity) / SUM(quantity vendue), rattaché à la date de vente ; montant retourné = SUM(return_amt)", "%",
     "Par produit, catégorie, canal, magasin.", "Mensuelle", "store_returns, web_returns, store_sales, web_sales, item",
     "Motif de retour exploitable (libellés aléatoires).",
     "Retours jusqu'à 2 ans après la vente : le taux d'une période récente est provisoire. Jointure (ticket, produit) non unique.",
     "Q9, Q10", "Couvert", f"Magasin {ret[0]:.2%} ; Web {ret[1]:.2%}"),
    ("K9", "Stock disponible et ruptures", "Quantité en stock à une date donnée ; nombre de couples produit × entrepôt à zéro.",
     "SUM(inv_quantity_on_hand) à la date d'inventaire ; COUNT(*) WHERE inv_quantity_on_hand = 0", "Unités ; nombre",
     "Entrepôts (5) uniquement ; photo hebdomadaire.", "Hebdomadaire", "inventory, item, warehouse",
     "Stock magasin, mouvements d'entrée et sortie.",
     "Un stock null n'est pas un stock nul. Pas de lien avec les ventes magasin.",
     "Q11, Q12", "Couvert (entrepôts)", f"Au 2005-12-12 : {fmt(stk[0])} unités ; {fmt(stk[1])} couples à 0"),
    ("K10", "Taux de conversion web", "Part des clics rattachés à une vente.",
     "COUNT(wcs_sales_sk non null) / COUNT(*)", "%", "Site web ; par page, produit, période.", "Quotidienne",
     "web_clickstreams, web_sales, web_page", "Type d'événement, identifiant de session.",
     "Dépend de l'hypothèse H1 ; pas d'entonnoir vue → panier → achat ; 42 % des clics anonymes.",
     "Q13", "Partiel", f"{conv:.2%} des clics"),
    ("K11", "CA par m² et par employé", "Productivité commerciale d'un magasin.",
     "K1 magasin / s_floor_space ; K1 magasin / s_number_employees", "Unité monétaire par m² ; par employé",
     "Magasins (12).", "Annuelle", "store_sales, store", "Historique de la surface et des effectifs (valeur unique par magasin).",
     "Surface et effectif supposés constants sur 5 ans.", "Q5", "Couvert (réserve)",
     f"{m2[0]:.2f} par unité de surface ; {fmt(m2[1])} par employé (sur 5 ans)"),
    ("K12", "Note moyenne des avis", "Satisfaction exprimée par les clients sur un produit.",
     "AVG(pr_review_rating) ; COUNT(*)", "Note sur 5 ; nombre d'avis", "Par produit, catégorie.", "Mensuelle",
     "product_reviews, item", "—", "Biais de sélection (seuls certains clients notent) ; corrélation ≠ causalité avec les ventes.",
     "Q14", "Couvert", f"{rev[0]:.2f} / 5 sur {fmt(rev[1])} avis"),
    ("K13", "Rentabilité complète d'un magasin", "Résultat d'un magasin après coûts fixes.",
     "K6 magasin − (loyer + masse salariale + charges)", "Unité monétaire", "Magasins.", "Mensuelle",
     "Non disponible dans le kit", "Coûts fixes, budgets.", "Besoin non couvert : conservé comme besoin, non calculé.",
     "Q18", "Non disponible", "—"),
]
wb = Workbook()
sheet(wb.active, COLS, KPI, [6, 22, 34, 38, 16, 34, 14, 26, 26, 40, 10, 14, 30])
wb.active.title = "Dictionnaire KPI"
wb.save(BASE / "UC01_dictionnaire_KPI.xlsx")
print("OK UC01_dictionnaire_KPI.xlsx")

# ---------- Inventaire des sources ----------
QUAL = {
    "store_sales": ("ss_ticket_number + ss_item_sk (non unique)", "Bonne : montants cohérents, FK nulles < 0,1 %", "CA, transactions, panier, remises, marge", "Fait — Gold fact_sales"),
    "web_sales": ("ws_order_number + ws_item_sk (non unique)", "Bonne : montants cohérents, FK nulles < 0,1 %", "CA web, livraison, entrepôt", "Fait — Gold fact_sales"),
    "store_returns": ("sr_ticket_number + sr_item_sk", "Moyenne : 112 retours > quantité vendue", "Taux et coût des retours", "Fait — Gold fact_returns"),
    "web_returns": ("wr_order_number + wr_item_sk", "Bonne", "Taux et coût des retours", "Fait — Gold fact_returns"),
    "inventory": ("inv_date_sk + inv_item_sk + inv_warehouse_sk (unique)", "Moyenne : 232 380 lignes sur produits du refresh", "Stock hebdomadaire", "Fait — Gold fact_inventory"),
    "web_clickstreams": ("aucune", "Partielle : 90 % sans vente, 42 % anonymes, pas de type d'événement", "Conversion web", "Fait — Gold fact_clicks"),
    "product_reviews": ("pr_review_sk", "Bonne", "Satisfaction produit", "Fait — Gold fact_reviews"),
    "item": ("i_item_sk", "Bonne ; i_rec_end_date vide, i_container constant", "Analyse produit / catégorie", "Dimension dim_item"),
    "item_marketprices": ("imp_sk", "Moyenne : concurrents codés", "Comparaison de prix", "Dimension / fait secondaire"),
    "promotion": ("p_promo_sk", "Faible : dates aberrantes", "Analyse descriptive des promotions", "Dimension dim_promotion"),
    "customer": ("c_customer_sk", "Bonne ; données personnelles ; c_first_sales_date incohérent", "Segmentation", "Dimension dim_customer (pseudonymisée)"),
    "customer_address": ("ca_address_sk", "Bonne", "Localisation client", "Dimension dim_customer"),
    "customer_demographics": ("cd_demo_sk", "Bonne", "Segmentation", "Dimension dim_customer_demo"),
    "household_demographics": ("hd_demo_sk", "Bonne", "Segmentation", "Dimension dim_household"),
    "income_band": ("ib_income_band_sk", "Bonne", "Tranches de revenu", "Dimension dim_household"),
    "store": ("s_store_sk", "Moyenne : s_closed_date_sk aberrant", "Performance magasin", "Dimension dim_store"),
    "warehouse": ("w_warehouse_sk", "Bonne", "Stock par entrepôt", "Dimension dim_warehouse"),
    "web_page": ("wp_web_page_sk", "Bonne", "Analyse des pages", "Dimension dim_web_page"),
    "web_site": ("web_site_sk", "Bonne", "Analyse par site", "Dimension dim_web_site"),
    "date_dim": ("d_date_sk", "Bonne ; d_holiday inutilisable", "Axe temps", "Dimension dim_date"),
    "time_dim": ("t_time_sk", "Bonne", "Analyse horaire", "Dimension dim_time"),
    "reason": ("r_reason_sk", "Inexploitable : libellés aléatoires", "—", "Silver uniquement"),
    "ship_mode": ("sm_ship_mode_sk", "Inexploitable : libellés aléatoires", "—", "Silver uniquement"),
    "item_marketprices_audit": ("—", "Rapport de génération, non tabulaire", "Traçabilité", "Bronze (métadonnée)"),
}
wb = Workbook()
ws = wb.active
ws.title = "Kit"
sheet(ws, ["Information", "Valeur constatée", "Statut"], [
    ("Nom du kit", "retail_project (data/ + data_refresh/)", "Vérifié"),
    ("Provenance", "Kit fourni par le formateur, issu de TPCx-BB selon l'énoncé", "Vérifié"),
    ("Version", "Aucune version dans le kit ni indiquée par le formateur", "Non communiqué"),
    ("Date de mise à disposition", "16/11/2026 (fichiers préparés le 15/11/2026 23:34-23:36)", "Vérifié"),
    ("Source de distribution", "Lien Microsoft Teams partagé par le formateur", "Vérifié"),
    ("Format", "Texte délimité '|', sans en-tête, CRLF ; 2 CSV d'audit", "Vérifié"),
    ("Volume total", "1 033 993 587 octets (data/ 1 024 448 074 ; data_refresh/ 9 545 513)", "Vérifié"),
    ("Nombre de fichiers", "36 (24 dans data/, 12 dans data_refresh/)", "Vérifié"),
    ("Outil de génération", "Non documenté (rapport d'audit de générateur présent)", "Hypothèse"),
    ("Noms de colonnes", "Repris du schéma TPCx-BB, nombre de colonnes vérifié", "Déduit"),
], [28, 70, 16])

inv = read_csv("inventaire_fichiers.csv")
rows = []
for r in inv[1:]:
    k, qual, usage, dest = QUAL.get(r[1], ("", "", "", ""))
    cols = ", ".join(SCHEMA.get(r[1], []))
    rows.append(r[:4] + [r[4], int(r[5]), float(r[6]), int(r[7]), int(r[8]), cols, k, qual, usage, dest])
sheet(wb.create_sheet("Fichiers"),
      ["Lot", "Table", "Domaine", "Chemin", "Format", "Taille (octets)", "Taille (Mo)", "Nb lignes",
       "Nb colonnes", "Noms des colonnes (schéma TPCx-BB)", "Clé candidate", "Qualité constatée",
       "Usage analytique", "Destination logique"],
      rows, [12, 22, 20, 46, 26, 14, 10, 12, 8, 60, 30, 36, 30, 26])

prof = read_csv("profil_colonnes.csv")
sheet(wb.create_sheet("Colonnes"), prof[0] + ["Remarque"],
      [p[:5] + [int(p[5]), float(p[6]), int(p[7]), ""] for p in prof[1:]],
      [22, 28, 12, 22, 22, 14, 10, 12, 30])

rel = read_csv("relations_controles.csv")
sheet(wb.create_sheet("Relations"), rel[0] + ["Statut"],
      [r + ["Vérifiée" if r[9] == "0" else "Orphelins à traiter"] for r in rel[1:]],
      [20, 24, 22, 22, 10, 10, 12, 10, 8, 12, 18])

sheet(wb.create_sheet("Domaines"), ["Domaine", "Fichiers observés", "Présent", "Exploitable", "Commentaire"], [
    ("Ventes magasin", "store_sales", "Oui", "Oui", "667 579 lignes, 89 100 tickets, 12 magasins"),
    ("Ventes web", "web_sales", "Oui", "Oui", "668 052 lignes, 89 100 commandes"),
    ("Retours", "store_returns, web_returns, reason", "Oui", "Oui (sans motifs)", "Libellés de motif aléatoires"),
    ("Produits", "item, item_marketprices", "Oui", "Oui", "17 820 produits, 9 catégories"),
    ("Clients", "customer, customer_address, customer_demographics, household_demographics, income_band", "Oui", "Oui", "Données personnelles"),
    ("Magasins / entrepôts", "store, warehouse", "Oui", "Oui", "12 magasins, 5 entrepôts"),
    ("Stocks", "inventory", "Oui", "Partiel", "Entrepôts uniquement, hebdomadaire, pas de mouvements"),
    ("Navigation", "web_clickstreams, web_page, web_site", "Oui", "Partiel", "Pas de type d'événement ni de session"),
    ("Promotions", "promotion", "Oui", "Partiel", "Dates aberrantes"),
    ("Avis produits", "product_reviews", "Oui", "Oui", "Texte libre + note"),
    ("Dates et temps", "date_dim, time_dim", "Oui", "Oui", "d_holiday inutilisable"),
    ("Coûts, budgets, objectifs", "—", "Non", "—", "Source complémentaire nécessaire"),
    ("Trafic magasin", "—", "Non", "—", "Source complémentaire nécessaire"),
], [24, 50, 10, 16, 50])
wb.save(BASE / "UC01_inventaire_sources.xlsx")
print("OK UC01_inventaire_sources.xlsx")
