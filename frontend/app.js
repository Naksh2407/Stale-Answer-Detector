const API_BASE = window.location.protocol + "//" + window.location.hostname + ":8000";

const COLORS = { 100: "green", 50: "amber", 0: "red", null: "gray" };

const SAMPLES = {
    pricing: "The Pro plan costs $20 per month and includes 10GB of storage. The v2 API is the current version for this service.",
    api: "The latest version of the API is v1.0, which supports webhooks. The older v2 API has been deprecated."
};

document.addEventListener("DOMContentLoaded", () => {
    initApp();
});

function initApp() {
    setupListeners();
    pingStatus();
    loadStats();
    loadHistory();

    setInterval(pingStatus, 10000);
}

function setupListeners() {
    document.getElementById("check-btn").addEventListener("click", () => performAudit());
    document.getElementById("check-url-btn").addEventListener("click", () => performUrlAudit());
    document.getElementById("clear-history").addEventListener("click", () => clearHistory());
    document.getElementById("clear-btn").addEventListener("click", () => clearInput());
    document.getElementById("copy-rewrite-btn").addEventListener("click", () => copyCorrectedText());

    document.getElementById("answer-input").addEventListener("input", (e) => {
        document.getElementById("char-count").textContent = `${e.target.value.length} / 8000`;
    });

    // Preset dropdown
    document.getElementById("preset-select").addEventListener("change", (e) => {
        const val = e.target.value;
        if (SAMPLES[val]) {
            document.getElementById("answer-input").value = SAMPLES[val];
            document.getElementById("char-count").textContent = `${SAMPLES[val].length} / 8000`;
            performAudit(SAMPLES[val]);
        }
        e.target.value = ""; // reset dropdown
    });

    // Tabs
    document.querySelectorAll(".tab-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
            document.querySelectorAll(".tab-content").forEach(c => c.classList.add("hidden"));
            e.target.classList.add("active");
            const tab = e.target.dataset.tab;
            document.getElementById(`tab-${tab}`).classList.remove("hidden");
        });
    });
}

function clearInput() {
    document.getElementById("answer-input").value = "";
    document.getElementById("url-input").value = "";
    document.getElementById("char-count").textContent = "0 / 8000";
    document.getElementById("results-section").classList.add("hidden");
}

async function pingStatus() {
    const dot = document.getElementById("status-dot");
    const txt = document.getElementById("status-text");
    try {
        const res = await fetch(`${API_BASE}/health`);
        if (res.ok) {
            dot.className = "dot online";
            txt.textContent = "Gateway Online";
        } else {
            throw new Error();
        }
    } catch {
        dot.className = "dot offline";
        txt.textContent = "Gateway Disconnected";
    }
}

async function loadStats() {
    try {
        const res = await fetch(`${API_BASE}/stats`);
        if (res.ok) {
            const data = await res.json();
            document.getElementById("stat-total").textContent = data.total_checks;
            document.getElementById("stat-avg").textContent = data.avg_freshness ? `${data.avg_freshness}%` : "--";
            document.getElementById("stat-stale").textContent = data.stale_answers;
        }
    } catch (e) { console.error("Stats load failed", e); }
}

async function loadHistory() {
    try {
        const res = await fetch(`${API_BASE}/history`);
        if (res.ok) {
            const data = await res.json();
            const list = document.getElementById("history-list");
            list.replaceChildren();

            if (data.entries.length === 0) {
                list.innerHTML = `<div class="empty-hint">No recent audits</div>`;
                return;
            }

            data.entries.forEach(e => {
                const item = document.createElement("div");
                item.className = "history-item";
                item.innerHTML = `
                    <div class="history-item-top">
                        <span>${e.overall_freshness !== null ? e.overall_freshness + '%' : 'N/A'}</span>
                        <span>${new Date(e.ts * 1000).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                    </div>
                    <div class="history-item-preview">${escapeHtml(e.preview)}</div>
                `;
                item.addEventListener("click", () => {
                    document.getElementById("answer-input").value = e.preview;
                    performAudit(e.preview);
                });
                list.appendChild(item);
            });
        }
    } catch (e) { console.error("History load failed", e); }
}

async function performAudit(textOverride = null) {
    const textarea = document.getElementById("answer-input");
    const answer = textOverride || textarea.value.trim();
    if (!answer) return;

    textarea.value = answer;
    document.getElementById("char-count").textContent = `${answer.length} / 8000`;

    setLoading(true, "check-btn");
    try {
        const res = await fetch(`${API_BASE}/check`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ answer }),
        });
        const data = await res.json();
        renderResults(answer, data);
        loadStats();
        loadHistory();
    } catch (e) {
        alert("Verification failed. Is the backend running?");
    } finally {
        setLoading(false, "check-btn");
    }
}

