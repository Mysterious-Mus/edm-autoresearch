# edm-linear-euler-churn-nfe50

## Proposal
- Hypothesis: Switching to Euler solver with moderate stochasticity may improve FID by trading off some accuracy for more steps within the NFE budget, allowing finer trajectory discretization and potential better sample quality.
- Schedule: edm discretization with linear sigma schedule
- Update rule: euler
- Solver: euler
- Stochasticity: enabled with S_churn=15, S_min=0.05, S_max=50, S_noise=1.003
- Budget allocation: Maximum number of Euler steps under the fixed NFE budget, allowing approximately double the steps compared to Heun for finer schedule coverage.
- Score manipulation: none

## Sampler Config
- S_churn: 15
- S_max: 50
- S_min: 0.05
- S_noise: 1.003
- discretization: edm
- rho: 7
- scaling: none
- schedule: linear
- solver: euler

## Result
- Status: completed
- FID: 13.3702
- FID enabled: True
- NFE budget: 50
- Actual NFE: 50
- Sampling steps: 50
- Seed count: 5000
- Generation seconds: 99.045
- FID seconds: 9.952
