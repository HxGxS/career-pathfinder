#!/usr/bin/env python3
"""Build the offline Career Pathfinder dashboard from a tracker data file.

Reads career_tracker_YYYY-MM-DD[_vN].json and writes the matching
career_dashboard_YYYY-MM-DD[_vN].html next to it: one self-contained page,
no internet, no outside scripts or fonts, data embedded. See
.claude/skills/career-tracker-dashboard/SKILL.md.

Design: colours come from the Career Pathfinder mascot illustration (cloak charcoal,
robe cream, gold trim, flame orange, terracotta, robe-pattern blue), checked with the
dataviz validator: the verdict scale is a one-hue ordinal ramp that passes in light
and dark mode; text tokens clear 4.5:1 on their card surface; tier and ghost badges
use the fixed status colours, always with an icon and a label (never colour alone).
Every chart has a table view, and dark/light mode follows the system with a toggle.
Wording follows the design plugin's UX copy review (plain labels: Good match, Check
first, Possible ghost job, Must-haves, Same kind of work / Related work / Less obvious
fit); layout and accessibility follow its design critique and WCAG 2.1 AA review
(visible control borders and focus rings, a proper dialog for details, role titles as
buttons, keyboard tabs, a "Needs your attention" strip, charts folded away by default).

Safety: posting text is untrusted. The data is embedded as JSON with every "<"
escaped, and the page only ever inserts it with textContent, never as HTML, so
nothing in an advert can run in the browser. Links are kept only when they are
https addresses or relative paths to the user's own files (tracker_schema.safe_link),
checked here and again in the page.

Usage:
  python3 scripts/build_dashboard.py [DATA_FILE_OR_FOLDER] [--out PATH] [--check]

With a folder (default: current folder) the newest tracker in it is used.
--check validates the data and prints the counts without writing the page.
Exit 0 on success; 1 if validation found problems; 2 on a usage or read error.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tracker_schema as ts  # noqa: E402

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; img-src data:;__CONNECT__">
<title>Career Pathfinder</title>
<style>
/* Palette from the mascot illustration. Light = robe cream; dark = cloak charcoal.
   Type scale: 12 / 14 / 16 / 20 / 28. */
:root{
  --page:#f3ece6; --card:#fbf7f3; --line:#e4d8cf; --control:#8a7e84; --hover:#f1e7df;
  --ink:#2a2430; --ink2:#5a4f55; --muted:#6f6469;
  --accent:#9a4524; --bar:#4d6f9a; --meter:#a9502c; --track:#eadfd6;
  --v1:#e0a060; --v2:#c9813f; --v3:#ad642c; --v4:#8c4b22; --v5:#6a3618;
  --good:#0ca30c; --warn:#fab219; --serious:#ec835a; --closed:#8a8086;
  --shadow:0 1px 2px rgba(42,36,48,.06),0 4px 16px rgba(42,36,48,.05);
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --page:#26232a; --card:#2f2b33; --line:#433d48; --control:#857a82; --hover:#38333d;
  --ink:#f3e9e1; --ink2:#cdbfb6; --muted:#a89c96;
  --accent:#f0a65a; --bar:#8fb0d4; --meter:#dcaa48; --track:#3d3742;
  --v1:#9d5c34; --v2:#b8703b; --v3:#d08745; --v4:#e5a156; --v5:#f7c27c;
  --closed:#a89c96; --shadow:none;
}}
:root[data-theme="dark"]{
  --page:#26232a; --card:#2f2b33; --line:#433d48; --control:#857a82; --hover:#38333d;
  --ink:#f3e9e1; --ink2:#cdbfb6; --muted:#a89c96;
  --accent:#f0a65a; --bar:#8fb0d4; --meter:#dcaa48; --track:#3d3742;
  --v1:#9d5c34; --v2:#b8703b; --v3:#d08745; --v4:#e5a156; --v5:#f7c27c;
  --closed:#a89c96; --shadow:none;
}
*{box-sizing:border-box}
body{margin:0;background:var(--page);color:var(--ink);
  font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
main{max-width:1240px;margin:0 auto;padding:24px 16px 48px}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:4px}
header.top{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-bottom:20px}
h1{font-size:28px;line-height:1.2;margin:0}
.sub{color:var(--muted);font-size:14px;margin-top:4px}
button,select,input{font:inherit;color:inherit}
.quiet{background:none;border:0;color:var(--ink2);font-size:14px;cursor:pointer;padding:6px 8px;min-height:32px;border-radius:6px}
.quiet:hover{background:var(--hover)}
.tiles{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin-bottom:8px}
.tile{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px;box-shadow:var(--shadow)}
.tile .v{font-size:28px;font-weight:650;line-height:1.1}
.tile .k{display:flex;align-items:center;gap:6px;font-size:16px;font-weight:600;margin-top:6px}
.tile .d{color:var(--muted);font-size:14px}
.note{color:var(--muted);font-size:14px;margin:0 0 16px}
.attention{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:20px}
.attention .lab{font-weight:600;font-size:14px;margin-right:4px}
.chip{background:var(--card);border:1px solid var(--control);border-radius:999px;padding:6px 14px;min-height:32px;cursor:pointer;font-size:14px}
.chip[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:var(--card)}
.chip .n{font-weight:650}
details.insights{margin-bottom:24px}
details.insights>summary{cursor:pointer;color:var(--accent);font-size:14px;padding:6px 0;min-height:32px;list-style:none}
details.insights>summary::-webkit-details-marker{display:none}
.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:8px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;box-shadow:var(--shadow);min-width:0}
.card-head{display:flex;justify-content:space-between;align-items:baseline;gap:8px;margin-bottom:8px}
.card-head h2{font-size:16px;margin:0}
.linkbtn{background:none;border:0;color:var(--accent);cursor:pointer;font-size:14px;padding:4px 6px;min-height:28px;border-radius:6px}
.hbar{display:grid;grid-template-columns:120px 1fr 28px;align-items:center;gap:10px;margin:6px 0;font-size:14px}
.hbar .lab{color:var(--ink2)}
.hbar .fill{height:10px;border-radius:0 4px 4px 0;min-width:2px}
.hbar .num{text-align:right;font-variant-numeric:tabular-nums}
.meter{margin:10px 0}
.meter .row{display:flex;justify-content:space-between;font-size:14px;margin-bottom:4px;gap:8px}
.meter .row span:first-child{color:var(--ink2)}
.meter .track{height:8px;background:var(--track);border-radius:4px;overflow:hidden}
.meter .fill{height:8px;background:var(--meter);border-radius:4px}
.mini{width:100%;border-collapse:collapse;font-size:14px}
.mini td,.mini th{padding:4px 0;border-bottom:1px solid var(--line);text-align:left}
.mini td:last-child,.mini th:last-child{text-align:right}
nav.tabs{display:flex;gap:4px;border-bottom:1px solid var(--line);margin-bottom:12px;overflow-x:auto}
nav.tabs button{background:none;border:0;border-bottom:2px solid transparent;padding:10px 12px;min-height:44px;cursor:pointer;color:var(--ink2);white-space:nowrap}
nav.tabs button[aria-selected="true"]{color:var(--ink);border-bottom-color:var(--accent);font-weight:600}
.filters{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:12px}
.filters input[type=search],.filters select{background:var(--card);border:1px solid var(--control);border-radius:8px;padding:6px 10px;min-height:36px}
.filters input[type=search]{flex:1 1 260px;min-width:200px}
details.more{position:relative}
details.more>summary{cursor:pointer;list-style:none;border:1px solid var(--control);border-radius:8px;padding:6px 12px;min-height:36px;display:flex;align-items:center;background:var(--card)}
details.more>summary::-webkit-details-marker{display:none}
details.more .panel{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:8px}
.filters label{display:flex;align-items:center;gap:6px;color:var(--ink2);font-size:14px;min-height:32px;padding:0 4px;cursor:pointer}
.filters input[type=checkbox]{width:18px;height:18px}
.count{color:var(--muted);font-size:14px;margin-left:auto}
.tablewrap{background:var(--card);border:1px solid var(--line);border-radius:12px;overflow-x:auto;box-shadow:var(--shadow)}
table.roles{width:100%;border-collapse:collapse}
table.roles th{font-size:12px;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;text-align:left;padding:12px 14px;border-bottom:1px solid var(--line);white-space:nowrap}
table.roles td{padding:12px 14px;border-bottom:1px solid var(--line);vertical-align:top}
table.roles tbody tr.role{cursor:pointer}
table.roles tbody tr.role:hover{background:var(--hover)}
.group td{background:var(--page);font-size:14px;font-weight:650;padding:8px 14px;cursor:default}
.rowbtn{background:none;border:0;padding:0;font-weight:600;text-align:left;cursor:pointer;color:var(--ink);font-size:16px}
.rowbtn:hover{text-decoration:underline}
.meta{color:var(--muted);font-size:14px}
.score{font-size:20px;font-weight:650;line-height:1}
.score small{font-size:12px;font-weight:400;color:var(--muted);display:block;margin-top:4px}
.badge{display:inline-flex;align-items:center;gap:6px;font-size:14px;color:var(--ink2);margin:4px 10px 0 0}
.dot{width:8px;height:8px;border-radius:50%;flex:none}
.soon{color:var(--accent);font-weight:600}
.empty{padding:28px;text-align:center;color:var(--muted)}
.docs{font-size:14px;color:var(--ink2)}
.drawer-bg{position:fixed;inset:0;background:rgba(20,16,22,.45);display:none}
.drawer{position:fixed;top:0;right:0;height:100%;width:min(560px,100%);background:var(--card);border-left:1px solid var(--line);overflow:auto;transform:translateX(100%);transition:transform .2s;visibility:hidden}
.drawer.open{transform:none;visibility:visible}.drawer-bg.open{display:block}
.drawer header{position:sticky;top:0;background:var(--card);padding:18px 20px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between;gap:12px}
.drawer h2{margin:0;font-size:20px}
.drawer section{padding:14px 20px;border-bottom:1px solid var(--line)}
.drawer h3{margin:0 0 8px;font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}
.drawer dl{display:grid;grid-template-columns:150px 1fr;gap:6px 12px;margin:0;font-size:14px}
.drawer dt{color:var(--muted)}.drawer dd{margin:0;word-break:break-word;white-space:pre-wrap}
.drawer details summary{cursor:pointer;color:var(--accent);font-size:14px;min-height:28px}
.btn{background:var(--card);border:1px solid var(--control);border-radius:8px;padding:6px 14px;min-height:36px;cursor:pointer}
a{color:var(--accent)}
.glossary dt{font-weight:600;margin-top:14px}.glossary dd{margin:2px 0 0;color:var(--ink2)}
.readme h3{font-size:16px;margin:18px 0 6px}.readme p,.readme li{color:var(--ink2)}
.edit{display:grid;gap:4px;margin:8px 0}
.edit select,.edit input,.edit textarea{background:var(--card);border:1px solid var(--control);border-radius:8px;padding:6px 10px;min-height:36px;width:100%;font:inherit;color:inherit}
.editbar{display:flex;align-items:center;gap:12px;margin-top:10px}
.tip{position:fixed;pointer-events:none;background:var(--ink);color:var(--card);font-size:12px;padding:4px 8px;border-radius:6px;display:none}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
@media (max-width:900px){.tiles{grid-template-columns:repeat(2,minmax(0,1fr))}.cards{grid-template-columns:1fr}}
@media (max-width:640px){
  table.roles thead{display:none}
  table.roles tr.role{display:block;padding:10px 0;border-bottom:1px solid var(--line)}
  table.roles tr.role td{display:flex;gap:10px;border:0;padding:4px 14px}
  table.roles tr.role td[data-label]::before{content:attr(data-label);flex:0 0 110px;color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.04em;padding-top:2px}
  .group td{display:block}
}
@media (prefers-reduced-motion:reduce){.drawer{transition:none}}
</style>
</head>
<body>
<main id="main">
  <header class="top">
    <div><h1>Career Pathfinder</h1><div class="sub" id="version"></div></div>
    <button class="quiet" id="theme" aria-label="Change appearance">Appearance: Auto</button>
  </header>
  <div class="tiles" id="tiles"></div>
  <p class="note" id="note"></p>
  <div class="attention" id="attention"></div>
  <details class="insights" id="insights">
    <summary id="insights-sum">Show charts</summary>
    <div class="cards">
      <div class="card" id="c-verdict"></div>
      <div class="card" id="c-type"></div>
      <div class="card" id="c-coverage"></div>
    </div>
  </details>
  <nav class="tabs" id="tabs" role="tablist" aria-label="Sections"></nav>
  <div class="filters" id="filters">
    <label class="sr" for="q">Search</label>
    <input type="search" id="q" placeholder="Search by job, company, place or note">
    <select id="f-profile" aria-label="Profile"></select>
    <select id="sort" aria-label="Sort">
      <option value="score">Best fit first</option>
      <option value="deadline">Closing soonest</option>
      <option value="posted">Newest first</option>
    </select>
    <details class="more" id="more">
      <summary>More filters</summary>
      <div class="panel">
        <select id="f-elig" aria-label="Must-haves"></select>
        <select id="f-verdict" aria-label="Fit"></select>
        <select id="f-status" aria-label="Your status"></select>
        <label><input type="checkbox" id="f-soon"> Closing within 14 days</label>
        <label><input type="checkbox" id="f-warn"> Has a caution note</label>
      </div>
    </details>
    <span class="count" id="count" role="status" aria-live="polite"></span>
  </div>
  <div id="view" role="tabpanel" tabindex="-1"></div>
</main>
<div class="drawer-bg" id="drawer-bg"></div>
<aside class="drawer" id="drawer" role="dialog" aria-modal="true" aria-labelledby="drawer-title"></aside>
<div class="tip" id="tip" aria-hidden="true"></div>
<script type="application/json" id="data">__DATA__</script>
<script>
(function(){
"use strict";
const D = JSON.parse(document.getElementById("data").textContent);
const F = D.__fields, C = D.__counts;
const roles = D.roles || [], fits = D.profile_fit || [], profiles = D.profiles || [];
const $ = id => document.getElementById(id);
const t = v => v == null ? "" : String(v);
function el(tag, props, kids){
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(props || {})) {
    if (k === "text") n.textContent = v; else if (k === "cls") n.className = v; else n.setAttribute(k, v);
  }
  for (const c of [].concat(kids || [])) if (c != null && c !== "") n.append(c);
  return n;
}
function safeLink(v){
  v = t(v).trim();
  if (/^https:\/\/\S+$/i.test(v)) return v;
  if (!v || /^[a-z][a-z0-9+.-]*:/i.test(v) || v.startsWith("/") || v.startsWith("\\")) return "";
  if (v.split(/[\\/]/).includes("..")) return "";
  return v;
}
function group(r){
  if (t(r.verification_status) === "Closed") return "closed";
  if (t(r.ghost_job).trim()) return "ghost";
  return t(r.eligibility) === "Eligible" ? "tier1" : "tier2";
}
// Plain-language labels (data keeps the workflow's own values).
const STATUS = {
  tier1:{label:"Good match", plural:"Good matches", hint:"Meet all your must-haves", color:"var(--good)", icon:"✔"},
  tier2:{label:"Check first", plural:"Check first", hint:"One detail to confirm", color:"var(--warn)", icon:"?"},
  ghost:{label:"Possible ghost job", plural:"Possible ghost jobs", hint:"Shown, not counted", color:"var(--serious)", icon:"◌"},
  closed:{label:"Closed", plural:"Closed", hint:"No longer open", color:"var(--closed)", icon:"–"}
};
const TYPE = {Direct:"Same kind of work", Adjacent:"Related work", Unexpected:"Less obvious fit"};
const ELIG = {"Eligible":"Meets must-haves", "Eligibility unclear":"One thing to confirm"};
const DOC = {"Not written":"not written", "Waiting for your review decision":"waiting for your decision", "Reviewed: changes applied":"done, changes applied", "Reviewed: kept as is":"done, kept as is"};
const typeText = v => t(v).replace(/Direct|Adjacent|Unexpected/g, m => TYPE[m]);
const VERDICTS = ["Strong fit","Good fit","Moderate fit","Weak fit","Poor fit"];
const VCOLOR = {"Strong":"var(--v5)","Good":"var(--v4)","Moderate":"var(--v3)","Weak":"var(--v2)","Poor":"var(--v1)"};
const pids = r => t(r.matched_profiles).split(/[,;\s]+/).filter(Boolean);
const parseDate = v => { const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(t(v).trim()); return m ? new Date(+m[1], +m[2]-1, +m[3]) : null; };
const today = (() => { const d = new Date(); d.setHours(0,0,0,0); return d; })();
const daysLeft = r => { const d = parseDate(r.deadline); return d ? Math.round((d - today) / 864e5) : null; };
function badge(kind, text){
  const s = STATUS[kind];
  return el("span", {cls:"badge"}, [el("span", {cls:"dot", style:"background:" + s.color, "aria-hidden":"true"}), el("span", {"aria-hidden":"true", text:s.icon}), text || s.label]);
}
function cautionBadge(r){
  if (!t(r.warning_flags).trim()) return null;
  return el("span", {cls:"badge", title:t(r.warning_flags)}, [el("span", {cls:"dot", style:"background:var(--warn)", "aria-hidden":"true"}), el("span", {"aria-hidden":"true", text:"⚠"}), "Caution"]);
}
function deadlineNode(r){
  const raw = t(r.deadline), n = daysLeft(r);
  if (n == null) return el("span", {cls:"meta", text: raw || "not listed"});
  if (n < 0) return el("span", {cls:"meta", text: raw + " · passed"});
  const when = n === 0 ? "today" : n === 1 ? "in 1 day" : "in " + n + " days";
  return el("span", {cls: n <= 7 ? "soon" : "meta", text: raw + " · " + when});
}

// Appearance toggle (a per-viewer convenience; works without storage)
const themes = ["auto","light","dark"], themeName = {auto:"Auto", light:"Light", dark:"Dark"};
let theme = "auto";
try { theme = localStorage.getItem("cp-theme") || "auto"; } catch (e) {}
function applyTheme(){
  if (theme === "auto") document.documentElement.removeAttribute("data-theme"); else document.documentElement.setAttribute("data-theme", theme);
  $("theme").textContent = "Appearance: " + themeName[theme];
}
$("theme").addEventListener("click", () => { theme = themes[(themes.indexOf(theme) + 1) % 3]; try { localStorage.setItem("cp-theme", theme); } catch (e) {} applyTheme(); });
applyTheme();

// Header, tiles, note
$("version").textContent = "Updated " + t(D.__built).replace(" ", " at ");
[["tier1", C.tier1], ["tier2", C.tier2], ["ghost", C.ghost], ["closed", C.closed]].forEach(([k, v]) => $("tiles").append(
  el("div", {cls:"tile"}, [el("div", {cls:"v", text:t(v)}),
    el("div", {cls:"k"}, [el("span", {cls:"dot", style:"background:" + STATUS[k].color, "aria-hidden":"true"}), STATUS[k].plural]),
    el("div", {cls:"d", text:STATUS[k].hint})])));
$("note").textContent = t(C.unique) + " roles found · " + t(C.overlap) + " fit more than one of your profiles · Select a role to see everything about it";

// Needs your attention
let attn = null;
const active = roles.filter(r => ["tier1","tier2"].includes(group(r)));
const ATTN = {
  soon:{label:"closing within 14 days", test:r => { const n = daysLeft(r); return n != null && n >= 0 && n <= 14; }},
  ready:{label:"ready to apply", test:r => t(r.status) === "Ready to apply"},
  waiting:{label:"waiting for your decision", test:r => [r.cv_status, r.letter_status].some(s => t(s) === "Waiting for your review decision")}
};
function drawAttention(){
  const box = $("attention"); box.replaceChildren(el("span", {cls:"lab", text:"Needs your attention:"}));
  const items = Object.entries(ATTN).map(([k, a]) => [k, a, active.filter(a.test).length]).filter(x => x[2] > 0);
  if (!items.length) { box.append(el("span", {cls:"meta", text:"Nothing right now."})); return; }
  items.forEach(([k, a, n]) => {
    const b = el("button", {cls:"chip", "aria-pressed": String(attn === k)}, [el("span", {cls:"n", text:t(n)}), " " + a.label]);
    b.addEventListener("click", () => { attn = attn === k ? null : k; if (tab !== "roles") selectTab("roles"); drawAttention(); render(); });
    box.append(b);
  });
}

// Tooltip (extra help on hover; every value is also shown as text)
const tip = $("tip");
function hover(node, text){
  node.addEventListener("mousemove", e => { tip.textContent = text; tip.style.display = "block"; tip.style.left = (e.clientX + 12) + "px"; tip.style.top = (e.clientY + 12) + "px"; });
  node.addEventListener("mouseleave", () => { tip.style.display = "none"; });
}

// Charts, folded away by default (the table comes first)
let insightsOpen = false;
try { insightsOpen = localStorage.getItem("cp-insights") === "open"; } catch (e) {}
$("insights").open = insightsOpen;
const syncInsights = () => { $("insights-sum").textContent = $("insights").open ? "Hide charts" : "Show charts"; };
$("insights").addEventListener("toggle", () => { syncInsights(); try { localStorage.setItem("cp-insights", $("insights").open ? "open" : "closed"); } catch (e) {} });
syncInsights();
function card(id, title, rows, drawRows){
  const box = $(id), body = el("div"), table = el("table", {cls:"mini"});
  table.append(el("tr", {}, [el("th", {text:"Item"}), el("th", {text:"Count"})]));
  rows.forEach(([k, v, extra]) => table.append(el("tr", {}, [el("td", {text:k}), el("td", {text: extra || t(v)})])));
  let showTable = false;
  const toggle = el("button", {cls:"linkbtn", text:"View as table"});
  toggle.addEventListener("click", () => { showTable = !showTable; toggle.textContent = showTable ? "View as chart" : "View as table"; body.replaceChildren(showTable ? table : drawRows()); });
  box.append(el("div", {cls:"card-head"}, [el("h2", {text:title}), toggle]), body);
  body.append(drawRows());
}
function bars(rows, colorOf){
  const max = Math.max(1, ...rows.map(r => r[1]));
  const wrap = el("div");
  rows.forEach(([k, v]) => {
    const row = el("div", {cls:"hbar"}, [el("span", {cls:"lab", text:k}),
      el("div", {}, el("div", {cls:"fill", style:"width:" + (100 * v / max) + "%;background:" + colorOf(k)})), el("span", {cls:"num", text:t(v)})]);
    hover(row, k + ": " + v + " role" + (v === 1 ? "" : "s"));
    wrap.append(row);
  });
  return wrap;
}
const vRows = VERDICTS.map(v => [v.replace(" fit",""), active.filter(r => t(r.verdict).startsWith(v)).length, null]);
card("c-verdict", "How well they fit", vRows, () => bars(vRows, k => VCOLOR[k]));
const tRows = Object.keys(TYPE).map(c => [TYPE[c], active.filter(r => t(r.category).includes(c)).length, null]);
card("c-type", "How close to your experience", tRows, () => bars(tRows, () => "var(--bar)"));
const target = 20, pp = C.per_profile || {};
const cRows = Object.entries(pp).map(([p, n]) => { const pr = profiles.find(x => t(x.id) === p); return [p + (pr && pr.title ? " · " + t(pr.title) : ""), n, n + " of " + target]; });
card("c-coverage", "Progress towards 20 roles per profile", cRows, () => {
  const wrap = el("div");
  if (!cRows.length) wrap.append(el("div", {cls:"meta", text:"No profiles yet. They appear here once you approve them in chat."}));
  cRows.forEach(([k, n]) => {
    const m = el("div", {cls:"meter"}, [el("div", {cls:"row"}, [el("span", {text:k}), el("span", {text:n + " of " + target})]),
      el("div", {cls:"track"}, el("div", {cls:"fill", style:"width:" + Math.min(100, 100 * n / target) + "%"}))]);
    hover(m, n + " of " + target + " roles found for " + k.split(" · ")[0]);
    wrap.append(m);
  });
  return wrap;
});

// Filters
function opts(id, label, values){ const s = $(id); s.append(el("option", {value:"", text:label})); values.forEach(([v, l]) => s.append(el("option", {value:v, text:l}))); }
opts("f-profile", "All profiles", profiles.map(p => [t(p.id), t(p.id) + (p.title ? " · " + t(p.title) : "")]));
opts("f-elig", "Must-haves: all", Object.entries(ELIG));
opts("f-verdict", "Fit: any", VERDICTS.map(v => [v, v]));
opts("f-status", "Your status: any", F.status.map(s => [s, s]));
["q","f-profile","f-elig","f-verdict","f-status","sort","f-soon","f-warn"].forEach(id => $(id).addEventListener("input", render));

// Tabs (arrow keys move between them)
const TABS = [["roles","Matches"],["ghost","Possible ghost jobs"],["closed","Closed"],["fit","Scores by profile"],["glossary","What terms mean"],["readme","About this search"]];
let tab = "roles";
function selectTab(k, focus){
  tab = k;
  [...$("tabs").children].forEach(b => { const on = b.dataset.tab === k; b.setAttribute("aria-selected", String(on)); b.tabIndex = on ? 0 : -1; if (on && focus) b.focus(); });
  $("view").setAttribute("aria-labelledby", "tab-" + k);
  render();
}
TABS.forEach(([k, label], i) => {
  const b = el("button", {role:"tab", id:"tab-" + k, "aria-controls":"view", "data-tab":k, text:label});
  b.addEventListener("click", () => selectTab(k));
  b.addEventListener("keydown", e => {
    if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
    const next = (i + (e.key === "ArrowRight" ? 1 : -1) + TABS.length) % TABS.length;
    selectTab(TABS[next][0], true);
  });
  $("tabs").append(b);
});

function matches(r){
  const q = $("q").value.trim().toLowerCase();
  if (q && ![r.job_title, r.company, r.location_remote, r.notes, r.role_key, r.key_gap].some(v => t(v).toLowerCase().includes(q))) return false;
  if ($("f-profile").value && !pids(r).includes($("f-profile").value)) return false;
  if ($("f-elig").value && t(r.eligibility) !== $("f-elig").value) return false;
  if ($("f-verdict").value && !t(r.verdict).startsWith($("f-verdict").value)) return false;
  if ($("f-status").value && t(r.status) !== $("f-status").value) return false;
  if ($("f-warn").checked && !t(r.warning_flags).trim()) return false;
  if ($("f-soon").checked && !ATTN.soon.test(r)) return false;
  if (attn && !ATTN[attn].test(r)) return false;
  return true;
}
function sorted(list){
  const how = $("sort").value, far = new Date(9999,0,1), old = new Date(1,0,1);
  return list.slice().sort((a, b) => how === "deadline" ? (parseDate(a.deadline) || far) - (parseDate(b.deadline) || far)
    : how === "posted" ? (parseDate(b.date_posted) || old) - (parseDate(a.date_posted) || old)
    : (Number(b.top_fit_score) || 0) - (Number(a.top_fit_score) || 0));
}
const EMPTY = {
  filtered:"No roles match these filters. Try clearing a filter or searching for something else.",
  ghost:"No possible ghost jobs. Every advert found looks active.",
  closed:"No closed roles. If an advert you're tracking closes, the role moves here."
};
function rolesTable(groups){
  const pool = roles.filter(r => groups.includes(group(r)));
  const list = sorted(pool.filter(matches));
  $("count").textContent = "Showing " + list.length + " of " + pool.length;
  if (!list.length) {
    const msg = !pool.length && groups[0] === "ghost" ? EMPTY.ghost : !pool.length && groups[0] === "closed" ? EMPTY.closed : EMPTY.filtered;
    return el("div", {cls:"tablewrap"}, el("div", {cls:"empty", text:msg}));
  }
  const head = el("tr", {}, ["#","Role","Fit","Must-haves","Kind of match","Closes","Your status","CV and letter"].map(h => el("th", {scope:"col", text:h})));
  const body = el("tbody");
  groups.forEach(g => {
    const rows = list.filter(r => group(r) === g);
    if (!rows.length) return;
    if (groups.length > 1) body.append(el("tr", {cls:"group"}, el("td", {colspan:"8", text:STATUS[g].plural + " (" + rows.length + ")"})));
    rows.forEach(r => {
      const open = el("button", {cls:"rowbtn", "aria-label":"Open details for " + t(r.job_title) + " at " + t(r.company), text:t(r.job_title)});
      open.addEventListener("click", e => { e.stopPropagation(); openDrawer(r, open); });
      const roleCell = el("td", {"data-label":"Role"}, [open, el("div", {cls:"meta", text:[t(r.company), t(r.location_remote)].filter(Boolean).join(" · ")}),
        el("div", {}, [g === "ghost" ? badge("ghost", "Possible ghost job (score " + t(r.ghost_job).split(":")[0].trim() + ")") : null, g === "closed" ? badge("closed") : null, cautionBadge(r)])]);
      const fitCell = el("td", {"data-label":"Fit"}, el("div", {cls:"score"}, [t(r.top_fit_score) || "–", el("small", {text:t(r.verdict)})]));
      const tr = el("tr", {cls:"role"}, [el("td", {cls:"meta", "data-label":"#", text:t(r.number)}), roleCell, fitCell,
        el("td", {"data-label":"Must-haves"}, badge(t(r.eligibility) === "Eligible" ? "tier1" : "tier2", ELIG[t(r.eligibility)] || "One thing to confirm")),
        el("td", {cls:"meta", "data-label":"Kind of match", text:typeText(r.category)}), el("td", {"data-label":"Closes"}, deadlineNode(r)),
        el("td", {"data-label":"Your status", text:t(r.status) || "Not started"}),
        el("td", {cls:"docs", "data-label":"CV and letter"}, [el("div", {text:"CV " + (DOC[t(r.cv_status)] || "not written")}), el("div", {text:"Letter " + (DOC[t(r.letter_status)] || "not written")})])]);
      tr.addEventListener("click", () => openDrawer(r, open));
      body.append(tr);
    });
  });
  return el("div", {cls:"tablewrap"}, el("table", {cls:"roles"}, [el("caption", {cls:"sr", text:"Roles"}), el("thead", {}, head), body]));
}

// Details panel (a dialog: focus stays inside; Escape or Close returns focus)
let opener = null;
function linkOrText(v){ const h = safeLink(v); return h ? el("a", {href:h, target:"_blank", rel:"noopener noreferrer", text:t(v)}) : t(v); }
function section(title, pairs){
  const dl = el("dl");
  pairs.forEach(([k, v]) => { if (v == null || v === "") return; dl.append(el("dt", {text:k}), el("dd", {}, v)); });
  return dl.children.length ? el("section", {}, [el("h3", {text:title}), dl]) : null;
}
function docLine(status, file){ return el("span", {}, [DOC[t(status)] ? DOC[t(status)].charAt(0).toUpperCase() + DOC[t(status)].slice(1) : "Not written", file ? " · " : "", file ? linkOrText(file) : ""]); }
function openDrawer(r, from){
  opener = from || null;
  const dr = $("drawer"); dr.replaceChildren();
  const close = el("button", {cls:"btn", "aria-label":"Close details", text:"Close"});
  close.addEventListener("click", closeDrawer);
  dr.append(el("header", {}, [el("div", {}, [el("h2", {id:"drawer-title", text:t(r.job_title)}), el("div", {cls:"meta", text:t(r.company) + " · #" + t(r.number)})]), close]));
  const g = group(r);
  dr.append(el("section", {}, [badge(g), cautionBadge(r), el("div", {cls:"score", style:"margin-top:10px"}, [t(r.top_fit_score) || "–", el("small", {text:t(r.verdict) + (t(r.fit_by_profile) ? " · " + t(r.fit_by_profile) : "")})])]));
  fits.filter(f => t(f.role_number) === t(r.number)).forEach(f => dr.append(section("How it fits " + t(f.profile_id),
    [["Score breakdown", t(f.score_breakdown)], ["Why it fits", t(f.fit_rationale)], ["Main gap", t(f.key_gap)], ["Still unknown", t(f.uncertainty)], ["Right to work", t(f.right_to_work)]])));
  [section("The job", [["Location", t(r.location_remote)], ["Type and hours", t(r.employment_type_hours)], ["Seniority", t(r.seniority)], ["Kind of match", typeText(r.category)], ["Main gap", t(r.key_gap)]]),
   section("Pay", [["Listed pay", t(r.listing_salary)], ["Market estimate", t(r.market_salary_estimate)], ["Source", t(r.salary_source_date)]]),
   section("Your must-haves", [["Must-haves", ELIG[t(r.eligibility)] || t(r.eligibility)], ["Visa notes", t(r.work_auth_notes)]]),
   section("Cautions", [["Ghost-job score", t(r.ghost_job)], ["Caution notes", t(r.warning_flags)]]),
   section("Advert and key dates", [["Advert", linkOrText(r.source_url)], ["Source type", t(r.source_type)], ["Posted", t(r.date_posted) + (t(r.original_posting_date_text) ? " (" + t(r.original_posting_date_text) + ")" : "")], ["Found", t(r.date_found)], ["Last checked", t(r.date_verified)], ["Closes", deadlineNode(r)], ["Reference number", t(r.requisition_id)], ["Recruiter", t(r.recruiter)]]),
   section("Your CV and letter", [["Job description", linkOrText(r.job_description_file)], ["CV", docLine(r.cv_status, r.cv_file)], ["Cover letter", docLine(r.letter_status, r.letter_file)]]),
   D.__editable ? notesForm(r) : section("Your notes (ask in chat to change them)", [["Your status", t(r.status) || "Not started"], ["Next step", t(r.next_step)], ["Next-step date", t(r.next_step_date)], ["Notes", t(r.notes)]])
  ].forEach(s => s && dr.append(s));
  const all = el("dl");
  F.role.forEach(([k, label]) => { const v = k === "cv" ? (t(r.cv_status) + " " + t(r.cv_file)) : k === "cover_letter" ? (t(r.letter_status) + " " + t(r.letter_file)) : t(r[k]); all.append(el("dt", {text:label}), el("dd", {text:v})); });
  dr.append(el("section", {}, el("details", {}, [el("summary", {text:"Show every detail"}), all])));
  $("main").inert = true;
  dr.classList.add("open"); $("drawer-bg").classList.add("open"); close.focus();
}
// Editing your own fields (only when opened with scripts/dashboard.py on this computer)
function field(label, control){ return el("label", {cls:"edit"}, [el("span", {cls:"meta", text:label}), control]); }
function notesForm(r){
  const sec = el("section", {}, el("h3", {text:"Your notes"}));
  const status = el("select", {"aria-label":"Your status"});
  F.status.forEach(s => { const o = el("option", {value:s, text:s}); if ((t(r.status) || "Not started") === s) o.selected = true; status.append(o); });
  const step = el("input", {type:"text", maxlength:"200", value:t(r.next_step)});
  const date = el("input", {type:"date", value:t(r.next_step_date)});
  const notes = el("textarea", {rows:"4", maxlength:"2000"}); notes.value = t(r.notes);
  const msg = el("div", {cls:"meta", role:"status", "aria-live":"polite"});
  const save = el("button", {cls:"btn", text:"Save changes"});
  save.addEventListener("click", async () => {
    save.disabled = true; msg.textContent = "Saving\u2026";
    try {
      const res = await fetch("/api/update", {method:"POST", headers:{"Content-Type":"application/json", "X-CP-Token":D.__token},
        body:JSON.stringify({role_key:t(r.role_key), status:status.value, next_step:step.value, next_step_date:date.value, notes:notes.value})});
      const out = await res.json();
      if (!res.ok || !out.ok) throw new Error(out.error || "Not saved");
      Object.assign(r, out.role);
      msg.textContent = "Saved as tracker version " + out.version + ".";
      drawAttention(); render();
    } catch (e) { msg.textContent = "Not saved: " + e.message; }
    save.disabled = false;
  });
  sec.append(field("Your status", status), field("Next step", step), field("Next-step date", date), field("Notes", notes), el("div", {cls:"editbar"}, [save, msg]));
  return sec;
}
function closeDrawer(){
  if (!$("drawer").classList.contains("open")) return;
  $("drawer").classList.remove("open"); $("drawer-bg").classList.remove("open"); $("main").inert = false;
  if (opener) opener.focus();
}
$("drawer-bg").addEventListener("click", closeDrawer);
document.addEventListener("keydown", e => {
  const dr = $("drawer");
  if (!dr.classList.contains("open")) return;
  if (e.key === "Escape") { closeDrawer(); return; }
  if (e.key !== "Tab") return;
  const f = [...dr.querySelectorAll("button, a[href], summary")];
  if (!f.length) return;
  if (e.shiftKey && document.activeElement === f[0]) { e.preventDefault(); f[f.length - 1].focus(); }
  else if (!e.shiftKey && document.activeElement === f[f.length - 1]) { e.preventDefault(); f[0].focus(); }
});

function fitTable(){
  const list = fits.filter(f => !$("f-profile").value || t(f.profile_id) === $("f-profile").value);
  $("count").textContent = "Showing " + list.length + " of " + fits.length;
  const cols = [["role_number","#"],["job_title","Role"],["profile_id","Profile"],["fit_score","Fit"],["verdict","Verdict"],["score_breakdown","Score breakdown"],["key_gap","Main gap"]];
  const head = el("tr", {}, cols.map(([, l]) => el("th", {scope:"col", text:l})));
  const body = el("tbody", {}, list.map(f => el("tr", {}, cols.map(([k, l]) => el("td", {cls: k === "score_breakdown" || k === "key_gap" ? "meta" : "", text:t(f[k])})))));
  return el("div", {cls:"tablewrap"}, el("table", {cls:"roles"}, [el("caption", {cls:"sr", text:"Scores by profile"}), el("thead", {}, head), body]));
}
function glossary(){
  const dl = el("dl", {cls:"glossary"});
  (F.glossary || []).forEach(([term, meaning]) => dl.append(el("dt", {text:term}), el("dd", {text:meaning})));
  return el("div", {cls:"card"}, dl);
}
function readme(){
  const R = D.read_me || {}, box = el("div", {cls:"card readme"});
  const add = (title, v) => { if (v == null || v === "" || (Array.isArray(v) && !v.length) || (typeof v === "object" && !Array.isArray(v) && !Object.keys(v).length)) return;
    box.append(el("h3", {text:title}));
    if (Array.isArray(v)) box.append(el("ul", {}, v.map(x => el("li", {text:t(x)}))));
    else if (typeof v === "object") box.append(el("ul", {}, Object.entries(v).map(([a, b]) => el("li", {text:a + ": " + t(b)}))));
    else box.append(el("p", {text:t(v)})); };
  add("About this search", "These are the roles found for your approved profiles. A fit score shows how well a role matches your profile; it never predicts whether you'll get an offer. Visa notes are a guide, not legal advice. Possible ghost jobs are shown so you can judge them, but they don't count towards your 20 roles. Your status and notes are yours: change them by asking in chat, or on this page when it's opened with scripts/dashboard.py. Unsure what a word means? See “What terms mean”.");
  add("Scope", R.scope); add("Search budget used", R.budget_used);
  add("Counts", {"Roles found":C.unique, "Good matches":C.tier1, "Check first":C.tier2, "Possible ghost jobs shown":C.ghost, "Possible ghost jobs dropped":t(R.ghost_jobs_dropped), "Closed":C.closed, "Fit more than one profile":C.overlap});
  add("Roles found per profile", C.per_profile); add("Left out, by reason", R.dropped_by_reason);
  add("Shortfalls", R.shortfalls); add("Roles you can't apply for (the advert's own words)", R.ineligible);
  add("Pay and date conventions", R.conventions); add("Incident log", R.incidents); add("Notes", R.notes);
  profiles.forEach(p => { box.append(el("h3", {text:t(p.id) + " · " + t(p.title) + " (approved " + t(p.approved) + ")"})); box.append(el("p", {style:"white-space:pre-wrap", text:t(p.text)})); });
  return box;
}
function render(){
  const tableTabs = ["roles","ghost","closed","fit"];
  $("filters").style.display = tableTabs.includes(tab) ? "" : "none";
  const v = tab === "roles" ? rolesTable(["tier1","tier2"]) : tab === "ghost" ? rolesTable(["ghost"]) : tab === "closed" ? rolesTable(["closed"])
    : tab === "fit" ? fitTable() : tab === "glossary" ? glossary() : readme();
  $("view").replaceChildren(v);
}
drawAttention();
selectTab("roles");
})();
</script>
</body>
</html>
"""


