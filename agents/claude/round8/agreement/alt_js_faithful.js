// JS variant implementing the CANDIDATE contract: whitespace and case folding come from the contract's normative tables.
const WS = new Set(require("./tables/python_whitespace.json"));
const FOLD = require("./tables/casefold_full.json");
function collapse(s) { const out = []; let cur = ""; for (const ch of s) { if (WS.has(ch.codePointAt(0))) { if (cur) out.push(cur); cur = ""; } else cur += ch; } if (cur) out.push(cur); return out.join(" "); }
function fold(s) { let r = ""; for (const ch of s) { const f = FOLD[ch.codePointAt(0)]; r += f === undefined ? ch : f; } return r; }
function norm(s) { return collapse(fold(s.normalize("NFKC"))); }
function groupByWindow(events, window) {
  if (!Array.isArray(events)) throw { code: "E_TYPE" };
  if (!Number.isInteger(window) || window <= 0) throw { code: "E_WINDOW" };
  for (const e of events) {
    if (typeof e !== "object" || e === null || ["device", "kind", "message"].some(f => typeof e[f] !== "string")) throw { code: "E_TYPE" };
    if (!Number.isInteger(e.timestamp)) throw { code: "E_TYPE" };
  }
  const groups = [], open = new Map();
  const sorted = events.map((e, i) => [e, i]).sort((a, b) => a[0].timestamp - b[0].timestamp || a[1] - b[1]).map(x => x[0]);
  for (const e of sorted) {
    const k = JSON.stringify([norm(e.device), norm(e.kind), collapse(e.message)]); const g = open.get(k);
    if (g && e.timestamp - g.first < window) { g.last = e.timestamp; g.count++; }
    else { const [d, kd, m] = JSON.parse(k); const n = { device: d, kind: kd, message: m, first: e.timestamp, last: e.timestamp, count: 1 }; open.set(k, n); groups.push(n); }
  }
  return groups;
}
module.exports = { groupByWindow };
