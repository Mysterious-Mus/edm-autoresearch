#!/usr/bin/env python3
"""Launch one AutoResearch sampling experiment from TOML configs.

The experiment config is intended to be edited by the research agent. The fixed
config holds assignment controls that should not drift across proposals: model,
seeds, image count, and NFE budget.
"""

import argparse
import hashlib
import json
import math
import os
import re
import socket
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXED_CONFIG = ROOT / "autoresearch" / "fixed.toml"


SAMPLER_CLI_KEYS = {
    "sigma_min": "--sigma_min",
    "sigma_max": "--sigma_max",
    "rho": "--rho",
    "S_churn": "--S_churn",
    "S_min": "--S_min",
    "S_max": "--S_max",
    "S_noise": "--S_noise",
    "solver": "--solver",
    "discretization": "--disc",
    "schedule": "--schedule",
    "scaling": "--scaling",
}


SUPPORTED_SCORE_MANIPULATIONS = {"none"}


def parse_value(text):
    text = text.strip()
    if text in {"true", "false"}:
        return text == "true"
    if text in {"inf", "+inf"}:
        return math.inf
    if text == "-inf":
        return -math.inf
    if text.startswith('"') and text.endswith('"'):
        return bytes(text[1:-1], "utf-8").decode("unicode_escape")
    if text.startswith("'") and text.endswith("'"):
        return text[1:-1]
    if text.startswith("[") and text.endswith("]"):
        inner = text[1:-1].strip()
        if not inner:
            return []
        return [parse_value(part.strip()) for part in inner.split(",")]
    try:
        if any(ch in text.lower() for ch in [".", "e"]):
            return float(text)
        return int(text)
    except ValueError:
        return text


def strip_comment(line):
    in_single = False
    in_double = False
    escaped = False
    for idx, char in enumerate(line):
        if escaped:
            escaped = False
            continue
        if char == "\\" and in_double:
            escaped = True
            continue
        if char == "'" and not in_double:
            in_single = not in_single
            continue
        if char == '"' and not in_single:
            in_double = not in_double
            continue
        if char == "#" and not in_single and not in_double:
            return line[:idx]
    return line


def load_simple_toml(path):
    data = {}
    section = data
    section_name = None
    for line_number, raw_line in enumerate(Path(path).read_text().splitlines(), start=1):
        line = strip_comment(raw_line).strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            section_name = line[1:-1].strip()
            if not section_name:
                raise ValueError(f"{path}:{line_number}: empty section name")
            section = data.setdefault(section_name, {})
            continue
        if "=" not in line:
            raise ValueError(f"{path}:{line_number}: expected key = value")
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"{path}:{line_number}: empty key")
        section[key] = parse_value(value)
    return data


