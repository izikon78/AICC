// JS variant a vendor would naturally write from the SHARED contract text: JS defaults for "casefold" and "whitespace".
function collapse(s) { return s.split(/\s+/).filter(x => x.length).join(" "); }
function norm(s) { return collapse(s.normalize("NFKC").toLowerCase()); }
function groupByWindow(events, window) {
  if (!Array.isArray(events)) throw { code: "E_TYPE" };
  if (!Number.isInteger(window) || window <= 0) throw { code: "E_WINDOW" };
  for (const e of events) {
    if (typeof e !== "object" || e === null || ["device", "kind", "message"].some(f => typeof e[f] !== "string")) throw { code: "E_TYPE" };
    if (!Number.isInteger(e.timestamp)) throw { code: "E_TYPE" };
  }
  const groups = [], open = new Map();
  for (const e of [...events].sort((a, b) => a.timestamp - b.timestamp)) {
    const k = JSON.stringify([norm(e.device), norm(e.kind), collapse(e.message)]); const g = open.get(k);
    if (g && e.timestamp - g.first < window) { g.last = e.timestamp; g.count++; }
    else { const [d, kd, m] = JSON.parse(k); const n = { device: d, kind: kd, message: m, first: e.timestamp, last: e.timestamp, count: 1 }; open.set(k, n); groups.push(n); }
  }
  return groups;
}
module.exports = { groupByWindow };
