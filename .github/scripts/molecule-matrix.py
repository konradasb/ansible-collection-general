# Copyright 2026 konradasb
# SPDX-License-Identifier: MIT

"""Print the Molecule jobs to run, as a GitHub Actions matrix.

Reads the paths that changed, one per line, on standard input, or runs every
role's scenarios with --all. A role is tested when a file under it changed,
and every role when a file they all share did. Each job is one platform of
one scenario of one role, roles/ROLE/molecule/SCENARIO:

    {"role": "dicerd", "scenario": "default", "platform": "debian-12", "runner": "ubuntu-latest"}

A scenario whose driver is docker runs on ubuntu-latest. One whose driver is
default runs on the machine itself, so each of its platforms is named after
the runner it runs on, such as macos-latest.

GitHub runs at most 256 jobs from one matrix. Past that, each scenario's
platforms run together in one job, whose platform is empty.

Writes matrix=JSON to $GITHUB_OUTPUT when it is set, and to standard output
otherwise.
"""

import argparse
import json
import os
import pathlib
import sys

import yaml

MATRIX_LIMIT = 256

# Files every role depends on: a change to one tests them all.
SHARED_PATHS = (
    "galaxy.yml",
    "meta/",
    ".github/workflows/test.yaml",
    ".github/scripts/molecule-matrix.py",
)

DOCKER_RUNNER = "ubuntu-latest"


def changed_roles(changed_paths, all_roles):
    """Return the roles the changed paths affect."""
    roles = set()
    for path in changed_paths:
        if path.startswith(SHARED_PATHS):
            return set(all_roles)

        parts = pathlib.PurePosixPath(path).parts
        if len(parts) > 1 and parts[0] == "roles" and parts[1] in all_roles:
            roles.add(parts[1])

    return roles


def scenario_jobs(role, scenario_directory):
    """Return a job for each platform of the scenario."""
    with open(scenario_directory / "molecule.yml", encoding="utf-8") as file:
        molecule = yaml.safe_load(file)

    driver = molecule.get("driver", {}).get("name", "default")
    jobs = []
    for platform in molecule.get("platforms", []):
        if driver == "docker":
            runner = DOCKER_RUNNER
        elif driver == "default":
            runner = platform["name"]
        else:
            sys.exit(f"{scenario_directory}: no runner is known for the {driver} driver")

        jobs.append(
            {
                "role": role,
                "scenario": scenario_directory.name,
                "platform": platform["name"],
                "runner": runner,
            }
        )

    return jobs


def group_by_scenario(jobs):
    """Return a job for each scenario and runner, running all its platforms.

    A platform that is its runner stays one job, as it runs only there.
    """
    grouped = {}
    for job in jobs:
        key = (job["role"], job["scenario"], job["runner"])
        platform = job["platform"] if job["platform"] == job["runner"] else ""
        grouped[key] = {**job, "platform": platform}

    return list(grouped.values())


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--all", action="store_true", help="test every role")
    args = parser.parse_args()

    roles_directory = pathlib.Path("roles")
    all_roles = sorted(path.name for path in roles_directory.iterdir() if path.is_dir())

    if args.all:
        roles = set(all_roles)
    else:
        changed_paths = [line.strip() for line in sys.stdin if line.strip()]
        roles = changed_roles(changed_paths, all_roles)

    jobs = []
    for role in sorted(roles):
        for scenario_directory in sorted((roles_directory / role / "molecule").glob("*/")):
            if (scenario_directory / "molecule.yml").is_file():
                jobs.extend(scenario_jobs(role, scenario_directory))

    if len(jobs) > MATRIX_LIMIT:
        jobs = group_by_scenario(jobs)
    if len(jobs) > MATRIX_LIMIT:
        sys.exit(f"{len(jobs)} scenarios are more than a matrix can run")

    matrix = json.dumps({"include": jobs})
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as file:
            file.write(f"matrix={matrix}\n")
            file.write(f"empty={'true' if not jobs else 'false'}\n")
    else:
        print(matrix)


if __name__ == "__main__":
    main()