def toml_scalar(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isinf(value):
            return "inf" if value > 0 else "-inf"
        return str(value)
    return json.dumps(str(value))


def dump_simple_toml(data):
    lines = []
    for section_name, values in data.items():
        lines.append(f"[{section_name}]")
        for key, value in values.items():
            if isinstance(value, list):
                rendered = "[" + ", ".join(toml_scalar(item) for item in value) + "]"
            else:
                rendered = toml_scalar(value)
            lines.append(f"{key} = {rendered}")
        lines.append("")
    return "\n".join(lines)


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def seed_count(seed_spec):
    total = 0
    for part in str(seed_spec).split(","):
        part = part.strip()
        match = re.fullmatch(r"(\d+)-(\d+)", part)
        if match:
            start, end = int(match.group(1)), int(match.group(2))
            total += end - start + 1
        elif part:
            total += 1
    return total


def steps_from_nfe(nfe_budget, solver):
    if nfe_budget < 1:
        raise ValueError("nfe_budget must be at least 1")
    if solver == "euler":
        return nfe_budget
    if solver == "heun":
        return max(1, (nfe_budget + 1) // 2)
    raise ValueError(f"unsupported solver for NFE accounting: {solver}")


def nfe_from_steps(num_steps, solver):
    if solver == "euler":
        return num_steps
    if solver == "heun":
        return 2 * num_steps - 1
    raise ValueError(f"unsupported solver for NFE accounting: {solver}")


def free_tcp_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def subprocess_env(command):
    env = os.environ.copy()
    if command and Path(command[0]).name != "torchrun":
        env["MASTER_ADDR"] = env.get("MASTER_ADDR", "localhost")
        env["MASTER_PORT"] = str(free_tcp_port())
        env["RANK"] = env.get("RANK", "0")
        env["LOCAL_RANK"] = env.get("LOCAL_RANK", "0")
        env["WORLD_SIZE"] = env.get("WORLD_SIZE", "1")
    return env


def run_command(command, cwd, log_path, stream_output=True):
    started = time.time()
    stdout_tail = ""
    with Path(log_path).open("w", encoding="utf-8") as log:
        log.write("$ " + " ".join(command) + "\n\n")
        log.flush()
        proc = subprocess.Popen(
            command,
            cwd=str(cwd),
            env=subprocess_env(command),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
        )
        assert proc.stdout is not None
        while True:
            chunk = proc.stdout.read(1)
            if chunk == "" and proc.poll() is not None:
                break
            if not chunk:
                continue
            log.write(chunk)
            log.flush()
            stdout_tail = (stdout_tail + chunk)[-4000:]
            if stream_output:
                sys.stdout.write(chunk)
                sys.stdout.flush()
        returncode = proc.wait()
    return {
        "command": command,
        "returncode": returncode,
        "elapsed_seconds": round(time.time() - started, 3),
        "log": str(log_path),
        "stdout_tail": stdout_tail,
    }


def build_agent_report(fixed, experiment, result):
    proposal = experiment.get("proposal", {})
    sampler = experiment.get("sampler", {})
    evaluation = fixed.get("evaluation", {})
    fid_eval = result.get("fid_evaluation") or {}
    return {
        "proposal": {
            "name": proposal.get("name", ""),
            "hypothesis": proposal.get("hypothesis", ""),
            "timestep_or_noise_schedule": proposal.get("timestep_or_noise_schedule", ""),
            "update_rule": proposal.get("update_rule", ""),
            "solver_type": proposal.get("solver_type", ""),
            "stochastic_updates": proposal.get("stochastic_updates", ""),
            "budget_allocation": proposal.get("budget_allocation", ""),
            "score_manipulation": proposal.get("score_manipulation", "none"),
        },
        "sampler": dict(sampler),
        "result": {
            "status": result.get("status"),
            "fid": result.get("fid"),
            "fid_enabled": bool(evaluation.get("compute_fid", False)),
            "nfe_budget": result.get("nfe_budget"),
            "actual_nfe": result.get("actual_nfe"),
            "num_steps": result.get("num_steps"),
            "seed_count": result.get("seed_count"),
            "solver": result.get("solver"),
            "generation_seconds": (result.get("generation") or {}).get("elapsed_seconds"),
            "fid_seconds": fid_eval.get("elapsed_seconds"),
            "completed_at": result.get("completed_at"),
        },
    }


def render_agent_report(report):
    proposal = report["proposal"]
    sampler = report["sampler"]
    result = report["result"]
    lines = [
        f"# {proposal.get('name') or 'experiment'}",
        "",
        "## Proposal",
        f"- Hypothesis: {proposal.get('hypothesis', '')}",
        f"- Schedule: {proposal.get('timestep_or_noise_schedule', '')}",
        f"- Update rule: {proposal.get('update_rule', '')}",
        f"- Solver: {proposal.get('solver_type', '')}",
        f"- Stochasticity: {proposal.get('stochastic_updates', '')}",
        f"- Budget allocation: {proposal.get('budget_allocation', '')}",
        f"- Score manipulation: {proposal.get('score_manipulation', 'none')}",
        "",
        "## Sampler Config",
    ]
    for key in sorted(sampler):
        lines.append(f"- {key}: {sampler[key]}")
    lines.extend(
        [
            "",
            "## Result",
            f"- Status: {result.get('status')}",
            f"- FID: {result.get('fid')}",
            f"- FID enabled: {result.get('fid_enabled')}",
            f"- NFE budget: {result.get('nfe_budget')}",
            f"- Actual NFE: {result.get('actual_nfe')}",
            f"- Sampling steps: {result.get('num_steps')}",
            f"- Seed count: {result.get('seed_count')}",
            f"- Generation seconds: {result.get('generation_seconds')}",
            f"- FID seconds: {result.get('fid_seconds')}",
        ]
    )
    return "\n".join(lines) + "\n"


def write_agent_report(fixed, experiment, result, experiment_dir):
    report = build_agent_report(fixed, experiment, result)
    report_path = experiment_dir / "agent_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    (experiment_dir / "agent_report.toml").write_text(dump_simple_toml(report), encoding="utf-8")
    (experiment_dir / "agent_report.md").write_text(render_agent_report(report), encoding="utf-8")
    return report_path


def build_generate_command(fixed, experiment, experiment_dir, num_steps):
    model = fixed.get("model", {})
    run = fixed.get("run", {})
    sampler = experiment.get("sampler", {})
    proposal = experiment.get("proposal", {})

    score_manipulation = str(proposal.get("score_manipulation", "none"))
    if score_manipulation not in SUPPORTED_SCORE_MANIPULATIONS:
        raise ValueError(
            f"score_manipulation={score_manipulation!r} is documented in the config, "
            "but this launcher only supports 'none' until generate.py is extended."
        )

    outdir = experiment_dir / str(run.get("outdir_name", "images"))
    command = [
        sys.executable,
        str(ROOT / "generate.py"),
        f"--outdir={outdir}",
        f"--seeds={run['seeds']}",
        f"--batch={run.get('batch', 64)}",
        f"--steps={num_steps}",
        f"--network={model['network']}",
    ]
    if run.get("subdirs", False):
        command.append("--subdirs")

    for key, cli_key in SAMPLER_CLI_KEYS.items():
        if key in sampler:
            command.append(f"{cli_key}={sampler[key]}")

    nproc = int(run.get("nproc_per_node", 1))
    if nproc > 1:
        command = [
            "torchrun",
            "--standalone",
            f"--nproc_per_node={nproc}",
        ] + command[1:]
    return command, outdir


def maybe_run_fid(fixed, images_dir, experiment_dir, stream_output=True):
    evaluation = fixed.get("evaluation", {})
    if not evaluation.get("compute_fid", False):
        return None

    command = [
        sys.executable,
        str(ROOT / "fid.py"),
        "calc",
        f"--images={images_dir}",
        f"--ref={evaluation['reference_stats']}",
        f"--num={evaluation.get('num_images', seed_count(fixed['run']['seeds']))}",
        f"--batch={evaluation.get('batch', fixed['run'].get('batch', 64))}",
    ]
    result = run_command(command, ROOT, experiment_dir / "fid.log", stream_output=stream_output)
    matches = re.findall(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*$", result["stdout_tail"], flags=re.MULTILINE)
    result["fid"] = float(matches[-1]) if matches else None
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", required=True, type=Path, help="Experiment folder containing config.toml")
    parser.add_argument("--fixed", default=DEFAULT_FIXED_CONFIG, type=Path, help="Immutable run config")
    parser.add_argument("--config", default="config.toml", help="Experiment config filename")
    parser.add_argument("--quiet", action="store_true", help="Do not stream generate.py/fid.py output to the terminal")
    args = parser.parse_args()

    experiment_dir = args.experiment.resolve()
    config_path = experiment_dir / args.config
    fixed_path = args.fixed.resolve()
    if not config_path.exists():
        raise SystemExit(f"Missing experiment config: {config_path}")
    if not fixed_path.exists():
        raise SystemExit(f"Missing fixed config: {fixed_path}")

    fixed = load_simple_toml(fixed_path)
    experiment = load_simple_toml(config_path)
    sampler = experiment.get("sampler", {})
    solver = str(sampler.get("solver", "heun"))
    nfe_budget = int(fixed["run"]["nfe_budget"])
    num_steps = steps_from_nfe(nfe_budget, solver)
    actual_nfe = nfe_from_steps(num_steps, solver)

    command, images_dir = build_generate_command(fixed, experiment, experiment_dir, num_steps)
    (experiment_dir / "command.txt").write_text(" ".join(command) + "\n", encoding="utf-8")

    result = {
        "status": "running",
        "experiment_dir": str(experiment_dir),
        "fixed_config": str(fixed_path),
        "experiment_config": str(config_path),
        "fixed_config_sha256": sha256_file(fixed_path),
        "experiment_config_sha256": sha256_file(config_path),
        "seed_count": seed_count(fixed["run"]["seeds"]),
        "nfe_budget": nfe_budget,
        "num_steps": num_steps,
        "actual_nfe": actual_nfe,
        "solver": solver,
        "images_dir": str(images_dir),
    }
    (experiment_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    generate_result = run_command(command, ROOT, experiment_dir / "generate.log", stream_output=not args.quiet)
    result["generation"] = generate_result
    result["status"] = "generated" if generate_result["returncode"] == 0 else "generation_failed"

    if generate_result["returncode"] == 0:
        fid_result = maybe_run_fid(fixed, images_dir, experiment_dir, stream_output=not args.quiet)
        if fid_result is not None:
            result["fid_evaluation"] = fid_result
            result["fid"] = fid_result.get("fid")
            result["status"] = "completed" if fid_result["returncode"] == 0 else "fid_failed"
        else:
            result["status"] = "completed"

    result["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    (experiment_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (experiment_dir / "result.toml").write_text(dump_simple_toml({"result": result}), encoding="utf-8")
    result["agent_report"] = str(write_agent_report(fixed, experiment, result, experiment_dir))
    (experiment_dir / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    if result["status"] != "completed":
        raise SystemExit(f"Experiment ended with status={result['status']}. See {experiment_dir}")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
