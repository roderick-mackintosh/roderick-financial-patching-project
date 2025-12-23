#!/usr/bin/env python3
"""
Aggregate per-host patch results into summary JSON/CSV and zip artifact.

Reads host-level JSON files from artifacts/results/, produces:
- artifacts/summary.json
- artifacts/summary.csv
- artifacts/patch_results_<timestamp>.zip (contains per-host results + summaries)
"""

import argparse
import csv
import json
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


def load_host_results(results_dir: Path) -> List[Dict[str, Any]]:
    results = []
    for path in sorted(results_dir.glob("*.json")):
        try:
            with path.open() as fh:
                data = json.load(fh)
                data["_source_file"] = path
                results.append(data)
        except Exception as exc:  # pylint: disable=broad-except
            print(f"Warning: failed to read {path}: {exc}", file=sys.stderr)
    return results


def compute_compliance(host_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(host_results)
    patched_hosts = 0
    host_summaries = []

    for host in host_results:
        updates_applied = host.get("updates_applied") or []
        reboot_performed = bool(host.get("reboot_performed"))
        health = host.get("health_check_status", "unknown")
        patched = bool(updates_applied) or reboot_performed or health == "passed"

        patched_hosts += 1 if patched else 0
        host_summaries.append(
            {
                "inventory_hostname": host.get("inventory_hostname", "unknown"),
                "os_family": host.get("os_family", "unknown"),
                "os_version": host.get("os_version", "unknown"),
                "health_check_status": health,
                "updates_applied_count": len(updates_applied),
                "reboot_performed": reboot_performed,
                "packages_before_count": len(host.get("packages_before") or []),
                "packages_after_count": len(host.get("packages_after") or []),
            }
        )

    compliance_percent = (patched_hosts / total * 100) if total else 0.0

    return {
        "total_hosts": total,
        "patched_hosts": patched_hosts,
        "unpatched_hosts": max(total - patched_hosts, 0),
        "compliance_percent": round(compliance_percent, 2),
        "hosts": host_summaries,
    }


def write_summary_json(summary: Dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w") as fh:
        json.dump(summary, fh, indent=2)


def write_summary_csv(hosts: List[Dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "inventory_hostname",
        "os_family",
        "os_version",
        "health_check_status",
        "updates_applied_count",
        "reboot_performed",
        "packages_before_count",
        "packages_after_count",
    ]
    with output_path.open("w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for host in hosts:
            writer.writerow(host)


def build_zip(artifact_dir: Path, results_dir: Path, summary_json: Path, summary_csv: Path) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    zip_path = artifact_dir / f"patch_results_{timestamp}.zip"
    artifact_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
        for path in sorted(results_dir.glob("*.json")):
            zipf.write(path, path.relative_to(artifact_dir))
        zipf.write(summary_json, summary_json.relative_to(artifact_dir))
        zipf.write(summary_csv, summary_csv.relative_to(artifact_dir))
    return zip_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate patch results.")
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path("artifacts/results"),
        help="Directory containing per-host JSON results.",
    )
    parser.add_argument(
        "--artifact-dir",
        type=Path,
        default=Path("artifacts"),
        help="Directory to write summaries and zip artifact.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    results_dir = args.results_dir
    artifact_dir = args.artifact_dir

    if not results_dir.exists():
        print(f"No results directory found at {results_dir}", file=sys.stderr)
        return 1

    host_results = load_host_results(results_dir)
    summary_data = compute_compliance(host_results)
    summary_data["generated_at"] = datetime.now(timezone.utc).isoformat()

    summary_json = artifact_dir / "summary.json"
    summary_csv = artifact_dir / "summary.csv"

    write_summary_json(summary_data, summary_json)
    write_summary_csv(summary_data["hosts"], summary_csv)

    zip_path = build_zip(artifact_dir, results_dir, summary_json, summary_csv)
    print(f"Wrote summary JSON: {summary_json}")
    print(f"Wrote summary CSV: {summary_csv}")
    print(f"Wrote zip artifact: {zip_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
