# very-high-stochastic-heun-edm-nfe20

## Proposal
- Hypothesis: Push stochasticity to an extreme to test if even higher noise injection yields further FID improvement, exploring the limit before potential degradation.
- Schedule: edm discretization with linear sigma schedule, same as baseline
- Update rule: stochastic heun with very high noise injection
- Solver: heun
- Stochasticity: enabled with S_churn=80, S_min=0.15, S_max=100, S_noise=1
- Budget allocation: maximum number of Heun steps under the fixed NFE budget, same as baseline
- Score manipulation: none

## Sampler Config
- S_churn: 80
- S_max: 100
- S_min: 0.15
- S_noise: 1
- discretization: edm
- rho: 7
- scaling: none
- schedule: linear
- solver: heun

## Result
- Status: completed
- FID: 10.1439
- FID enabled: True
- NFE budget: 20
- Actual NFE: 19
- Sampling steps: 10
- Seed count: 5000
- Generation seconds: 68.861
- FID seconds: 11.615
