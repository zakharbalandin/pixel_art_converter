# Ansible Deployment for Pixel Art Converter

## 🏗️ Infrastructure

| Host | IP Address | Role |
|------|------------|------|
| server | 192.168.122.4 | Flask App + PostgreSQL Database |
| node1 | 192.168.122.5 | Monitoring (Prometheus, Grafana, Loki) |
| node2 | 192.168.122.6 | Secondary Flask App |

## 📁 Project Structure

```
ansible/
├── ansible.cfg              # Ansible configuration
├── inventory                # Host inventory
├── playbook.yml             # Main deployment playbook
├── templates/
│   ├── prometheus.yml.j2    # Prometheus config template
│   ├── loki-config.yml.j2   # Loki config template
│   └── grafana-datasources.yml.j2  # Grafana datasources
└── README.md                # This file
```

## 🚀 Quick Start

### 1. Prerequisites

On your Ansible controller (workstation):

```bash
# Install Ansible
sudo apt update
sudo apt install ansible -y

# Install required collections
ansible-galaxy collection install community.docker
```

On target VMs, ensure:
- SSH access is configured
- User has sudo privileges

### 2. Test Connectivity

```bash
cd ansible/
ansible all -m ping
```

Expected output:
```
server | SUCCESS => { "ping": "pong" }
node1  | SUCCESS => { "ping": "pong" }
node2  | SUCCESS => { "ping": "pong" }
```

### 3. Deploy Everything

```bash
# Full deployment
ansible-playbook playbook.yml

# Or step by step:
ansible-playbook playbook.yml --tags docker      # Install Docker first
ansible-playbook playbook.yml --tags database    # Then database
ansible-playbook playbook.yml --tags app         # Then application
ansible-playbook playbook.yml --tags monitoring  # Finally monitoring
```

## 📊 After Deployment

### Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| Web App (Primary) | http://192.168.122.4:5000 | - |
| Web App (Secondary) | http://192.168.122.6:5000 | - |
| Grafana | http://192.168.122.5:3000 | admin / admin |
| Prometheus | http://192.168.122.5:9090 | - |
| Loki API | http://192.168.122.5:3100 | - |

### Verify Deployment

```bash
# Check web apps
curl http://192.168.122.4:5000/health
curl http://192.168.122.6:5000/health

# Check Prometheus targets
curl http://192.168.122.5:9090/api/v1/targets

# Check Grafana
curl http://192.168.122.5:3000/api/health
```

## 🔧 Useful Commands

```bash
# Check syntax
ansible-playbook playbook.yml --syntax-check

# Dry run (no changes)
ansible-playbook playbook.yml --check

# Verbose output
ansible-playbook playbook.yml -v

# Run on specific host
ansible-playbook playbook.yml --limit server

# View all hosts
ansible all --list-hosts

# Run ad-hoc commands
ansible all -m shell -a "docker ps"
ansible app_servers -m shell -a "curl localhost:5000/health"
```

## 🔄 Update Application

To update the application after code changes:

```bash
# Rebuild and redeploy app containers
ansible-playbook playbook.yml --tags app
```

## 🛠️ Troubleshooting

### SSH Connection Failed
```bash
# Test SSH manually
ssh student@192.168.122.4

# Copy SSH key
ssh-copy-id student@192.168.122.4
```

### Docker Not Starting
```bash
# Check Docker status on remote host
ansible server -m shell -a "systemctl status docker"
```

### Container Issues
```bash
# Check container logs
ansible server -m shell -a "docker logs pixel_art_converter_web"

# Check running containers
ansible all -m shell -a "docker ps"
```

### Database Connection Failed
```bash
# Check if PostgreSQL is running
ansible server -m shell -a "docker logs pixel_art_converter_db"

# Test database connection
ansible server -m shell -a "docker exec pixel_art_converter_db pg_isready -U postgres"
```

## 📈 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ANSIBLE CONTROLLER                          │
│                        (Your Workstation)                           │
│                                                                     │
│  $ ansible-playbook playbook.yml                                    │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │ SSH
                ┌─────────────────┼─────────────────┐
                │                 │                 │
                ▼                 ▼                 ▼
┌───────────────────┐ ┌───────────────────┐ ┌───────────────────┐
│      SERVER       │ │       NODE1       │ │       NODE2       │
│  192.168.122.4    │ │  192.168.122.5    │ │  192.168.122.6    │
├───────────────────┤ ├───────────────────┤ ├───────────────────┤
│                   │ │                   │ │                   │
│  ┌─────────────┐  │ │  ┌─────────────┐  │ │  ┌─────────────┐  │
│  │  Flask App  │  │ │  │ Prometheus  │  │ │  │  Flask App  │  │
│  │   :5000     │  │ │  │   :9090     │  │ │  │   :5000     │  │
│  └─────────────┘  │ │  └─────────────┘  │ │  └──────┬──────┘  │
│         │         │ │                   │ │         │         │
│         │         │ │  ┌─────────────┐  │ │         │         │
│  ┌──────▼──────┐  │ │  │   Grafana   │  │ │         │         │
│  │ PostgreSQL  │  │ │  │   :3000     │  │ │         │         │
│  │   :5432     │◄─┼─┼──┼─────────────┼──┼─┼─────────┘         │
│  └─────────────┘  │ │  └─────────────┘  │ │  Connects to      │
│                   │ │                   │ │  server's DB      │
│                   │ │  ┌─────────────┐  │ │                   │
│                   │ │  │    Loki     │  │ │                   │
│                   │ │  │   :3100     │  │ │                   │
│                   │ │  └─────────────┘  │ │                   │
│                   │ │                   │ │                   │
└───────────────────┘ └───────────────────┘ └───────────────────┘
```

## 📝 Variables Reference

### Inventory Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `app_name` | pixel_art_converter | Application name |
| `app_port` | 5000 | Flask app port |
| `db_name` | pixel_art_db | Database name |
| `db_user` | postgres | Database user |
| `db_password` | postgres | Database password |
| `db_port` | 5432 | PostgreSQL port |
| `prometheus_port` | 9090 | Prometheus port |
| `grafana_port` | 3000 | Grafana port |
| `loki_port` | 3100 | Loki port |
