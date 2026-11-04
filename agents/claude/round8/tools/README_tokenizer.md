# Tokenizer setup used for this report
- `pip install tiktoken` (version used: 0.14.0).
- tiktoken normally downloads `o200k_base.tiktoken` and `cl100k_base.tiktoken` from openaipublic.blob.core.windows.net.
  That host was blocked in my sandbox, so I rebuilt both files from the copy bundled in the npm package gpt-tokenizer 4.1.0:
  `npm install gpt-tokenizer@4.1.0 && node tools/export_ranks.js` (run where node_modules lives).
- The rebuilt files are byte-identical to OpenAI's: their SHA-256 equals the `expected_hash` hard-coded in tiktoken
  (o200k_base 446a9538..., cl100k_base 223921b7...). They were placed in a directory named by `TIKTOKEN_CACHE_DIR`
  under the SHA-1 of their download URL, which is where tiktoken looks before downloading, and tiktoken re-verifies the hash.
- If your machine can reach the download host, skip all of this: plain `pip install tiktoken` gives the same files.
- These counts measure text artefacts only. They are not model inference, reasoning or billing tokens.
