# baseline-heun-edm-nfe50

## Proposal
- Hypothesis: Baseline EDM-style Heun sampler under the fixed NFE 50 budget.
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
- FID: 7.67612
- FID enabled: True
- NFE budget: 50
- Actual NFE: 49
- Sampling steps: 25
- Seed count: 5000
- Generation seconds: 121.629
- FID seconds: 10.204
