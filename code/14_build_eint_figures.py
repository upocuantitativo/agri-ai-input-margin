# -*- coding: utf-8 -*-
"""
14_build_eint_figures.py

Builds the FINAL figure set for the submission to
*Economics of Innovation and New Technology* (Taylor & Francis).

Output tree
-----------
article/EINT_submission/figures/
    Figure1.png ... Figure5.png          main text, 300 dpi, RGB, 180 mm wide
    supplementary/FigureS1.png ... FigureS11.png   copied from figures/

Provenance
----------
Every number plotted is READ FROM results/12_ai_observable.json, which is the
output of analysis/12_ai_observable.py.  Nothing is recomputed and nothing is
hard-coded, with the single exception of the axis/label strings.  The JSON key
used for each series is stated in the SOURCE comment above each figure.

Figures 1-4 are re-renderings of figures fig11-fig14 at print resolution;
Figure 4 additionally carries a THIRD bar series (median nitrogen dose) that
replaces a table cut from the manuscript.  Figure 5 is new.

Style
-----
Same palette family as figs 11-15 of 12_ai_observable.py:
    #1f4e79 dark blue (primary)   #c0504d brick red (secondary)
    #8fa9c4 light blue            #bdbdbd grey (placebo / neutral)
    #e8a33d amber -- added ONLY for the third series of Figure 4.  Checked with
    the dataviz palette validator: worst adjacent CVD separation dE 13.5
    (protan) / 19.7 (tritan) and normal-vision dE 22.2, all above the dE 8
    target; its sub-3:1 contrast against white is relieved by the value label
    printed on every bar.
"""
import json
import os
import shutil

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib.ticker import ScalarFormatter
from PIL import Image

# --------------------------------------------------------------- paths
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
RES = os.path.join(ROOT, "results")
FIG_SRC = os.path.join(ROOT, "figures")
OUT = os.path.join(ROOT, "article", "EINT_submission", "figures")
OUT_SUP = os.path.join(OUT, "supplementary")
os.makedirs(OUT, exist_ok=True)
os.makedirs(OUT_SUP, exist_ok=True)

with open(os.path.join(RES, "12_ai_observable.json"), encoding="utf-8") as f:
    R = json.load(f)

# --------------------------------------------------------------- style
MM180 = 180 / 25.4          # 180 mm in inches -> 2126 px at 300 dpi
DPI = 300

BLUE = "#1f4e79"
RED = "#c0504d"
LBLUE = "#8fa9c4"
GREY = "#bdbdbd"
AMBER = "#e8a33d"
INK = "#222222"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 9.5,
    "axes.titlesize": 10.5,
    "axes.labelsize": 9.5,
    "xtick.labelsize": 9.0,
    "ytick.labelsize": 9.0,
    "legend.fontsize": 9.0,
    "axes.edgecolor": "#555555",
    "axes.linewidth": 0.8,
    "axes.labelcolor": INK,
    "text.color": INK,
    "xtick.color": "#555555",
    "ytick.color": "#555555",
    "grid.color": "#cccccc",
    "grid.linewidth": 0.6,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
})


def panel_tag(ax, tag):
    """(a) / (b) tag in the upper-left outside corner of the axes."""
    ax.text(-0.10, 1.06, tag, transform=ax.transAxes, fontsize=10.5,
            fontweight="bold", va="bottom", ha="left", color=INK)


def save(fig, name):
    """Save at 300 dpi and flatten RGBA -> RGB on white (journal requirement)."""
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=DPI)
    plt.close(fig)
    im = Image.open(path)
    if im.mode != "RGB":
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.split()[-1] if im.mode == "RGBA" else None)
        bg.save(path, dpi=(DPI, DPI))
    else:
        im.save(path, dpi=(DPI, DPI))
    print("  wrote", path, Image.open(path).size, Image.open(path).mode)


