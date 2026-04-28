# edm-linear-heun-churn-nfe50

## Proposal
- Hypothesis: Introducing moderate stochasticity via S_churn may improve sample diversity and quality under the same NFE budget by allowing small noise injection during sampling, potentially escaping local optima.
- Schedule: edm discretization with linear sigma schedule
- Update rule: heun
- Solver: heun
- Stochasticity: enabled with S_churn=20, S_min=0.05, S_max=50, S_noise=1.003
- Budget allocation: maximum number of Heun steps under the fixed NFE budget
- Score manipulation: none

## Sampler Config
- S_churn: 20
- S_max: 50
- S_min: 0.05
- S_noise: 1.003
- discretization: edm
- rho: 7
- scaling: none
- schedule: linear
- solver: heun

## Result
- Status: completed
- FID: 7.78896
- FID enabled: True
- NFE budget: 50
- Actual NFE: 49
- Sampling steps: 25
- Seed count: 5000
- Generation seconds: 121.788
- FID seconds: 9.908
