import docker
from typing import Dict, List, Any, Optional
import logging

class VolumeManager:
    """
    Manages Docker volumes with operations like listing, creating, removing volumes,
    and getting volume details and usage information.
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
    
    def list_volumes(self) -> List[Dict[str, Any]]:
        """
        List all volumes.
        
        Returns:
            List[Dict]: List of volume information dictionaries
        """
        try:
            volumes = self.client.volumes.list()
            volume_list = []
            
            for volume in volumes:
                volume_info = {
                    'name': volume.name,
                    'driver': volume.attrs.get('Driver', 'local'),
                    'mountpoint': volume.attrs.get('Mountpoint', ''),
                    'created': volume.attrs.get('CreatedAt', ''),
                    'scope': volume.attrs.get('Scope', 'local'),
                    'labels': volume.attrs.get('Labels') or {},
                    'options': volume.attrs.get('Options') or {},
                    'usage': self._get_volume_usage(volume.name)
                }
                volume_list.append(volume_info)
            
            return volume_list
        except Exception as e:
            logging.error(f"Error listing volumes: {e}")
            raise Exception(f"Failed to list volumes: {str(e)}")
    
    def get_volume_details(self, volume_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific volume.
        
        Args:
            volume_name (str): Volume name
            
        Returns:
            Dict: Detailed volume information
        """
        try:
            volume = self.client.volumes.get(volume_name)
            
            details = {
                'name': volume.name,
                'driver': volume.attrs.get('Driver', 'local'),
                'mountpoint': volume.attrs.get('Mountpoint', ''),
                'created': volume.attrs.get('CreatedAt', ''),
                'scope': volume.attrs.get('Scope', 'local'),
                'labels': volume.attrs.get('Labels') or {},
                'options': volume.attrs.get('Options') or {},
                'usage': self._get_volume_usage(volume_name),
                'containers_using': self._get_containers_using_volume(volume_name)
            }
            
            return details
        except docker.errors.NotFound:
            raise Exception(f"Volume '{volume_name}' not found")
        except Exception as e:
            logging.error(f"Error getting volume details: {e}")
            raise Exception(f"Failed to get volume details: {str(e)}")
    
    def create_volume(self, name: Optional[str] = None, driver: str = 'local', 
                     labels: Optional[Dict[str, str]] = None, 
                     options: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Create a new volume.
        
        Args:
            name (str, optional): Volume name (auto-generated if not provided)
            driver (str): Volume driver (default: 'local')
            labels (dict, optional): Labels to set on the volume
            options (dict, optional): Driver-specific options
            
        Returns:
            Dict: Created volume information
        """
        try:
            volume = self.client.volumes.create(
                name=name,
                driver=driver,
                labels=labels or {},
                driver_opts=options or {}
            )
            
            return {
                'message': f"Volume '{volume.name}' created successfully",
                'name': volume.name,
                'driver': volume.attrs.get('Driver', 'local'),
                'mountpoint': volume.attrs.get('Mountpoint', ''),
                'created': volume.attrs.get('CreatedAt', ''),
                'labels': volume.attrs.get('Labels') or {},
                'options': volume.attrs.get('Options') or {},
                'status': 'created'
            }
        except docker.errors.APIError as e:
            if 'already exists' in str(e).lower():
                raise Exception(f"Volume '{name}' already exists")
            raise Exception(f"Failed to create volume: {str(e)}")
        except Exception as e:
            logging.error(f"Error creating volume: {e}")
            raise Exception(f"Failed to create volume: {str(e)}")
    
    def remove_volume(self, volume_name: str, force: bool = False) -> Dict[str, str]:
        """
        Remove a volume.
        
        Args:
            volume_name (str): Volume name
            force (bool): Force removal of volume
            
        Returns:
            Dict: Removal operation result
        """
        try:
            volume = self.client.volumes.get(volume_name)
            volume.remove(force=force)
            
            return {
                'message': f"Volume '{volume_name}' removed successfully",
                'name': volume_name,
                'status': 'removed'
            }
        except docker.errors.NotFound:
            raise Exception(f"Volume '{volume_name}' not found")
        except docker.errors.APIError as e:
            if 'volume is in use' in str(e).lower():
                containers = self._get_containers_using_volume(volume_name)
                container_names = [c['name'] for c in containers]
                raise Exception(f"Cannot remove volume '{volume_name}' - it's being used by containers: {', '.join(container_names)}. Stop containers first or use force=True")
            raise Exception(f"Failed to remove volume: {str(e)}")
        except Exception as e:
            logging.error(f"Error removing volume: {e}")
            raise Exception(f"Failed to remove volume: {str(e)}")
    
    def prune_volumes(self) -> Dict[str, Any]:
        """
        Remove unused volumes.
        
        Returns:
            Dict: Prune operation result
        """
        try:
            result = self.client.volumes.prune()
            
            return {
                'message': 'Volume pruning completed',
                'volumes_deleted': result.get('VolumesDeleted', []),
                'space_reclaimed': self._format_size(result.get('SpaceReclaimed', 0)),
                'space_reclaimed_bytes': result.get('SpaceReclaimed', 0)
            }
        except Exception as e:
            logging.error(f"Error pruning volumes: {e}")
            raise Exception(f"Failed to prune volumes: {str(e)}")
    
    def inspect_volume(self, volume_name: str) -> Dict[str, Any]:
        """
        Inspect a volume (alias for get_volume_details).
        
        Args:
            volume_name (str): Volume name
            
        Returns:
            Dict: Volume inspection details
        """
        return self.get_volume_details(volume_name)
    
    def _get_volume_usage(self, volume_name: str) -> Dict[str, Any]:
        """
        Get volume usage information.
        
        Args:
            volume_name (str): Volume name
            
        Returns:
            Dict: Usage information
        """
        try:
            # Try to get volume usage from system df
            df_info = self.client.df()
            volumes_info = df_info.get('Volumes', [])
            
            for vol_info in volumes_info:
                if vol_info.get('Name') == volume_name:
                    return {
                        'size': self._format_size(vol_info.get('Size', 0)),
                        'size_bytes': vol_info.get('Size', 0),
                        'ref_count': vol_info.get('RefCount', 0)
                    }
            
            return {
                'size': 'Unknown',
                'size_bytes': 0,
                'ref_count': 0
            }
        except Exception:
            return {
                'size': 'Unknown',
                'size_bytes': 0,
                'ref_count': 0
            }
    
    def _get_containers_using_volume(self, volume_name: str) -> List[Dict[str, str]]:
        """
        Get list of containers using a specific volume.
        
        Args:
            volume_name (str): Volume name
            
        Returns:
            List[Dict]: List of containers using the volume
        """
        try:
            containers = self.client.containers.list(all=True)
            using_containers = []
            
            for container in containers:
                mounts = container.attrs.get('Mounts', [])
                for mount in mounts:
                    if mount.get('Type') == 'volume' and mount.get('Name') == volume_name:
                        using_containers.append({
                            'id': container.id[:12],
                            'name': container.name,
                            'status': container.status,
                            'mount_destination': mount.get('Destination', '')
                        })
                        break
            
            return using_containers
        except Exception:
            return []
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in bytes to human readable format."""
        if size_bytes == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def get_volume_stats(self) -> Dict[str, Any]:
        """
        Get overall volume statistics.
        
        Returns:
            Dict: Volume statistics
        """
        try:
            volumes = self.client.volumes.list()
            df_info = self.client.df()
            volumes_df = df_info.get('Volumes', [])
            
            total_size = sum(vol.get('Size', 0) for vol in volumes_df)
            total_count = len(volumes)
            
            # Count volumes by driver
            drivers = {}
            for volume in volumes:
                driver = volume.attrs.get('Driver', 'local')
                drivers[driver] = drivers.get(driver, 0) + 1
            
            return {
                'total_volumes': total_count,
                'total_size': self._format_size(total_size),
                'total_size_bytes': total_size,
                'drivers': drivers,
                'unused_volumes': len([vol for vol in volumes_df if vol.get('RefCount', 0) == 0])
            }
        except Exception as e:
            logging.error(f"Error getting volume stats: {e}")
            raise Exception(f"Failed to get volume statistics: {str(e)}")

