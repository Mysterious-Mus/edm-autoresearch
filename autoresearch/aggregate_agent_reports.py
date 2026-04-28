#!/usr/bin/env python3
"""Aggregate AutoResearch agent reports across task run folders."""

import argparse
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def json_safe(value):
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    return value


def task_sort_key(task_dir):
    name = task_dir.name
    if name.startswith("nfe"):
        try:
            return (0, int(name[3:]))
        except ValueError:
            pass
    return (1, name)


def run_sort_key(run_dir):
    prefix = run_dir.name.split("-", 1)[0]
    try:
        return (int(prefix), run_dir.name)
    except ValueError:
        return (10**9, run_dir.name)


def run_record(task_dir, run_dir):
    report_path = run_dir / "agent_report.json"
    result_path = run_dir / "result.json"
    config_path = run_dir / "config.toml"

    report = load_json(report_path)
    result = report.get("result", {})
    full_result = load_json(result_path) if result_path.exists() else {}
    proposal = report.get("proposal", {})

    return {
        "task": task_dir.name,
        "run": run_dir.name,
        "proposal_name": proposal.get("name"),
        "hypothesis": proposal.get("hypothesis"),
        "timestep_or_noise_schedule": proposal.get("timestep_or_noise_schedule"),
        "update_rule": proposal.get("update_rule"),
        "solver_type": proposal.get("solver_type"),
        "stochastic_updates": proposal.get("stochastic_updates"),
        "budget_allocation": proposal.get("budget_allocation"),
        "score_manipulation": proposal.get("score_manipulation"),
        "sampler": json_safe(report.get("sampler", {})),
        "status": result.get("status"),
        "fid": result.get("fid"),
        "nfe_budget": result.get("nfe_budget"),
        "actual_nfe": result.get("actual_nfe"),
        "num_steps": result.get("num_steps"),
        "seed_count": result.get("seed_count"),
        "solver": result.get("solver"),
        "generation_seconds": result.get("generation_seconds"),
        "fid_seconds": result.get("fid_seconds"),
        "completed_at": result.get("completed_at"),
        "paths": {
            "run_dir": str(run_dir.relative_to(ROOT)),
            "agent_report": str(report_path.relative_to(ROOT)),
            "result": str(result_path.relative_to(ROOT)) if result_path.exists() else None,
            "config": str(config_path.relative_to(ROOT)) if config_path.exists() else None,
            "fid_log": full_result.get("fid_evaluation", {}).get("log"),
            "generate_log": full_result.get("generation", {}).get("log"),
        },
    }


def summarize_task(task, runs):
    completed = [run for run in runs if run.get("status") == "completed" and run.get("fid") is not None]
    baseline = next((run for run in completed if run["run"] == "000-baseline"), None)
    best = min(completed, key=lambda run: run["fid"]) if completed else None
    failed = [run for run in runs if run.get("status") != "completed"]

    summary = {
        "task": task,
        "nfe_budget": baseline.get("nfe_budget") if baseline else None,
        "num_runs": len(runs),
        "num_completed": len(completed),
        "num_failed": len(failed),
        "baseline_run": baseline,
        "best_run": best,
        "completed_runs": completed,
        "failed_runs": failed,
    }
    if baseline and best:
        summary["absolute_fid_improvement"] = baseline["fid"] - best["fid"]
        summary["relative_fid_improvement_percent"] = (
            (baseline["fid"] - best["fid"]) / baseline["fid"] * 100
        )
    return summary


def collect(tasks_dir):
    tasks = {}
    for task_dir in sorted((path for path in tasks_dir.iterdir() if path.is_dir()), key=task_sort_key):
        runs_dir = task_dir / "runs"
        if not runs_dir.exists():
            continue
        runs = []
        for run_dir in sorted((path for path in runs_dir.iterdir() if path.is_dir()), key=run_sort_key):
            if (run_dir / "agent_report.json").exists():
                runs.append(run_record(task_dir, run_dir))
        if runs:
            tasks[task_dir.name] = summarize_task(task_dir.name, runs)
    return {"tasks_dir": str(tasks_dir.relative_to(ROOT)), "tasks": tasks}


def format_value(value):
    if isinstance(value, float):
        return f"{value:.4f}"
    if value is None:
        return "n/a"
    return str(value)


def write_markdown(aggregate, path):
    lines = ["# Aggregated AutoResearch Agent Reports", ""]
    for task, summary in aggregate["tasks"].items():
        lines.extend(
            [
                f"## {task}",
                "",
                f"- NFE budget: {format_value(summary['nfe_budget'])}",
                f"- Completed runs: {summary['num_completed']} / {summary['num_runs']}",
                f"- Baseline FID: {format_value((summary['baseline_run'] or {}).get('fid'))}",
                f"- Best FID: {format_value((summary['best_run'] or {}).get('fid'))}",
                f"- Absolute FID improvement: {format_value(summary.get('absolute_fid_improvement'))}",
                f"- Relative FID improvement: {format_value(summary.get('relative_fid_improvement_percent'))}%",
                "",
                "| Run | Proposal | Solver | Actual NFE | FID | Status | Main change |",
                "| --- | --- | --- | ---: | ---: | --- | --- |",
            ]
        )
        for run in summary["completed_runs"] + summary["failed_runs"]:
            change = run.get("stochastic_updates") or run.get("hypothesis") or ""
            change = change.replace("\n", " ")
            lines.append(
                "| {run} | {proposal} | {solver} | {nfe} | {fid} | {status} | {change} |".format(
                    run=run["run"],
                    proposal=run.get("proposal_name") or "",
                    solver=run.get("solver") or run.get("solver_type") or "",
                    nfe=format_value(run.get("actual_nfe")),
                    fid=format_value(run.get("fid")),
                    status=run.get("status") or "",
                    change=change,
                )
            )
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks-dir", type=Path, default=ROOT / "autoresearch" / "tasks")
    parser.add_argument("--json-out", type=Path, default=ROOT / "agent_answers" / "aggregated_agent_reports.json")
    parser.add_argument("--md-out", type=Path, default=ROOT / "agent_answers" / "aggregated_agent_reports.md")
    args = parser.parse_args()

    tasks_dir = args.tasks_dir.resolve()
    aggregate = collect(tasks_dir)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(aggregate, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    write_markdown(aggregate, args.md_out)
    print(f"Wrote {args.json_out}")
    print(f"Wrote {args.md_out}")


if __name__ == "__main__":
    main()