# ==================================================================== Figure 1
# SOURCE: A_descriptivos_IA.serie_mundial  (year, ai_ag, share_permil)
def figure1():
    s = R["A_descriptivos_IA"]["serie_mundial"]
    yr = np.array([r["year"] for r in s], dtype=float)
    works = np.array([r["ai_ag"] for r in s], dtype=float)
    share = np.array([r["share_permil"] for r in s], dtype=float)

    fig, ax = plt.subplots(1, 2, figsize=(MM180, 3.05))

    ax[0].plot(yr, works, marker="o", ms=3.2, lw=1.8, color=BLUE,
               mfc="white", mew=1.0)
    ax[0].set_yscale("log")
    ax[0].yaxis.set_major_formatter(ScalarFormatter())
    ax[0].set_title("AI-in-agriculture publications (world)")
    ax[0].set_xlabel("Year")
    ax[0].set_ylabel("Works per year (log scale)")

    ax[1].plot(yr, share, marker="s", ms=3.2, lw=1.8, color=RED,
               mfc="white", mew=1.0)
    ax[1].set_title("Share of world research output")
    ax[1].set_xlabel("Year")
    ax[1].set_ylabel("AI-in-agriculture works\nper 1,000 works")

    for i, a in enumerate(ax):
        a.axvline(2016, ls="--", c="#777777", lw=1.0, zorder=0)
        a.annotate("2016", xy=(2016, 1.0), xycoords=("data", "axes fraction"),
                   xytext=(3, -11), textcoords="offset points",
                   fontsize=8.5, color="#555555", ha="left", va="top")
        a.grid(alpha=.35, lw=.6)
        a.set_axisbelow(True)
        a.set_xlim(yr.min() - 0.7, yr.max() + 0.7)
        a.set_xticks(np.arange(2000, 2025, 5))
        panel_tag(a, "(a)" if i == 0 else "(b)")

    fig.tight_layout(rect=[0, 0, 1, 0.97])
    save(fig, "Figure1.png")


# ==================================================================== Figure 2
# SOURCE (left) : HA2_margen_de_valor_y_complementariedad.margen_especializacion
#                 .{log_yield,log_n_x,log_nue}.z_spec -> b, se
# SOURCE (right): HA2_margen_de_valor_y_complementariedad
#                 .condicional_a_complementos.log_n_x.efectos_marginales
#                 .{p10,p50,p90} -> efecto_marginal, se
def figure2():
    h = R["HA2_margen_de_valor_y_complementariedad"]

    ys = ["log_yield", "log_n_x", "log_nue"]
    labs = ["Yield\n(output level)", "Nitrogen dose\n(input)",
            "Nitrogen use\nefficiency"]
    b = np.array([h["margen_especializacion"][y]["z_spec"]["b"] for y in ys])
    se = np.array([h["margen_especializacion"][y]["z_spec"]["se"] for y in ys])
    cols = [LBLUE, RED, BLUE]

    mg = h["condicional_a_complementos"]["log_n_x"]["efectos_marginales"]
    ks = ["p10", "p50", "p90"]
    bb = np.array([mg[k]["efecto_marginal"] for k in ks])
    ss = np.array([mg[k]["se"] for k in ks])

    fig, ax = plt.subplots(1, 2, figsize=(MM180, 3.55))

    ax[0].bar(np.arange(3), b, width=.62, color=cols,
              edgecolor="#2b2b2b", linewidth=.5,
              yerr=1.96 * se, capsize=4,
              error_kw=dict(ecolor=INK, elinewidth=1.0, capthick=1.0))
    ax[0].axhline(0, c=INK, lw=.9)
    ax[0].set_xticks(np.arange(3))
    ax[0].set_xticklabels(labs, fontsize=8.8)
    ax[0].set_ylabel("Effect of +1 SD of AI specialisation\n(log points)")
    ax[0].set_title("Where the value of AI shows up")
    for i, (v, e) in enumerate(zip(b, 1.96 * se)):
        off = 6 if v >= 0 else -6
        va = "bottom" if v >= 0 else "top"
        ax[0].annotate(f"{v:+.3f}", xy=(i, v + np.sign(v) * e),
                       xytext=(0, off), textcoords="offset points",
                       ha="center", va=va, fontsize=8.5, color=INK)
    ax[0].margins(y=.22)

    ax[1].errorbar(np.arange(3), bb, yerr=1.96 * ss, fmt="o", ms=7,
                   capsize=4, lw=1.4, color=RED, mfc="white", mew=1.8,
                   ecolor=RED)
    ax[1].axhline(0, c=INK, lw=.9)
    ax[1].set_xticks(np.arange(3))
    ax[1].set_xticklabels(["Low\ncomplements\n(P10)", "Median\n(P50)",
                           "High\ncomplements\n(P90)"], fontsize=8.8)
    ax[1].set_xlim(-.50, 2.85)
    ax[1].set_ylabel("Effect of AI on nitrogen dose\n(log points)")
    ax[1].set_title("Input saving requires complements")
    for i, v in enumerate(bb):
        ax[1].annotate(f"{v:+.3f}", xy=(i, v), xytext=(9, 0),
                       textcoords="offset points", ha="left", va="center",
                       fontsize=8.5, color=INK)
    ax[1].margins(y=.20)

    for i, a in enumerate(ax):
        a.grid(alpha=.35, axis="y", lw=.6)
        a.set_axisbelow(True)
        panel_tag(a, "(a)" if i == 0 else "(b)")

    fig.tight_layout(rect=[0, 0, 1, 0.97])
    save(fig, "Figure2.png")


