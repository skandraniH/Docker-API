import docker
from typing import Dict, List, Any
import logging
import platform
import psutil

class SystemManager:
    """
    Manages Docker system information including Docker version, system info, 
    disk usage, and monitoring Docker daemon status.
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
    
    def get_docker_version(self) -> Dict[str, Any]:
        """
        Get Docker version information.
        
        Returns:
            Dict: Docker version details
        """
        try:
            version_info = self.client.version()
            
            return {
                'version': version_info.get('Version', 'unknown'),
                'api_version': version_info.get('ApiVersion', 'unknown'),
                'min_api_version': version_info.get('MinAPIVersion', 'unknown'),
                'git_commit': version_info.get('GitCommit', 'unknown'),
                'go_version': version_info.get('GoVersion', 'unknown'),
                'os': version_info.get('Os', 'unknown'),
                'arch': version_info.get('Arch', 'unknown'),
                'kernel_version': version_info.get('KernelVersion', 'unknown'),
                'build_time': version_info.get('BuildTime', 'unknown'),
                'experimental': version_info.get('Experimental', False)
            }
        except Exception as e:
            logging.error(f"Error getting Docker version: {e}")
            raise Exception(f"Failed to get Docker version: {str(e)}")
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get Docker system information.
        
        Returns:
            Dict: System information
        """
        try:
            info = self.client.info()
            
            system_info = {
                'containers': info.get('Containers', 0),
                'containers_running': info.get('ContainersRunning', 0),
                'containers_paused': info.get('ContainersPaused', 0),
                'containers_stopped': info.get('ContainersStopped', 0),
                'images': info.get('Images', 0),
                'server_version': info.get('ServerVersion', 'unknown'),
                'storage_driver': info.get('Driver', 'unknown'),
                'logging_driver': info.get('LoggingDriver', 'unknown'),
                'cgroup_driver': info.get('CgroupDriver', 'unknown'),
                'cgroup_version': info.get('CgroupVersion', 'unknown'),
                'kernel_version': info.get('KernelVersion', 'unknown'),
                'operating_system': info.get('OperatingSystem', 'unknown'),
                'os_type': info.get('OSType', 'unknown'),
                'architecture': info.get('Architecture', 'unknown'),
                'ncpu': info.get('NCPU', 0),
                'mem_total': self._format_size(info.get('MemTotal', 0)),
                'mem_total_bytes': info.get('MemTotal', 0),
                'docker_root_dir': info.get('DockerRootDir', 'unknown'),
                'http_proxy': info.get('HttpProxy', ''),
                'https_proxy': info.get('HttpsProxy', ''),
                'no_proxy': info.get('NoProxy', ''),
                'name': info.get('Name', 'unknown'),
                'labels': info.get('Labels') or [],
                'experimental_build': info.get('ExperimentalBuild', False),
                'live_restore_enabled': info.get('LiveRestoreEnabled', False),
                'default_runtime': info.get('DefaultRuntime', 'unknown'),
                'runtimes': list(info.get('Runtimes', {}).keys()),
                'swarm': self._format_swarm_info(info.get('Swarm', {})),
                'plugins': self._format_plugins_info(info.get('Plugins', {}))
            }
            
            return system_info
        except Exception as e:
            logging.error(f"Error getting system info: {e}")
            raise Exception(f"Failed to get system info: {str(e)}")
    
    def get_disk_usage(self) -> Dict[str, Any]:
        """
        Get Docker disk usage information.
        
        Returns:
            Dict: Disk usage details
        """
        try:
            df_info = self.client.df()
            
            # Process containers
            containers_info = df_info.get('Containers', [])
            containers_size = sum(c.get('SizeRw', 0) + c.get('SizeRootFs', 0) for c in containers_info)
            
            # Process images
            images_info = df_info.get('Images', [])
            images_size = sum(img.get('Size', 0) for img in images_info)
            images_shared_size = sum(img.get('SharedSize', 0) for img in images_info)
            
            # Process volumes
            volumes_info = df_info.get('Volumes', [])
            volumes_size = sum(vol.get('Size', 0) for vol in volumes_info)
            
            # Process build cache
            build_cache_info = df_info.get('BuildCache', [])
            build_cache_size = sum(cache.get('Size', 0) for cache in build_cache_info)
            
            return {
                'containers': {
                    'count': len(containers_info),
                    'size': self._format_size(containers_size),
                    'size_bytes': containers_size,
                    'reclaimable': self._format_size(sum(c.get('SizeRw', 0) for c in containers_info if c.get('State') != 'running')),
                    'reclaimable_bytes': sum(c.get('SizeRw', 0) for c in containers_info if c.get('State') != 'running')
                },
                'images': {
                    'count': len(images_info),
                    'size': self._format_size(images_size),
                    'size_bytes': images_size,
                    'shared_size': self._format_size(images_shared_size),
                    'shared_size_bytes': images_shared_size,
                    'reclaimable': self._format_size(sum(img.get('Size', 0) for img in images_info if not img.get('Containers', 0))),
                    'reclaimable_bytes': sum(img.get('Size', 0) for img in images_info if not img.get('Containers', 0))
                },
                'volumes': {
                    'count': len(volumes_info),
                    'size': self._format_size(volumes_size),
                    'size_bytes': volumes_size,
                    'reclaimable': self._format_size(sum(vol.get('Size', 0) for vol in volumes_info if vol.get('RefCount', 0) == 0)),
                    'reclaimable_bytes': sum(vol.get('Size', 0) for vol in volumes_info if vol.get('RefCount', 0) == 0)
                },
                'build_cache': {
                    'count': len(build_cache_info),
                    'size': self._format_size(build_cache_size),
                    'size_bytes': build_cache_size,
                    'reclaimable': self._format_size(build_cache_size),
                    'reclaimable_bytes': build_cache_size
                },
                'total': {
                    'size': self._format_size(containers_size + images_size + volumes_size + build_cache_size),
                    'size_bytes': containers_size + images_size + volumes_size + build_cache_size
                }
            }
        except Exception as e:
            logging.error(f"Error getting disk usage: {e}")
            raise Exception(f"Failed to get disk usage: {str(e)}")
    
    def get_daemon_status(self) -> Dict[str, Any]:
        """
        Get Docker daemon status and health information.
        
        Returns:
            Dict: Daemon status
        """
        try:
            # Test if daemon is responsive
            ping_result = self.client.ping()
            
            # Get basic info
            info = self.client.info()
            version = self.client.version()
            
            return {
                'status': 'running',
                'ping': ping_result,
                'server_version': version.get('Version', 'unknown'),
                'api_version': version.get('ApiVersion', 'unknown'),
                'containers_running': info.get('ContainersRunning', 0),
                'containers_total': info.get('Containers', 0),
                'images_total': info.get('Images', 0),
                'storage_driver': info.get('Driver', 'unknown'),
                'logging_driver': info.get('LoggingDriver', 'unknown'),
                'warnings': info.get('Warnings') or [],
                'experimental': info.get('ExperimentalBuild', False),
                'live_restore': info.get('LiveRestoreEnabled', False)
            }
        except Exception as e:
            logging.error(f"Error getting daemon status: {e}")
            return {
                'status': 'not_running',
                'error': str(e),
                'ping': False
            }
    
    def get_overall_statistics(self) -> Dict[str, Any]:
        """
        Get overall Docker statistics summary.
        
        Returns:
            Dict: Overall statistics
        """
        try:
            info = self.client.info()
            df_info = self.client.df()
            
            # Calculate totals
            total_containers = info.get('Containers', 0)
            running_containers = info.get('ContainersRunning', 0)
            stopped_containers = info.get('ContainersStopped', 0)
            paused_containers = info.get('ContainersPaused', 0)
            
            total_images = info.get('Images', 0)
            
            volumes_info = df_info.get('Volumes', [])
            total_volumes = len(volumes_info)
            
            networks = self.client.networks.list()
            total_networks = len(networks)
            
            # Calculate disk usage
            containers_size = sum(c.get('SizeRw', 0) + c.get('SizeRootFs', 0) for c in df_info.get('Containers', []))
            images_size = sum(img.get('Size', 0) for img in df_info.get('Images', []))
            volumes_size = sum(vol.get('Size', 0) for vol in volumes_info)
            
            return {
                'containers': {
                    'total': total_containers,
                    'running': running_containers,
                    'stopped': stopped_containers,
                    'paused': paused_containers,
                    'disk_usage': self._format_size(containers_size)
                },
                'images': {
                    'total': total_images,
                    'disk_usage': self._format_size(images_size)
                },
                'volumes': {
                    'total': total_volumes,
                    'disk_usage': self._format_size(volumes_size)
                },
                'networks': {
                    'total': total_networks
                },
                'system': {
                    'docker_version': info.get('ServerVersion', 'unknown'),
                    'storage_driver': info.get('Driver', 'unknown'),
                    'total_disk_usage': self._format_size(containers_size + images_size + volumes_size),
                    'cpu_count': info.get('NCPU', 0),
                    'memory_total': self._format_size(info.get('MemTotal', 0))
                }
            }
        except Exception as e:
            logging.error(f"Error getting overall statistics: {e}")
            raise Exception(f"Failed to get overall statistics: {str(e)}")
    
    def get_host_system_info(self) -> Dict[str, Any]:
        """
        Get host system information (non-Docker specific).
        
        Returns:
            Dict: Host system information
        """
        try:
            return {
                'platform': platform.platform(),
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'python_version': platform.python_version(),
                'cpu_count': psutil.cpu_count(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory': {
                    'total': self._format_size(psutil.virtual_memory().total),
                    'available': self._format_size(psutil.virtual_memory().available),
                    'percent': psutil.virtual_memory().percent,
                    'used': self._format_size(psutil.virtual_memory().used),
                    'free': self._format_size(psutil.virtual_memory().free)
                },
                'disk': {
                    'total': self._format_size(psutil.disk_usage('/').total),
                    'used': self._format_size(psutil.disk_usage('/').used),
                    'free': self._format_size(psutil.disk_usage('/').free),
                    'percent': psutil.disk_usage('/').percent
                }
            }
        except Exception as e:
            logging.error(f"Error getting host system info: {e}")
            raise Exception(f"Failed to get host system info: {str(e)}")
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in bytes to human readable format."""
        if size_bytes == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def _format_swarm_info(self, swarm_info: Dict[str, Any]) -> Dict[str, Any]:
        """Format Swarm information."""
        try:
            return {
                'node_id': swarm_info.get('NodeID', ''),
                'node_addr': swarm_info.get('NodeAddr', ''),
                'local_node_state': swarm_info.get('LocalNodeState', 'inactive'),
                'control_available': swarm_info.get('ControlAvailable', False),
                'error': swarm_info.get('Error', ''),
                'remote_managers': swarm_info.get('RemoteManagers', [])
            }
        except Exception:
            return {
                'node_id': '',
                'node_addr': '',
                'local_node_state': 'inactive',
                'control_available': False,
                'error': '',
                'remote_managers': []
            }
    
    def _format_plugins_info(self, plugins_info: Dict[str, Any]) -> Dict[str, List[str]]:
        """Format plugins information."""
        try:
            return {
                'volume': [p.get('Name', '') for p in plugins_info.get('Volume', [])],
                'network': [p.get('Name', '') for p in plugins_info.get('Network', [])],
                'authorization': [p.get('Name', '') for p in plugins_info.get('Authorization', [])],
                'log': [p.get('Name', '') for p in plugins_info.get('Log', [])]
            }
        except Exception:
            return {
                'volume': [],
                'network': [],
                'authorization': [],
                'log': []
            }

