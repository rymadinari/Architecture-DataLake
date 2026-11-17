"""Profilage du kit TPCx-BB (UC-01, étape C et D).

Usage : .venv/bin/python J1_Retail_Intelligence/scripts/profilage.py
Produit les preuves dans 01_UC01_besoin_exploration/preuves/.
"""
import csv
import os
import sys
from pathlib import Path

import duckdb

sys.path.insert(0, str(Path(__file__).parent))
from schema_tpcxbb import DOMAINES, SCHEMA  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT / "retail_project"
OUT = ROOT / "J1_Retail_Intelligence" / "01_UC01_besoin_exploration" / "preuves"
OUT.mkdir(parents=True, exist_ok=True)

con = duckdb.connect()
log = open(OUT / "controles_resultats.txt", "w", encoding="utf-8")


def p(*a):
    print(*a)
    print(*a, file=log)


def q(sql):
    return con.execute(sql).fetchall()


# 1. Chargement : une vue par fichier (data = lot initial, r_ = data_refresh)
files = []
for lot, prefix in (("data", ""), ("data_refresh", "r_")):
    for d in sorted((KIT / lot).iterdir()):
        f = d / f"{d.name}.dat"
        if not f.exists():
            continue
        cols = SCHEMA[d.name]
        names = "[" + ",".join(f"'{c}'" for c in cols) + "]"
        con.execute(
            f"CREATE VIEW {prefix}{d.name} AS SELECT * FROM read_csv('{f}', delim='|', "
            f"header=false, names={names}, sample_size=-1, quote='', escape='')")
        files.append((lot, d.name, prefix + d.name, f))

# 2. Inventaire
inv_rows = []
for lot, table, view, f in files:
    n = q(f"SELECT count(*) FROM {view}")[0][0]
    inv_rows.append({
        "lot": lot, "table": table, "domaine": DOMAINES[table],
        "chemin": str(f.relative_to(ROOT)), "format": "texte délimité '|' sans en-tête, CRLF",
        "taille_octets": f.stat().st_size, "taille_Mo": round(f.stat().st_size / 1e6, 2),
        "nb_lignes": n, "nb_colonnes": len(SCHEMA[table]),
    })
for lot in ("data", "data_refresh"):
    f = KIT / lot / "item_marketprices" / "item_marketprices_audit.csv"
    inv_rows.append({
        "lot": lot, "table": "item_marketprices_audit", "domaine": "Métadonnées de génération",
        "chemin": str(f.relative_to(ROOT)), "format": "CSV ',' avec en-tête (rapport texte)",
        "taille_octets": f.stat().st_size, "taille_Mo": round(f.stat().st_size / 1e6, 2),
        "nb_lignes": sum(1 for _ in open(f, encoding="utf-8")), "nb_colonnes": 8,
    })
