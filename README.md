# konradasb.general

[![test](https://github.com/konradasb/ansible-collection-general/actions/workflows/test.yaml/badge.svg)](https://github.com/konradasb/ansible-collection-general/actions/workflows/test.yaml)
[![Ansible Galaxy](https://img.shields.io/badge/galaxy-konradasb.general-blue)](https://galaxy.ansible.com/ui/repo/published/konradasb/general/)
[![License: MIT](https://img.shields.io/github/license/konradasb/ansible-collection-general)](LICENSE)

Roles that install, configure and run the software konradasb ships. Each
role is named after the program it installs, and its variables after the
role.

## Contents

### Dicer

[Dicer](https://dicer.sh) runs virtual machines from container images, on
one host: the daemon on the hosts that run them, and the command line on the
machines that manage them.

| Role | |
|---|---|
| [`konradasb.general.dicerd`](roles/dicerd/README.md) | Installs Dicer from its package repository, configures `dicerd` and runs it. The `dicer` command line comes with it. |
| [`konradasb.general.dicer`](roles/dicer/README.md) | Installs the `dicer` command line from Dicer's releases, on Linux or macOS, and writes users' remotes. |

## Requirements

- ansible-core 2.18 or later.
- `community.general`, which `ansible-galaxy` installs with the collection.

Each role's requirements, for the hosts it sets up, are in its README.

## Install

```console
$ ansible-galaxy collection install konradasb.general
```

or in a `requirements.yml`:

```yaml
collections:
  - name: konradasb.general
```

## Use

```yaml
- name: Set up the Dicer hosts
  hosts: dicer_hosts
  become: true
  roles:
    - role: konradasb.general.dicerd
      vars:
        dicerd_config:
          metrics:
            enable: true

- name: Install dicer on the workstations
  hosts: workstations
  become: true
  roles:
    - role: konradasb.general.dicer
      vars:
        dicer_remotes_users:
          - alice
        dicer_remotes:
          compute1:
            address: compute1.example.com:7443
        dicer_remote_current: compute1
```

Networks and kernels are then made with the `dicer` command line: see
Dicer's [Quickstart](https://dicer.sh/docs/getting-started/quickstart/).

## Development

Each role has its own [Molecule](https://ansible.readthedocs.io/projects/molecule/)
scenarios, in `roles/ROLE/molecule/`, run from the role's directory:

```console
$ python3 -m pip install ansible-core ansible-lint molecule 'molecule-plugins[docker]'
$ ansible-galaxy collection install community.general community.docker ansible.posix
$ ansible-lint
$ cd roles/dicerd
$ molecule test                               # every platform
$ molecule test --platform-name debian-12     # one
```

A scenario with the docker driver runs each platform in a container: those
of `dicerd` run systemd, but Docker gives them no KVM, so they check the
role, not Dicer's instances. One with the default driver runs on the machine
itself, and only in CI, on the runner each platform is named after, such as
`dicer`'s `macos` scenario.

CI tests the roles a change touches, and all of them when it touches what
they share, such as `galaxy.yml`, or on its weekly run:
[`.github/scripts/molecule-matrix.py`](.github/scripts/molecule-matrix.py)
makes a job of each platform of each scenario. A new role's scenarios are
picked up from its `molecule/` directory.

Pull requests are squash-merged, and their titles follow
[Conventional Commits](https://www.conventionalcommits.org/), which a check
enforces: `feat:` for a new feature, `fix:` for a fix, and `!`, as in
`feat!:`, for a change that breaks existing playbooks.

## Releasing

[release-please](https://github.com/googleapis/release-please) keeps a
pull request open that bumps `galaxy.yml`'s version and writes
`CHANGELOG.md` from the commits since the last release. Merging it tags the
release, publishes the collection to Ansible Galaxy, and attaches it to the
GitHub release. Before 1.0, a breaking change bumps the minor version.

The workflow needs a Galaxy API key, from
[galaxy.ansible.com/ui/token](https://galaxy.ansible.com/ui/token/), as the
repository secret `GALAXY_API_KEY`, and Actions allowed to create pull
requests, under *Settings → Actions → General*.

## License

MIT. See [LICENSE](LICENSE).
