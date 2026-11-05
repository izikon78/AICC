const fs = require('fs'); const o200k = require('gpt-tokenizer/encoding/o200k_base');
const arr = JSON.parse(fs.readFileSync(0, 'utf8')); console.log(JSON.stringify(arr.map(s => o200k.encode(s).length)));
