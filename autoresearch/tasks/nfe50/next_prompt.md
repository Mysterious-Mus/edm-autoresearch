You are the AutoResearch agent for a CIFAR-10 diffusion sampling assignment.

Goal: propose the next sampler-only config that may improve FID while obeying the fixed controls.

Fixed controls, do not change:
- dataset: cifar10-32x32
- network: https://nvlabs-fi-cdn.nvidia.com/edm/pretrained/baseline/baseline-cifar10-32x32-uncond-vp.pkl
- seeds: 0-4999
- sample count: 5000
- NFE budget: 50
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

Task: cifar10-nfe50
Best completed run so far: 000-baseline with FID 7.67612

Completed and attempted runs:

## 000-baseline
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

Config used:
```toml
# Auto-generated from the task-level baseline config.

[proposal]
name = "baseline-heun-edm-nfe50"
hypothesis = "Baseline EDM-style Heun sampler under the fixed NFE 50 budget."
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

Config used:
```toml
[proposal]
name = "ve-linear-heun-nfe50"
hypothesis = "Testing VE discretization with linear schedule, which may provide a different noise trajectory and improve sample quality under the same NFE budget."
timestep_or_noise_schedule = "ve discretization with linear sigma schedule"
update_rule = "heun"
solver_type = "heun"
stochastic_updates = "disabled"
budget_allocation = "maximum number of Heun steps under the fixed NFE budget"
score_manipulation = "none"

[sampler]
solver = "heun"
discretization = "ve"
schedule = "linear"
scaling = "none"
rho = 7
S_churn = 0
S_min = 0
S_max = inf
S_noise = 1
```

## 002-candidate
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

Config used:
```toml
[proposal]
name = "edm-linear-heun-churn-nfe50"
hypothesis = "Introducing moderate stochasticity via S_churn may improve sample diversity and quality under the same NFE budget by allowing small noise injection during sampling, potentially escaping local optima."
timestep_or_noise_schedule = "edm discretization with linear sigma schedule"
update_rule = "heun"
solver_type = "heun"
stochastic_updates = "enabled with S_churn=20, S_min=0.05, S_max=50, S_noise=1.003"
budget_allocation = "maximum number of Heun steps under the fixed NFE budget"
score_manipulation = "none"

[sampler]
solver = "heun"
discretization = "edm"
schedule = "linear"
scaling = "none"
rho = 7
S_churn = 20
S_min = 0.05
S_max = 50
S_noise = 1.003
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
