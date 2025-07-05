import docker
from typing import Dict, List, Any, Optional
import logging

class ContainerManager:
    """
    Manages Docker containers with operations like listing, starting, stopping, 
    restarting, removing containers, and getting container logs and details.
    """
    
    def __init__(self):
        """Initialize Docker client connection."""
        try:
            self.client = docker.from_env()
            # Test connection
            self.client.ping()
        except Exception as e:
            logging.error(f"Failed to connect to Docker daemon: {e}")
            raise ConnectionError("Cannot connect to Docker daemon. Make sure Docker is running.")
    
    def list_containers(self, all_containers: bool = False) -> List[Dict[str, Any]]:
        """
        List all containers (running by default, or all if specified).
        
        Args:
            all_containers (bool): If True, list all containers including stopped ones
            
        Returns:
            List[Dict]: List of container information dictionaries
        """
        try:
            containers = self.client.containers.list(all=all_containers)
            container_list = []
            
            for container in containers:
                container_info = {
                    'id': container.id[:12],  # Short ID
                    'name': container.name,
                    'image': container.image.tags[0] if container.image.tags else container.image.id[:12],
                    'status': container.status,
                    'created': container.attrs['Created'],
                    'ports': container.attrs.get('NetworkSettings', {}).get('Ports', {}),
                    'labels': container.labels
                }
                container_list.append(container_info)
            
            return container_list
        except Exception as e:
            logging.error(f"Error listing containers: {e}")
            raise Exception(f"Failed to list containers: {str(e)}")
    
    def get_container_details(self, container_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific container.
        
        Args:
            container_id (str): Container ID or name
            
        Returns:
            Dict: Detailed container information
        """
        try:
            container = self.client.containers.get(container_id)
            
            details = {
                'id': container.id,
                'name': container.name,
                'image': container.image.tags[0] if container.image.tags else container.image.id[:12],
                'status': container.status,
                'created': container.attrs['Created'],
                'started': container.attrs['State'].get('StartedAt'),
                'finished': container.attrs['State'].get('FinishedAt'),
                'exit_code': container.attrs['State'].get('ExitCode'),
                'ports': container.attrs.get('NetworkSettings', {}).get('Ports', {}),
                'networks': list(container.attrs.get('NetworkSettings', {}).get('Networks', {}).keys()),
                'mounts': [mount['Source'] + ':' + mount['Destination'] for mount in container.attrs.get('Mounts', [])],
                'environment': container.attrs['Config'].get('Env', []),
                'labels': container.labels,
                'command': container.attrs['Config'].get('Cmd'),
                'working_dir': container.attrs['Config'].get('WorkingDir'),
                'restart_policy': container.attrs['HostConfig'].get('RestartPolicy', {})
            }
            
            return details
        except docker.errors.NotFound:
            raise Exception(f"Container '{container_id}' not found")
        except Exception as e:
            logging.error(f"Error getting container details: {e}")
            raise Exception(f"Failed to get container details: {str(e)}")
    
    def start_container(self, container_id: str) -> Dict[str, str]:
        """
        Start a stopped container.
        
        Args:
            container_id (str): Container ID or name
            
        Returns:
            Dict: Success message with container info
        """
        try:
            container = self.client.containers.get(container_id)
            container.start()
            
            return {
                'message': f"Container '{container.name}' started successfully",
                'container_id': container.id[:12],
                'name': container.name,
                'status': 'started'
            }
        except docker.errors.NotFound:
            raise Exception(f"Container '{container_id}' not found")
        except docker.errors.APIError as e:
            if 'already started' in str(e).lower():
                raise Exception(f"Container '{container_id}' is already running")
            raise Exception(f"Failed to start container: {str(e)}")
        except Exception as e:
            logging.error(f"Error starting container: {e}")
            raise Exception(f"Failed to start container: {str(e)}")
    
    def stop_container(self, container_id: str, timeout: int = 10) -> Dict[str, str]:
        """
        Stop a running container.
        
        Args:
            container_id (str): Container ID or name
            timeout (int): Seconds to wait before killing the container
            
        Returns:
            Dict: Success message with container info
        """
        try:
            container = self.client.containers.get(container_id)
            container.stop(timeout=timeout)
            
            return {
                'message': f"Container '{container.name}' stopped successfully",
                'container_id': container.id[:12],
                'name': container.name,
                'status': 'stopped'
            }
        except docker.errors.NotFound:
            raise Exception(f"Container '{container_id}' not found")
        except docker.errors.APIError as e:
            if 'already stopped' in str(e).lower():
                raise Exception(f"Container '{container_id}' is already stopped")
            raise Exception(f"Failed to stop container: {str(e)}")
        except Exception as e:
            logging.error(f"Error stopping container: {e}")
            raise Exception(f"Failed to stop container: {str(e)}")
    
    def restart_container(self, container_id: str, timeout: int = 10) -> Dict[str, str]:
        """
        Restart a container.
        
        Args:
            container_id (str): Container ID or name
            timeout (int): Seconds to wait before killing the container
            
        Returns:
            Dict: Success message with container info
        """
        try:
            container = self.client.containers.get(container_id)
            container.restart(timeout=timeout)
            
            return {
                'message': f"Container '{container.name}' restarted successfully",
                'container_id': container.id[:12],
                'name': container.name,
                'status': 'restarted'
            }
        except docker.errors.NotFound:
            raise Exception(f"Container '{container_id}' not found")
        except Exception as e:
            logging.error(f"Error restarting container: {e}")
            raise Exception(f"Failed to restart container: {str(e)}")
    
    def remove_container(self, container_id: str, force: bool = False) -> Dict[str, str]:
        """
        Remove a container.
        
        Args:
            container_id (str): Container ID or name
            force (bool): Force removal of running container
            
        Returns:
            Dict: Success message with container info
        """
        try:
            container = self.client.containers.get(container_id)
            container_name = container.name
            container.remove(force=force)
            
            return {
                'message': f"Container '{container_name}' removed successfully",
                'container_id': container_id,
                'name': container_name,
                'status': 'removed'
            }
        except docker.errors.NotFound:
            raise Exception(f"Container '{container_id}' not found")
        except docker.errors.APIError as e:
            if 'cannot remove running container' in str(e).lower():
                raise Exception(f"Cannot remove running container '{container_id}'. Stop it first or use force=True")
            raise Exception(f"Failed to remove container: {str(e)}")
        except Exception as e:
            logging.error(f"Error removing container: {e}")
            raise Exception(f"Failed to remove container: {str(e)}")
    
    def get_container_logs(self, container_id: str, tail: int = 100, follow: bool = False) -> Dict[str, Any]:
        """
        Get logs from a container.
        
        Args:
            container_id (str): Container ID or name
            tail (int): Number of lines to show from the end of logs
            follow (bool): Follow log output (not recommended for API)
            
        Returns:
            Dict: Container logs and metadata
        """
        try:
            container = self.client.containers.get(container_id)
            logs = container.logs(tail=tail, follow=follow).decode('utf-8')
            
            return {
                'container_id': container.id[:12],
                'name': container.name,
                'logs': logs,
                'tail': tail,
                'timestamp': container.attrs['State'].get('StartedAt')
            }
        except docker.errors.NotFound:
            raise Exception(f"Container '{container_id}' not found")
        except Exception as e:
            logging.error(f"Error getting container logs: {e}")
            raise Exception(f"Failed to get container logs: {str(e)}")
    
    def create_container(self, image: str, name: Optional[str] = None, **kwargs) -> Dict[str, str]:
        """
        Create a new container from an image.
        
        Args:
            image (str): Docker image name
            name (str, optional): Container name
            **kwargs: Additional container creation parameters
            
        Returns:
            Dict: Created container information
        """
        try:
            container = self.client.containers.create(image, name=name, **kwargs)
            
            return {
                'message': f"Container created successfully",
                'container_id': container.id[:12],
                'name': container.name,
                'image': image,
                'status': 'created'
            }
        except docker.errors.ImageNotFound:
            raise Exception(f"Image '{image}' not found")
        except docker.errors.APIError as e:
            if 'already in use' in str(e).lower():
                raise Exception(f"Container name '{name}' is already in use")
            raise Exception(f"Failed to create container: {str(e)}")
        except Exception as e:
            logging.error(f"Error creating container: {e}")
            raise Exception(f"Failed to create container: {str(e)}")