with open(OUT / "inventaire_fichiers.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(inv_rows[0]), delimiter=";")
    w.writeheader()
    w.writerows(inv_rows)
p("== INVENTAIRE ==")
for r in inv_rows:
    p(f"{r['lot']:13} {r['table']:24} {r['taille_Mo']:>9} Mo {r['nb_lignes']:>10} lignes {r['nb_colonnes']:>3} col")
p("Total octets :", sum(r["taille_octets"] for r in inv_rows), "| fichiers :", len(inv_rows))

# 3. Profil colonne par colonne (lot initial uniquement)
col_rows = []
for lot, table, view, f in files:
    if lot != "data":
        continue
    for r in con.execute(f"SUMMARIZE {view}").fetchdf().to_dict("records"):
        col_rows.append({
            "table": table, "colonne": r["column_name"], "type_detecte": r["column_type"],
            "min": str(r["min"])[:40], "max": str(r["max"])[:40],
            "distinct_approx": r["approx_unique"], "pct_null": r["null_percentage"],
            "nb_lignes": r["count"],
        })
with open(OUT / "profil_colonnes.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(col_rows[0]), delimiter=";")
    w.writeheader()
    w.writerows(col_rows)
p("\n== COLONNES AVEC VALEURS NULLES (lot initial) ==")
for r in col_rows:
    if float(r["pct_null"]) > 0:
        p(f"{r['table']:24} {r['colonne']:28} {float(r['pct_null']):6.2f} %")

# 4. Unicité des clés candidates
p("\n== UNICITÉ DES CLÉS CANDIDATES ==")
keys = {
    "customer": "c_customer_sk", "customer_address": "ca_address_sk",
    "customer_demographics": "cd_demo_sk", "household_demographics": "hd_demo_sk",
    "item": "i_item_sk", "store": "s_store_sk", "date_dim": "d_date_sk",
    "time_dim": "t_time_sk", "promotion": "p_promo_sk", "warehouse": "w_warehouse_sk",
    "web_page": "wp_web_page_sk", "web_site": "web_site_sk", "reason": "r_reason_sk",
    "product_reviews": "pr_review_sk", "item_marketprices": "imp_sk",
    "store_sales": "ss_ticket_number, ss_item_sk", "web_sales": "ws_order_number, ws_item_sk",
    "store_returns": "sr_ticket_number, sr_item_sk", "web_returns": "wr_order_number, wr_item_sk",
    "inventory": "inv_date_sk, inv_item_sk, inv_warehouse_sk",
}
key_rows = []
for t, k in keys.items():
    n, d = q(f"SELECT count(*), count(DISTINCT ({k})) FROM {t}")[0]
    nulls = q(f"SELECT count(*) FROM {t} WHERE " + " OR ".join(f"{c.strip()} IS NULL" for c in k.split(",")))[0][0]
    key_rows.append((t, k, n, d, nulls, "UNIQUE" if n == d and nulls == 0 else "NON UNIQUE"))
    p(f"{t:24} ({k}) lignes={n} distinct={d} nulls={nulls} -> {key_rows[-1][-1]}")

# 5. Intégrité référentielle (lignes de faits sans correspondance)
p("\n== RELATIONS : CLÉS ÉTRANGÈRES SANS CORRESPONDANCE ==")
rels = [
    ("store_sales", "ss_item_sk", "item", "i_item_sk"),
    ("store_sales", "ss_store_sk", "store", "s_store_sk"),
    ("store_sales", "ss_customer_sk", "customer", "c_customer_sk"),
    ("store_sales", "ss_sold_date_sk", "date_dim", "d_date_sk"),
    ("store_sales", "ss_sold_time_sk", "time_dim", "t_time_sk"),
    ("store_sales", "ss_promo_sk", "promotion", "p_promo_sk"),
    ("store_sales", "ss_cdemo_sk", "customer_demographics", "cd_demo_sk"),
    ("store_sales", "ss_hdemo_sk", "household_demographics", "hd_demo_sk"),
    ("store_sales", "ss_addr_sk", "customer_address", "ca_address_sk"),
    ("web_sales", "ws_item_sk", "item", "i_item_sk"),
    ("web_sales", "ws_bill_customer_sk", "customer", "c_customer_sk"),
    ("web_sales", "ws_sold_date_sk", "date_dim", "d_date_sk"),
    ("web_sales", "ws_web_site_sk", "web_site", "web_site_sk"),
    ("web_sales", "ws_web_page_sk", "web_page", "wp_web_page_sk"),
    ("web_sales", "ws_warehouse_sk", "warehouse", "w_warehouse_sk"),
    ("web_sales", "ws_ship_mode_sk", "ship_mode", "sm_ship_mode_sk"),
    ("web_sales", "ws_promo_sk", "promotion", "p_promo_sk"),
    ("store_returns", "sr_item_sk", "item", "i_item_sk"),
    ("store_returns", "sr_store_sk", "store", "s_store_sk"),
    ("store_returns", "sr_reason_sk", "reason", "r_reason_sk"),
    ("web_returns", "wr_item_sk", "item", "i_item_sk"),
    ("web_returns", "wr_reason_sk", "reason", "r_reason_sk"),
    ("inventory", "inv_item_sk", "item", "i_item_sk"),
    ("inventory", "inv_warehouse_sk", "warehouse", "w_warehouse_sk"),
    ("inventory", "inv_date_sk", "date_dim", "d_date_sk"),
    ("web_clickstreams", "wcs_item_sk", "item", "i_item_sk"),
    ("web_clickstreams", "wcs_web_page_sk", "web_page", "wp_web_page_sk"),
    ("web_clickstreams", "wcs_user_sk", "customer", "c_customer_sk"),
    ("web_clickstreams", "wcs_click_date_sk", "date_dim", "d_date_sk"),
    ("product_reviews", "pr_item_sk", "item", "i_item_sk"),
    ("product_reviews", "pr_user_sk", "customer", "c_customer_sk"),
    ("customer", "c_current_addr_sk", "customer_address", "ca_address_sk"),
    ("customer", "c_current_cdemo_sk", "customer_demographics", "cd_demo_sk"),
    ("customer", "c_current_hdemo_sk", "household_demographics", "hd_demo_sk"),
    ("household_demographics", "hd_income_band_sk", "income_band", "ib_income_band_sk"),
    ("item_marketprices", "imp_item_sk", "item", "i_item_sk"),
    ("promotion", "p_item_sk", "item", "i_item_sk"),
]
rel_rows = []
for ft, fk, dt, pk in rels:
    tot, nul, orphan = q(f"""
        SELECT count(*), count(*) FILTER (WHERE f.{fk} IS NULL),
               count(*) FILTER (WHERE f.{fk} IS NOT NULL AND d.{pk} IS NULL)
        FROM {ft} f LEFT JOIN (SELECT DISTINCT {pk} FROM {dt}) d ON f.{fk} = d.{pk}""")[0]
    ftype = q(f"SELECT typeof({fk}) FROM {ft} WHERE {fk} IS NOT NULL LIMIT 1")
    dtype = q(f"SELECT typeof({pk}) FROM {dt} LIMIT 1")[0][0]
    ftype = ftype[0][0] if ftype else "-"
    rel_rows.append((ft, fk, dt, pk, ftype, dtype, tot, nul, round(100 * nul / tot, 2), orphan))
    p(f"{ft}.{fk} -> {dt}.{pk} [{ftype}/{dtype}] lignes={tot} null={nul} ({100*nul/tot:.2f}%) orphelins={orphan}")
with open(OUT / "relations_controles.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh, delimiter=";")
    w.writerow(["table_fait", "cle_etrangere", "table_ref", "cle_ref", "type_fk", "type_pk",
                "nb_lignes", "nb_null", "pct_null", "nb_orphelins"])
    w.writerows(rel_rows)

# 6. Contrôles métier
p("\n== PÉRIODES COUVERTES ==")
for t, c in (("store_sales", "ss_sold_date_sk"), ("web_sales", "ws_sold_date_sk"),
             ("store_returns", "sr_returned_date_sk"), ("web_returns", "wr_returned_date_sk"),
             ("inventory", "inv_date_sk"), ("web_clickstreams", "wcs_click_date_sk"),
             ("r_store_sales", "ss_sold_date_sk"), ("r_web_sales", "ws_sold_date_sk"),
             ("r_inventory", "inv_date_sk"), ("r_web_clickstreams", "wcs_click_date_sk")):
    r = q(f"SELECT min(d.d_date), max(d.d_date), count(DISTINCT d.d_date) FROM {t} f "
          f"JOIN date_dim d ON f.{c} = d.d_date_sk")[0]
    p(f"{t:22} du {r[0]} au {r[1]} ({r[2]} jours distincts)")
p("date_dim :", q("SELECT min(d_date), max(d_date) FROM date_dim")[0])
p("inventory : dates d'inventaire distinctes =", q("SELECT count(DISTINCT inv_date_sk) FROM inventory")[0][0],
  "| écart en jours =", q("SELECT list(DISTINCT d) FROM (SELECT inv_date_sk - lag(inv_date_sk) OVER (ORDER BY inv_date_sk) d FROM (SELECT DISTINCT inv_date_sk FROM inventory)) WHERE d IS NOT NULL")[0][0])

p("\n== GRAIN DES VENTES ==")
for t, tick, item in (("store_sales", "ss_ticket_number", "ss_item_sk"), ("web_sales", "ws_order_number", "ws_item_sk")):
    r = q(f"SELECT count(*), count(DISTINCT {tick}), round(count(*)/count(DISTINCT {tick}),2) FROM {t}")[0]
    p(f"{t}: lignes={r[0]} tickets/commandes distincts={r[1]} lignes par ticket={r[2]}")

p("\n== COHÉRENCE DES MONTANTS ==")
p("store_sales ext_sales_price <> quantity*sales_price (écart>0.01) :",
  q("SELECT count(*) FROM store_sales WHERE abs(ss_ext_sales_price - ss_quantity*ss_sales_price) > 0.01")[0][0])
p("store_sales net_profit <> net_paid - ext_wholesale_cost :",
  q("SELECT count(*) FROM store_sales WHERE abs(ss_net_profit - (ss_net_paid - ss_ext_wholesale_cost)) > 0.01")[0][0])
p("store_sales sales_price > list_price :",
  q("SELECT count(*) FROM store_sales WHERE ss_sales_price > ss_list_price")[0][0])
p("store_sales net_profit < 0 (lignes) :",
  q("SELECT count(*), round(100*count(*)/(SELECT count(*) FROM store_sales),2) FROM store_sales WHERE ss_net_profit < 0")[0])
p("web_sales ext_sales_price <> quantity*sales_price :",
  q("SELECT count(*) FROM web_sales WHERE abs(ws_ext_sales_price - ws_quantity*ws_sales_price) > 0.01")[0][0])
p("web_sales ship_date < sold_date :",
  q("SELECT count(*) FROM web_sales WHERE ws_ship_date_sk < ws_sold_date_sk")[0][0])
p("quantités min/max store / web :",
  q("SELECT min(ss_quantity), max(ss_quantity) FROM store_sales")[0], q("SELECT min(ws_quantity), max(ws_quantity) FROM web_sales")[0])
p("inventory quantity_on_hand min/max/null :",
  q("SELECT min(inv_quantity_on_hand), max(inv_quantity_on_hand), count(*) FILTER (WHERE inv_quantity_on_hand IS NULL) FROM inventory")[0])

p("\n== RETOURS -> VENTES ==")
p("store_returns retrouvés dans store_sales (ticket+item) :",
  q("SELECT count(*), count(s.ss_item_sk) FROM store_returns r LEFT JOIN store_sales s ON r.sr_ticket_number=s.ss_ticket_number AND r.sr_item_sk=s.ss_item_sk")[0])
p("web_returns retrouvés dans web_sales (order+item) :",
  q("SELECT count(*), count(s.ws_item_sk) FROM web_returns r LEFT JOIN web_sales s ON r.wr_order_number=s.ws_order_number AND r.wr_item_sk=s.ws_item_sk")[0])
p("store_returns quantité retournée > quantité vendue :",
  q("SELECT count(*) FROM store_returns r JOIN store_sales s ON r.sr_ticket_number=s.ss_ticket_number AND r.sr_item_sk=s.ss_item_sk WHERE r.sr_return_quantity > s.ss_quantity")[0][0])
p("store_returns date retour < date vente :",
  q("SELECT count(*) FROM store_returns r JOIN store_sales s ON r.sr_ticket_number=s.ss_ticket_number AND r.sr_item_sk=s.ss_item_sk WHERE r.sr_returned_date_sk < s.ss_sold_date_sk")[0][0])
p("taux de lignes retournées store / web (%) :",
  q("SELECT round(100.0*(SELECT count(*) FROM store_returns)/(SELECT count(*) FROM store_sales),2), round(100.0*(SELECT count(*) FROM web_returns)/(SELECT count(*) FROM web_sales),2)")[0])

p("\n== NAVIGATION ==")
p("clics totaux / avec wcs_sales_sk / avec wcs_user_sk :",
  q("SELECT count(*), count(wcs_sales_sk), count(wcs_user_sk) FROM web_clickstreams")[0])
p("wcs_sales_sk retrouvé dans web_sales.ws_order_number :",
  q("SELECT count(*) FROM (SELECT DISTINCT wcs_sales_sk s FROM web_clickstreams WHERE wcs_sales_sk IS NOT NULL) c JOIN (SELECT DISTINCT ws_order_number o FROM web_sales) w ON c.s=w.o")[0][0],
  "sur", q("SELECT count(DISTINCT wcs_sales_sk) FROM web_clickstreams")[0][0], "valeurs distinctes")

p("\n== RÉFÉRENTIELS ==")
p("store :", q("SELECT s_store_sk, s_store_name, s_city, s_state, s_closed_date_sk, s_number_employees FROM store ORDER BY 1"))
p("store.s_closed_date_sk -> date :", q("SELECT s_store_sk, d_date FROM store LEFT JOIN date_dim ON s_closed_date_sk=d_date_sk ORDER BY 1"))
p("item catégories :", q("SELECT i_category, count(*) FROM item GROUP BY 1 ORDER BY 2 DESC"))
p("item i_rec_end_date renseigné :", q("SELECT count(i_rec_end_date) FROM item")[0][0], "| i_item_id distincts :", q("SELECT count(DISTINCT i_item_id) FROM item")[0][0])
p("item prix courant min/max/null :", q("SELECT min(i_current_price), max(i_current_price), count(*)-count(i_current_price) FROM item")[0])
p("customer_demographics genres :", q("SELECT cd_gender, count(*) FROM customer_demographics GROUP BY 1"))
p("customer c_birth_year min/max :", q("SELECT min(c_birth_year), max(c_birth_year) FROM customer")[0])
p("customer c_last_review_date exemples :", q("SELECT c_last_review_date FROM customer LIMIT 3"))
p("customer emails distincts / lignes :", q("SELECT count(DISTINCT c_email_address), count(*) FROM customer")[0])
p("reason exemples :", q("SELECT * FROM reason LIMIT 3"))
p("ship_mode exemples :", q("SELECT sm_type, sm_carrier FROM ship_mode LIMIT 3"))
p("web_page types :", q("SELECT wp_type, count(*) FROM web_page GROUP BY 1"))
p("promotion canaux (email/tv) :", q("SELECT p_channel_email, p_channel_tv, count(*) FROM promotion GROUP BY 1,2 ORDER BY 3 DESC"))
p("product_reviews note min/max :", q("SELECT pr_review_rating, count(*) FROM product_reviews GROUP BY 1 ORDER BY 1"))

p("\n== LOT DATA_REFRESH ==")
for t, k in (("customer", "c_customer_sk"), ("item", "i_item_sk"), ("customer_address", "ca_address_sk")):
    r = q(f"SELECT min({k}), max({k}), (SELECT count(*) FROM r_{t} x JOIN {t} y USING ({k})) FROM r_{t}")[0]
    p(f"r_{t}: clés {r[0]}..{r[1]}, chevauchement avec lot initial = {r[2]}")
p("r_store_sales tickets déjà présents dans store_sales :",
  q("SELECT count(*) FROM (SELECT DISTINCT ss_ticket_number FROM r_store_sales) r JOIN (SELECT DISTINCT ss_ticket_number FROM store_sales) s USING (ss_ticket_number)")[0][0])
p("r_store_sales items absents de item (initial) mais présents dans r_item :",
  q("SELECT count(*) FROM r_store_sales WHERE ss_item_sk NOT IN (SELECT i_item_sk FROM item) AND ss_item_sk IN (SELECT i_item_sk FROM r_item)")[0][0])
p("r_web_sales lignes avec ws_bill_hdemo_sk null :", q("SELECT count(*) - count(ws_bill_hdemo_sk), count(*) FROM r_web_sales")[0])
p("r_store_sales tickets min/max/distincts :", q("SELECT min(ss_ticket_number), max(ss_ticket_number), count(DISTINCT ss_ticket_number) FROM r_store_sales")[0])
p("r_store_returns retrouvés dans store_sales initial / dans r_store_sales :",
  q("SELECT count(*), count(s.ss_item_sk) FROM r_store_returns r LEFT JOIN store_sales s ON r.sr_ticket_number=s.ss_ticket_number AND r.sr_item_sk=s.ss_item_sk")[0],
  q("SELECT count(*), count(s.ss_item_sk) FROM r_store_returns r LEFT JOIN r_store_sales s ON r.sr_ticket_number=s.ss_ticket_number AND r.sr_item_sk=s.ss_item_sk")[0])
p("r_web_returns retrouvés dans web_sales initial / dans r_web_sales :",
  q("SELECT count(*), count(s.ws_item_sk) FROM r_web_returns r LEFT JOIN web_sales s ON r.wr_order_number=s.ws_order_number AND r.wr_item_sk=s.ws_item_sk")[0],
  q("SELECT count(*), count(s.ws_item_sk) FROM r_web_returns r LEFT JOIN r_web_sales s ON r.wr_order_number=s.ws_order_number AND r.wr_item_sk=s.ws_item_sk")[0])

p("\n== CONTRÔLES COMPLÉMENTAIRES ==")
p("inventory : produits orphelins (absents de data/item) min/max/distincts :",
  q("SELECT min(inv_item_sk), max(inv_item_sk), count(DISTINCT inv_item_sk) FROM inventory WHERE inv_item_sk NOT IN (SELECT i_item_sk FROM item)")[0])
p("inventory : ces produits existent dans data_refresh/item :",
  q("SELECT count(DISTINCT inv_item_sk) FROM inventory WHERE inv_item_sk IN (SELECT i_item_sk FROM r_item)")[0][0])
p("store_sales : tickets avec >1 client, magasin ou date :",
  q("SELECT count(*) FROM (SELECT ss_ticket_number FROM store_sales GROUP BY 1 HAVING count(DISTINCT ss_customer_sk)>1 OR count(DISTINCT ss_store_sk)>1 OR count(DISTINCT ss_sold_date_sk)>1)")[0][0])
p("web_sales : commandes avec >1 client facturé ou date :",
  q("SELECT count(*) FROM (SELECT ws_order_number FROM web_sales GROUP BY 1 HAVING count(DISTINCT ws_bill_customer_sk)>1 OR count(DISTINCT ws_sold_date_sk)>1)")[0][0])
p("store_sales : doublons exacts (lignes identiques) :",
  q("SELECT (SELECT count(*) FROM store_sales) - (SELECT count(*) FROM (SELECT DISTINCT * FROM store_sales))")[0][0])
p("store_sales : exemples de (ticket, item) répétés :",
  q("SELECT ss_ticket_number, ss_item_sk, count(*) FROM store_sales GROUP BY 1,2 HAVING count(*)>1 ORDER BY 1 LIMIT 3"))
p("CA net payé (net_paid) par année et canal :",
  q("SELECT d_year, 'store', round(sum(ss_net_paid)) FROM store_sales JOIN date_dim ON ss_sold_date_sk=d_date_sk GROUP BY 1 "
    "UNION ALL SELECT d_year, 'web', round(sum(ws_net_paid)) FROM web_sales JOIN date_dim ON ws_sold_date_sk=d_date_sk GROUP BY 1 ORDER BY 1,2"))
p("CA net payé et tickets par magasin :",
  q("SELECT ss_store_sk, round(sum(ss_net_paid)), count(DISTINCT ss_ticket_number) FROM store_sales GROUP BY 1 ORDER BY 1"))
p("taux de remise global store (ext_discount/ext_list, %) et part coupons (%) :",
  q("SELECT round(100*sum(ss_ext_discount_amt)/sum(ss_ext_list_price),2), round(100*sum(ss_coupon_amt)/sum(ss_ext_sales_price),2) FROM store_sales")[0])
p("panier moyen store / web (net_paid par ticket/commande) :",
  q("SELECT round(sum(ss_net_paid)/count(DISTINCT ss_ticket_number),2) FROM store_sales")[0][0],
  q("SELECT round(sum(ws_net_paid)/count(DISTINCT ws_order_number),2) FROM web_sales")[0][0])
p("clients acheteurs distincts store / web :",
  q("SELECT count(DISTINCT ss_customer_sk) FROM store_sales")[0][0], q("SELECT count(DISTINCT ws_bill_customer_sk) FROM web_sales")[0][0])
p("clics avec wcs_sales_sk mais wcs_user_sk null :",
  q("SELECT count(*) FROM web_clickstreams WHERE wcs_sales_sk IS NOT NULL AND wcs_user_sk IS NULL")[0][0])
p("product_reviews.pr_order_sk présents dans ws_order_number / min-max :",
  q("SELECT count(*) FROM product_reviews WHERE pr_order_sk IN (SELECT ws_order_number FROM web_sales)")[0][0],
  q("SELECT min(pr_order_sk), max(pr_order_sk) FROM product_reviews")[0])
p("date_dim.d_holiday répartition :", q("SELECT d_holiday, count(*) FROM date_dim GROUP BY 1"))
p("item.i_container répartition :", q("SELECT i_container, count(*) FROM item GROUP BY 1"))
p("customer : c_first_sales_date hors 2001-2005 / total renseigné :",
  q("SELECT count(*) FILTER (WHERE d.d_date NOT BETWEEN DATE '2001-01-01' AND DATE '2005-12-31'), count(*) FROM customer c JOIN date_dim d ON c.c_first_sales_date_sk=d.d_date_sk")[0])
p("customer : premier envoi avant premier achat :",
  q("SELECT count(*) FROM customer WHERE c_first_shipto_date_sk < c_first_sales_date_sk")[0][0])
p("promotion : dates de début min/max :",
  q("SELECT min(d.d_date), max(d.d_date) FROM promotion p JOIN date_dim d ON p.p_start_date_sk=d.d_date_sk")[0])
p("store_sales : lignes avec promo dont la vente est hors période de la promotion :",
  q("SELECT count(*) FROM store_sales s JOIN promotion p ON s.ss_promo_sk=p.p_promo_sk WHERE s.ss_sold_date_sk NOT BETWEEN p.p_start_date_sk AND p.p_end_date_sk")[0][0])
p("web_site : noms distincts :", q("SELECT web_name, count(*) FROM web_site GROUP BY 1 ORDER BY 1"))
log.close()
print("\nPreuves écrites dans", OUT)
