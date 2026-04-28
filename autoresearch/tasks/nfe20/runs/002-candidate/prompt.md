You are the AutoResearch agent for a CIFAR-10 diffusion sampling assignment.

Goal: propose the next sampler-only config that may improve FID while obeying the fixed controls.

Fixed controls, do not change:
- dataset: cifar10-32x32
- network: https://nvlabs-fi-cdn.nvidia.com/edm/pretrained/baseline/baseline-cifar10-32x32-uncond-vp.pkl
- seeds: 0-4999
- sample count: 5000
- NFE budget: 20
- FID reference: https://nvlabs-fi-cdn.nvidia.com/edm/fid-refs/cifar10-32x32.npz

Allowed changes:
- timestep/noise schedule: sampler discretization, schedule, rho, sigma_min, sigma_max
- update rule and solver: euler or heun
- stochasticity: S_churn, S_min, S_max, S_noise
- budget allocation description, while the launcher enforces the fixed NFE budget
- score manipulation must stay 'none' unless generate.py is extended

Supported sampler keys:
- solver: euler or heun
- discretization: vp, ve, iddpm, edm
- schedule: vp, ve, linear
- scaling: vp, none
- rho, sigma_min, sigma_max, S_churn, S_min, S_max, S_noise

Task: cifar10-nfe20
Best completed run so far: 001-candidate with FID 10.7674

Completed and attempted runs:

## 000-baseline
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

Config used:
```toml
# Auto-generated from the task-level baseline config.

[proposal]
name = "baseline-heun-edm-nfe20"
hypothesis = "Baseline EDM-style Heun sampler under the fixed NFE 20 budget."
timestep_or_noise_schedule = "edm discretization with linear sigma schedule"
update_rule = "heun"
solver_type = "heun"
stochastic_updates = "disabled"
budget_allocation = "maximum number of Heun steps under the fixed NFE budget"
score_manipulation = "none"

[sampler]
solver = "heun"
discretization = "edm"
schedule = "linear"
scaling = "none"
rho = 7
S_churn = 0
S_min = 0
S_max = inf
S_noise = 1
```

## 001-candidate
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

Config used:
```toml
[proposal]
name = "stochastic-heun-edm-nfe20"
hypothesis = "Introduce moderate stochasticity via S_churn to potentially improve sample diversity and FID, while keeping the same NFE budget."
timestep_or_noise_schedule = "edm discretization with linear sigma schedule, same as baseline"
update_rule = "stochastic heun with controlled noise injection"
solver_type = "heun"
stochastic_updates = "enabled with S_churn=40, S_min=0.05, S_max=50, S_noise=1"
budget_allocation = "maximum number of Heun steps under the fixed NFE budget, same as baseline"
score_manipulation = "none"

[sampler]
solver = "heun"
discretization = "edm"
schedule = "linear"
scaling = "none"
rho = 7
S_churn = 40
S_min = 0.05
S_max = 50
S_noise = 1
```

Return only the next experiment config.toml. Do not include analysis outside the TOML.
Use this exact shape:
```toml
[proposal]
name = "short-descriptive-name"
hypothesis = "What sampler change is being tested and why it might improve FID."
timestep_or_noise_schedule = "Describe the timestep or noise schedule."
update_rule = "Describe the update rule."
solver_type = "euler or heun"
stochastic_updates = "disabled, or describe S_churn/S_min/S_max/S_noise"
budget_allocation = "How the fixed NFE budget is allocated across the trajectory."
score_manipulation = "none"

[sampler]
solver = "heun"
discretization = "edm"
schedule = "linear"
scaling = "none"
rho = 7
S_churn = 0
S_min = 0
S_max = inf
S_noise = 1
```
