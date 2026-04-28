# Aggregated AutoResearch Agent Reports

## nfe20

- NFE budget: 20
- Completed runs: 5 / 5
- Baseline FID: 55.9529
- Best FID: 10.1439
- Absolute FID improvement: 45.8090
- Relative FID improvement: 81.8706%

| Run | Proposal | Solver | Actual NFE | FID | Status | Main change |
| --- | --- | --- | ---: | ---: | --- | --- |
| 000-baseline | baseline-heun-edm-nfe20 | heun | 19 | 55.9529 | completed | disabled |
| 001-candidate | stochastic-heun-edm-nfe20 | heun | 19 | 10.7674 | completed | enabled with S_churn=40, S_min=0.05, S_max=50, S_noise=1 |
| 002-candidate | reduced-stochastic-heun-edm-nfe20 | heun | 19 | 10.9438 | completed | enabled with S_churn=20, S_min=0.02, S_max=30, S_noise=1 |
| 003-candidate | increased-stochastic-heun-edm-nfe20 | heun | 19 | 10.7248 | completed | enabled with S_churn=60, S_min=0.1, S_max=80, S_noise=1 |
| 004-candidate | very-high-stochastic-heun-edm-nfe20 | heun | 19 | 10.1439 | completed | enabled with S_churn=80, S_min=0.15, S_max=100, S_noise=1 |

## nfe50

- NFE budget: 50
- Completed runs: 4 / 4
- Baseline FID: 7.6761
- Best FID: 7.6761
- Absolute FID improvement: 0.0000
- Relative FID improvement: 0.0000%

| Run | Proposal | Solver | Actual NFE | FID | Status | Main change |
| --- | --- | --- | ---: | ---: | --- | --- |
| 000-baseline | baseline-heun-edm-nfe50 | heun | 49 | 7.6761 | completed | disabled |
| 001-candidate | ve-linear-heun-nfe50 | heun | 49 | 8.3139 | completed | disabled |
| 002-candidate | edm-linear-heun-churn-nfe50 | heun | 49 | 7.7890 | completed | enabled with S_churn=20, S_min=0.05, S_max=50, S_noise=1.003 |
| 003-candidate | edm-linear-euler-churn-nfe50 | euler | 50 | 13.3702 | completed | enabled with S_churn=15, S_min=0.05, S_max=50, S_noise=1.003 |
