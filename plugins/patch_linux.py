#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2025, Your Name <your.email@example.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


# ---------------------------------------------------------------------------
# DOCUMENTATION / EXAMPLES / RETURN  (used by ansible-doc)
# ---------------------------------------------------------------------------

DOCUMENTATION = r'''
---
module: my_module
short_description: A brief one-line description of what this module does.
version_added: "1.0.0"

description:
  - A longer description of the module.
  - Supports check mode.

options:
  name:
    description:
      - The name of the resource to manage.
    required: true
    type: str
  state:
    description:
      - Whether the resource should exist or not.
    type: str
    choices: [ present, absent ]
    default: present
  value:
    description:
      - An optional value associated with the resource.
    type: str
    required: false

author:
  - Your Name (@github_handle)
'''

EXAMPLES = r'''
- name: Ensure resource is present
  my_namespace.my_collection.my_module:
    name: foo
    state: present
    value: bar

- name: Ensure resource is absent
  my_namespace.my_collection.my_module:
    name: foo
    state: absent
'''

RETURN = r'''
name:
  description: The name of the managed resource.
  returned: always
  type: str
  sample: foo
state:
  description: The desired state that was applied.
  returned: always
  type: str
  sample: present
value:
  description: The value associated with the resource (if applicable).
  returned: when state is present
  type: str
  sample: bar
'''

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

# Standard library imports go here.
# import os
# import json

# Ansible utility imports – always use these rather than raw sys.exit().
from ansible.module_utils.basic import AnsibleModule


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def get_current_state(module, name):
    """
    Detect whether the managed resource already exists and return its
    current configuration.

    Returns a dict with at least:
      exists        (bool)   – whether the resource is present
      current_value (str)    – current value, or None
    """
    exists = False
    current_value = None

    # TODO: replace with your real detection logic.
    # Examples:
    #   - read a config file
    #   - call an API / SDK
    #   - run a command via module.run_command()
    #
    # rc, stdout, stderr = module.run_command(['myapp', 'get', name])
    # if rc == 0:
    #     exists = True
    #     current_value = stdout.strip()

    return dict(exists=exists, current_value=current_value)


def create_or_update_resource(module, name, value):
    """
    Create or update the managed resource.
    Should raise an exception (or call module.fail_json) on error.
    """
    # TODO: implement create / update logic.
    #
    # rc, stdout, stderr = module.run_command(['myapp', 'set', name, value])
    # if rc != 0:
    #     module.fail_json(msg=f"Failed to set resource '{name}': {stderr}")
    pass


def delete_resource(module, name):
    """
    Remove the managed resource.
    Should raise an exception (or call module.fail_json) on error.
    """
    # TODO: implement removal logic.
    #
    # rc, stdout, stderr = module.run_command(['myapp', 'delete', name])
    # if rc != 0:
    #     module.fail_json(msg=f"Failed to delete resource '{name}': {stderr}")
    pass


# ---------------------------------------------------------------------------
# Core module logic
# ---------------------------------------------------------------------------

def run_module():
    # ------------------------------------------------------------------
    # 1. Define the argument spec
    # ------------------------------------------------------------------
    argument_spec = dict(
        name=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        value=dict(type='str', required=False, no_log=False),
    )

    # ------------------------------------------------------------------
    # 2. Instantiate AnsibleModule
    #    supports_check_mode=True means we promise to honour --check.
    # ------------------------------------------------------------------
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    # ------------------------------------------------------------------
    # 3. Retrieve validated parameters
    # ------------------------------------------------------------------
    name  = module.params['name']
    state = module.params['state']
    value = module.params.get('value')

    # ------------------------------------------------------------------
    # 4. Seed the result dict – always include 'changed' and 'failed'.
    # ------------------------------------------------------------------
    result = dict(
        changed=False,
        failed=False,
        name=name,
        state=state,
    )

    # ------------------------------------------------------------------
    # 5. Main logic
    # ------------------------------------------------------------------
    try:
        current = get_current_state(module, name)

        if state == 'present':

            if not current['exists']:
                # Resource is missing – create it.
                if not module.check_mode:
                    create_or_update_resource(module, name, value)
                result['changed'] = True
                result['msg'] = f"Resource '{name}' created."
                result['value'] = value

            elif current['current_value'] != value:
                # Resource exists but differs from desired – update it.
                if not module.check_mode:
                    create_or_update_resource(module, name, value)
                result['changed'] = True
                result['msg'] = f"Resource '{name}' updated."
                result['value'] = value
                result['diff'] = dict(
                    before=current['current_value'],
                    after=value,
                )

            else:
                # Already in the desired state – nothing to do.
                result['changed'] = False
                result['msg'] = f"Resource '{name}' is already present and up-to-date."
                result['value'] = current['current_value']

        elif state == 'absent':

            if current['exists']:
                if not module.check_mode:
                    delete_resource(module, name)
                result['changed'] = True
                result['msg'] = f"Resource '{name}' removed."
            else:
                result['changed'] = False
                result['msg'] = f"Resource '{name}' is already absent."

    except Exception as e:
        module.fail_json(msg=f"Unhandled error: {str(e)}", **result)

    # ------------------------------------------------------------------
    # 6. Return the result to Ansible.
    # ------------------------------------------------------------------
    module.exit_json(**result)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    run_module()


if __name__ == '__main__':
    main()
