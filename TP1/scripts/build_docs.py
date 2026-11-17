"""Génère les PDF des livrables à partir des sources Markdown (sources/*.md).

Usage : .venv/bin/python J1_Retail_Intelligence/scripts/build_docs.py
Rendu : Markdown -> HTML (python-markdown) -> PDF (Chrome headless).
"""
import subprocess
import tempfile
from pathlib import Path

import markdown

BASE = Path(__file__).resolve().parents[1]
SRC = BASE / "sources"

TARGETS = {
    "UC01_cadrage_metier.md": "01_UC01_besoin_exploration/UC01_cadrage_metier.pdf",
    "UC01_questions_decisionnelles.md": "01_UC01_besoin_exploration/UC01_questions_decisionnelles.pdf",
    "UC01_qualification_donnees.md": "01_UC01_besoin_exploration/UC01_qualification_donnees.pdf",
    "UC01_limites_et_hypotheses.md": "01_UC01_besoin_exploration/UC01_limites_et_hypotheses.pdf",
    "UC02_comparaison_architectures.md": "02_UC02_architecture/UC02_comparaison_architectures.pdf",
    "UC02_architecture_cible.md": "02_UC02_architecture/UC02_architecture_cible.pdf",
    "UC02_schema_flux.md": "02_UC02_architecture/UC02_schema_flux.pdf",
    "UC02_positionnement_composants.md": "02_UC02_architecture/UC02_positionnement_composants.pdf",
    "UC02_gouvernance.md": "02_UC02_architecture/UC02_gouvernance.pdf",
    "UC02_local_vers_azure.md": "02_UC02_architecture/UC02_local_vers_azure.pdf",
    "contribution_ryma_dinari.md": "05_contribution_individuelle/contribution_ryma_dinari.pdf",
}

TEMPLATE = """<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<title>{title}</title><style>{css}</style></head><body>
<header class="run">Retail Intelligence Platform — TP Jour 1 — IPSSI</header>
{body}</body></html>"""


def build(name, target):
    text = (SRC / name).read_text(encoding="utf-8")
    title = text.splitlines()[0].lstrip("# ").strip()
    body = markdown.markdown(text, extensions=["tables", "md_in_html", "sane_lists", "attr_list"])
    html = TEMPLATE.format(title=title, css=(SRC / "style.css").read_text(encoding="utf-8"), body=body)
    out = BASE / target
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as fh:
        fh.write(html)
    subprocess.run(
        ["google-chrome", "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={out}", fh.name],
        check=True, capture_output=True)
    Path(fh.name).unlink()
    print("OK", out.relative_to(BASE))


if __name__ == "__main__":
    for n, t in TARGETS.items():
        if (SRC / n).exists():
            build(n, t)
