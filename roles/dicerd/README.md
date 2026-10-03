# konradasb.general.dicerd

Installs [Dicer](https://dicer.sh) from its package repository, writes
`dicerd`'s configuration, and runs `dicerd` as a systemd service.

The `dicer` package has the daemon, `dicerd`, and the `dicer` command line.
It turns IPv4 forwarding on, creates the `dicer` group, and installs the
firewalld zone `dicerd` binds its bridges to. For the command line alone, on
a machine that manages a daemon elsewhere, see the
[`konradasb.general.dicer`](../dicer/README.md) role.

## Requirements

- A host on x86_64 or aarch64 running one of:
  - Debian 12 or 13
  - Ubuntu 22.04 or 24.04
  - Fedora
  - RHEL, Rocky Linux or AlmaLinux 9 or 10, with EPEL, which the role turns on
  - openSUSE Tumbleweed
- KVM: `/dev/kvm` must exist.
- `become: true`.
- For `--check` on Debian and Ubuntu, `python3-apt` and `python3-debian`,
  which Ansible's apt and deb822_repository modules need, and install
  themselves only in a normal run.

## Role variables

`ansible-doc -t role konradasb.general.dicerd` shows them all, from
[`meta/argument_specs.yml`](meta/argument_specs.yml), which the role checks
them against before it runs.

| Variable | Default | |
|---|---|---|
| `dicerd_version` | `""` | The package's version, such as `0.3.0`. Empty installs the newest. |
| `dicerd_package_state` | `present` | `latest` upgrades on every run. |
| `dicerd_repository_manage` | `true` | Add the repository at `pkg.dicer.sh`. |
| `dicerd_repository_url` | `https://pkg.dicer.sh` | |
| `dicerd_repository_key_url` | `{{ dicerd_repository_url }}/gpg.key` | |
| `dicerd_epel_manage` | `true` | Turn EPEL on, on RHEL and its rebuilds. |
| `dicerd_kvm_check` | `true` | Fail unless the host has `/dev/kvm`. |
| `dicerd_config` | `{}` | `dicerd`'s configuration. |
| `dicerd_tls_certificate` | `""` | The TCP API's certificate, as PEM. |
| `dicerd_tls_private_key` | `""` | Its private key, as PEM. |
| `dicerd_tls_client_ca` | `""` | The CA client certificates must be signed by, as PEM. |
| `dicerd_group_members` | `[]` | Users added to the `dicer` group. |
| `dicerd_service_enabled` | `true` | Start `dicerd` at boot. |
| `dicerd_service_state` | `started` | `started` or `stopped`. |

### `dicerd_config`

`dicerd_config` holds the keys of the
[daemon's configuration](https://dicer.sh/docs/reference/configuration/) as
they are in `/etc/dicerd/config.yaml`. The role merges it over its base,
which gives the daemon's socket to the `dicer` group, writes the file, and
checks it with `dicerd validate` first: a configuration the daemon would
refuse never replaces a working one. A change restarts `dicerd`, which leaves
running instances running.

A `data_dir` or `run_dir` moved from the defaults is created, and added to
the service's `ReadWritePaths` in a drop-in.

Registry passwords are best kept out of the file: give `password_file`, or a
`credential_helper`, rather than `password`.

### TLS

The TLS files given are written under `/etc/dicerd/tls`, the private key
readable only by root, and set in `api.tcp.tls`. `api.tcp.listen`, in
`dicerd_config`, turns the TCP API on. See
[Remote access](https://dicer.sh/docs/guides/remote-access/).

### The `dicer` group

A member of the `dicer` group can do anything with the daemon, which is as
much as root on the host. A user in `dicerd_group_members` that does not
exist is created. The role adds users and never removes them.

## Dependencies

`community.general`, for the zypper modules on openSUSE.

## Example playbook

```yaml
- name: Set up Dicer
  hosts: dicerd_hosts
  become: true
  roles:
    - role: konradasb.general.dicerd
      vars:
        dicerd_version: 0.3.0
        dicerd_config:
          api:
            tcp:
              listen: 0.0.0.0:7443
          metrics:
            enable: true
            listen: 0.0.0.0:9101
          images:
            gc_max_size: 50GiB
        dicerd_tls_certificate: "{{ lookup('ansible.builtin.file', 'tls/' ~ inventory_hostname ~ '.pem') }}"
        dicerd_tls_private_key: "{{ lookup('ansible.builtin.file', 'tls/' ~ inventory_hostname ~ '-key.pem') }}"
        dicerd_tls_client_ca: "{{ lookup('ansible.builtin.file', 'tls/ca.pem') }}"
        dicerd_group_members:
          - alice
```

Keep the private key in Ansible Vault.

## License

MIT
