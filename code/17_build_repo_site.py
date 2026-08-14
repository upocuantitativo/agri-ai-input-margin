# -*- coding: utf-8 -*-
"""Build index.html for the replication repository (served by GitHub Pages).

Unlike the artifact version this is a complete standalone document and it points
at the PNGs already committed under figures/published/, so nothing is duplicated.
"""
import io, os

REPO = r"C:\Users\Usuario\OneDrive - Universidad Pablo de Olavide de Sevilla\Escritorio\1_ARTÍCULO\ENVIADOS\5_AIAGRLICULTURE\article\EINT_submission\replication"
OUT = os.path.join(REPO, "index.html")

MAIN = [
    ("1", "Figure1.png", "The emergence of agricultural AI",
     "World publications combining AI and agricultural terms (log scale) and their share of world research output per 1,000 works, 2000\u20132024. The dashed line marks 2016.",
     "\u00a74.7", "12_ai_observable.py"),
    ("2", "Figure2.png", "Where the value of AI appears",
     "Left: effect of one standard deviation of AI specialisation on yield, nitrogen dose and nitrogen use efficiency. Right: marginal effect on the nitrogen dose at low, median and high predetermined complements.",
     "\u00a74.9", "12_ai_observable.py"),
    ("3", "Figure3.png", "Is complement dependence generic?",
     "One common specification applied to four technological waves. The embodied waves and the placebo depend on complements positively, on the output margin; AI is the only negative one.",
     "\u00a74.10", "12_ai_observable.py"),
    ("4", "Figure4.png", "Gains by technological era",
     "Annual growth of world cereal yield, median nitrogen dose and nitrogen use efficiency across three eras. The nitrogen-dose series replaces a table cut for length.",
     "\u00a74.11", "14_build_eint_figures.py"),
    ("5", "Figure5.png", "A learned function does not travel",
     "Out-of-sample R\u00b2 when a yield model trained on the row region is evaluated on the column region, with the region-specific nitrogen elasticities that cause the failure.",
     "\u00a74.12", "14_build_eint_figures.py"),
]

SUPP = [
    ("S1", "World production by crop group", "\u00a74.2"),
    ("S2", "World cereal yield and its growth rate", "\u00a74.2"),
    ("S3", "Spain: hectares of arable land per tractor", "\u00a74.2"),
    ("S4", "Cereal yield versus nitrogen applied", "\u00a74.2"),
    ("S5", "\u03c3-convergence and \u03b2-convergence", "\u00a74.6"),
    ("S6", "Median cereal yield by income group", "\u00a74.6"),
    ("S7", "Permutation importance of the predictors", "\u00a74.1"),
    ("S8", "Generic versus specific prediction error", "\u00a74.4"),
    ("S9", "World agricultural employment", "\u00a74.5"),
    ("S10", "Partial dependence on nitrogen and irrigation", "\u00a74.2"),
    ("S11", "Event study, base year 2015", "\u00a74.11"),
]

main_cards = "\n".join(
    f"""      <figure class="card">
        <div class="card-head">
          <span class="fignum">Figure {num}</span>
          <h3>{title}</h3>
          <p class="meta"><span class="chip chip-main">Main text</span><span class="cite">cited in {sec}</span><code class="prov">{src}</code></p>
        </div>
        <button class="shot" type="button" data-title="Figure {num} &mdash; {title}">
          <img src="figures/published/{fn}" alt="{title}" loading="lazy">
        </button>
        <figcaption>{cap}</figcaption>
      </figure>"""
    for num, fn, title, cap, sec, src in MAIN)

supp_cards = "\n".join(
    f"""      <figure class="card card-s">
        <div class="card-head">
          <span class="fignum">Figure {num}</span>
          <h3>{title}</h3>
          <p class="meta"><span class="chip chip-supp">Supplementary</span><span class="cite">cited in {sec}</span></p>
        </div>
        <button class="shot" type="button" data-title="Figure {num} &mdash; {title}">
          <img src="figures/published/supplementary/Figure{num}.png" alt="{title}" loading="lazy">
        </button>
      </figure>"""
    for num, title, sec in SUPP)

HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fifteen Figures, Five Kept</title>
<meta name="description" content="Every figure from the agricultural-AI input-margin paper, and the replication package behind them.">
<style>
  :root {
    --ground:#f4f6f8; --surface:#ffffff; --sunk:#eaeef2;
    --ink:#111820; --ink-2:#3d4a57; --muted:#6d7a87;
    --line:#d8dee5; --line-soft:#e6eaef;
    --accent:#1f4e79; --accent-soft:#e3ecf4;
    --warm:#b0403c; --warm-soft:#f6e5e4;
    --shadow:0 1px 2px rgba(17,24,32,.06), 0 8px 24px rgba(17,24,32,.05);
    --serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif;
    --sans:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
    --mono:ui-monospace,SFMono-Regular,"SF Mono",Menlo,Consolas,monospace;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --ground:#0d1319; --surface:#151d25; --sunk:#1b242d;
      --ink:#e8edf2; --ink-2:#b7c2cd; --muted:#8593a0;
      --line:#2a3540; --line-soft:#212b34;
      --accent:#7db2e0; --accent-soft:#1a2c3d;
      --warm:#e08a86; --warm-soft:#33211f;
      --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px rgba(0,0,0,.3);
    }
  }
  :root[data-theme="dark"] {
    --ground:#0d1319; --surface:#151d25; --sunk:#1b242d;
    --ink:#e8edf2; --ink-2:#b7c2cd; --muted:#8593a0;
    --line:#2a3540; --line-soft:#212b34;
    --accent:#7db2e0; --accent-soft:#1a2c3d;
    --warm:#e08a86; --warm-soft:#33211f;
    --shadow:0 1px 2px rgba(0,0,0,.4), 0 8px 24px rgba(0,0,0,.3);
  }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--ground); color:var(--ink);
    font-family:var(--sans); font-size:16px; line-height:1.55; -webkit-font-smoothing:antialiased; }
  a { color:var(--accent); }
  .wrap { max-width:1120px; margin:0 auto; padding:clamp(28px,5vw,60px) clamp(18px,4vw,40px) 96px; }

  header { border-bottom:1px solid var(--line); padding-bottom:28px; margin-bottom:40px; }
  .eyebrow { font-size:12px; letter-spacing:.14em; text-transform:uppercase; color:var(--muted); margin:0 0 12px; }
  h1 { font-family:var(--serif); font-weight:600; font-size:clamp(30px,4.4vw,44px);
    line-height:1.12; margin:0 0 14px; text-wrap:balance; letter-spacing:-.01em; }
  .standfirst { margin:0; max-width:66ch; color:var(--ink-2); font-size:17px; }

  .tally { display:flex; flex-wrap:wrap; gap:10px; margin-top:26px; }
  .stat { background:var(--surface); border:1px solid var(--line-soft); border-radius:10px;
    padding:12px 16px; min-width:132px; box-shadow:var(--shadow); }
  .stat b { display:block; font-family:var(--serif); font-size:26px; font-weight:600;
    line-height:1.1; font-variant-numeric:tabular-nums; }
  .stat span { font-size:12.5px; color:var(--muted); }
  .stat.is-main b { color:var(--accent); }
  .stat.is-supp b { color:var(--warm); }

  .repo { display:flex; flex-wrap:wrap; gap:8px; margin-top:22px; }
  .repo a { display:inline-block; padding:7px 13px; border-radius:8px; font-size:13.5px;
    text-decoration:none; border:1px solid var(--line); background:var(--surface); color:var(--ink); }
  .repo a:hover { border-color:var(--accent); color:var(--accent); }
  .repo a code { font-family:var(--mono); font-size:12.5px; color:var(--muted); }

  h2 { font-family:var(--serif); font-weight:600; font-size:23px; letter-spacing:-.005em; margin:0 0 6px; }
  .section-note { margin:0 0 22px; color:var(--muted); font-size:14.5px; max-width:72ch; }
  section + section { margin-top:56px; }

  .grid { display:grid; gap:20px; }
  .grid-main { grid-template-columns:1fr; }
  .grid-supp { grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); }

  .card { background:var(--surface); border:1px solid var(--line-soft); border-radius:12px;
    padding:18px 18px 20px; margin:0; box-shadow:var(--shadow);
    display:flex; flex-direction:column; gap:14px; }
  .card-head h3 { font-family:var(--serif); font-weight:600; font-size:19px; margin:2px 0 8px; letter-spacing:-.005em; }
  .card-s .card-head h3 { font-size:16.5px; }
  .fignum { font-family:var(--mono); font-size:11.5px; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); }
  .meta { display:flex; flex-wrap:wrap; align-items:center; gap:8px; margin:0; font-size:12.5px; }
  .chip { display:inline-block; padding:2px 9px; border-radius:999px; font-size:11.5px; font-weight:600; letter-spacing:.02em; }
  .chip-main { background:var(--accent-soft); color:var(--accent); }
  .chip-supp { background:var(--warm-soft); color:var(--warm); }
  .cite { color:var(--ink-2); font-variant-numeric:tabular-nums; }
  .prov { color:var(--muted); font-family:var(--mono); font-size:11.5px; }

  .shot { display:block; width:100%; padding:10px; border:1px solid var(--line-soft);
    border-radius:8px; background:var(--sunk); cursor:zoom-in; transition:border-color .15s ease; }
  .shot:hover, .shot:focus-visible { border-color:var(--accent); }
  .shot:focus-visible { outline:2px solid var(--accent); outline-offset:2px; }
  .shot img { display:block; width:100%; height:auto; border-radius:4px; background:#fff; }

  figcaption { font-size:14px; color:var(--ink-2); max-width:78ch; margin:0; }

  dialog { border:none; padding:0; background:transparent; max-width:min(1400px,96vw); max-height:94vh; }
  dialog::backdrop { background:rgba(8,12,16,.82); }
  .lb { background:var(--surface); border-radius:12px; padding:14px; display:flex; flex-direction:column; gap:10px; }
  .lb img { max-width:100%; max-height:80vh; height:auto; border-radius:6px; background:#fff; }
  .lb-bar { display:flex; justify-content:space-between; align-items:center; gap:16px; }
  .lb-bar strong { font-family:var(--serif); font-weight:600; font-size:15px; }
  .lb-bar button { border:1px solid var(--line); background:var(--sunk); color:var(--ink);
    border-radius:7px; padding:5px 13px; font:inherit; font-size:13px; cursor:pointer; }
  .lb-bar button:hover { border-color:var(--accent); }

  footer { margin-top:64px; padding-top:22px; border-top:1px solid var(--line); font-size:13.5px; color:var(--muted); }
  footer code { font-family:var(--mono); font-size:12.5px; color:var(--ink-2); }
  @media (prefers-reduced-motion: reduce) { * { transition:none !important; } }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <p class="eyebrow">Replication package &middot; agricultural AI and the input margin</p>
    <h1>Fifteen figures, five kept</h1>
    <p class="standfirst">Every figure from <em>Fewer inputs, not more yield: agricultural AI and its digital complements</em>, in the order a reader meets it. The five that stay in the main text carry the AI argument; the eleven that move to the supplement carry the historical benchmark. Two of the five are not what they were: Figure&nbsp;4 gained a third series to absorb a table cut for length, and Figure&nbsp;5 did not exist before.</p>
    <div class="tally">
      <div class="stat is-main"><b>5</b><span>in the main text</span></div>
      <div class="stat is-supp"><b>11</b><span>in the supplement</span></div>
      <div class="stat"><b>300</b><span>dpi, 179.9&nbsp;mm wide</span></div>
      <div class="stat"><b>3,659</b><span>country-years, 169 countries</span></div>
    </div>
    <nav class="repo">
      <a href="https://github.com/upocuantitativo/agri-ai-input-margin">Read me first</a>
      <a href="https://github.com/upocuantitativo/agri-ai-input-margin/tree/main/code">Analysis code <code>01&ndash;17</code></a>
      <a href="https://github.com/upocuantitativo/agri-ai-input-margin/tree/main/data/processed">Processed panels</a>
      <a href="https://github.com/upocuantitativo/agri-ai-input-margin/tree/main/results">Estimation output <code>*.json</code></a>
      <a href="https://github.com/upocuantitativo/agri-ai-input-margin/blob/main/docs/DATA_DICTIONARY.md">Data dictionary</a>
      <a href="https://github.com/upocuantitativo/agri-ai-input-margin/blob/main/docs/LINKAGE.md">How the sources are merged</a>
      <a href="https://github.com/upocuantitativo/agri-ai-input-margin/blob/main/docs/OPENALEX_QUERIES.md">OpenAlex queries</a>
      <a href="https://github.com/upocuantitativo/agri-ai-input-margin/blob/main/docs/SUPPLEMENTARY_TABLES.md">Supplementary tables S1&ndash;S12</a>
    </nav>
  </header>

  <section>
    <h2>Main text</h2>
    <p class="section-note">Reproduced at the resolution submitted. Captions are the ones printed in the manuscript; the script that draws each one is named beside it.</p>
    <div class="grid grid-main">
__MAIN__
    </div>
  </section>

  <section>
    <h2>Supplementary</h2>
    <p class="section-note">These are the figures numbered 1&ndash;10 in the previous version, plus the event study. They are still cited by number in the text, now as Figure&nbsp;S1&ndash;S11. Click any figure to enlarge it.</p>
    <div class="grid grid-supp">
__SUPP__
    </div>
  </section>

  <footer>
    Everything here regenerates from the deposited data: <code>python code/14_build_eint_figures.py</code> redraws the five main figures from <code>results/12_ai_observable.json</code>. Figures S1&ndash;S10 were produced at 130&nbsp;dpi and S11 at 200&nbsp;dpi; they are published at source resolution rather than upscaled. Code is MIT licensed, derived data CC&nbsp;BY&nbsp;4.0.
  </footer>
</div>

<dialog id="lb">
  <div class="lb">
    <div class="lb-bar"><strong id="lb-title"></strong><button type="button" id="lb-close">Close</button></div>
    <img id="lb-img" alt="">
  </div>
</dialog>

<script>
  var lb = document.getElementById('lb'),
      lbImg = document.getElementById('lb-img'),
      lbTitle = document.getElementById('lb-title');
  document.querySelectorAll('.shot').forEach(function (b) {
    b.addEventListener('click', function () {
      var img = b.querySelector('img');
      lbImg.src = img.src;
      lbImg.alt = img.alt;
      lbTitle.textContent = b.dataset.title;
      lb.showModal();
    });
  });
  document.getElementById('lb-close').addEventListener('click', function () { lb.close(); });
  lb.addEventListener('click', function (e) { if (e.target === lb) lb.close(); });
</script>
</body>
</html>
"""

html = HTML.replace("__MAIN__", main_cards).replace("__SUPP__", supp_cards)
io.open(OUT, "w", encoding="utf-8").write(html)
print("written:", OUT, "%.0f KB" % (os.path.getsize(OUT) / 1024))

# every referenced image must exist
missing = []
for _, fn, _, _, _, _ in MAIN:
    if not os.path.exists(os.path.join(REPO, "figures", "published", fn)):
        missing.append(fn)
for num, _, _ in SUPP:
    p = os.path.join(REPO, "figures", "published", "supplementary", "Figure%s.png" % num)
    if not os.path.exists(p):
        missing.append(os.path.basename(p))
print("missing images:", missing if missing else "none")