# ==================================================================== Figure 3
# SOURCE: HA3_test_diferencial_entre_oleadas.<wave>.interaccion -> b, se, p
def figure3():
    h3 = R["HA3_test_diferencial_entre_oleadas"]
    order = [
        ("oleada_fertilizante_1961_1990", "Fertiliser\n1961-1990", LBLUE),
        ("oleada_mecanizacion_1961_2009", "Mechanisation\n1961-2009", LBLUE),
        ("oleada_IA_2000_2023", "AI\n2000-2023", RED),
        ("placebo_investigacion_no_IA_2000_2023",
         "Placebo:\nnon-AI research\n2000-2023", GREY),
    ]
    order = [(k, l, c) for k, l, c in order if h3.get(k)]
    vals = np.array([h3[k]["interaccion"]["b"] for k, _, _ in order])
    errs = np.array([1.96 * h3[k]["interaccion"]["se"] for k, _, _ in order])
    ps = [h3[k]["interaccion"]["p"] for k, _, _ in order]

    fig, ax = plt.subplots(figsize=(MM180, 3.6))
    x = np.arange(len(order))
    ax.bar(x, vals, width=.55, color=[c for _, _, c in order],
           edgecolor="#2b2b2b", linewidth=.5, yerr=errs, capsize=4,
           error_kw=dict(ecolor=INK, elinewidth=1.0, capthick=1.0))
    ax.axhline(0, c=INK, lw=.9)
    ax.set_xticks(x)
    ax.set_xticklabels([l for _, l, _ in order])
    ax.set_ylabel("Technology x complements interaction\n"
                  "(effect on log cereal yield)")
    ax.set_title("Is complement dependence generic? Technology waves compared")
    ax.grid(alpha=.35, axis="y", lw=.6)
    ax.set_axisbelow(True)

    for i, (v, e, p) in enumerate(zip(vals, errs, ps)):
        star = "*" if p < .05 else ""
        off = 6 if v >= 0 else -6
        va = "bottom" if v >= 0 else "top"
        ax.annotate(f"{v:+.3f}{star}", xy=(i, v + np.sign(v) * e),
                    xytext=(0, off), textcoords="offset points",
                    ha="center", va=va, fontsize=8.5, color=INK)
    ax.margins(y=.24)

    fig.tight_layout(rect=[0, 0.085, 1, 1])
    fig.text(0.055, 0.025,
             "* p < 0.05; whiskers are 95% CIs. Positive = the technology "
             "pays more where complements are stronger.",
             fontsize=8, color="#555555", ha="left", va="bottom")
    save(fig, "Figure3.png")


# ==================================================================== Figure 4
# SOURCE: HA4_DiD_y_comparacion_de_eras.crecimiento_anual_pct_por_era
#         .rendimiento_cereal_mundial          -> series 1
#         .eficiencia_del_nitrogeno_mediana    -> series 2
#         .dosis_de_nitrogeno_mediana          -> series 3 (NEW, replaces a table)
def figure4():
    e = R["HA4_DiD_y_comparacion_de_eras"]["crecimiento_anual_pct_por_era"]
    eras = ["revolucion_verde_1961_1990",
            "post_revolucion_verde_1991_2015",
            "era_IA_2016_2023"]
    era_lab = ["Green Revolution\n1961-1990", "Post-Green Revolution\n1991-2015",
               "AI era\n2016-2023"]

    series = [
        ("rendimiento_cereal_mundial", "Cereal yield (area-weighted mean)",
         BLUE, ""),
        ("dosis_de_nitrogeno_mediana", "Nitrogen dose (median)", AMBER, "///"),
        ("eficiencia_del_nitrogeno_mediana",
         "Nitrogen use efficiency (median)", RED, "..."),
    ]

    x = np.arange(3)
    w = .26
    fig, ax = plt.subplots(figsize=(MM180, 3.9))

    for j, (key, lab, col, hatch) in enumerate(series):
        vals = np.array([e[key][k] for k in eras], dtype=float)
        pos = x + (j - 1) * w
        ax.bar(pos, vals, w * .90, label=lab, color=col, hatch=hatch,
               edgecolor="#2b2b2b", linewidth=.5)
        for xi, v in zip(pos, vals):
            off = 5 if v >= 0 else -5
            va = "bottom" if v >= 0 else "top"
            ax.annotate(f"{v:+.2f}", xy=(xi, v), xytext=(0, off),
                        textcoords="offset points", ha="center", va=va,
                        fontsize=8.0, color=INK)

    ax.axhline(0, c=INK, lw=.9)
    ax.set_xticks(x)
    ax.set_xticklabels(era_lab)
    ax.set_ylabel("Annual growth (%/year)")
    ax.set_title("Gains by technological era: output, input and efficiency")
    ax.grid(alpha=.35, axis="y", lw=.6)
    ax.set_axisbelow(True)
    ax.margins(y=.20)
    ax.legend(loc="upper right", frameon=True, framealpha=.95,
              edgecolor="#cccccc", ncol=1)

    fig.tight_layout(rect=[0, 0, 1, 0.99])
    save(fig, "Figure4.png")


