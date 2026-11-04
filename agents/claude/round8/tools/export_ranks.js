// Rebuild a .tiktoken rank file ("<base64 bytes> <rank>\n" per line) from gpt-tokenizer's bundled table.
const fs = require('fs'), crypto = require('crypto');
for (const [name, expected] of [["o200k_base", "446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d"],
                                ["cl100k_base", "223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7"]]) {
  const mod = require(`${process.cwd()}/node_modules/gpt-tokenizer/cjs/bpeRanks/${name}.js`);
  const ranks = mod.default || mod;
  let out = "", kinds = {};
  ranks.forEach((tok, rank) => {
    if (tok === undefined || tok === null) return;
    const kind = typeof tok === "string" ? "string" : (Array.isArray(tok) ? "bytes" : typeof tok); kinds[kind] = (kinds[kind] || 0) + 1;
    const buf = typeof tok === "string" ? Buffer.from(tok, "utf8") : Buffer.from(tok);
    out += buf.toString("base64") + " " + rank + "\n";
  });
  const sha = crypto.createHash("sha256").update(out).digest("hex");
  fs.writeFileSync(`${name}.tiktoken`, out);
  console.log(name, "entries", Object.values(kinds).reduce((a, b) => a + b, 0), JSON.stringify(kinds), "sha256 match:", sha === expected, sha.slice(0, 16));
}
