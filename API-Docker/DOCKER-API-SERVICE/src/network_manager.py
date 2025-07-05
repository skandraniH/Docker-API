import docker
from typing import Dict, List, Any, Optional
import logging

class NetworkManager:
    """
    Manages Docker networks with operations like listing, creating, removing networks,
    and connecting/disconnecting containers to networks.
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
    
    def list_networks(self) -> List[Dict[str, Any]]:
        """
        List all networks.
        
        Returns:
            List[Dict]: List of network information dictionaries
        """
        try:
            networks = self.client.networks.list()
            network_list = []
            
            for network in networks:
                network_info = {
                    'id': network.id[:12],
                    'name': network.name,
                    'driver': network.attrs.get('Driver', 'unknown'),
                    'scope': network.attrs.get('Scope', 'local'),
                    'created': network.attrs.get('Created', ''),
                    'internal': network.attrs.get('Internal', False),
                    'attachable': network.attrs.get('Attachable', False),
                    'ingress': network.attrs.get('Ingress', False),
                    'ipam': self._format_ipam(network.attrs.get('IPAM', {})),
                    'labels': network.attrs.get('Labels') or {},
                    'containers': self._get_network_containers(network),
                    'options': network.attrs.get('Options') or {}
                }
                network_list.append(network_info)
            
            return network_list
        except Exception as e:
            logging.error(f"Error listing networks: {e}")
            raise Exception(f"Failed to list networks: {str(e)}")
    
    def get_network_details(self, network_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific network.
        
        Args:
            network_id (str): Network ID or name
            
        Returns:
            Dict: Detailed network information
        """
        try:
            network = self.client.networks.get(network_id)
            
            details = {
                'id': network.id,
                'name': network.name,
                'driver': network.attrs.get('Driver', 'unknown'),
                'scope': network.attrs.get('Scope', 'local'),
                'created': network.attrs.get('Created', ''),
                'internal': network.attrs.get('Internal', False),
                'attachable': network.attrs.get('Attachable', False),
                'ingress': network.attrs.get('Ingress', False),
                'enable_ipv6': network.attrs.get('EnableIPv6', False),
                'ipam': self._format_ipam(network.attrs.get('IPAM', {})),
                'labels': network.attrs.get('Labels') or {},
                'options': network.attrs.get('Options') or {},
                'containers': self._get_network_containers(network),
                'config_from': network.attrs.get('ConfigFrom', {}),
                'config_only': network.attrs.get('ConfigOnly', False)
            }
            
            return details
        except docker.errors.NotFound:
            raise Exception(f"Network '{network_id}' not found")
        except Exception as e:
            logging.error(f"Error getting network details: {e}")
            raise Exception(f"Failed to get network details: {str(e)}")
    
    def create_network(self, name: str, driver: str = 'bridge', 
                      internal: bool = False, attachable: bool = False,
                      labels: Optional[Dict[str, str]] = None,
                      options: Optional[Dict[str, str]] = None,
                      ipam: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new network.
        
        Args:
            name (str): Network name
            driver (str): Network driver (default: 'bridge')
            internal (bool): Restrict external access to the network
            attachable (bool): Enable manual container attachment
            labels (dict, optional): Labels to set on the network
            options (dict, optional): Driver-specific options
            ipam (dict, optional): IPAM configuration
            
        Returns:
            Dict: Created network information
        """
        try:
            network = self.client.networks.create(
                name=name,
                driver=driver,
                internal=internal,
                attachable=attachable,
                labels=labels or {},
                options=options or {},
                ipam=ipam
            )
            
            return {
                'message': f"Network '{name}' created successfully",
                'id': network.id[:12],
                'name': network.name,
                'driver': driver,
                'internal': internal,
                'attachable': attachable,
                'labels': labels or {},
                'status': 'created'
            }
        except docker.errors.APIError as e:
            if 'already exists' in str(e).lower():
                raise Exception(f"Network '{name}' already exists")
            raise Exception(f"Failed to create network: {str(e)}")
        except Exception as e:
            logging.error(f"Error creating network: {e}")
            raise Exception(f"Failed to create network: {str(e)}")
    
    def remove_network(self, network_id: str) -> Dict[str, str]:
        """
        Remove a network.
        
        Args:
            network_id (str): Network ID or name
            
        Returns:
            Dict: Removal operation result
        """
        try:
            network = self.client.networks.get(network_id)
            network_name = network.name
            
            # Check if network is in use
            containers = self._get_network_containers(network)
            if containers:
                container_names = [c['name'] for c in containers]
                raise Exception(f"Cannot remove network '{network_name}' - it's being used by containers: {', '.join(container_names)}. Disconnect containers first")
            
            network.remove()
            
            return {
                'message': f"Network '{network_name}' removed successfully",
                'id': network_id,
                'name': network_name,
                'status': 'removed'
            }
        except docker.errors.NotFound:
            raise Exception(f"Network '{network_id}' not found")
        except docker.errors.APIError as e:
            if 'has active endpoints' in str(e).lower():
                raise Exception(f"Cannot remove network '{network_id}' - it has active endpoints. Disconnect containers first")
            raise Exception(f"Failed to remove network: {str(e)}")
        except Exception as e:
            if "it's being used by containers" in str(e):
                raise e
            logging.error(f"Error removing network: {e}")
            raise Exception(f"Failed to remove network: {str(e)}")
    
    def connect_container(self, network_id: str, container_id: str, 
                         aliases: Optional[List[str]] = None,
                         ipv4_address: Optional[str] = None,
                         ipv6_address: Optional[str] = None) -> Dict[str, str]:
        """
        Connect a container to a network.
        
        Args:
            network_id (str): Network ID or name
            container_id (str): Container ID or name
            aliases (list, optional): Network aliases for the container
            ipv4_address (str, optional): IPv4 address for the container
            ipv6_address (str, optional): IPv6 address for the container
            
        Returns:
            Dict: Connection operation result
        """
        try:
            network = self.client.networks.get(network_id)
            container = self.client.containers.get(container_id)
            
            # Check if container is already connected
            current_containers = self._get_network_containers(network)
            if any(c['id'] == container.id[:12] for c in current_containers):
                raise Exception(f"Container '{container.name}' is already connected to network '{network.name}'")
            
            network.connect(
                container,
                aliases=aliases,
                ipv4_address=ipv4_address,
                ipv6_address=ipv6_address
            )
            
            return {
                'message': f"Container '{container.name}' connected to network '{network.name}' successfully",
                'network_id': network.id[:12],
                'network_name': network.name,
                'container_id': container.id[:12],
                'container_name': container.name,
                'status': 'connected'
            }
        except docker.errors.NotFound as e:
            if 'network' in str(e).lower():
                raise Exception(f"Network '{network_id}' not found")
            else:
                raise Exception(f"Container '{container_id}' not found")
        except docker.errors.APIError as e:
            raise Exception(f"Failed to connect container to network: {str(e)}")
        except Exception as e:
            if "already connected" in str(e):
                raise e
            logging.error(f"Error connecting container to network: {e}")
            raise Exception(f"Failed to connect container to network: {str(e)}")
    
    def disconnect_container(self, network_id: str, container_id: str, force: bool = False) -> Dict[str, str]:
        """
        Disconnect a container from a network.
        
        Args:
            network_id (str): Network ID or name
            container_id (str): Container ID or name
            force (bool): Force disconnection
            
        Returns:
            Dict: Disconnection operation result
        """
        try:
            network = self.client.networks.get(network_id)
            container = self.client.containers.get(container_id)
            
            # Check if container is connected
            current_containers = self._get_network_containers(network)
            if not any(c['id'] == container.id[:12] for c in current_containers):
                raise Exception(f"Container '{container.name}' is not connected to network '{network.name}'")
            
            network.disconnect(container, force=force)
            
            return {
                'message': f"Container '{container.name}' disconnected from network '{network.name}' successfully",
                'network_id': network.id[:12],
                'network_name': network.name,
                'container_id': container.id[:12],
                'container_name': container.name,
                'status': 'disconnected'
            }
        except docker.errors.NotFound as e:
            if 'network' in str(e).lower():
                raise Exception(f"Network '{network_id}' not found")
            else:
                raise Exception(f"Container '{container_id}' not found")
        except docker.errors.APIError as e:
            raise Exception(f"Failed to disconnect container from network: {str(e)}")
        except Exception as e:
            if "not connected" in str(e):
                raise e
            logging.error(f"Error disconnecting container from network: {e}")
            raise Exception(f"Failed to disconnect container from network: {str(e)}")
    
    def prune_networks(self) -> Dict[str, Any]:
        """
        Remove unused networks.
        
        Returns:
            Dict: Prune operation result
        """
        try:
            result = self.client.networks.prune()
            
            return {
                'message': 'Network pruning completed',
                'networks_deleted': result.get('NetworksDeleted', [])
            }
        except Exception as e:
            logging.error(f"Error pruning networks: {e}")
            raise Exception(f"Failed to prune networks: {str(e)}")
    
    def inspect_network(self, network_id: str) -> Dict[str, Any]:
        """
        Inspect a network (alias for get_network_details).
        
        Args:
            network_id (str): Network ID or name
            
        Returns:
            Dict: Network inspection details
        """
        return self.get_network_details(network_id)
    
    def _get_network_containers(self, network) -> List[Dict[str, str]]:
        """
        Get list of containers connected to a network.
        
        Args:
            network: Docker network object
            
        Returns:
            List[Dict]: List of connected containers
        """
        try:
            containers = []
            network_containers = network.attrs.get('Containers', {})
            
            for container_id, container_info in network_containers.items():
                containers.append({
                    'id': container_id[:12],
                    'name': container_info.get('Name', 'unknown'),
                    'ipv4_address': container_info.get('IPv4Address', '').split('/')[0] if container_info.get('IPv4Address') else '',
                    'ipv6_address': container_info.get('IPv6Address', '').split('/')[0] if container_info.get('IPv6Address') else '',
                    'mac_address': container_info.get('MacAddress', ''),
                    'endpoint_id': container_info.get('EndpointID', '')[:12]
                })
            
            return containers
        except Exception:
            return []
    
    def _format_ipam(self, ipam_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format IPAM configuration for display.
        
        Args:
            ipam_config (dict): Raw IPAM configuration
            
        Returns:
            Dict: Formatted IPAM configuration
        """
        try:
            formatted_ipam = {
                'driver': ipam_config.get('Driver', 'default'),
                'options': ipam_config.get('Options') or {},
                'config': []
            }
            
            config_list = ipam_config.get('Config', [])
            for config in config_list:
                formatted_config = {
                    'subnet': config.get('Subnet', ''),
                    'gateway': config.get('Gateway', ''),
                    'ip_range': config.get('IPRange', ''),
                    'aux_addresses': config.get('AuxiliaryAddresses') or {}
                }
                formatted_ipam['config'].append(formatted_config)
            
            return formatted_ipam
        except Exception:
            return {
                'driver': 'unknown',
                'options': {},
                'config': []
            }
    
    def get_network_stats(self) -> Dict[str, Any]:
        """
        Get overall network statistics.
        
        Returns:
            Dict: Network statistics
        """
        try:
            networks = self.client.networks.list()
            
            # Count networks by driver
            drivers = {}
            scopes = {}
            total_containers = 0
            
            for network in networks:
                driver = network.attrs.get('Driver', 'unknown')
                scope = network.attrs.get('Scope', 'local')
                
                drivers[driver] = drivers.get(driver, 0) + 1
                scopes[scope] = scopes.get(scope, 0) + 1
                
                containers = self._get_network_containers(network)
                total_containers += len(containers)
            
            return {
                'total_networks': len(networks),
                'drivers': drivers,
                'scopes': scopes,
                'total_connected_containers': total_containers,
                'system_networks': len([n for n in networks if n.name in ['bridge', 'host', 'none']])
            }
        except Exception as e:
            logging.error(f"Error getting network stats: {e}")
            raise Exception(f"Failed to get network statistics: {str(e)}")