# ==================================================================== Figure 5
# SOURCE: HA5_no_transferibilidad_de_la_funcion_aprendida
#         .matriz_R2_entrenar_en_fila_evaluar_en_columna   -> heatmap
#         .elasticidad_del_nitrogeno_por_region            -> right panel
#         .R2_medio_misma_region_holdout_temporal          -> subtitle
#         .R2_medio_otra_region                            -> subtitle
SHORT = {
    "Middle East, North Africa, Afghanistan & Pakistan": "MENA &\nPakistan",
    "Sub-Saharan Africa": "Sub-Saharan\nAfrica",
    "Europe & Central Asia": "Europe &\nCentral Asia",
    "Latin America & Caribbean": "Latin America\n& Caribbean",
    "East Asia & Pacific": "East Asia\n& Pacific",
}


def figure5():
    h5 = R["HA5_no_transferibilidad_de_la_funcion_aprendida"]
    mat = h5["matriz_R2_entrenar_en_fila_evaluar_en_columna"]
    el = h5["elasticidad_del_nitrogeno_por_region"]

    regions = list(mat.keys())                       # keep JSON order
    short = [SHORT[r.strip()] for r in regions]
    M = np.array([[mat[tr][te] for te in regions] for tr in regions],
                 dtype=float)

    same = h5["R2_medio_misma_region_holdout_temporal"]
    other = h5["R2_medio_otra_region"]

    fig = plt.figure(figsize=(MM180, 4.55))
    gs = fig.add_gridspec(2, 2, width_ratios=[1.0, 0.50],
                          height_ratios=[1.0, 0.055],
                          wspace=0.10, hspace=0.42,
                          left=0.155, right=0.985, top=0.80, bottom=0.135)
    axh = fig.add_subplot(gs[0, 0])
    axb = fig.add_subplot(gs[0, 1], sharey=None)
    axc = fig.add_subplot(gs[1, 0])

    # ---- heatmap: diverging, hard-centred at R2 = 0 -----------------------
    # 'RdBu' (NOT RdBu_r) so that NEGATIVE R2 is red = clearly bad and
    # positive R2 is blue, matching the manuscript's primary colour.
    cmap = plt.get_cmap("RdBu")
    norm = TwoSlopeNorm(vmin=float(M.min()), vcenter=0.0, vmax=float(M.max()))
    im = axh.imshow(M, cmap=cmap, norm=norm, aspect="auto")

    n = len(regions)
    axh.set_xticks(np.arange(n))
    axh.set_yticks(np.arange(n))
    axh.set_xticklabels(short, fontsize=8.0)
    axh.set_yticklabels(short, fontsize=8.0)
    axh.set_xlabel("Evaluated on", fontsize=9.5, labelpad=6)
    axh.set_ylabel("Trained on", fontsize=9.5, labelpad=6)
    axh.tick_params(length=0)
    for sp in axh.spines.values():
        sp.set_visible(False)

    # 2 px surface gap between cells (interior boundaries only, so the outer
    # edge of the grid does not leave a clipped sliver on the border cells)
    axh.set_xticks(np.arange(.5, n - 1, 1), minor=True)
    axh.set_yticks(np.arange(.5, n - 1, 1), minor=True)
    axh.grid(which="minor", color="white", lw=1.6)
    axh.grid(which="major", visible=False)
    axh.tick_params(which="minor", length=0)

    for i in range(n):
        for j in range(n):
            v = M[i, j]
            r, g, bl, _ = cmap(norm(v))
            lum = 0.299 * r + 0.587 * g + 0.114 * bl
            axh.text(j, i, f"{v:.2f}", ha="center", va="center",
                     fontsize=8.5, color="white" if lum < 0.55 else "#111111",
                     fontweight="bold" if i == j else "normal")
        # diagonal: black box + a shape cue, so the "own region" cells are not
        # identified by colour alone
        axh.add_patch(plt.Rectangle((i - .5, i - .5), 1, 1, fill=False,
                                    edgecolor="black", lw=1.8, zorder=5))

    axh.set_title("Region-to-region transfer of the learned yield function",
                  fontsize=10.5, pad=22)
    axh.annotate("Boxed diagonal = own region (temporal hold-out). "
                 f"Mean $R^2$: own region {same:.2f}, other region {other:.2f}.",
                 xy=(0, 1.045), xycoords="axes fraction", fontsize=8.2,
                 color="#555555", ha="left", va="bottom")

    cb = fig.colorbar(im, cax=axc, orientation="horizontal")
    cb.set_label("Out-of-sample $R^2$  (0 = no better than predicting the mean)",
                 fontsize=8.5)
    cb.ax.tick_params(labelsize=8)
    cb.outline.set_linewidth(.6)
    cb.outline.set_edgecolor("#888888")

    # ---- right panel: N elasticity by region, rows aligned with the heatmap
    vals = np.array([el[r] for r in regions], dtype=float)
    ypos = np.arange(n)
    colors = [RED if v < 0 else BLUE for v in vals]
    axb.barh(ypos, vals, height=.62, color=colors,
             edgecolor="#2b2b2b", linewidth=.5)
    axb.axvline(0, c=INK, lw=.9)
    axb.set_ylim(n - .5, -.5)                 # same orientation as imshow
    axb.set_yticks(ypos)
    axb.set_yticklabels([])
    axb.tick_params(axis="y", length=0)
    axb.set_xlabel("Nitrogen elasticity\nof yield", fontsize=9.0)
    axb.set_title("Why transfer fails", fontsize=10.5, pad=22)
    axb.grid(alpha=.35, axis="x", lw=.6)
    axb.set_axisbelow(True)
    # leave room for the value label printed beyond each bar end
    axb.set_xlim(-0.36, 0.58)
    axb.set_xticks([-0.2, 0.0, 0.2, 0.4])
    axb.tick_params(axis="x", labelsize=7.5)
    for yi, v in zip(ypos, vals):
        axb.annotate(f"{v:+.3f}", xy=(v, yi),
                     xytext=(4 if v >= 0 else -4, 0),
                     textcoords="offset points", fontsize=8.0,
                     ha="left" if v >= 0 else "right", va="center", color=INK)
    for sp in ("top", "right"):
        axb.spines[sp].set_visible(False)

    save(fig, "Figure5.png")


