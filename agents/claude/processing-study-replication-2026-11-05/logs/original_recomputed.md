rows 45, unique combinations 45 of 30, all output signatures match within job: True
AICC register+bind median 1.6723 ms (max 2.4208 ms)

| Job | Mode | Plans | Pipeline median s | min-max s | Worker median s | min-max s | Peak MiB median | CPU median s |
|---|---|---|---:|---:|---:|---:|---:|---:|
| repeated-shuffled | reference | reference | 6.231347 | 5.743-7.988 | 10.667214 | 9.393-12.161 | 814.402 | 6.156 |
| repeated-shuffled | static | partitioned | 3.226232 | 3.163-3.337 | 7.366733 | 7.008-8.033 | 561.715 | 3.141 |
| repeated-shuffled | aicc_static | partitioned | 3.227102 | 3.223-4.406 | 7.620207 | 6.899-8.658 | 561.828 | 3.172 |
| repeated-shuffled | learned | partitioned | 3.182558 | 2.951-4.081 | 7.792786 | 6.549-8.270 | 563.672 | 3.172 |
| repeated-shuffled | aicc_learned | partitioned | 3.625496 | 3.189-3.664 | 7.281121 | 6.819-8.307 | 563.086 | 3.578 |
| diverse-shuffled | reference | reference | 8.649674 | 8.058-10.203 | 19.112862 | 18.882-21.197 | 1060.156 | 8.500 |
| diverse-shuffled | static | partitioned | 6.417942 | 6.272-7.123 | 17.015386 | 15.542-17.643 | 845.504 | 6.391 |
| diverse-shuffled | aicc_static | partitioned | 6.506443 | 6.366-6.773 | 17.796901 | 16.159-18.037 | 846.207 | 6.469 |
| diverse-shuffled | learned | partitioned | 6.255770 | 6.248-8.063 | 17.077512 | 16.382-19.620 | 849.512 | 6.234 |
| diverse-shuffled | aicc_learned | partitioned | 6.609283 | 6.328-6.891 | 17.658272 | 15.466-17.855 | 847.387 | 6.516 |
| ordered-stream | reference | reference | 7.796452 | 7.261-8.866 | 8.753058 | 8.208-9.742 | 515.523 | 7.734 |
| ordered-stream | static | ordered | 5.385320 | 5.318-5.907 | 6.140841 | 6.085-6.922 | 135.762 | 5.312 |
| ordered-stream | aicc_static | ordered | 5.326457 | 5.158-5.343 | 6.079846 | 5.944-6.186 | 135.777 | 5.219 |
| ordered-stream | learned | partitioned | 6.028008 | 5.959-6.213 | 6.855133 | 6.758-7.186 | 210.996 | 6.016 |
| ordered-stream | aicc_learned | partitioned | 5.461108 | 5.380-5.473 | 6.146807 | 6.121-6.191 | 210.742 | 5.391 |

| Mode | Sum pipeline medians s | vs reference | Sum worker medians s | vs reference |
|---|---:|---:|---:|---:|
| reference | 22.677474 | 0.000% | 38.533134 | 0.000% |
| static | 15.029494 | 33.725% | 30.522960 | 20.788% |
| aicc_static | 15.060003 | 33.590% | 31.496953 | 18.260% |
| learned | 15.466336 | 31.799% | 31.725430 | 17.667% |
| aicc_learned | 15.695887 | 30.786% | 31.086201 | 19.326% |

| Job | Baseline → candidate | Pipeline saved % | Worker saved % | Peak MiB saved % |
|---|---|---:|---:|---:|
| repeated-shuffled | reference → static | 48.23% | 30.94% | 31.03% |
| repeated-shuffled | static → aicc_static | -0.03% | -3.44% | -0.02% |
| repeated-shuffled | static → learned | 1.35% | -5.78% | -0.35% |
| repeated-shuffled | learned → aicc_learned | -13.92% | 6.57% | 0.10% |
| repeated-shuffled | reference → aicc_static | 48.21% | 28.56% | 31.01% |
| diverse-shuffled | reference → static | 25.80% | 10.97% | 20.25% |
| diverse-shuffled | static → aicc_static | -1.38% | -4.59% | -0.08% |
| diverse-shuffled | static → learned | 2.53% | -0.37% | -0.47% |
| diverse-shuffled | learned → aicc_learned | -5.65% | -3.40% | 0.25% |
| diverse-shuffled | reference → aicc_static | 24.78% | 6.89% | 20.18% |
| ordered-stream | reference → static | 30.93% | 29.84% | 73.67% |
| ordered-stream | static → aicc_static | 1.09% | 0.99% | -0.01% |
| ordered-stream | static → learned | -11.93% | -11.63% | -55.42% |
| ordered-stream | learned → aicc_learned | 9.40% | 10.33% | 0.12% |
| ordered-stream | reference → aicc_static | 31.68% | 30.54% | 73.66% |

granularity: 8096 differential cases, all outputs equal: True

```
[
 {
  "mode": "ordinary_split",
  "median_seconds": 0.2706516000034753,
  "min_seconds": 0.2681402000016533,
  "max_seconds": 0.2848202000022866
 },
 {
  "mode": "ordinary_fused",
  "median_seconds": 0.24871310000889935,
  "min_seconds": 0.22674270000425167,
  "max_seconds": 0.25091319999773987
 },
 {
  "mode": "aicc_split",
  "median_seconds": 4.615542500017909,
  "min_seconds": 4.456707600009395,
  "max_seconds": 5.800828799983719
 },
 {
  "mode": "aicc_fused",
  "median_seconds": 2.2867129999794997,
  "min_seconds": 2.27304830000503,
  "max_seconds": 2.495043300004909
 },
 {
  "mode": "ordinary_batch",
  "median_seconds": 0.19251969998003915,
  "min_seconds": 0.18819190000067465,
  "max_seconds": 0.6760331999976188
 },
 {
  "mode": "aicc_batch",
  "median_seconds": 0.20363420000649057,
  "min_seconds": 0.18653510001604445,
  "max_seconds": 0.22783739998703822
 }
]
```
