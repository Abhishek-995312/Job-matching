const $ = id => document.getElementById(id);
const CIRCUMFERENCE = 339.29;

// build an element safely: textContent never interprets HTML
function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined) e.textContent = text;
  return e;
}

function renderChips(containerId, items, cls) {
  const box = $(containerId);
  box.replaceChildren();
  if (!items || !items.length) {
    box.appendChild(el("span", "legend", "None"));
    return;
  }
  items.forEach(s => box.appendChild(el("span", "chip " + cls, s)));
}

function gaugeColor(p) {
  return p >= 70 ? "var(--green)" : p >= 40 ? "var(--amber)" : "var(--red)";
}

function showScore(r) {
  const p = r.compatibility_percent;
  $("arc").style.stroke = gaugeColor(p);
  $("arc").setAttribute("stroke-dashoffset", CIRCUMFERENCE * (1 - p / 100));
  $("pct").textContent = Math.round(p) + "%";

  const skill = Math.round(r.skill_score * 100);
  const sem = Math.round(r.semantic_score * 100);
  $("skillBar").style.width = skill + "%";
  $("semBar").style.width = sem + "%";
  $("skillTxt").textContent = "(" + skill + "%)";
  $("semTxt").textContent = "(" + sem + "%)";
  $("sections").textContent = "Sections detected: " + (r.sections_found || []).join(", ");
}

function showSuggestions(s) {
  const card = $("suggCard");
  if (!s) { card.style.display = "none"; return; }
  card.style.display = "block";
  $("source").textContent = s.source || "";
  $("summary").textContent = s.summary || "";

  const rewrites = $("rewrites");
  rewrites.replaceChildren();
  (s.bullet_rewrites || []).forEach(b => {
    const d = el("div", "rewrite");
    d.appendChild(el("div", "old", b.original));
    d.appendChild(el("div", "new", b.improved));
    d.appendChild(el("div", "why", b.why));
    rewrites.appendChild(d);
  });

  const gaps = $("gaps");
  gaps.replaceChildren();
  (s.skill_gap_advice || []).forEach(g => {
    const li = el("li");
    li.appendChild(el("strong", "", g.skill + ": "));
    li.appendChild(document.createTextNode(g.how_to_address));
    gaps.appendChild(li);
  });
  $("gapH").style.display = gaps.children.length ? "block" : "none";

  const qs = $("questions");
  qs.replaceChildren();
  (s.interview_questions || []).forEach(q => {
    const li = el("li", "", q.question + " ");
    li.appendChild(el("span", "type", "(" + q.type + ")"));
    qs.appendChild(li);
  });
  $("qH").style.display = qs.children.length ? "block" : "none";
}

async function analyze() {
  const file = $("resume").files[0];
  const jd = $("jd").value.trim();
  $("error").textContent = "";

  if (!file) { $("error").textContent = "Please choose a resume file."; return; }
  if (jd.length < 30) { $("error").textContent = "Please paste a longer job description."; return; }

  const form = new FormData();
  form.append("resume", file);
  form.append("jd_text", jd);
  form.append("include_suggestions", $("sugg").checked);

  const btn = $("go");
  btn.disabled = true;
  btn.textContent = "Analyzing...";

  try {
    const res = await fetch("/analyze", { method: "POST", body: form });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Request failed");

    showScore(data);
    renderChips("matched", data.matched_skills, "ok");
    renderChips("missReq", data.missing_required, "miss");
    renderChips("missPref", data.missing_preferred, "pref");
    showSuggestions(data.suggestions);

    $("results").style.display = "block";
    $("results").scrollIntoView({ behavior: "smooth" });
  } catch (err) {
    $("error").textContent = "Error: " + err.message;
  } finally {
    btn.disabled = false;
    btn.textContent = "Analyze";
  }
}

$("go").addEventListener("click", analyze);