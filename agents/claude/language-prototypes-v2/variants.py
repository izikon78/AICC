from tok import table
T = 'T0="Starting controller service for {} runs"\nT1="Restarting controller service for run {} of {}"\n'
V = {
 "brief_@1_code_only": '@1(n:I){R(i:0<n){?(i=0):!7(T0,n):!7(T1,i+1,n)}}',
 "brief_@1_with_table": T + '@1(n:I){R(i:0<n){?(i=0):!7(T0,n):!7(T1,i+1,n)}}',
 "V2_kw_table": T + 'fn main(n:i32){for i<n{if i==0{log(T0,n)}else{log(T1,i+1,n)}}}',
 "V3_pyish_table": T + 'main n:i32 = for i<n: if i==0: log T0 n else log T1 i+1 n',
 "V4_sexpr_table": T + '(fn main (n i32) (for i n (if (= i 0) (log T0 n) (log T1 (+ i 1) n))))',
 "V5_prefix_table": T + 'fn1 main n:i32 for i n if = i 0 log T0 n log T1 + i 1 n',
 "V6_kw_inline": 'fn main(n:i32){for i<n{if i==0{log"Starting controller service for {n} runs"}else{log"Restarting controller service for run {i+1} of {n}"}}}',
 "V7_brief_inline": '@1(n:I){R(i:0<n){?(i=0):!7("Starting controller service for {n} runs"):!7("Restarting controller service for run {i+1} of {n}")}}',
 "V8_kw_inline_ternary": 'fn main(n:i32){for i<n{log(i==0?"Starting controller service for {n} runs":"Restarting controller service for run {i+1} of {n}")}}',
 "V9_prefix_inline": 'fn1 main n:i32 for i n if = i 0 log"Starting controller service for {n} runs" log"Restarting controller service for run {i+1} of {n}"',
}
table(V)
