import docker
from typing import Dict, List, Any, Optional
import logging

class ImageManager:
    """
    Manages Docker images with operations like listing, pulling, removing, 
    building images, and getting image details and size information.
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
    
    def list_images(self, all_images: bool = False) -> List[Dict[str, Any]]:
        """
        List all images.
        
        Args:
            all_images (bool): If True, list all images including intermediate ones
            
        Returns:
            List[Dict]: List of image information dictionaries
        """
        try:
            images = self.client.images.list(all=all_images)
            image_list = []
            
            for image in images:
                # Handle images without tags (dangling images)
                tags = image.tags if image.tags else ['<none>:<none>']
                
                image_info = {
                    'id': image.id.split(':')[1][:12],  # Short ID
                    'tags': tags,
                    'repository': tags[0].split(':')[0] if ':' in tags[0] else tags[0],
                    'tag': tags[0].split(':')[1] if ':' in tags[0] else 'latest',
                    'created': image.attrs['Created'],
                    'size': self._format_size(image.attrs['Size']),
                    'size_bytes': image.attrs['Size'],
                    'virtual_size': self._format_size(image.attrs.get('VirtualSize', image.attrs['Size'])),
                    'labels': image.attrs['Config'].get('Labels') or {},
                    'architecture': image.attrs.get('Architecture', 'unknown'),
                    'os': image.attrs.get('Os', 'unknown')
                }
                image_list.append(image_info)
            
            return image_list
        except Exception as e:
            logging.error(f"Error listing images: {e}")
            raise Exception(f"Failed to list images: {str(e)}")
    
    def get_image_details(self, image_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific image.
        
        Args:
            image_id (str): Image ID, name, or tag
            
        Returns:
            Dict: Detailed image information
        """
        try:
            image = self.client.images.get(image_id)
            
            details = {
                'id': image.id,
                'tags': image.tags,
                'created': image.attrs['Created'],
                'size': self._format_size(image.attrs['Size']),
                'size_bytes': image.attrs['Size'],
                'virtual_size': self._format_size(image.attrs.get('VirtualSize', image.attrs['Size'])),
                'architecture': image.attrs.get('Architecture', 'unknown'),
                'os': image.attrs.get('Os', 'unknown'),
                'docker_version': image.attrs.get('DockerVersion'),
                'author': image.attrs.get('Author', ''),
                'config': {
                    'cmd': image.attrs['Config'].get('Cmd'),
                    'entrypoint': image.attrs['Config'].get('Entrypoint'),
                    'env': image.attrs['Config'].get('Env', []),
                    'exposed_ports': list(image.attrs['Config'].get('ExposedPorts', {}).keys()),
                    'labels': image.attrs['Config'].get('Labels') or {},
                    'user': image.attrs['Config'].get('User', ''),
                    'working_dir': image.attrs['Config'].get('WorkingDir', ''),
                    'volumes': list(image.attrs['Config'].get('Volumes', {}).keys())
                },
                'history': self._get_image_history(image_id)
            }
            
            return details
        except docker.errors.ImageNotFound:
            raise Exception(f"Image '{image_id}' not found")
        except Exception as e:
            logging.error(f"Error getting image details: {e}")
            raise Exception(f"Failed to get image details: {str(e)}")
    
    def pull_image(self, image_name: str, tag: str = 'latest') -> Dict[str, Any]:
        """
        Pull an image from a registry.
        
        Args:
            image_name (str): Image name (e.g., 'nginx', 'ubuntu')
            tag (str): Image tag (default: 'latest')
            
        Returns:
            Dict: Pull operation result
        """
        try:
            full_image_name = f"{image_name}:{tag}"
            image = self.client.images.pull(image_name, tag=tag)
            
            return {
                'message': f"Image '{full_image_name}' pulled successfully",
                'image_id': image.id.split(':')[1][:12],
                'tags': image.tags,
                'size': self._format_size(image.attrs['Size']),
                'status': 'pulled'
            }
        except docker.errors.ImageNotFound:
            raise Exception(f"Image '{image_name}:{tag}' not found in registry")
        except docker.errors.APIError as e:
            raise Exception(f"Failed to pull image: {str(e)}")
        except Exception as e:
            logging.error(f"Error pulling image: {e}")
            raise Exception(f"Failed to pull image: {str(e)}")
    
    def remove_image(self, image_id: str, force: bool = False, no_prune: bool = False) -> Dict[str, str]:
        """
        Remove an image.
        
        Args:
            image_id (str): Image ID, name, or tag
            force (bool): Force removal of image
            no_prune (bool): Do not delete untagged parent images
            
        Returns:
            Dict: Removal operation result
        """
        try:
            image = self.client.images.get(image_id)
            image_tags = image.tags.copy() if image.tags else ['<none>:<none>']
            
            self.client.images.remove(image_id, force=force, noprune=no_prune)
            
            return {
                'message': f"Image removed successfully",
                'image_id': image_id,
                'tags': image_tags,
                'status': 'removed'
            }
        except docker.errors.ImageNotFound:
            raise Exception(f"Image '{image_id}' not found")
        except docker.errors.APIError as e:
            if 'image is being used' in str(e).lower():
                raise Exception(f"Cannot remove image '{image_id}' - it's being used by containers. Use force=True or stop containers first")
            raise Exception(f"Failed to remove image: {str(e)}")
        except Exception as e:
            logging.error(f"Error removing image: {e}")
            raise Exception(f"Failed to remove image: {str(e)}")
    
    def build_image(self, path: str, tag: Optional[str] = None, dockerfile: str = 'Dockerfile', **kwargs) -> Dict[str, Any]:
        """
        Build an image from a Dockerfile.
        
        Args:
            path (str): Path to build context
            tag (str, optional): Tag for the built image
            dockerfile (str): Name of Dockerfile (default: 'Dockerfile')
            **kwargs: Additional build parameters
            
        Returns:
            Dict: Build operation result
        """
        try:
            image, build_logs = self.client.images.build(
                path=path,
                tag=tag,
                dockerfile=dockerfile,
                **kwargs
            )
            
            # Extract build logs
            logs = []
            for log in build_logs:
                if 'stream' in log:
                    logs.append(log['stream'].strip())
            
            return {
                'message': f"Image built successfully",
                'image_id': image.id.split(':')[1][:12],
                'tags': image.tags,
                'size': self._format_size(image.attrs['Size']),
                'build_logs': logs[-10:],  # Last 10 log lines
                'status': 'built'
            }
        except docker.errors.BuildError as e:
            raise Exception(f"Build failed: {str(e)}")
        except docker.errors.APIError as e:
            raise Exception(f"Failed to build image: {str(e)}")
        except Exception as e:
            logging.error(f"Error building image: {e}")
            raise Exception(f"Failed to build image: {str(e)}")
    
    def search_images(self, term: str, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Search for images in Docker Hub.
        
        Args:
            term (str): Search term
            limit (int): Maximum number of results
            
        Returns:
            List[Dict]: Search results
        """
        try:
            results = self.client.images.search(term, limit=limit)
            
            search_results = []
            for result in results:
                search_info = {
                    'name': result['name'],
                    'description': result.get('description', ''),
                    'stars': result.get('star_count', 0),
                    'official': result.get('is_official', False),
                    'automated': result.get('is_automated', False)
                }
                search_results.append(search_info)
            
            return search_results
        except Exception as e:
            logging.error(f"Error searching images: {e}")
            raise Exception(f"Failed to search images: {str(e)}")
    
    def prune_images(self, dangling_only: bool = True) -> Dict[str, Any]:
        """
        Remove unused images.
        
        Args:
            dangling_only (bool): Only remove dangling images (default: True)
            
        Returns:
            Dict: Prune operation result
        """
        try:
            filters = {'dangling': True} if dangling_only else {}
            result = self.client.images.prune(filters=filters)
            
            return {
                'message': 'Image pruning completed',
                'images_deleted': result.get('ImagesDeleted', []),
                'space_reclaimed': self._format_size(result.get('SpaceReclaimed', 0)),
                'space_reclaimed_bytes': result.get('SpaceReclaimed', 0)
            }
        except Exception as e:
            logging.error(f"Error pruning images: {e}")
            raise Exception(f"Failed to prune images: {str(e)}")
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in bytes to human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    
    def _get_image_history(self, image_id: str) -> List[Dict[str, Any]]:
        """Get image layer history."""
        try:
            history = self.client.api.history(image_id)
            formatted_history = []
            
            for layer in history[:5]:  # Limit to first 5 layers
                layer_info = {
                    'id': layer.get('Id', '<missing>')[:12],
                    'created': layer.get('Created'),
                    'created_by': layer.get('CreatedBy', '')[:100] + '...' if len(layer.get('CreatedBy', '')) > 100 else layer.get('CreatedBy', ''),
                    'size': self._format_size(layer.get('Size', 0))
                }
                formatted_history.append(layer_info)
            
            return formatted_history
        except Exception:
            return []

