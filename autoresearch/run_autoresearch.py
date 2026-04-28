#!/usr/bin/env python3
"""Run an AutoResearch loop for one NFE task.

The loop is intentionally simple:
1. run the task baseline if needed;
2. summarize all completed runs into a prompt;
3. ask an external LLM command for the next config.toml;
4. run that config and repeat.

If no LLM command is configured, the script writes the prompt to next_prompt.md
and stops after the baseline. This makes the workflow usable manually first and
easy to automate later.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from run_experiment import dump_simple_toml, load_simple_toml


ROOT = Path(__file__).resolve().parents[1]


CONFIG_TEMPLATE = """[proposal]
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
"""


def task_path(path):
    path = Path(path)
    return path if path.is_absolute() else (ROOT / path).resolve()


def resolve_from(base_dir, path_text):
    path = Path(str(path_text))
    return path if path.is_absolute() else (base_dir / path).resolve()


def completed(run_dir):
    result_path = run_dir / "result.json"
    if not result_path.exists():
        return False
    try:
        result = json.loads(result_path.read_text())
    except json.JSONDecodeError:
        return False
    return result.get("status") == "completed"


def run_single_experiment(run_dir, fixed_config):
    command = [
        sys.executable,
        str(ROOT / "autoresearch" / "run_experiment.py"),
        "--fixed",
        str(fixed_config),
        "--experiment",
        str(run_dir),
    ]
    subprocess.run(command, cwd=str(ROOT), check=True)


def ensure_baseline_config(task_config, baseline_dir):
    config_path = baseline_dir / "config.toml"
    if config_path.exists():
        return
    proposal = task_config.get("baseline_proposal")
    sampler = task_config.get("baseline_sampler")
    if proposal is None or sampler is None:
        raise SystemExit(
            "Missing baseline config. Add [baseline_proposal] and [baseline_sampler] "
            f"to the task config, or create {config_path} manually."
        )
    baseline_dir.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        "# Auto-generated from the task-level baseline config.\n\n"
        + dump_simple_toml({"proposal": proposal, "sampler": sampler}),
        encoding="utf-8",
    )


def collect_run_reports(runs_dir):
    reports = []
    for run_dir in sorted(path for path in runs_dir.iterdir() if path.is_dir()):
        config_path = run_dir / "config.toml"
        agent_report_path = run_dir / "agent_report.md"
        result_path = run_dir / "result.json"
        if not config_path.exists():
            continue
        result = {}
        if result_path.exists():
            try:
                result = json.loads(result_path.read_text())
            except json.JSONDecodeError:
                result = {"status": "invalid_result_json"}
        reports.append(
            {
                "name": run_dir.name,
                "run_dir": run_dir,
                "config": config_path.read_text(encoding="utf-8"),
                "agent_report": agent_report_path.read_text(encoding="utf-8") if agent_report_path.exists() else "",
                "status": result.get("status", "not_run"),
                "fid": result.get("fid"),
                "actual_nfe": result.get("actual_nfe"),
            }
        )
    return reports


def best_completed_report(reports):
    completed_reports = [report for report in reports if report["status"] == "completed" and report["fid"] is not None]
    if not completed_reports:
        return None
    return min(completed_reports, key=lambda report: report["fid"])


def build_prompt(task_dir, task_config, fixed_config, reports):
    task = task_config.get("task", {})
    fixed = load_simple_toml(fixed_config)
    best = best_completed_report(reports)

    lines = [
        "You are the AutoResearch agent for a CIFAR-10 diffusion sampling assignment.",
        "",
        "Goal: propose the next sampler-only config that may improve FID while obeying the fixed controls.",
        "",
        "Fixed controls, do not change:",
        f"- dataset: {fixed['model']['dataset']}",
        f"- network: {fixed['model']['network']}",
        f"- seeds: {fixed['run']['seeds']}",
        f"- sample count: {fixed['evaluation']['num_images']}",
        f"- NFE budget: {fixed['run']['nfe_budget']}",
        f"- FID reference: {fixed['evaluation']['reference_stats']}",
        "",
        "Allowed changes:",
        "- timestep/noise schedule: sampler discretization, schedule, rho, sigma_min, sigma_max",
        "- update rule and solver: euler or heun",
        "- stochasticity: S_churn, S_min, S_max, S_noise",
        "- budget allocation description, while the launcher enforces the fixed NFE budget",
        "- score manipulation must stay 'none' unless generate.py is extended",
        "",
        "Supported sampler keys:",
        "- solver: euler or heun",
        "- discretization: vp, ve, iddpm, edm",
        "- schedule: vp, ve, linear",
        "- scaling: vp, none",
        "- rho, sigma_min, sigma_max, S_churn, S_min, S_max, S_noise",
        "",
        f"Task: {task.get('name', task_dir.name)}",
    ]
    if best is not None:
        lines.append(f"Best completed run so far: {best['name']} with FID {best['fid']}")
    lines.extend(["", "Completed and attempted runs:"])

    for report in reports:
        lines.extend(
            [
                "",
                f"## {report['name']}",
                report["agent_report"] or "(No agent report yet.)",
                "Config used:",
                "```toml",
                report["config"].strip(),
                "```",
            ]
        )

    lines.extend(
        [
            "",
            "Return only the next experiment config.toml. Do not include analysis outside the TOML.",
            "Use this exact shape:",
            "```toml",
            CONFIG_TEMPLATE.strip(),
            "```",
        ]
    )
    return "\n".join(lines) + "\n"


def extract_toml(text):
    match = re.search(r"```(?:toml)?\s*(.*?)```", text, flags=re.DOTALL | re.IGNORECASE)
    return (match.group(1) if match else text).strip() + "\n"


def ask_llm(command, prompt, run_dir):
    proc = subprocess.run(
        command,
        input=prompt,
        cwd=str(ROOT),
        text=True,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    (run_dir / "llm_stdout.txt").write_text(proc.stdout, encoding="utf-8")
    (run_dir / "llm_stderr.txt").write_text(proc.stderr, encoding="utf-8")
    if proc.returncode != 0:
        raise RuntimeError(f"LLM command failed with exit code {proc.returncode}; see {run_dir}")
    config_text = extract_toml(proc.stdout)
    parsed = load_simple_toml_from_text(config_text, run_dir / "config.toml")
    if "proposal" not in parsed or "sampler" not in parsed:
        raise ValueError("LLM output must contain [proposal] and [sampler] sections")
    return config_text


def load_simple_toml_from_text(text, display_path):
    temp_path = display_path.with_suffix(".validate.toml")
    temp_path.write_text(text, encoding="utf-8")
    try:
        return load_simple_toml(temp_path)
    finally:
        temp_path.unlink(missing_ok=True)


def next_run_dir(runs_dir):
    existing = [path.name for path in runs_dir.iterdir() if path.is_dir()]
    indices = []
    for name in existing:
        match = re.match(r"^(\d+)-", name)
        if match:
            indices.append(int(match.group(1)))
    next_index = max(indices, default=-1) + 1
    return runs_dir / f"{next_index:03d}-candidate"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True, type=Path, help="Task folder containing config.toml")
    parser.add_argument("--max-trials", type=int, default=None, help="Override task max_trials")
    parser.add_argument("--llm-command", default=None, help="Command that reads prompt on stdin and writes config TOML")
    parser.add_argument("--rerun-baseline", action="store_true", help="Run the baseline even if result.json is complete")
    parser.add_argument("--prompt-only", action="store_true", help="Build next prompt after baseline without calling an LLM")
    args = parser.parse_args()

    task_dir = task_path(args.task)
    task_config_path = task_dir / "config.toml"
    task_config = load_simple_toml(task_config_path)
    task = task_config["task"]
    fixed_config = resolve_from(task_dir, task["fixed_config"])
    runs_dir = task_dir / "runs"
    baseline_dir = resolve_from(task_dir, task["baseline_run"])
    max_trials = args.max_trials if args.max_trials is not None else int(task.get("max_trials", 1))
    ensure_baseline_config(task_config, baseline_dir)

    if args.rerun_baseline or not completed(baseline_dir):
        run_single_experiment(baseline_dir, fixed_config)

    llm_command = args.llm_command or os.environ.get("AUTORESEARCH_LLM_CMD") or task_config.get("llm", {}).get("command", "")

    for _ in range(max_trials):
        reports = collect_run_reports(runs_dir)
        prompt = build_prompt(task_dir, task_config, fixed_config, reports)
        prompt_path = task_dir / "next_prompt.md"
        prompt_path.write_text(prompt, encoding="utf-8")

        if args.prompt_only or not llm_command:
            print(f"Wrote next-step prompt to {prompt_path}")
            print("Set AUTORESEARCH_LLM_CMD or [llm].command to automate config generation.")
            return

        run_dir = next_run_dir(runs_dir)
        run_dir.mkdir(parents=True, exist_ok=False)
        (run_dir / "prompt.md").write_text(prompt, encoding="utf-8")
        config_text = ask_llm(llm_command, prompt, run_dir)
        (run_dir / "config.toml").write_text(config_text, encoding="utf-8")
        run_single_experiment(run_dir, fixed_config)


if __name__ == "__main__":
    main()