# ============================================================= supplementary
SUP = [
    ("fig1_produccion_mundial.png", "FigureS1.png"),
    ("fig2_desaceleracion_rendimiento.png", "FigureS2.png"),
    ("fig3_mecanizacion_espana.png", "FigureS3.png"),
    ("fig4_nitrogeno.png", "FigureS4.png"),
    ("fig5_convergencia.png", "FigureS5.png"),
    ("fig6_rendimiento_por_renta.png", "FigureS6.png"),
    ("fig7_importancia.png", "FigureS7.png"),
    ("fig8_generico_vs_especifico.png", "FigureS8.png"),
    ("fig9_empleo.png", "FigureS9.png"),
    ("fig10_dependencia_parcial.png", "FigureS10.png"),
    ("fig15_event_study.png", "FigureS11.png"),
]


def supplementary():
    for src, dst in SUP:
        s = os.path.join(FIG_SRC, src)
        d = os.path.join(OUT_SUP, dst)
        if not os.path.exists(s):
            print("  MISSING", s)
            continue
        im = Image.open(s)
        dpi = im.info.get("dpi", (DPI, DPI))
        if im.mode != "RGB":                       # flatten RGBA on white
            bg = Image.new("RGB", im.size, (255, 255, 255))
            bg.paste(im, mask=im.split()[-1] if im.mode == "RGBA" else None)
            bg.save(d, dpi=dpi)
        else:
            shutil.copyfile(s, d)
        print("  wrote", d, Image.open(d).size, Image.open(d).mode)


if __name__ == "__main__":
    print("Main figures ->", OUT)
    figure1()
    figure2()
    figure3()
    figure4()
    figure5()
    print("Supplementary ->", OUT_SUP)
    supplementary()
    print("done.")
