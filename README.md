# roderick-financial-patching-project

This repository holds Ansible automation for the financial patching project.

Conventions:
- `inventories/` contains environment inventories (`production`, `staging`).
- `roles/` contains reusable Ansible roles, e.g. `roles/common`.
- `group_vars/` and `host_vars/` contain configuration for groups/hosts.
- `playbooks/` contains orchestration playbooks.

Quick start:

1. Install Ansible and recommended tooling: `pip install ansible ansible-lint molecule yamllint`.
2. Run linting: `ansible-lint` and `yamllint`.
3. Run playbook (example): `ansible-playbook -i inventories/production playbooks/site.yml`.

See `docs/ansible-best-practices.md` for recommended practices.
