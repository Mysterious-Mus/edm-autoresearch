# reduced-stochastic-heun-edm-nfe20

## Proposal
- Hypothesis: Reduce stochasticity from previous best run to find a more optimal balance between noise injection and deterministic refinement, potentially further lowering FID.
- Schedule: edm discretization with linear sigma schedule, same as baseline
- Update rule: stochastic heun with reduced noise injection
- Solver: heun
- Stochasticity: enabled with S_churn=20, S_min=0.02, S_max=30, S_noise=1
- Budget allocation: maximum number of Heun steps under the fixed NFE budget, same as baseline
- Score manipulation: none

## Sampler Config
- S_churn: 20
- S_max: 30
- S_min: 0.02
- S_noise: 1
- discretization: edm
- rho: 7
- scaling: none
- schedule: linear
- solver: heun

## Result
- Status: completed
- FID: 10.9438
- FID enabled: True
- NFE budget: 20
- Actual NFE: 19
- Sampling steps: 10
- Seed count: 5000
- Generation seconds: 42.637
- FID seconds: 10.465
