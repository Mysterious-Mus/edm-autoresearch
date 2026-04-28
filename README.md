# AutoResearch Experiment Harness

This repository contains an AutoResearch harness built on top of NVIDIA EDM.
The original EDM README has been preserved as `[README-edm.md](./README-edm.md)`.
Set up the Python/CUDA environment by following the requirements and environment
instructions in `README-edm.md` before running any of the commands below.

The harness keeps each sampling proposal as an experiment folder. In `autoresearch/`:

- `fixed_nfe20.toml`: immutable controls for the NFE 20 case.
- `fixed_nfe50.toml`: immutable controls for the NFE 50 case.
- `fixed_smoke.toml`: tiny non-FID config for plumbing checks.
- `tasks/nfe20/config.toml`: AutoResearch loop config for the NFE 20 case.
- `tasks/nfe50/config.toml`: AutoResearch loop config for the NFE 50 case.
- `experiments/*/config.toml`: agent-editable sampler proposal.
- `experiments/*/result.json`: machine-readable outcome written after a run.
- `experiments/*/generate.log`: full generation log for debugging.
- `tasks/*/runs/*/agent_report.md`: compact report for the next agent decision.

## Quick Checks

Run a smoke experiment:

```bash
python autoresearch/run_experiment.py \
  --fixed autoresearch/fixed_smoke.toml \
  --experiment autoresearch/experiments/smoke-nfe20
```

Run one assignment-scale NFE 20 baseline:

```bash
python autoresearch/run_experiment.py \
  --fixed autoresearch/fixed_nfe20.toml \
  --experiment autoresearch/tasks/nfe20/runs/000-baseline
```

The launcher derives the number of sampling steps from the fixed NFE budget and
the configured solver, so the agent can change sampler choices without quietly
changing the comparison budget.

## LLM Setup

Configure an LLM command before launching `autoresearch/run_autoresearch.py`.
The command must read the prompt from stdin and print only the next experiment
TOML to stdout. You can provide it with `AUTORESEARCH_LLM_CMD` or with
`[llm].command` in the task config.

For a generic local or hosted CLI:

```bash
export AUTORESEARCH_LLM_CMD='your-llm-cli --model your-model'
```

For an OpenAI-compatible HTTP API, use the included wrapper:

```bash
export OPENAI_ENDPOINT='https://your-provider.example.com/v1'
export OPENAI_API_KEY='your-api-key'
export OPENAI_MODEL_NAME='your-model-name'
export AUTORESEARCH_LLM_CMD='python autoresearch/openai_compatible_next_config.py'
```

`OPENAI_ENDPOINT` can be either the base `/v1` URL or the full
`/chat/completions` URL. Optional knobs:

```bash
export OPENAI_TEMPERATURE='0.7'
export OPENAI_MAX_TOKENS='1200'
```

If no LLM command is configured, the loop can still run the baseline and write
`next_prompt.md`, but it will not automatically propose the next config.

## Launch AutoResearch

After the EDM environment and LLM command are configured, launch a task:

```bash
python autoresearch/run_autoresearch.py --task autoresearch/tasks/nfe20
python autoresearch/run_autoresearch.py --task autoresearch/tasks/nfe50
```

The assignment-scale fixed configs use 5,000 generated images for FID:

```toml
[run]
seeds = "0-4999"
batch = 64

[evaluation]
compute_fid = true
num_images = 5000
```

The assignment asks for fixed seeds and fixed budgets, so those controls belong
in the fixed config. The experiment config is for sampler changes only:
timestep/noise schedule, update rule, solver, stochasticity, budget allocation
description, score-function manipulation description, and sampler
hyperparameters supported by `generate.py`.