# smoke-nfe20-heun-edm

## Proposal
- Hypothesis: Verify the experiment harness with the baseline EDM-style Heun sampler under the fixed NFE budget.
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
- FID: None
- FID enabled: False
- NFE budget: 20
- Actual NFE: 19
- Sampling steps: 10
- Seed count: 4
- Generation seconds: 4.217
- FID seconds: None
