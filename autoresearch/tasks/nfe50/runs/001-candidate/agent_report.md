# ve-linear-heun-nfe50

## Proposal
- Hypothesis: Testing VE discretization with linear schedule, which may provide a different noise trajectory and improve sample quality under the same NFE budget.
- Schedule: ve discretization with linear sigma schedule
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
- discretization: ve
- rho: 7
- scaling: none
- schedule: linear
- solver: heun

## Result
- Status: completed
- FID: 8.31394
- FID enabled: True
- NFE budget: 50
- Actual NFE: 49
- Sampling steps: 25
- Seed count: 5000
- Generation seconds: 160.213
- FID seconds: 12.332
