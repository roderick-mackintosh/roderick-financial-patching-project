# Ansible Best Practices — Summary and Guidelines

This document summarizes practical Ansible best practices inspired by the Red Hat COP "Automation Good Practices" (https://redhat-cop.github.io/automation-good-practices/). It focuses on repository layout, playbook and role design, variables and secrets handling, testing, CI, security, and maintainability.

> Note: This is a concise, opinionated summary for project use — see the linked source for more detail and prescriptive patterns.

## Goals
- Produce reliable, idempotent automation
- Make playbooks and roles easy to read, reuse, and test
- Keep secrets and sensitive data secure
- Automate quality checks with CI

## Repository layout
- Use a clear layout at repository root: `inventories/`, `roles/`, `playbooks/`, `group_vars/`, `host_vars/`, and `documentation/`.
- Keep short, focused playbooks in `playbooks/` and reusable logic inside `roles/`.
- Use `ansible.cfg` at repository root to configure defaults (inventory path, retry files, callback plugins, roles_path).

Example structure:

```
playbooks/
roles/
inventories/
  production/
  staging/
group_vars/
host_vars/
ansible.cfg
README.md
documentation/
```

## Roles and playbooks
- Design roles to be idempotent and parameterized via `defaults/main.yml` and `vars/main.yml` (favor `defaults` for sensible defaults).
- Each role should have a single responsibility (installing a package, configuring a service, etc.).
- Avoid monolithic playbooks—compose them from smaller playbooks and include or import roles where appropriate.
- Use role meta for dependencies rather than chaining multiple roles within a single role.

## Variables and secrets
- Prefer explicit variable names and avoid implicit variable merging that hides intent.
- Keep secrets out of the repo: use Ansible Vault, a secrets manager (HashiCorp Vault, AWS Secrets Manager), or external credential stores.
- Use group_vars or host_vars only for non-sensitive configuration; rely on vault-encrypted files for secrets.
- Document required variables and provide example variable files (e.g., `vars.example.yml`) with non-sensitive placeholders.

## Idempotence and checks
- Ensure tasks are idempotent: use module arguments that check state rather than running shell commands when possible.
- Avoid `shell`/`command` unless necessary; prefer native Ansible modules.
- Use `check_mode` support for roles and test with `ansible-playbook --check` where feasible.
- Add `changed_when` and `failed_when` only when you need custom evaluation; keep defaults otherwise.

## Error handling and retries
- Use `retries/delay` with `until` when waiting on services or resources that may take time.
- Fail fast for fatal conditions but try to make non-fatal checks informational.
- Use `block`/`rescue`/`always` for sequences that need cleanup or rolling back partial changes.

## Testing and CI
- Test roles and playbooks locally via `molecule` with a lightweight driver (Docker/GCE) for unit and integration tests.
- Add linting (e.g., `ansible-lint`) and static checks in CI pipelines to catch style and correctness issues early.
- Automate running `molecule test`, `ansible-lint`, and `yamllint` in CI on pull requests.
- Include simple smoke tests after deployment (verify service ports, endpoints, or process state).

## Documentation and examples
- Keep a clear `README.md` at repo root with quickstart steps and supported inventory layout.
- Document role inputs/outputs as `README.md` inside each `roles/<role>/` directory (including default variables and example usage).
- Provide example playbooks for common scenarios (deploy, upgrade, rollback).

## Security and least privilege
- Execute tasks with the least privilege required. Avoid running everything as `become: true` unless necessary.
- Use `become_user` and target specific operations to minimize blast radius.
- Limit sensitive logging — be cautious with debug statements that may print secrets.

## Performance and scaling
- Use `strategy: free` and smart `serial` settings for rolling updates when managing many hosts.
- Control fork/parallelism in `ansible.cfg` (`forks`) appropriate to controller and network capacity.
- Avoid heavy per-host loops; prefer bulk operations when possible.

## Reuse and community roles
- Prefer in-house roles for organization-specific policies, but evaluate community roles carefully.
- When using community roles, pin versions (via `requirements.yml`) and vet them for license, quality, and security.

## Common tooling
- Linting: `ansible-lint`, `yamllint`.
- Testing: `molecule` (with `testinfra` or `ansible` scenarios).
- Secrets: `ansible-vault` or external secrets manager integrations.
- Dependency management: `ansible-galaxy` `requirements.yml` for role dependencies.

## Practical conventions (quick checklist)
- Repository contains `ansible.cfg` and a documented inventory layout.
- Roles are small, single-purpose, and idempotent.
- Defaults defined in `defaults/main.yml`, sensitive data encrypted with Vault.
- CI runs `ansible-lint`, `yamllint`, and `molecule` tests on PRs.
- Documentation for each role exists in `roles/<role>/README.md`.

## References
- Red Hat COP — Automation Good Practices: https://redhat-cop.github.io/automation-good-practices/
- Ansible docs: https://docs.ansible.com/

---

If you want, I can expand this into a longer checklist, add a `requirements.yml` example, or scaffold a starter repo layout with `ansible.cfg` and a sample role. 
