// Batch runner: reads [{events, window}] from stdin, writes [{ok, groups} | {ok:false, code}] for the chosen variant.
const impl = require(process.argv[2]); const cases = JSON.parse(require("fs").readFileSync(0, "utf8"));
console.log(JSON.stringify(cases.map(c => { try { return { ok: true, groups: impl.groupByWindow(c.events, c.window) }; } catch (e) { return { ok: false, code: e.code || String(e) }; } })));
