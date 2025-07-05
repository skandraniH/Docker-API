# Docker Management API

A comprehensive REST API service built with Flask and Python for managing Docker containers, images, volumes, networks, and system information. This project provides a complete web-based interface to interact with Docker daemon through HTTP endpoints.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Docker Commands Reference](#docker-commands-reference)
- [Usage Examples](#usage-examples)
- [Error Handling](#error-handling)
- [Development](#development)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Overview

The Docker Management API is a RESTful web service that provides programmatic access to Docker operations. It abstracts Docker's command-line interface into HTTP endpoints, making it easy to integrate Docker management capabilities into web applications, monitoring systems, or automation tools.

### Key Benefits

- **RESTful Interface**: Standard HTTP methods (GET, POST, DELETE) for all operations
- **Comprehensive Coverage**: Supports containers, images, volumes, networks, and system information
- **Error Handling**: Robust error handling with meaningful error messages
- **Cross-Origin Support**: CORS enabled for web application integration
- **Detailed Responses**: Rich JSON responses with comprehensive information
- **Health Monitoring**: Built-in health check and system monitoring endpoints

## Features

### Container Management
- List all containers (running and stopped)
- Get detailed container information
- Create, start, stop, restart containers
- Remove containers with force option
- Retrieve container logs
- Monitor container status

### Image Management
- List all Docker images
- Pull images from Docker registries
- Build images from Dockerfile
- Remove images with cleanup options
- Search Docker Hub for images
- Prune unused images
- Get detailed image information and history

### Volume Management
- List all Docker volumes
- Create and remove volumes
- Get volume usage statistics
- Prune unused volumes
- Monitor volume usage by containers
- Support for different volume drivers

### Network Management
- List all Docker networks
- Create custom networks
- Remove networks
- Connect/disconnect containers to networks
- Network statistics and monitoring
- Support for different network drivers

### System Information
- Docker version and system information
- Disk usage statistics
- Docker daemon status monitoring
- Overall system statistics
- Host system information
- Resource usage monitoring

## Project Structure

```
docker_management_api/
├── src/
│   ├── container_manager.py    # Container operations manager
│   ├── image_manager.py        # Image operations manager
│   ├── volume_manager.py       # Volume operations manager
│   ├── network_manager.py      # Network operations manager
│   ├── system_manager.py       # System information manager
│   ├── main.py                 # Main Flask application
│   └── static/                 # Static files (if needed)
├── venv/                       # Virtual environment
├── requirements.txt            # Python dependencies
└── README.md                   # This documentation
```

### Manager Classes

Each manager class is responsible for a specific aspect of Docker management:

- **ContainerManager**: Handles all container-related operations
- **ImageManager**: Manages Docker images and registry operations
- **VolumeManager**: Controls volume creation, deletion, and monitoring
- **NetworkManager**: Manages Docker networks and container connectivity
- **SystemManager**: Provides system information and monitoring capabilities

## Installation

### Prerequisites

- Python 3.8 or higher
- Docker Engine installed and running
- Docker daemon accessible (usually requires Docker group membership)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd docker_management_api
```

### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Verify Docker Access

```bash
docker ps  # Should list containers without errors
```

## Quick Start

### Start the API Server

```bash
cd docker_management_api
source venv/bin/activate
python src/main.py
```

The API will be available at `http://localhost:5000`

### Test the API

```bash
# Health check
curl http://localhost:5000/health

# List containers
curl http://localhost:5000/api/containers

# Get system information
curl http://localhost:5000/api/system/info
```

### View API Documentation

Visit `http://localhost:5000/api/commands` to see all available endpoints.

## API Documentation

### Base URL
```
http://localhost:5000/api
```

### Authentication
Currently, no authentication is required. In production, consider implementing API keys or OAuth.

### Response Format
All responses follow this structure:
```json
{
    "success": true,
    "data": { ... },
    "error": null
}
```

Error responses:
```json
{
    "success": false,
    "error": "Error message",
    "data": null
}
```



### Container Endpoints

#### List Containers
```http
GET /api/containers
```

Query Parameters:
- `all` (boolean): Include stopped containers (default: false)

Example Response:
```json
{
    "containers": [
        {
            "id": "abc123def456",
            "name": "my-container",
            "image": "nginx:latest",
            "status": "running",
            "created": "2024-01-01T12:00:00Z",
            "ports": {"80/tcp": [{"HostPort": "8080"}]},
            "labels": {}
        }
    ],
    "count": 1,
    "success": true
}
```

#### Get Container Details
```http
GET /api/containers/{container_id}
```

#### Start Container
```http
POST /api/containers/{container_id}/start
```

#### Stop Container
```http
POST /api/containers/{container_id}/stop
```

Request Body (optional):
```json
{
    "timeout": 10
}
```

#### Restart Container
```http
POST /api/containers/{container_id}/restart
```

#### Remove Container
```http
DELETE /api/containers/{container_id}/remove
```

Query Parameters:
- `force` (boolean): Force removal of running container

#### Get Container Logs
```http
GET /api/containers/{container_id}/logs
```

Query Parameters:
- `tail` (integer): Number of lines to retrieve (default: 100)

#### Create Container
```http
POST /api/containers
```

Request Body:
```json
{
    "image": "nginx:latest",
    "name": "my-nginx",
    "ports": {"80/tcp": 8080},
    "environment": ["ENV_VAR=value"],
    "volumes": {"/host/path": {"bind": "/container/path", "mode": "rw"}}
}
```

### Image Endpoints

#### List Images
```http
GET /api/images
```

Query Parameters:
- `all` (boolean): Include intermediate images (default: false)

#### Get Image Details
```http
GET /api/images/{image_id}
```

#### Pull Image
```http
POST /api/images/pull
```

Request Body:
```json
{
    "image": "nginx",
    "tag": "latest"
}
```

#### Remove Image
```http
DELETE /api/images/{image_id}/remove
```

Query Parameters:
- `force` (boolean): Force removal
- `no_prune` (boolean): Don't delete untagged parent images

#### Build Image
```http
POST /api/images/build
```

Request Body:
```json
{
    "path": "/path/to/build/context",
    "tag": "my-image:latest",
    "dockerfile": "Dockerfile"
}
```

#### Search Images
```http
GET /api/images/search
```

Query Parameters:
- `term` (string): Search term (required)
- `limit` (integer): Maximum results (default: 25)

#### Prune Images
```http
POST /api/images/prune
```

Query Parameters:
- `dangling_only` (boolean): Only remove dangling images (default: true)

### Volume Endpoints

#### List Volumes
```http
GET /api/volumes
```

#### Get Volume Details
```http
GET /api/volumes/{volume_name}
```

#### Create Volume
```http
POST /api/volumes
```

Request Body:
```json
{
    "name": "my-volume",
    "driver": "local",
    "labels": {"environment": "production"},
    "options": {"type": "nfs", "device": ":/path/to/dir"}
}
```

#### Remove Volume
```http
DELETE /api/volumes/{volume_name}/remove
```

Query Parameters:
- `force` (boolean): Force removal

#### Prune Volumes
```http
POST /api/volumes/prune
```

#### Get Volume Statistics
```http
GET /api/volumes/stats
```

### Network Endpoints

#### List Networks
```http
GET /api/networks
```

#### Get Network Details
```http
GET /api/networks/{network_id}
```

#### Create Network
```http
POST /api/networks
```

Request Body:
```json
{
    "name": "my-network",
    "driver": "bridge",
    "internal": false,
    "attachable": true,
    "labels": {"environment": "production"},
    "ipam": {
        "driver": "default",
        "config": [{"subnet": "172.20.0.0/16"}]
    }
}
```

#### Remove Network
```http
DELETE /api/networks/{network_id}/remove
```

#### Connect Container to Network
```http
POST /api/networks/{network_id}/connect
```

Request Body:
```json
{
    "container": "container_id",
    "aliases": ["web-server"],
    "ipv4_address": "172.20.0.10"
}
```

#### Disconnect Container from Network
```http
POST /api/networks/{network_id}/disconnect
```

Request Body:
```json
{
    "container": "container_id",
    "force": false
}
```

#### Prune Networks
```http
POST /api/networks/prune
```

#### Get Network Statistics
```http
GET /api/networks/stats
```

### System Endpoints

#### Get Docker Version
```http
GET /api/system/version
```

#### Get System Information
```http
GET /api/system/info
```

#### Get Disk Usage
```http
GET /api/system/df
```

#### Get Daemon Status
```http
GET /api/system/status
```

#### Get Overall Statistics
```http
GET /api/system/stats
```

#### Get Host System Information
```http
GET /api/system/host
```

### Utility Endpoints

#### Get Available Commands
```http
GET /api/commands
```

Returns a comprehensive list of all available API endpoints with descriptions.

#### Health Check
```http
GET /health
```

Returns the health status of the API and Docker daemon.

## Docker Commands Reference

This section provides equivalent Docker CLI commands for each API operation, helping you understand the relationship between the API and Docker's command-line interface.

### Container Commands

| API Endpoint | Docker CLI Equivalent | Description |
|--------------|----------------------|-------------|
| `GET /api/containers` | `docker ps` | List running containers |
| `GET /api/containers?all=true` | `docker ps -a` | List all containers |
| `GET /api/containers/{id}` | `docker inspect {id}` | Get container details |
| `POST /api/containers/{id}/start` | `docker start {id}` | Start container |
| `POST /api/containers/{id}/stop` | `docker stop {id}` | Stop container |
| `POST /api/containers/{id}/restart` | `docker restart {id}` | Restart container |
| `DELETE /api/containers/{id}/remove` | `docker rm {id}` | Remove container |
| `DELETE /api/containers/{id}/remove?force=true` | `docker rm -f {id}` | Force remove container |
| `GET /api/containers/{id}/logs` | `docker logs {id}` | Get container logs |
| `GET /api/containers/{id}/logs?tail=50` | `docker logs --tail 50 {id}` | Get last 50 log lines |
| `POST /api/containers` | `docker create` | Create container |

### Image Commands

| API Endpoint | Docker CLI Equivalent | Description |
|--------------|----------------------|-------------|
| `GET /api/images` | `docker images` | List images |
| `GET /api/images?all=true` | `docker images -a` | List all images |
| `GET /api/images/{id}` | `docker inspect {id}` | Get image details |
| `POST /api/images/pull` | `docker pull {image}` | Pull image |
| `DELETE /api/images/{id}/remove` | `docker rmi {id}` | Remove image |
| `DELETE /api/images/{id}/remove?force=true` | `docker rmi -f {id}` | Force remove image |
| `POST /api/images/build` | `docker build` | Build image |
| `GET /api/images/search?term={term}` | `docker search {term}` | Search Docker Hub |
| `POST /api/images/prune` | `docker image prune` | Remove unused images |
| `POST /api/images/prune?dangling_only=false` | `docker image prune -a` | Remove all unused images |

### Volume Commands

| API Endpoint | Docker CLI Equivalent | Description |
|--------------|----------------------|-------------|
| `GET /api/volumes` | `docker volume ls` | List volumes |
| `GET /api/volumes/{name}` | `docker volume inspect {name}` | Get volume details |
| `POST /api/volumes` | `docker volume create` | Create volume |
| `DELETE /api/volumes/{name}/remove` | `docker volume rm {name}` | Remove volume |
| `DELETE /api/volumes/{name}/remove?force=true` | `docker volume rm -f {name}` | Force remove volume |
| `POST /api/volumes/prune` | `docker volume prune` | Remove unused volumes |
| `GET /api/volumes/stats` | `docker system df` | Get volume statistics |

### Network Commands

| API Endpoint | Docker CLI Equivalent | Description |
|--------------|----------------------|-------------|
| `GET /api/networks` | `docker network ls` | List networks |
| `GET /api/networks/{id}` | `docker network inspect {id}` | Get network details |
| `POST /api/networks` | `docker network create` | Create network |
| `DELETE /api/networks/{id}/remove` | `docker network rm {id}` | Remove network |
| `POST /api/networks/{id}/connect` | `docker network connect {network} {container}` | Connect container |
| `POST /api/networks/{id}/disconnect` | `docker network disconnect {network} {container}` | Disconnect container |
| `POST /api/networks/prune` | `docker network prune` | Remove unused networks |

### System Commands

| API Endpoint | Docker CLI Equivalent | Description |
|--------------|----------------------|-------------|
| `GET /api/system/version` | `docker version` | Get Docker version |
| `GET /api/system/info` | `docker info` | Get system information |
| `GET /api/system/df` | `docker system df` | Get disk usage |
| `GET /api/system/stats` | `docker stats --no-stream` | Get resource statistics |
| `GET /health` | `docker version` | Check Docker daemon |

### Advanced Docker Commands

#### Container Management
```bash
# Run a container with port mapping
docker run -d -p 8080:80 --name my-nginx nginx:latest

# API equivalent
curl -X POST http://localhost:5000/api/containers \
  -H "Content-Type: application/json" \
  -d '{
    "image": "nginx:latest",
    "name": "my-nginx",
    "ports": {"80/tcp": 8080},
    "detach": true
  }'

# Execute command in running container
docker exec -it my-nginx bash

# Copy files to/from container
docker cp file.txt my-nginx:/tmp/
docker cp my-nginx:/tmp/file.txt ./

# View container resource usage
docker stats my-nginx --no-stream

# Get container processes
docker top my-nginx
```

#### Image Management
```bash
# Build image with build arguments
docker build --build-arg VERSION=1.0 -t my-app:1.0 .

# API equivalent
curl -X POST http://localhost:5000/api/images/build \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/path/to/context",
    "tag": "my-app:1.0",
    "buildargs": {"VERSION": "1.0"}
  }'

# Tag an image
docker tag my-app:1.0 my-app:latest

# Push image to registry
docker push my-app:1.0

# Save/load images
docker save my-app:1.0 > my-app.tar
docker load < my-app.tar

# Get image history
docker history my-app:1.0
```

#### Volume Management
```bash
# Create volume with specific driver
docker volume create --driver local \
  --opt type=nfs \
  --opt o=addr=192.168.1.1,rw \
  --opt device=:/path/to/dir \
  my-nfs-volume

# API equivalent
curl -X POST http://localhost:5000/api/volumes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-nfs-volume",
    "driver": "local",
    "options": {
      "type": "nfs",
      "o": "addr=192.168.1.1,rw",
      "device": ":/path/to/dir"
    }
  }'

# Mount volume in container
docker run -v my-volume:/data nginx:latest

# Backup volume
docker run --rm -v my-volume:/data -v $(pwd):/backup ubuntu tar czf /backup/backup.tar.gz /data
```

#### Network Management
```bash
# Create custom bridge network
docker network create --driver bridge \
  --subnet=172.20.0.0/16 \
  --ip-range=172.20.240.0/20 \
  my-network

# API equivalent
curl -X POST http://localhost:5000/api/networks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-network",
    "driver": "bridge",
    "ipam": {
      "config": [{
        "subnet": "172.20.0.0/16",
        "ip_range": "172.20.240.0/20"
      }]
    }
  }'

# Connect container with specific IP
docker network connect --ip 172.20.0.10 my-network my-container

# Create overlay network (Swarm mode)
docker network create --driver overlay --attachable my-overlay
```


## Usage Examples

### Basic Container Operations

#### Example 1: Deploy a Web Server
```bash
# 1. Pull nginx image
curl -X POST http://localhost:5000/api/images/pull \
  -H "Content-Type: application/json" \
  -d '{"image": "nginx", "tag": "latest"}'

# 2. Create and start nginx container
curl -X POST http://localhost:5000/api/containers \
  -H "Content-Type: application/json" \
  -d '{
    "image": "nginx:latest",
    "name": "my-web-server",
    "ports": {"80/tcp": 8080}
  }'

# 3. Start the container
curl -X POST http://localhost:5000/api/containers/my-web-server/start

# 4. Check container status
curl http://localhost:5000/api/containers/my-web-server

# 5. View logs
curl http://localhost:5000/api/containers/my-web-server/logs?tail=20
```

#### Example 2: Database Setup with Volume
```bash
# 1. Create a volume for database data
curl -X POST http://localhost:5000/api/volumes \
  -H "Content-Type: application/json" \
  -d '{
    "name": "postgres-data",
    "labels": {"purpose": "database"}
  }'

# 2. Create PostgreSQL container with volume
curl -X POST http://localhost:5000/api/containers \
  -H "Content-Type: application/json" \
  -d '{
    "image": "postgres:13",
    "name": "my-postgres",
    "environment": [
      "POSTGRES_DB=myapp",
      "POSTGRES_USER=admin",
      "POSTGRES_PASSWORD=secret123"
    ],
    "ports": {"5432/tcp": 5432},
    "volumes": {"postgres-data": {"bind": "/var/lib/postgresql/data", "mode": "rw"}}
  }'

# 3. Start the database
curl -X POST http://localhost:5000/api/containers/my-postgres/start
```

#### Example 3: Multi-Container Application with Custom Network
```bash
# 1. Create custom network
curl -X POST http://localhost:5000/api/networks \
  -H "Content-Type: application/json" \
  -d '{
    "name": "app-network",
    "driver": "bridge",
    "ipam": {
      "config": [{"subnet": "172.20.0.0/16"}]
    }
  }'

# 2. Create database container
curl -X POST http://localhost:5000/api/containers \
  -H "Content-Type: application/json" \
  -d '{
    "image": "postgres:13",
    "name": "app-db",
    "environment": ["POSTGRES_DB=app", "POSTGRES_USER=user", "POSTGRES_PASSWORD=pass"]
  }'

# 3. Create web application container
curl -X POST http://localhost:5000/api/containers \
  -H "Content-Type: application/json" \
  -d '{
    "image": "node:16-alpine",
    "name": "app-web",
    "ports": {"3000/tcp": 3000},
    "environment": ["DATABASE_URL=postgresql://user:pass@app-db:5432/app"]
  }'

# 4. Connect both containers to the network
curl -X POST http://localhost:5000/api/networks/app-network/connect \
  -H "Content-Type: application/json" \
  -d '{"container": "app-db"}'

curl -X POST http://localhost:5000/api/networks/app-network/connect \
  -H "Content-Type: application/json" \
  -d '{"container": "app-web"}'

# 5. Start both containers
curl -X POST http://localhost:5000/api/containers/app-db/start
curl -X POST http://localhost:5000/api/containers/app-web/start
```

### System Monitoring Examples

#### Example 4: System Health Check
```bash
# Check API health
curl http://localhost:5000/health

# Get Docker system information
curl http://localhost:5000/api/system/info

# Check disk usage
curl http://localhost:5000/api/system/df

# Get overall statistics
curl http://localhost:5000/api/system/stats
```

#### Example 5: Resource Cleanup
```bash
# Stop all containers
curl http://localhost:5000/api/containers?all=true | \
  jq -r '.containers[] | select(.status=="running") | .name' | \
  while read container; do
    curl -X POST http://localhost:5000/api/containers/$container/stop
  done

# Remove stopped containers
curl http://localhost:5000/api/containers?all=true | \
  jq -r '.containers[] | select(.status=="exited") | .name' | \
  while read container; do
    curl -X DELETE http://localhost:5000/api/containers/$container/remove
  done

# Prune unused resources
curl -X POST http://localhost:5000/api/images/prune
curl -X POST http://localhost:5000/api/volumes/prune
curl -X POST http://localhost:5000/api/networks/prune
```

### Python Client Example

```python
import requests
import json

class DockerAPIClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        
    def list_containers(self, all_containers=False):
        """List containers."""
        params = {'all': 'true'} if all_containers else {}
        response = requests.get(f"{self.base_url}/api/containers", params=params)
        return response.json()
    
    def create_container(self, image, name=None, **kwargs):
        """Create a new container."""
        data = {'image': image}
        if name:
            data['name'] = name
        data.update(kwargs)
        
        response = requests.post(
            f"{self.base_url}/api/containers",
            json=data
        )
        return response.json()
    
    def start_container(self, container_id):
        """Start a container."""
        response = requests.post(
            f"{self.base_url}/api/containers/{container_id}/start"
        )
        return response.json()
    
    def get_system_info(self):
        """Get Docker system information."""
        response = requests.get(f"{self.base_url}/api/system/info")
        return response.json()

# Usage example
client = DockerAPIClient()

# List all containers
containers = client.list_containers(all_containers=True)
print(f"Found {containers['count']} containers")

# Create and start nginx container
result = client.create_container(
    image="nginx:latest",
    name="test-nginx",
    ports={"80/tcp": 8080}
)
print(f"Container created: {result}")

if result['success']:
    start_result = client.start_container("test-nginx")
    print(f"Container started: {start_result}")

# Get system information
system_info = client.get_system_info()
print(f"Docker version: {system_info['info']['docker_version']}")
```

### JavaScript/Node.js Client Example

```javascript
const axios = require('axios');

class DockerAPIClient {
    constructor(baseURL = 'http://localhost:5000') {
        this.client = axios.create({
            baseURL: baseURL,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }

    async listContainers(allContainers = false) {
        try {
            const response = await this.client.get('/api/containers', {
                params: { all: allContainers }
            });
            return response.data;
        } catch (error) {
            throw new Error(`Failed to list containers: ${error.message}`);
        }
    }

    async createContainer(image, options = {}) {
        try {
            const data = { image, ...options };
            const response = await this.client.post('/api/containers', data);
            return response.data;
        } catch (error) {
            throw new Error(`Failed to create container: ${error.message}`);
        }
    }

    async startContainer(containerId) {
        try {
            const response = await this.client.post(`/api/containers/${containerId}/start`);
            return response.data;
        } catch (error) {
            throw new Error(`Failed to start container: ${error.message}`);
        }
    }

    async getSystemInfo() {
        try {
            const response = await this.client.get('/api/system/info');
            return response.data;
        } catch (error) {
            throw new Error(`Failed to get system info: ${error.message}`);
        }
    }
}

// Usage example
async function main() {
    const client = new DockerAPIClient();

    try {
        // List containers
        const containers = await client.listContainers(true);
        console.log(`Found ${containers.count} containers`);

        // Create nginx container
        const createResult = await client.createContainer('nginx:latest', {
            name: 'test-nginx-js',
            ports: { '80/tcp': 8081 }
        });
        console.log('Container created:', createResult);

        // Start container
        if (createResult.success) {
            const startResult = await client.startContainer('test-nginx-js');
            console.log('Container started:', startResult);
        }

        // Get system info
        const systemInfo = await client.getSystemInfo();
        console.log(`Docker version: ${systemInfo.info.docker_version}`);

    } catch (error) {
        console.error('Error:', error.message);
    }
}

main();
```

## Error Handling

The API provides comprehensive error handling with meaningful error messages and appropriate HTTP status codes.

### HTTP Status Codes

| Status Code | Description | When Used |
|-------------|-------------|-----------|
| 200 | OK | Successful GET requests |
| 201 | Created | Successful POST requests (creation) |
| 400 | Bad Request | Invalid request parameters or missing required fields |
| 404 | Not Found | Resource (container, image, etc.) not found |
| 409 | Conflict | Resource already exists or conflicting state |
| 500 | Internal Server Error | Docker daemon errors or unexpected errors |
| 503 | Service Unavailable | Docker daemon not accessible |

### Error Response Format

```json
{
    "success": false,
    "error": "Detailed error message",
    "data": null
}
```

### Common Error Scenarios

#### Container Not Found
```bash
curl http://localhost:5000/api/containers/nonexistent
```
Response:
```json
{
    "success": false,
    "error": "Container 'nonexistent' not found"
}
```

#### Docker Daemon Not Running
```bash
curl http://localhost:5000/health
```
Response:
```json
{
    "status": "unhealthy",
    "error": "Cannot connect to Docker daemon. Make sure Docker is running.",
    "success": false
}
```

#### Invalid Request Data
```bash
curl -X POST http://localhost:5000/api/containers \
  -H "Content-Type: application/json" \
  -d '{}'
```
Response:
```json
{
    "success": false,
    "error": "Image name is required"
}
```

### Error Handling Best Practices

1. **Always check the `success` field** in responses
2. **Handle network errors** (connection refused, timeout)
3. **Implement retry logic** for transient errors
4. **Log errors** for debugging and monitoring
5. **Provide user-friendly error messages** in client applications

Example error handling in Python:
```python
import requests
import time

def safe_api_call(url, method='GET', **kwargs):
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            response = requests.request(method, url, **kwargs)
            data = response.json()
            
            if not data.get('success', False):
                raise Exception(f"API Error: {data.get('error', 'Unknown error')}")
            
            return data
            
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
            raise Exception("Cannot connect to Docker API")
        
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            raise Exception("API request timed out")

# Usage
try:
    containers = safe_api_call("http://localhost:5000/api/containers")
    print(f"Found {containers['count']} containers")
except Exception as e:
    print(f"Error: {e}")
```

## Development

### Setting Up Development Environment

1. **Clone the repository**
```bash
git clone <repository-url>
cd docker_management_api
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install development dependencies**
```bash
pip install pytest pytest-cov black flake8 mypy
```

5. **Run tests**
```bash
pytest tests/ -v --cov=src
```

### Code Structure Guidelines

#### Manager Classes
Each manager class should:
- Inherit from a base manager class (if implemented)
- Handle Docker client initialization
- Provide comprehensive error handling
- Return consistent data structures
- Include proper logging

#### API Endpoints
Each endpoint should:
- Use appropriate HTTP methods
- Include comprehensive error handling
- Return consistent JSON responses
- Include proper documentation
- Validate input parameters

#### Example Manager Class Structure
```python
import docker
import logging
from typing import Dict, List, Any

class BaseManager:
    def __init__(self):
        try:
            self.client = docker.from_env()
            self.client.ping()
        except Exception as e:
            logging.error(f"Failed to connect to Docker daemon: {e}")
            raise ConnectionError("Cannot connect to Docker daemon")

class ExampleManager(BaseManager):
    def list_resources(self) -> List[Dict[str, Any]]:
        """List all resources."""
        try:
            # Implementation here
            return []
        except Exception as e:
            logging.error(f"Error listing resources: {e}")
            raise Exception(f"Failed to list resources: {str(e)}")
```

### Testing

#### Unit Tests
```python
import pytest
from unittest.mock import Mock, patch
from src.container_manager import ContainerManager

class TestContainerManager:
    @patch('docker.from_env')
    def test_list_containers(self, mock_docker):
        # Mock Docker client
        mock_client = Mock()
        mock_docker.return_value = mock_client
        
        # Mock container data
        mock_container = Mock()
        mock_container.id = 'abc123'
        mock_container.name = 'test-container'
        mock_container.status = 'running'
        mock_client.containers.list.return_value = [mock_container]
        
        # Test
        manager = ContainerManager()
        containers = manager.list_containers()
        
        assert len(containers) == 1
        assert containers[0]['name'] == 'test-container'
```

#### Integration Tests
```python
import requests
import pytest

class TestAPIIntegration:
    @pytest.fixture
    def api_base_url(self):
        return "http://localhost:5000"
    
    def test_health_check(self, api_base_url):
        response = requests.get(f"{api_base_url}/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data['status'] in ['healthy', 'unhealthy']
    
    def test_list_containers(self, api_base_url):
        response = requests.get(f"{api_base_url}/api/containers")
        assert response.status_code == 200
        
        data = response.json()
        assert 'containers' in data
        assert 'count' in data
        assert data['success'] is True
```

### Adding New Features

#### Adding a New Manager
1. Create new manager class in `src/`
2. Implement required methods with error handling
3. Add comprehensive tests
4. Update main.py to include new endpoints
5. Update documentation

#### Adding New Endpoints
1. Define endpoint in main.py
2. Add error handling decorator
3. Implement request validation
4. Add comprehensive tests
5. Update API documentation

### Code Quality

#### Linting and Formatting
```bash
# Format code
black src/ tests/

# Check code style
flake8 src/ tests/

# Type checking
mypy src/
```

#### Pre-commit Hooks
Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
      - id: mypy
```

## Deployment

### Production Deployment

#### Using Docker (Recommended)

1. **Create Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Start application
CMD ["python", "src/main.py"]
```

2. **Build and run Docker image**
```bash
# Build image
docker build -t docker-management-api:latest .

# Run container with Docker socket mounted
docker run -d \
  --name docker-api \
  -p 5000:5000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  docker-management-api:latest
```

#### Using Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  docker-api:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - docker-api
    restart: unless-stopped
```

#### Production Configuration

1. **Environment Variables**
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key-here
export API_HOST=0.0.0.0
export API_PORT=5000
```

2. **Nginx Configuration** (`nginx.conf`)
```nginx
events {
    worker_connections 1024;
}

http {
    upstream docker_api {
        server docker-api:5000;
    }

    server {
        listen 80;
        server_name your-domain.com;
        
        location / {
            proxy_pass http://docker_api;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

3. **SSL/TLS Configuration**
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location / {
        proxy_pass http://docker_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Security Considerations

#### Docker Socket Security
- **Never expose Docker socket directly** to untrusted networks
- **Use Docker-in-Docker** for isolated environments
- **Implement authentication** for production deployments
- **Limit API access** using firewall rules

#### API Security
```python
# Add authentication middleware
from functools import wraps
from flask import request, jsonify

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.environ.get('API_KEY'):
            return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Apply to endpoints
@app.route('/api/containers', methods=['GET'])
@require_api_key
def list_containers():
    # Implementation
```

#### Rate Limiting
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/containers')
@limiter.limit("10 per minute")
def list_containers():
    # Implementation
```

### Monitoring and Logging

#### Application Logging
```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler(
        'logs/docker_api.log', 
        maxBytes=10240000, 
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

#### Health Monitoring
```python
@app.route('/metrics')
def metrics():
    """Prometheus-compatible metrics endpoint."""
    return Response(
        generate_metrics(),
        mimetype='text/plain'
    )

def generate_metrics():
    """Generate Prometheus metrics."""
    metrics = []
    
    # Docker daemon status
    try:
        system_mgr.get_daemon_status()
        metrics.append('docker_daemon_up 1')
    except:
        metrics.append('docker_daemon_up 0')
    
    # Container counts
    try:
        info = system_mgr.get_system_info()
        metrics.append(f'docker_containers_total {info["containers"]}')
        metrics.append(f'docker_containers_running {info["containers_running"]}')
        metrics.append(f'docker_images_total {info["images"]}')
    except:
        pass
    
    return '\n'.join(metrics)
```

## Contributing

We welcome contributions to the Docker Management API project! Please follow these guidelines:

### Getting Started
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Code Standards
- Follow PEP 8 style guidelines
- Add type hints to all functions
- Include comprehensive docstrings
- Write unit tests for new features
- Update documentation as needed

### Pull Request Process
1. Ensure all tests pass
2. Update README.md with details of changes
3. Update version numbers if applicable
4. Request review from maintainers

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check existing documentation
- Review API endpoints at `/api/commands`

## Changelog

### Version 1.0.0
- Initial release
- Complete Docker management API
- Support for containers, images, volumes, networks
- System information and monitoring
- Comprehensive documentation
- Error handling and logging
- Health check endpoints

---

**Docker Management API** - Making Docker management accessible through REST APIs.



## Connecting Containers to the Local Docker Daemon

To enable containers to communicate with the Docker daemon running on the local machine, it is common to mount the Docker socket into the container. This allows the container to use the host’s Docker engine to manage containers, images, and other Docker resources.

### Mounting the Docker Socket

When running your container, mount the Docker socket file from the host into the container:

```bash
docker run -v /var/run/docker.sock:/var/run/docker.sock ...
```

This exposes the Docker daemon socket inside the container at the same path.

### Important: Matching the Docker Socket Group ID (GID)

The Docker socket on the host has specific ownership and permissions. For example:

```text
srw-rw---- 1 root 1001 0 Jul  3 15:34 /var/run/docker.sock
```

The socket is owned by user `root` (UID 0).

The group ID (GID) is `1001`.

To allow your container user to access the Docker socket without running as root, you must create a group inside the container with GID `1001` and add your user to this group.

#### Example Dockerfile snippet:

```text
# Create docker group with GID matching host's docker.sock group
RUN groupadd -g 1001 docker

# Add your user (replace 'appuser') to this group
RUN usermod -aG docker appuser
```

Running the container with socket access:

```bash
docker run -v /var/run/docker.sock:/var/run/docker.sock \
  --user appuser \
  your-image
```

### Why do this?

The Docker socket is a Unix socket with restricted permissions.

- Matching the GID ensures your container user can communicate with the Docker daemon securely.

- Avoids running containers as root while still allowing Docker control.

### Notes for Windows with Docker Desktop and WSL 2

On Windows, Docker Desktop runs the Docker daemon inside a special WSL 2 distro named `docker-desktop`.

The Docker socket file `/var/run/docker.sock` is inside that distro, not directly accessible in Windows filesystem.

To connect containers to the Docker daemon on Windows, mount the Docker named pipe instead:

```bash
docker run -v \\.\pipe\docker_engine:\\.\pipe\docker_engine ...
```

Enable Docker Desktop WSL integration for your WSL distro to use Docker CLI inside WSL.

#   D o c k e r - A P I  
 #   D o c k e r - A P I  
 