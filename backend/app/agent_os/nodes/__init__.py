"""
Agent OS v2 Nodes Package.

Contains all workflow nodes for the distributed agent system.
Each node is a Celery task that can be routed to specialized queues.
"""

import os
import importlib
from typing import Dict, Any

# Auto-discover and register nodes
_NODES: Dict[str, Any] = {}


def discover_nodes():
    """Discover all node modules in this package."""
    package_dir = os.path.dirname(__file__)

    for filename in os.listdir(package_dir):
        if filename.endswith('.py') and filename != '__init__.py' and filename != '__pycache__':
            module_name = filename[:-3]  # Remove .py

            try:
                module = importlib.import_module(
                    f'.{module_name}',
                    package='app.agent_os.nodes'
                )

                # Look for task functions
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if callable(attr) and attr_name.endswith('_task'):
                        node_name = attr_name[:-5]  # Remove _task suffix
                        _NODES[node_name] = attr

            except ImportError as e:
                print(f"Failed to import node module {module_name}: {e}")


# Discover nodes on import
discover_nodes()


def get_node(node_name: str):
    """Get node function by name."""
    return _NODES.get(node_name)


def list_nodes() -> Dict[str, Any]:
    """List all available nodes."""
    return _NODES.copy()


def register_node(node_name: str, node_func):
    """Register a node function."""
    if node_name in _NODES:
        raise ValueError(f"Node '{node_name}' already registered")
    _NODES[node_name] = node_func