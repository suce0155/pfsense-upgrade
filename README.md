# Automate pfSense Upgrades Using Ansible

This repository contains Ansible playbooks and roles for automating the configuration, management, and sequential upgrading of pfSense firewalls. It includes specialized support for pfSense instances hosted as Proxmox virtual machines, allowing for automated snapshots before major configuration changes or upgrades.

## Features

* **Automated Upgrades & Snapshots:** Incrementally upgrades pfSense through major versions (2.5.x → 2.7.x → 2.7.2 → 2.8.x), taking automatic Proxmox VM snapshots at each step to ensure safe rollbacks.
* **IPSec Auditing:** Checks existing IPSec configurations for outdated or weak encryption algorithms.
* **SSH Management:** Enables SSH access and automatically adds the necessary firewall rules.
* **API Package Installation:** Automates the installation of the third-party pfSense REST API package (`jaredhendrickson13/pfsense-api`).
* **Configuration Backups:** Captures and saves pfSense configuration backups during initial setup.

## Prerequisites

1. **Python 3** installed on the control node.
2. Install the required Python packages:
   ```bash
   pip3 install -r requirements.txt
   ```
3. A Proxmox environment (if utilizing the automated snapshot features during upgrading).
4. pfSense node(s) accessible via the network.

## Configuration

### Inventory Setup
Edit `inventory.ini` to define your pfSense hosts and their Proxmox `vmid`s.
```ini
[pfsense]
192.168.1.39 vmid=107

[pfsense:vars]
ansible_user=admin
ansible_password=pfsense
ansible_ssh_common_args='-o StrictHostKeyChecking=no'
```

### Group Variables
Edit `group_vars/pfsense.yml` to supply Proxmox API and pfSense webGUI credentials.
```yaml
proxmox_host: <proxmox_ip>:8006
proxmox_api_user: "ansible@pam"
proxmox_api_token_id: "snapshot-token"
proxmox_api_token_secret: "<token_secret>"
proxmox_validate_certs: false

fw_user: "admin"
fw_passw: "pfsense"
fw_port: "443"
```

## Playbook Structure

The primary playbook `main.yml` sequentially executes the following roles:
1. `check_ipsec`: Runs the `check_ipsec.py` script to audit VPN encryption.
2. `enable_ssh`: Configures pfSense to allow SSH and performs a config backup.
3. `add_ssh_FWrule`: Injects a firewall rule to explicitly allow SSH traffic to the management interface.
4. `version_check`: Determines the current pfSense version and initiates the appropriate upgrade loop, triggering Proxmox snapshots as safety checkpoints.
5. `install-pkg`: Installs the pfSense REST API package to enable further external automations.

## Usage

To run the complete automation suite against your pfSense VMs:

```bash
ansible-playbook -i inventory.ini main.yml
```

> **Note:** Ensure your control node has access to the Proxmox API port (typically `8006`) and the pfSense webGUI port before running the playbook.
