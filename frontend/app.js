const API = "http://localhost:8000/check";
const COLORS = { 100: "green", 50: "amber", 0: "red", null: "gray" };

document.getElementById("check").addEventListener("click", async () => {
  const answer = document.getElementById("answer").value.trim();
  if (!answer) return;

  setStatus("Checking...");
  const res = await fetch(API, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ answer }),
  });

  if (!res.ok) {
    setStatus("Something went wrong. Try again.");
    return;
  }
  const data = await res.json();
  render(answer, data);
  setStatus("");
});

function render(answer, data) {
  document.getElementById("overall").textContent =
    data.overall_freshness === null ? "No checkable claims" : `Freshness: ${data.overall_freshness}/100`;

  const out = document.getElementById("highlighted");
  out.replaceChildren();

  // Highlight claims that have valid spans, in order.
  const spanned = data.claims
    .filter(c => c.span)
    .sort((a, b) => a.span[0] - b.span[0]);

  let cursor = 0;
  for (const c of spanned) {
    if (c.span[0] < cursor) continue; // skip overlaps
    out.append(answer.slice(cursor, c.span[0]));
    const mark = document.createElement("mark");
    mark.className = `mark-${COLORS[c.score] || "gray"}`;
    mark.textContent = answer.slice(c.span[0], c.span[1]);
    mark.title = c.reason;
    out.append(mark);
    cursor = c.span[1];
  }
  out.append(answer.slice(cursor));

  renderList(data.claims);
}

function renderList(claims) {
  const list = document.getElementById("claims");
  list.replaceChildren();
  for (const c of claims) {
    const li = document.createElement("li");
    li.className = `mark-${COLORS[c.score] || "gray"}`;
    const head = document.createElement("strong");
    head.textContent = `${c.score === null ? "Not checked" : c.score + "/100"} · ${c.verdict}`;
    li.append(head, document.createElement("br"), c.reason);

    for (const s of c.sources) {
      const a = document.createElement("a");
      a.href = s.url;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      a.textContent = s.title || s.url;
      li.append(document.createElement("br"), a);
    }
    list.append(li);
  }
}

function setStatus(msg) {
  document.getElementById("status").textContent = msg;
}