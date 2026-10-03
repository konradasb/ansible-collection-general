# konradasb.general.dicer

Installs the `dicer` command line from
[Dicer's releases](https://github.com/konradasb/dicer/releases), on a
machine that talks to a daemon elsewhere, and writes users' remotes: the
daemons `dicer` talks to.

A host that runs the daemon gets `dicer` with it, from the
[`konradasb.general.dicerd`](../dicerd/README.md) role. This role installs it
anyway, into its own directory, if it is given that host.

## Requirements

- Linux or macOS, on x86_64 or arm64.
- `tar`, and access to github.com.
- `become: true` to install into a directory the connecting user cannot
  write, such as the default, `/usr/local/bin`, or to write other users'
  remotes.

## Role variables

`ansible-doc -t role konradasb.general.dicer` shows them all.

| Variable | Default | |
|---|---|---|
| `dicer_version` | `latest` | A release, such as `0.3.0`, or `latest`. |
| `dicer_install_directory` | `/usr/local/bin` | Where `dicer` is installed. |
| `dicer_releases_url` | `https://github.com/konradasb/dicer/releases` | |
| `dicer_remotes_users` | `[]` | Users whose `remotes.yaml` is written. |
| `dicer_remotes` | `{}` | The remotes, by name. |
| `dicer_remote_current` | `""` | The remote commands go to. Empty is the local daemon. |

Each archive is checked against the release's `checksums.txt` before it is
installed. `latest` follows each new release, which a pinned version does
not.

### Remotes

For each user in `dicer_remotes_users`, `dicer_remotes` and
`dicer_remote_current` are written to the user's `remotes.yaml`:
`~/.config/dicer` on Linux, and `~/Library/Application Support/dicer` on
macOS, as `dicer` reads it. The file is replaced, so a remote added with
`dicer remote add` lasts until the role runs again.

A remote's TLS files are named, not written: put them in place first. See
[Remote access](https://dicer.sh/docs/guides/remote-access/).

## Example playbook

```yaml
- name: Install dicer
  hosts: workstations
  become: true
  roles:
    - role: konradasb.general.dicer
      vars:
        dicer_version: 0.3.0
        dicer_remotes_users:
          - alice
        dicer_remotes:
          compute1:
            address: compute1.example.com:7443
            tls:
              ca_file: /home/alice/.dicer/ca.pem
              cert_file: /home/alice/.dicer/client.pem
              key_file: /home/alice/.dicer/client-key.pem
        dicer_remote_current: compute1
```

## License

MIT
