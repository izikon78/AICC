rows 45, unique combinations 45 of 45, all output signatures match within job: True
AICC register+bind median 0.9166 ms (max 4.8957 ms)

| Job | Mode | Plans | Pipeline median s | min-max s | Worker median s | min-max s | Peak MiB median | CPU median s |
|---|---|---|---:|---:|---:|---:|---:|---:|
| repeated-shuffled | reference | reference | 4.878065 | 4.643-4.993 | 7.161033 | 6.998-7.529 | 815.691 | 4.765 |
| repeated-shuffled | static | partitioned | 2.249717 | 2.079-2.319 | 4.524440 | 4.493-4.531 | 561.859 | 2.189 |
| repeated-shuffled | aicc_static | partitioned | 2.081067 | 2.042-2.220 | 4.396034 | 4.306-4.646 | 561.629 | 2.073 |
| repeated-shuffled | learned | partitioned | 2.292245 | 2.160-2.543 | 4.669369 | 4.363-4.954 | 564.164 | 2.145 |
| repeated-shuffled | aicc_learned | partitioned | 2.056383 | 2.012-2.243 | 4.277496 | 4.248-4.615 | 564.152 | 2.010 |
| diverse-shuffled | reference | reference | 6.269454 | 5.943-6.324 | 12.348188 | 11.888-12.818 | 1065.133 | 6.081 |
| diverse-shuffled | static | partitioned | 4.890549 | 4.871-5.731 | 11.288800 | 11.262-13.313 | 847.219 | 4.871 |
| diverse-shuffled | aicc_static | partitioned | 4.888657 | 4.788-5.047 | 11.364002 | 11.010-11.428 | 847.102 | 4.810 |
| diverse-shuffled | learned | partitioned | 4.999052 | 4.790-5.052 | 11.350079 | 11.016-11.782 | 849.434 | 4.950 |
| diverse-shuffled | aicc_learned | partitioned | 4.848849 | 4.839-5.051 | 11.347210 | 11.157-11.401 | 849.430 | 4.818 |
| ordered-stream | reference | reference | 5.148346 | 4.958-5.194 | 5.547906 | 5.343-5.594 | 515.688 | 4.934 |
| ordered-stream | static | ordered | 3.242011 | 3.192-3.584 | 3.582584 | 3.579-3.970 | 136.613 | 3.232 |
| ordered-stream | aicc_static | ordered | 3.258051 | 3.160-3.405 | 3.602285 | 3.525-3.755 | 136.777 | 3.242 |
| ordered-stream | learned | ordered | 3.139076 | 3.045-3.176 | 3.468085 | 3.378-3.553 | 139.141 | 3.124 |
| ordered-stream | aicc_learned | ordered | 3.347395 | 3.168-3.495 | 3.697820 | 3.531-3.890 | 139.305 | 3.246 |

| Mode | Sum pipeline medians s | vs reference | Sum worker medians s | vs reference |
|---|---:|---:|---:|---:|
| reference | 16.295865 | 0.000% | 25.057127 | 0.000% |
| static | 10.382276 | 36.289% | 19.395824 | 22.594% |
| aicc_static | 10.227775 | 37.237% | 19.362322 | 22.727% |
| learned | 10.430373 | 35.994% | 19.487533 | 22.228% |
| aicc_learned | 10.252627 | 37.084% | 19.322526 | 22.886% |

| Job | Baseline → candidate | Pipeline saved % | Worker saved % | Peak MiB saved % |
|---|---|---:|---:|---:|
| repeated-shuffled | reference → static | 53.88% | 36.82% | 31.12% |
| repeated-shuffled | static → aicc_static | 7.50% | 2.84% | 0.04% |
| repeated-shuffled | static → learned | -1.89% | -3.20% | -0.41% |
| repeated-shuffled | learned → aicc_learned | 10.29% | 8.39% | 0.00% |
| repeated-shuffled | reference → aicc_static | 57.34% | 38.61% | 31.15% |
| diverse-shuffled | reference → static | 21.99% | 8.58% | 20.46% |
| diverse-shuffled | static → aicc_static | 0.04% | -0.67% | 0.01% |
| diverse-shuffled | static → learned | -2.22% | -0.54% | -0.26% |
| diverse-shuffled | learned → aicc_learned | 3.00% | 0.03% | 0.00% |
| diverse-shuffled | reference → aicc_static | 22.02% | 7.97% | 20.47% |
| ordered-stream | reference → static | 37.03% | 35.42% | 73.51% |
| ordered-stream | static → aicc_static | -0.49% | -0.55% | -0.12% |
| ordered-stream | static → learned | 3.18% | 3.20% | -1.85% |
| ordered-stream | learned → aicc_learned | -6.64% | -6.62% | -0.12% |
| ordered-stream | reference → aicc_static | 36.72% | 35.07% | 73.48% |

granularity: 8096 differential cases, all outputs equal: True

```
[
 {
  "mode": "ordinary_split",
  "median_seconds": 0.1682603309999422,
  "min_seconds": 0.15103509499999745,
  "max_seconds": 0.18011918600006993
 },
 {
  "mode": "ordinary_fused",
  "median_seconds": 0.13818428600006882,
  "min_seconds": 0.13168713400000343,
  "max_seconds": 0.1405811930000027
 },
 {
  "mode": "aicc_split",
  "median_seconds": 3.5337825280000743,
  "min_seconds": 3.477208850000011,
  "max_seconds": 3.611336849000054
 },
 {
  "mode": "aicc_fused",
  "median_seconds": 1.823977967000019,
  "min_seconds": 1.7461113530000603,
  "max_seconds": 1.9304439589999447
 },
 {
  "mode": "ordinary_batch",
  "median_seconds": 0.12254203600002711,
  "min_seconds": 0.1222682379999469,
  "max_seconds": 0.13801156800002445
 },
 {
  "mode": "aicc_batch",
  "median_seconds": 0.12258736399996906,
  "min_seconds": 0.12205047600002672,
  "max_seconds": 0.1252720260000615
 }
]
```
