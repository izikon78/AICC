// E2b: WebAssembly sandbox boundary. The Round 7 controller compiled to Wasm calls two host imports (log_t0, log_t1)
// per run; compared with the same logic in plain JS. Measures boundary-crossing cost, not Wasm compute speed.
const fs = require("fs"), path = require("path");
require(path.join("/home/claude/sym/node_modules/wabt"))().then(wabt => {
  const bin = wabt.parseWat("controller.wat", fs.readFileSync("controller.wat", "utf8")).toBinary({}).buffer;
  let out = [];
  const imports = { env: { log_t0: n => out.push(`Starting controller service for ${n} runs`),
                           log_t1: (a, n) => out.push(`Restarting controller service for run ${a} of ${n}`) } };
  const t0c = process.hrtime.bigint(); const inst = new WebAssembly.Instance(new WebAssembly.Module(bin), imports);
  const instantiateUs = Number(process.hrtime.bigint() - t0c) / 1000;
  const js = n => { out = []; for (let i = 0; i < n; i++) i === 0 ? out.push(`Starting controller service for ${n} runs`) : out.push(`Restarting controller service for run ${i + 1} of ${n}`); return out; };
  const wasm = n => { out = []; inst.exports.main(n); return out; };
  for (const n of [3, 1000]) if (JSON.stringify(js(n)) !== JSON.stringify(wasm(n))) throw new Error("mismatch");
  const bench = (f, n, iters) => { for (let i = 0; i < iters / 10; i++) f(n); const per = [];
    for (let r = 0; r < 15; r++) { const t0 = process.hrtime.bigint(); for (let i = 0; i < iters; i++) f(n); per.push(Number(process.hrtime.bigint() - t0) / iters); }
    per.sort((a, b) => a - b); return { median_ns: per[7], p95_ns: per[14] }; };
  const res = { instantiate_us: instantiateUs, wasm_binary_bytes: bin.length };
  for (const [n, iters] of [[3, 200000], [1000, 2000]]) { res[`n=${n} plain JS`] = bench(js, n, iters); res[`n=${n} Wasm + host imports`] = bench(wasm, n, iters); }
  for (const [k, v] of Object.entries(res)) console.log(typeof v === "object" ? `  ${k.padEnd(34)} median ${(v.median_ns / 1000).toFixed(3)} us  p95 ${(v.p95_ns / 1000).toFixed(3)} us` : `  ${k}: ${typeof v === "number" ? v.toFixed(1) : v}`);
  fs.writeFileSync("wasm_results.json", JSON.stringify(res, null, 1));
});
