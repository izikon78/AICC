const fs = require('fs'); const o200k = require('gpt-tokenizer/encoding/o200k_base');
const s = fs.readFileSync(0, 'utf8'); const ids = o200k.encode(s);
console.log(JSON.stringify(ids.map(i => o200k.decode([i]))));
