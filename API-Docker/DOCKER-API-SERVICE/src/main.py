import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import logging

# Import all manager classes
from src.container_manager import ContainerManager
from src.image_manager import ImageManager
from src.volume_manager import VolumeManager
from src.network_manager import NetworkManager
from src.system_manager import SystemManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'docker-management-api-secret-key'

# Enable CORS for all routes
CORS(app)

# Initialize manager instances
try:
    container_mgr = ContainerManager()
    image_mgr = ImageManager()
    volume_mgr = VolumeManager()
    network_mgr = NetworkManager()
    system_mgr = SystemManager()
    logger.info("All Docker managers initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Docker managers: {e}")
    container_mgr = image_mgr = volume_mgr = network_mgr = system_mgr = None

def handle_error(func):
    """Decorator to handle errors and return JSON responses."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            return jsonify({
                'error': str(e),
                'success': False
            }), 500
    wrapper.__name__ = func.__name__
    return wrapper

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        if system_mgr:
            daemon_status = system_mgr.get_daemon_status()
            return jsonify({
                'status': 'healthy',
                'docker_daemon': daemon_status.get('status', 'unknown'),
                'api_version': 'v1.0',
                'success': True
            })
        else:
            return jsonify({
                'status': 'unhealthy',
                'error': 'Docker managers not initialized',
                'success': False
            }), 503
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'success': False
        }), 503

# ============================================================================
# CONTAINER ENDPOINTS
# ============================================================================

@app.route('/api/containers', methods=['GET'])
@handle_error
def list_containers():
    """List all containers."""
    all_containers = request.args.get('all', 'false').lower() == 'true'
    containers = container_mgr.list_containers(all_containers=all_containers)
    return jsonify({
        'containers': containers,
        'count': len(containers),
        'success': True
    })

@app.route('/api/containers/<container_id>', methods=['GET'])
@handle_error
def get_container_details(container_id):
    """Get details of a specific container."""
    details = container_mgr.get_container_details(container_id)
    return jsonify({
        'container': details,
        'success': True
    })

@app.route('/api/containers/<container_id>/start', methods=['POST'])
@handle_error
def start_container(container_id):
    """Start a container."""
    result = container_mgr.start_container(container_id)
    return jsonify({
        'result': result,
        'success': True
    })

@app.route('/api/containers/<container_id>/stop', methods=['POST'])
@handle_error
def stop_container(container_id):
    """Stop a container."""
    timeout = request.json.get('timeout', 10) if request.json else 10
    result = container_mgr.stop_container(container_id, timeout=timeout)
    return jsonify({
        'result': result,
        'success': True
    })

@app.route('/api/containers/<container_id>/restart', methods=['POST'])
@handle_error
def restart_container(container_id):
    """Restart a container."""
    timeout = request.json.get('timeout', 10) if request.json else 10
    result = container_mgr.restart_container(container_id, timeout=timeout)
    return jsonify({
        'result': result,
        'success': True
    })

@app.route('/api/containers/<container_id>/remove', methods=['DELETE'])
@handle_error
def remove_container(container_id):
    """Remove a container."""
    force = request.args.get('force', 'false').lower() == 'true'
    result = container_mgr.remove_container(container_id, force=force)
    return jsonify({
        'result': result,
        'success': True
    })

@app.route('/api/containers/<container_id>/logs', methods=['GET'])
@handle_error
def get_container_logs(container_id):
    """Get container logs."""
    tail = int(request.args.get('tail', 100))
    logs = container_mgr.get_container_logs(container_id, tail=tail)
    return jsonify({
        'logs': logs,
        'success': True
    })

@app.route('/api/containers', methods=['POST'])
@handle_error
def create_container():
    """Create a new container."""
    data = request.json
    if not data or 'image' not in data:
        return jsonify({
            'error': 'Image name is required',
            'success': False
        }), 400
    
    image = data['image']
    name = data.get('name')
    
    # Remove known parameters and pass the rest as kwargs
    kwargs = {k: v for k, v in data.items() if k not in ['image', 'name']}
    
    result = container_mgr.create_container(image, name=name, **kwargs)
    return jsonify({
        'result': result,
        'success': True
    }), 201

# ============================================================================
# IMAGE ENDPOINTS
# ============================================================================

@app.route('/api/images', methods=['GET'])
@handle_error
def list_images():
    """List all images."""
    all_images = request.args.get('all', 'false').lower() == 'true'
    images = image_mgr.list_images(all_images=all_images)
    return jsonify({
        'images': images,
        'count': len(images),
        'success': True
    })

@app.route('/api/images/<path:image_id>', methods=['GET'])
@handle_error
def get_image_details(image_id):
    """Get details of a specific image."""
    details = image_mgr.get_image_details(image_id)
    return jsonify({
        'image': details,
        'success': True
    })

@app.route('/api/images/pull', methods=['POST'])
@handle_error
def pull_image():
    """Pull an image from registry."""
    data = request.json
    if not data or 'image' not in data:
        return jsonify({
            'error': 'Image name is required',
            'success': False
        }), 400
    
    image_name = data['image']
    tag = data.get('tag', 'latest')
    
    result = image_mgr.pull_image(image_name, tag=tag)
    return jsonify({
        'result': result,
        'success': True
    })

@app.route('/api/images/<path:image_id>/remove', methods=['DELETE'])
@handle_error
def remove_image(image_id):
    """Remove an image."""
    force = request.args.get('force', 'false').lower() == 'true'
    no_prune = request.args.get('no_prune', 'false').lower() == 'true'
    result = image_mgr.remove_image(image_id, force=force, no_prune=no_prune)
    return jsonify({
        'result': result,
        'success': True
    })

@app.route('/api/images/build', methods=['POST'])
@handle_error
def build_image():
    """Build an image from Dockerfile."""
    data = request.json
    if not data or 'path' not in data:
        return jsonify({
            'error': 'Build path is required',
            'success': False
        }), 400
    
    path = data['path']
    tag = data.get('tag')
    dockerfile = data.get('dockerfile', 'Dockerfile')
    
    # Remove known parameters and pass the rest as kwargs
    kwargs = {k: v for k, v in data.items() if k not in ['path', 'tag', 'dockerfile']}
    
    result = image_mgr.build_image(path, tag=tag, dockerfile=dockerfile, **kwargs)
    return jsonify({
        'result': result,
        'success': True
    })

@app.route('/api/images/search', methods=['GET'])
@handle_error
def search_images():
    """Search for images in Docker Hub."""
    term = request.args.get('term')
    if not term:
        return jsonify({
            'error': 'Search term is required',
            'success': False
        }), 400
    
    limit = int(request.args.get('limit', 25))
    results = image_mgr.search_images(term, limit=limit)
    return jsonify({
        'results': results,
        'count': len(results),
        'success': True
    })

@app.route('/api/images/prune', methods=['POST'])
@handle_error
def prune_images():
    """Remove unused images."""
    dangling_only = request.args.get('dangling_only', 'true').lower() == 'true'
    result = image_mgr.prune_images(dangling_only=dangling_only)
    return jsonify({
        'result': result,
        'success': True
    })

# ============================================================================
# VOLUME ENDPOINTS
# ============================================================================

@app.route('/api/volumes', methods=['GET'])
@handle_error
def list_volumes():
    """List all volumes."""
    volumes = volume_mgr.list_volumes()
    return jsonify({
        'volumes': volumes,
        'count': len(volumes),
        'success': True
    })

@app.route('/api/volumes/<volume_name>', methods=['GET'])
@handle_error
def get_volume_details(volume_name):
    """Get details of a specific volume."""
    details = volume_mgr.get_volume_details(volume_name)
    return jsonify({
        'volume': details,
        'success': True
    })

@app.route('/api/volumes', methods=['POST'])
@handle_error
def create_volume():
    """Create a new volume."""
    data = request.json or {}
    
    name = data.get('name')
    driver = data.get('driver', 'local')
    labels = data.get('labels')
    options = data.get('options')
    
    result = volume_mgr.create_volume(name=name, driver=driver, labels=labels, options=options)
    return jsonify({
        'result': result,
        'success': True
    }), 201

@app.route('/api/volumes/<volume_name>/remove', methods=['DELETE'])
@handle_error
def remove_volume(volume_name):
    """Remove a volume."""
    force = request.args.get('force', 'false').lower() == 'true'
    result = volume_mgr.remove_volume(volume_name, force=force)
    return jsonify({
        'result': result,
        'success': True
    })

@app.route('/api/volumes/prune', methods=['POST'])
@handle_error
def prune_volumes():
    """Remove unused volumes."""
    result = volume_mgr.prune_volumes()
    return jsonify({
        'result': result,
        'success': True
    })

@app.route('/api/volumes/stats', methods=['GET'])
@handle_error
def get_volume_stats():
    """Get volume statistics."""
    stats = volume_mgr.get_volume_stats()
    return jsonify({
        'stats': stats,
        'success': True
    })

# ============================================================================
# NETWORK ENDPOINTS
# ============================================================================

@app.route('/api/networks', methods=['GET'])
@handle_error
def list_networks():
    """List all networks."""
    networks = network_mgr.list_networks()
    return jsonify({
        'networks': networks,
        'count': len(networks),
        'success': True
    })

@app.route('/api/networks/<network_id>', methods=['GET'])
@handle_error
def get_network_details(network_id):
    """Get details of a specific network."""
    details = network_mgr.get_network_details(network_id)
    return jsonify({
        'network': details,
        'success': True
    })

@app.route('/api/networks', methods=['POST'])
@handle_error
def create_network():
    """Create a new network."""
    data = request.json
    if not data or 'name' not in data:
        return jsonify({
            'error': 'Network name is required',
            'success': False
        }), 400
    
    name = data['name']
    driver = data.get('driver', 'bridge')
    internal = data.get('internal', False)
    attachable = data.get('attachable', False)
    labels = data.get('labels')
    options = data.get('options')
    ipam = data.get('ipam')
    
    result = network_mgr.create_network(
        name=name, driver=driver, internal=internal, 
        attachable=attachable, labels=labels, options=options, ipam=ipam
    )
    return jsonify({
        'result': result,
        'success': True
    }), 201

@app.route('/api/networks/<network_id>/remove', methods=['DELETE'])
@handle_error
def remove_network(network_id):
    """Remove a network."""
    result = network_mgr.remove_network(network_id)
    return jsonify({
        'result': result,
        'success': True
    })

@app.route('/api/networks/<network_id>/connect', methods=['POST'])
@handle_error
def connect_container_to_network(network_id):
    """Connect a container to a network."""
    data = request.json
    if not data or 'container' not in data:
        return jsonify({
            'error': 'Container ID is required',
            'success': False
        }), 400
    
    container_id = data['container']
    aliases = data.get('aliases')
    ipv4_address = data.get('ipv4_address')
    ipv6_address = data.get('ipv6_address')
    
    result = network_mgr.connect_container(
        network_id, container_id, aliases=aliases, 
        ipv4_address=ipv4_address, ipv6_address=ipv6_address
    )
    return jsonify({
        'result': result,
        'success': True
    })

@app.route('/api/networks/<network_id>/disconnect', methods=['POST'])
@handle_error
def disconnect_container_from_network(network_id):
    """Disconnect a container from a network."""
    data = request.json
    if not data or 'container' not in data:
        return jsonify({
            'error': 'Container ID is required',
            'success': False
        }), 400
    
    container_id = data['container']
    force = data.get('force', False)
    
    result = network_mgr.disconnect_container(network_id, container_id, force=force)
    return jsonify({
        'result': result,
        'success': True
    })

@app.route('/api/networks/prune', methods=['POST'])
@handle_error
def prune_networks():
    """Remove unused networks."""
    result = network_mgr.prune_networks()
    return jsonify({
        'result': result,
        'success': True
    })

@app.route('/api/networks/stats', methods=['GET'])
@handle_error
def get_network_stats():
    """Get network statistics."""
    stats = network_mgr.get_network_stats()
    return jsonify({
        'stats': stats,
        'success': True
    })

# ============================================================================
# SYSTEM ENDPOINTS
# ============================================================================

@app.route('/api/system/version', methods=['GET'])
@handle_error
def get_docker_version():
    """Get Docker version information."""
    version = system_mgr.get_docker_version()
    return jsonify({
        'version': version,
        'success': True
    })

@app.route('/api/system/info', methods=['GET'])
@handle_error
def get_system_info():
    """Get Docker system information."""
    info = system_mgr.get_system_info()
    return jsonify({
        'info': info,
        'success': True
    })

@app.route('/api/system/df', methods=['GET'])
@handle_error
def get_disk_usage():
    """Get Docker disk usage information."""
    usage = system_mgr.get_disk_usage()
    return jsonify({
        'usage': usage,
        'success': True
    })

@app.route('/api/system/status', methods=['GET'])
@handle_error
def get_daemon_status():
    """Get Docker daemon status."""
    status = system_mgr.get_daemon_status()
    return jsonify({
        'status': status,
        'success': True
    })

@app.route('/api/system/stats', methods=['GET'])
@handle_error
def get_overall_statistics():
    """Get overall Docker statistics."""
    stats = system_mgr.get_overall_statistics()
    return jsonify({
        'stats': stats,
        'success': True
    })

@app.route('/api/system/host', methods=['GET'])
@handle_error
def get_host_system_info():
    """Get host system information."""
    host_info = system_mgr.get_host_system_info()
    return jsonify({
        'host': host_info,
        'success': True
    })

# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.route('/api/commands', methods=['GET'])
def get_available_commands():
    """Get list of available Docker commands and their descriptions."""
    commands = {
        'containers': {
            'list': 'GET /api/containers - List all containers (add ?all=true for all)',
            'details': 'GET /api/containers/{id} - Get container details',
            'create': 'POST /api/containers - Create new container',
            'start': 'POST /api/containers/{id}/start - Start container',
            'stop': 'POST /api/containers/{id}/stop - Stop container',
            'restart': 'POST /api/containers/{id}/restart - Restart container',
            'remove': 'DELETE /api/containers/{id}/remove - Remove container',
            'logs': 'GET /api/containers/{id}/logs - Get container logs'
        },
        'images': {
            'list': 'GET /api/images - List all images',
            'details': 'GET /api/images/{id} - Get image details',
            'pull': 'POST /api/images/pull - Pull image from registry',
            'build': 'POST /api/images/build - Build image from Dockerfile',
            'remove': 'DELETE /api/images/{id}/remove - Remove image',
            'search': 'GET /api/images/search?term={term} - Search Docker Hub',
            'prune': 'POST /api/images/prune - Remove unused images'
        },
        'volumes': {
            'list': 'GET /api/volumes - List all volumes',
            'details': 'GET /api/volumes/{name} - Get volume details',
            'create': 'POST /api/volumes - Create new volume',
            'remove': 'DELETE /api/volumes/{name}/remove - Remove volume',
            'prune': 'POST /api/volumes/prune - Remove unused volumes',
            'stats': 'GET /api/volumes/stats - Get volume statistics'
        },
        'networks': {
            'list': 'GET /api/networks - List all networks',
            'details': 'GET /api/networks/{id} - Get network details',
            'create': 'POST /api/networks - Create new network',
            'remove': 'DELETE /api/networks/{id}/remove - Remove network',
            'connect': 'POST /api/networks/{id}/connect - Connect container to network',
            'disconnect': 'POST /api/networks/{id}/disconnect - Disconnect container from network',
            'prune': 'POST /api/networks/prune - Remove unused networks',
            'stats': 'GET /api/networks/stats - Get network statistics'
        },
        'system': {
            'version': 'GET /api/system/version - Get Docker version',
            'info': 'GET /api/system/info - Get system information',
            'df': 'GET /api/system/df - Get disk usage',
            'status': 'GET /api/system/status - Get daemon status',
            'stats': 'GET /api/system/stats - Get overall statistics',
            'host': 'GET /api/system/host - Get host system info'
        }
    }
    
    return jsonify({
        'commands': commands,
        'base_url': request.base_url.replace('/api/commands', ''),
        'success': True
    })

# Static file serving (for frontend if needed)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return jsonify({
            'message': 'Docker Management API',
            'version': '1.0',
            'endpoints': '/api/commands',
            'health': '/health'
        })

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return jsonify({
                'message': 'Docker Management API',
                'version': '1.0',
                'endpoints': '/api/commands',
                'health': '/health'
            })

if __name__ == '__main__':
    print("Starting Docker Management API...")
    print("API Documentation: http://localhost:5000/api/commands")
    print("Health Check: http://localhost:5000/health")
    app.run(host='0.0.0.0', port=5000, debug=True)

