# increased-stochastic-heun-edm-nfe20

## Proposal
- Hypothesis: Increase stochasticity beyond the best run to test if higher noise injection further improves sample diversity and lowers FID, exploring the upper bound of beneficial stochasticity.
- Schedule: edm discretization with linear sigma schedule, same as baseline
- Update rule: stochastic heun with increased noise injection
- Solver: heun
- Stochasticity: enabled with S_churn=60, S_min=0.1, S_max=80, S_noise=1
- Budget allocation: maximum number of Heun steps under the fixed NFE budget, same as baseline
- Score manipulation: none

## Sampler Config
- S_churn: 60
- S_max: 80
- S_min: 0.1
- S_noise: 1
- discretization: edm
- rho: 7
- scaling: none
- schedule: linear
- solver: heun

## Result
- Status: completed
- FID: 10.7248
- FID enabled: True
- NFE budget: 20
- Actual NFE: 19
- Sampling steps: 10
- Seed count: 5000
- Generation seconds: 43.124
- FID seconds: 9.791
