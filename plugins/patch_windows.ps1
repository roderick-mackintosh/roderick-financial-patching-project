#!powershell

# Copyright: (c) 2025, Your Name <your.email@example.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

#AnsibleRequires -CSharpUtil Ansible.Basic

# ---------------------------------------------------------------------------
# Module documentation (kept as a comment block; the real DOCUMENTATION
# lives in the adjacent .py "stub" file if you ship a proper collection).
# ---------------------------------------------------------------------------
# SYNOPSIS
#   A template Ansible module written in PowerShell.
# DESCRIPTION
#   Does something useful on a Windows host.
# OPTIONS
#   name      - (string, required)  The name of the thing to manage.
#   state     - (string, optional)  'present' or 'absent'. Default: present.
#   value     - (string, optional)  An optional value associated with name.
# ---------------------------------------------------------------------------

# ------------------------------------------------------------------
# 1.  Define the module argument spec
# ------------------------------------------------------------------
$spec = @{
    options             = @{
        name  = @{ type = 'str';  required = $true }
        state = @{ type = 'str';  default = 'present'; choices = @('present', 'absent') }
        value = @{ type = 'str';  required = $false; no_log = $false }
    }
    supports_check_mode = $true   # set to $false if you cannot dry-run safely
}

# Instantiate the Ansible.Basic helper – this also parses & validates params.
$module = [Ansible.Basic.AnsibleModule]::Create($args, $spec)

# ------------------------------------------------------------------
# 2.  Retrieve validated parameters
# ------------------------------------------------------------------
$name       = $module.Params.name
$state      = $module.Params.state
$value      = $module.Params.value

# ------------------------------------------------------------------
# 3.  Helper functions
# ------------------------------------------------------------------

function Get-CurrentState {
    <#
    .SYNOPSIS
        Detect whether the managed resource already exists / is configured.
    .OUTPUTS
        Hashtable with at least a key 'exists' ($true/$false) and any
        current settings you need to compare against desired state.
    #>
    param([string]$Name)

    # TODO: replace with your real detection logic.
    # Example: check for a registry key, file, service, etc.
    $exists = $false
    $currentValue = $null

    # --- EXAMPLE: registry key ---
    # $regPath = "HKLM:\SOFTWARE\MyApp\$Name"
    # if (Test-Path -LiteralPath $regPath) {
    #     $exists      = $true
    #     $currentValue = (Get-ItemProperty -LiteralPath $regPath).Value
    # }

    return @{
        exists       = $exists
        current_value = $currentValue
    }
}

function Set-Resource {
    <#
    .SYNOPSIS
        Create or update the managed resource.
    #>
    param(
        [string]$Name,
        [string]$Value
    )

    # TODO: implement create / update logic.
    # Example:
    # New-Item -Path "HKLM:\SOFTWARE\MyApp\$Name" -Force | Out-Null
    # Set-ItemProperty -Path "HKLM:\SOFTWARE\MyApp\$Name" -Name "Value" -Value $Value
}

function Remove-Resource {
    <#
    .SYNOPSIS
        Remove the managed resource.
    #>
    param([string]$Name)

    # TODO: implement removal logic.
    # Example:
    # Remove-Item -Path "HKLM:\SOFTWARE\MyApp\$Name" -Recurse -Force
}

# ------------------------------------------------------------------
# 4.  Main logic
# ------------------------------------------------------------------
try {
    $current = Get-CurrentState -Name $name

    if ($state -eq 'present') {

        if (-not $current.exists) {
            # Resource is missing – create it.
            if (-not $module.CheckMode) {
                Set-Resource -Name $name -Value $value
            }
            $module.Result.changed = $true
            $module.Result.msg     = "Resource '$name' created."

        } elseif ($current.current_value -ne $value) {
            # Resource exists but differs – update it.
            if (-not $module.CheckMode) {
                Set-Resource -Name $name -Value $value
            }
            $module.Result.changed    = $true
            $module.Result.msg        = "Resource '$name' updated."
            $module.Result.diff = @{
                before = $current.current_value
                after  = $value
            }

        } else {
            # Already in the desired state – nothing to do.
            $module.Result.changed = $false
            $module.Result.msg     = "Resource '$name' is already present and up-to-date."
        }

    } elseif ($state -eq 'absent') {

        if ($current.exists) {
            if (-not $module.CheckMode) {
                Remove-Resource -Name $name
            }
            $module.Result.changed = $true
            $module.Result.msg     = "Resource '$name' removed."
        } else {
            $module.Result.changed = $false
            $module.Result.msg     = "Resource '$name' is already absent."
        }
    }

    # Optionally surface extra data back to the playbook.
    $module.Result.name  = $name
    $module.Result.state = $state

} catch {
    # FailJson terminates execution and returns a failed result to Ansible.
    $module.FailJson("Unhandled error: $($_.Exception.Message)", $_)
}

# ------------------------------------------------------------------
# 5.  Exit – sends the JSON result back to Ansible.
# ------------------------------------------------------------------
$module.ExitJson()
