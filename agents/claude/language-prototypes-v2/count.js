// Usage: node count.js < input.json   where input.json = {"name": "text", ...}
// Prints JSON {name: {chars, bytes, o200k, cl100k, llama3, qwen25, deepseekv3, gemma3}}
const fs = require('fs');
const o200k = require('gpt-tokenizer/encoding/o200k_base');
const cl100k = require('gpt-tokenizer/encoding/cl100k_base');
const l3m = require('llama3-tokenizer-js'); const llama3 = l3m.default || l3m;
const qwen = require('@lenml/tokenizer-qwen2_5').fromPreTrained();
const dsv3 = require('@lenml/tokenizer-deepseek_v3').fromPreTrained();
const gemma = require('@lenml/tokenizer-gemma3').fromPreTrained();
const hf = (tok, s) => tok.encode(s, { add_special_tokens: false }).length;
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const out = {};
for (const [name, s] of Object.entries(input)) {
  out[name] = {
    chars: [...s].length,
    bytes: Buffer.byteLength(s, 'utf8'),
    o200k: o200k.encode(s).length,
    cl100k: cl100k.encode(s).length,
    llama3: llama3.encode(s, { bos: false, eos: false }).length,
    qwen25: hf(qwen, s),
    deepseekv3: hf(dsv3, s),
    gemma3: hf(gemma, s),
  };
}
console.log(JSON.stringify(out));
