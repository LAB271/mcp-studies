import importlib.util
import os
import sys

def load_spike_module(spike_name, module_name):
    """
    Load a module from a spike directory with a unique name to avoid collisions.
    
    Args:
        spike_name: Name of the spike directory (e.g., "001_demos")
        module_name: Name of the module file without .py (e.g., "main_server")
        
    Returns:
        The loaded module.
    """
    # Calculate path to the spike module
    # This file is in tests/test_utils.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    spike_dir = os.path.join(project_root, "spikes", spike_name)
    module_path = os.path.join(spike_dir, f"{module_name}.py")
    
    if not os.path.exists(module_path):
        raise FileNotFoundError(f"Module {module_name} not found in {spike_dir}")
        
    # Create a unique name for sys.modules
    unique_module_name = f"spike_{spike_name}_{module_name}"
    
    spec = importlib.util.spec_from_file_location(unique_module_name, module_path)
    if spec is None:
        raise ImportError(f"Could not load spec for {module_path}")
        
    module = importlib.util.module_from_spec(spec)
    
    # Add to sys.modules so relative imports inside the module might work if they use the same unique name
    sys.modules[unique_module_name] = module
    
    # Temporarily add spike dir to sys.path for internal imports
    sys.path.insert(0, spike_dir)
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
        
    return module