async function performUrlAudit() {
    const url = document.getElementById("url-input").value.trim();
    if (!url) return;

    setLoading(true, "check-url-btn");
    try {
        const res = await fetch(`${API_BASE}/check`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url }),
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "URL audit failed");
        }
        const data = await res.json();
        renderResults(url, data);
        loadStats();
        loadHistory();
    } catch (e) {
        alert(`URL Audit failed: ${e.message}`);
    } finally {
        setLoading(false, "check-url-btn");
    }
}

function renderResults(answer, data) {
    const resultsSec = document.getElementById("results-section");
    resultsSec.classList.remove("hidden");
    resultsSec.scrollIntoView({ behavior: "smooth" });
    document.getElementById("timing-badge").textContent = `${data.timing_seconds}s`;

    // Summary banner
    document.getElementById("summary-text").textContent = data.summary_sentence || "Audit completed.";

    // Score
    const score = data.overall_freshness;
    const num = document.getElementById("score-number");
    const title = document.getElementById("score-verdict");

    num.textContent = score !== null ? score : "--";
    num.style.color = score !== null ? (score > 70 ? "var(--success)" : (score > 40 ? "var(--amber)" : "var(--rose)")) : "var(--text-muted)";
    title.textContent = score === null ? "Insufficient Data" : (score > 70 ? "High Freshness" : "Stale Content Detected");

    // Highlights
    const out = document.getElementById("highlighted-output");
    out.replaceChildren();

    let cursor = 0;
    const claims = (data.claims || []).filter(c => c.span).sort((a,b) => a.span[0] - b.span[0]);

    for (const c of claims) {
        if (c.span[0] < cursor) continue;
        out.append(answer.slice(cursor, c.span[0]));
        const mark = document.createElement("mark");
        mark.className = `mark-${COLORS[c.score] || "gray"}`;
        mark.textContent = answer.slice(c.span[0], c.span[1]);
        mark.addEventListener("mouseenter", (e) => showTooltip(e, c));
        mark.addEventListener("mouseleave", hideTooltip);
        out.append(mark);
        cursor = c.span[1];
    }
    out.append(answer.slice(cursor));

    // Claims List
    const list = document.getElementById("claims-list");
    list.replaceChildren();
    data.claims.forEach(c => {
        const card = document.createElement("div");
        card.className = "claim-card";
        const color = COLORS[c.score] || "gray";

        let sources = c.sources.map(s => `
            <div class="source-item">
                <a href="${s.url}" target="_blank" class="source-link">🔗 ${escapeHtml(s.title || s.url)}</a>
                <span class="source-date mono">Updated: ${escapeHtml(s.published_date || 'Unknown')}</span>
            </div>
        `).join('');

        let notCheckedNote = c.verdict === "not_checked" ? `<div class="claim-reason text-rose"><strong>Skipped/Unchecked:</strong> ${escapeHtml(c.reason)}</div>` : "";

        card.innerHTML = `
            <div class="claim-card-top">
                <span class="claim-text">${escapeHtml(c.text)}</span>
                <span class="verdict-tag ${color}">${c.verdict.replace('_', ' ')}</span>
            </div>
            <div class="claim-reason">${escapeHtml(c.reason)}</div>
            ${notCheckedNote}
            <div class="source-list">${sources}</div>
        `;
        list.appendChild(card);
    });

    // Corrected Rewrite Pane
    const rewritePane = document.getElementById("rewrite-pane");
    if (data.corrected_answer) {
        rewritePane.classList.remove("hidden");
        document.getElementById("corrected-output").textContent = data.corrected_answer;
    } else {
        rewritePane.classList.add("hidden");
    }
}

function copyCorrectedText() {
    const text = document.getElementById("corrected-output").textContent;
    navigator.clipboard.writeText(text);
    alert("Corrected answer copied to clipboard!");
}

function showTooltip(e, c) {
    const tt = document.getElementById("tooltip");
    tt.textContent = c.reason;
    tt.style.left = `${e.clientX + 10}px`;
    tt.style.top = `${e.clientY + 10}px`;
    tt.classList.remove("hidden");
}

function hideTooltip() { document.getElementById("tooltip").classList.add("hidden"); }

function setLoading(b, btnId) {
    const btn = document.getElementById(btnId);
    btn.disabled = b;
    btn.querySelector(".spinner").classList.toggle("hidden", !b);
}

function escapeHtml(str) { return str ? str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;") : ''; }

function clearHistory() {
    document.getElementById("history-list").innerHTML = `<div class="empty-hint">No recent audits</div>`;
}