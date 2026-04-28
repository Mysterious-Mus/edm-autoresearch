# baseline-heun-edm-nfe20

## Proposal
- Hypothesis: Baseline EDM-style Heun sampler under the fixed NFE 20 budget.
- Schedule: edm discretization with linear sigma schedule
- Update rule: heun
- Solver: heun
- Stochasticity: disabled
- Budget allocation: maximum number of Heun steps under the fixed NFE budget
- Score manipulation: none

## Sampler Config
- S_churn: 0
- S_max: inf
- S_min: 0
- S_noise: 1
- discretization: edm
- rho: 7
- scaling: none
- schedule: linear
- solver: heun

## Result
- Status: completed
- FID: 55.9529
- FID enabled: True
- NFE budget: 20
- Actual NFE: 19
- Sampling steps: 10
- Seed count: 5000
- Generation seconds: 42.347
- FID seconds: 12.894