def build(data: dict, editable: bool = False, token: str = "") -> str:
    """The dashboard page. editable=True is used only by scripts/dashboard.py (served on
    this computer): it adds the Your notes form and lets the page send saves to it."""
    from datetime import datetime
    clean = json.loads(json.dumps(data))  # a copy we can add to
    for r in clean.get("roles") or []:
        for key in ts.LINK_KEYS:
            if r.get(key) and r[key] != "not listed" and not ts.safe_link(r[key]):
                r[key] = f"(link removed: not https or a relative file) {r[key]}"
    clean["__fields"] = {
        "role": ts.ROLE_FIELDS,
        "fit": ts.FIT_FIELDS,
        "main": ts.MAIN_FIELDS,
        "status": ts.STATUS_VALUES,
        "glossary": ts.GLOSSARY,
    }
    clean["__counts"] = ts.counts(data)
    clean["__built"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    clean["__editable"] = bool(editable)
    clean["__token"] = token if editable else ""
    payload = json.dumps(clean, ensure_ascii=False)
    # "<" escaped as \u003c: no "</script>" or "<!--" can end or break the data block.
    payload = payload.replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    page = PAGE.replace("__CONNECT__", " connect-src 'self';" if editable else "")
    return page.replace("__DATA__", payload)


def output_path(data_path: Path) -> Path:
    name = data_path.name.replace("career_tracker_", "career_dashboard_", 1)
    return data_path.with_name(Path(name).with_suffix(".html").name)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Build the offline Career Pathfinder dashboard.")
    ap.add_argument("source", nargs="?", default=".", help="tracker data file, or a folder holding them")
    ap.add_argument("--out", type=Path, default=None, help="where to write the page (default: next to the data file)")
    ap.add_argument("--check", action="store_true", help="validate and print counts only")
    args = ap.parse_args(argv)

    src = Path(args.source)
    data_path = ts.latest_tracker(src) if src.is_dir() else src
    if data_path is None or not data_path.exists():
        print(f"build_dashboard: no career_tracker_*.json found at {src}", file=sys.stderr)
        return 2
    try:
        data = ts.load(data_path)
    except (OSError, ValueError) as exc:
        print(f"build_dashboard: cannot read {data_path}: {exc}", file=sys.stderr)
        return 2

    problems = ts.validate(data)
    c = ts.counts(data)
    print(f"data: {data_path.name}")
    print(f"counts: unique={c['unique']} tier1={c['tier1']} tier2={c['tier2']} "
          f"ghost={c['ghost']} closed={c['closed']} overlap={c['overlap']} per_profile={c['per_profile']}")
    for p in problems:
        print(f"problem: {p}")
    if args.check:
        return 1 if problems else 0

    out = args.out or output_path(data_path)
    out.write_text(build(data), encoding="utf-8")
    print(f"saved={out}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
