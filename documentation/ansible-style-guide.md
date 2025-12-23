# Ansible Style Guide — Project Conventions

This document is an adapted, concise style guide inspired by the Met Norway Ansible style guide (https://github.com/metno/ansible-style-guide). It captures practical conventions for writing readable, maintainable, and testable Ansible content for this repository.

This is a guidance document — use judgment where your scenario requires deviation, and document any exceptions.

## Goals
- Keep playbooks and roles consistent and easy to review.
- Prefer clarity and idempotence over cleverness.
- Make testing and linting reliable and automated.

## Repository conventions
- Layout: keep a predictable structure at project root:

```
playbooks/
roles/
inventories/
group_vars/
host_vars/
documentation/
ansible.cfg
README.md
```

- Keep playbooks small and orchestration-focused; implement logic in roles.
- Use `requirements.yml` for pinned role dependencies.

## Naming conventions
- Role names: `snake_case` (e.g., `roles/common`, `roles/patching`).
- Files in roles: use the standard layout (`tasks/main.yml`, `handlers/main.yml`, `defaults/main.yml`, `vars/main.yml`, `meta/main.yml`, `templates/`, `files/`).
- Variables: `snake_case`, descriptive (e.g., `nginx_listen_port`, `patching_enabled`).
- Boolean variables: prefer explicit `true`/`false` values; name them to read naturally (`enable_foo: true`).

## Role design
- Single responsibility: each role should do one clear thing.
- Idempotence: prefer modules that declare desired state over `shell`/`command` where possible.
- Defaults and overrides:
  - Put sensible defaults in `defaults/main.yml`.
  - Put required or higher-precedence variables in `vars/main.yml` only when truly necessary.
- No hardcoded hosts or environment-specific values inside roles; consume via variables.
- Document input variables and their defaults in `roles/<role>/README.md`.

## Playbook structure
- Top-level playbooks should be short and readable; call roles with `roles:` and pass role parameters explicitly when needed.
- Use `become: true` only for tasks requiring privilege; avoid global `become: true` at the play level unless justified.
- Use `tags:` on tasks/roles where incremental execution or targeted runs are common.

## Tasks and handlers
- Keep tasks small and explicit. Break complex sequences into multiple tasks.
- Use `name:` on every task for clear output and logs.
- Handlers should be idempotent and named clearly (e.g., `restart nginx`), and invoked only when necessary.

## Conditionals and loops
- Use module parameters (e.g., `state: present`) rather than conditionals when possible.
- Avoid complex inline Jinja2 logic in `when:` or `with_items`; prefer preprocessing variables in `set_fact` or role defaults.
- Use `loop:` with `loop_control` for readable index or label handling.

## Variables management
- Keep secrets out of plain text in the repo. Use `ansible-vault` or an external secrets manager.
- Prefer explicit variable names and document them.
- Avoid deep implicit merges of dictionaries; prefer explicit merges with `combine()` if needed.

## Templates and files
- Templates: keep them small and avoid business logic in Jinja templates. Templates are for presentation of configuration, not for complex decisioning.
- Avoid `lookup('file', ...)` to fetch large content; prefer `template:` or role `files/` when appropriate.

## YAML style
- Use 2-space indentation.
- Quote strings that begin with special characters or look like numbers/dates to avoid YAML parsing surprises.
- Prefer explicit boolean values (`true`/`false`, not `yes`/`no`).

## Linting and checks
- Run `ansible-lint` and `yamllint` in CI for all PRs.
- Use a consistent `ansible-lint` config (`.ansible-lint` or `.ansible-lint.yml`) at repo root and document exceptions.

## Testing
- Use `molecule` for role testing. Provide a basic `molecule/default` scenario for core roles.
- Include simple smoke tests (Testinfra or local verification tasks) to validate important functionality.

## Error handling and idempotence
- Prefer module features to detect state instead of running commands and guessing changed/failed state.
- Use `failed_when` and `changed_when` only when module defaults are insufficient.
- Use `block`/`rescue`/`always` for operations that require cleanup on failure.

## Security
- Avoid logging secrets. Be cautious with `debug:` and never print sensitive variables.
- Use least-privilege principles for `become_user` and only escalate privileges for targeted tasks.

## Documentation
- Each role MUST contain a `README.md` describing:
  - Purpose
  - Inputs (variables and defaults)
  - Outputs (files created, services started)
  - Example usage snippet
- Keep `documentation/` up-to-date with conventions and examples.

## Git workflow and commit messages
- Commit messages should be concise and reference the role or playbook changed: `roles/common: add idempotent package task`.
- For breaking or structural changes, include a short rationale in the PR description.

## Examples (brief)
- Role usage in a playbook:

```yaml
- hosts: webservers
  become: true
  roles:
    - role: common
      nginx_listen_port: 8080
```

- Small task example:

```yaml
- name: Ensure NGINX package is installed
  ansible.builtin.package:
    name: nginx
    state: present
```

## Tooling recommendations
- Linting: `ansible-lint`, `yamllint`.
- Testing: `molecule` with Docker or other lightweight drivers.
- Secrets: `ansible-vault` or external secret backends.
- CI: run `ansible-lint`, `yamllint`, and `molecule test` on PRs.

## References
- Met Norway Ansible style guide (inspiration): https://github.com/metno/ansible-style-guide
- Ansible documentation: https://docs.ansible.com/

---

If you want, I can:
- Add a `.ansible-lint.yml` template and `molecule` scaffolding for `roles/common`.
- Create a `roles/example` scaffold with README and a basic `molecule` scenario.

Which of those would you like next?