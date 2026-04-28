# stochastic-heun-edm-nfe20

## Proposal
- Hypothesis: Introduce moderate stochasticity via S_churn to potentially improve sample diversity and FID, while keeping the same NFE budget.
- Schedule: edm discretization with linear sigma schedule, same as baseline
- Update rule: stochastic heun with controlled noise injection
- Solver: heun
- Stochasticity: enabled with S_churn=40, S_min=0.05, S_max=50, S_noise=1
- Budget allocation: maximum number of Heun steps under the fixed NFE budget, same as baseline
- Score manipulation: none

## Sampler Config
- S_churn: 40
- S_max: 50
- S_min: 0.05
- S_noise: 1
- discretization: edm
- rho: 7
- scaling: none
- schedule: linear
- solver: heun

## Result
- Status: completed
- FID: 10.7674
- FID enabled: True
- NFE budget: 20
- Actual NFE: 19
- Sampling steps: 10
- Seed count: 5000
- Generation seconds: 43.375
- FID seconds: 9.792
