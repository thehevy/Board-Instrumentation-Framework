"""
Interactive setup wizard for BIFF Quick Start.

Guides users through deployment configuration based on validated environment.
"""

from typing import Dict, Optional
from pathlib import Path
from .cli_helpers import (
    print_header, print_info, print_success, print_warning, print_error,
    prompt_user, select_from_menu, confirm_action
)


class SetupWizard:
    """Interactive setup wizard for BIFF deployment"""
    
    def __init__(self, validation_results: Dict):
        """Initialize wizard with environment validation results
        
        Args:
            validation_results: Dict from EnvironmentValidator.validate_all()
        """
        self.validation = validation_results
        self.config = {
            "deployment_type": None,
            "output_dir": None,
            "minion_namespace": "QuickStart",
            "oscar_ip": "localhost",
            "oscar_port": 1100,
            "marvin_port": 52001,
            "collectors": [],
            "use_existing": False,
            "biff_root": None
        }
    
    def run(self) -> Dict:
        """Run the interactive setup wizard
        
        Returns:
            Configuration dict for generators
        """
        print_header("BIFF Quick Start Setup Wizard")
        print()
        
        # Step 1: Deployment type
        self._select_deployment_type()
        
        # Step 2: Check for existing installation
        if self.validation.get("biff_paths") and self.validation["biff_paths"]["found"]:
            self._handle_existing_installation()
        
        # Step 3: Configuration options
        self._configure_deployment()
        
        # Step 4: Collector selection
        self._select_collectors()
        
        # Step 5: Output directory
        self._select_output_directory()
        
        # Step 6: Summary and confirmation
        if not self._confirm_configuration():
            print_warning("Setup cancelled by user")
            return None
        
        return self.config
    
    def _select_deployment_type(self):
        """Let user choose deployment type"""
        print_info("Choose your deployment type:")
        print()
        
        options = [
            ("local", "Single-Machine (Local)", "All components on localhost - fastest setup"),
            ("remote", "Network Deployment", "Minion on one machine, Oscar/Marvin on another"),
            ("container", "Container/K8s", "Docker or Kubernetes deployment"),
            ("multi", "Multi-Deployment", "Compare multiple environments side-by-side")
        ]
        
        descriptions = {}
        menu_items = []
        for value, label, desc in options:
            menu_items.append(label)
            descriptions[label] = desc
        
        # Show descriptions
        for i, item in enumerate(menu_items, 1):
            print(f"  {i}. {item}")
            print(f"     {descriptions[item]}")
            print()
        
        choice = select_from_menu(menu_items, "Select deployment type")
        
        # Map back to value
        for value, label, _ in options:
            if label == choice:
                self.config["deployment_type"] = value
                break
        
        print_success(f"Selected: {choice}")
        print()
    
    def _handle_existing_installation(self):
        """Ask if user wants to use existing BIFF installation"""
        biff_root = self.validation["biff_paths"]["root"]
        
        print_info(f"Existing BIFF installation detected at:")
        print(f"  {biff_root}")
        print()
        
        use_existing = confirm_action(
            "Use this installation? (Otherwise will create standalone setup)",
            default=True
        )
        
        if use_existing:
            self.config["use_existing"] = True
            self.config["biff_root"] = biff_root
            print_success("Will use existing BIFF installation")
        else:
            print_info("Will create new standalone configuration")
        
        print()
    
    def _configure_deployment(self):
        """Configure deployment-specific settings"""
        deployment_type = self.config["deployment_type"]
        
        if deployment_type == "local":
            print_info("Single-machine setup - using localhost for all components")
            self.config["oscar_ip"] = "localhost"
            self.config["oscar_port"] = 1100
            self.config["marvin_port"] = 52001
        
        elif deployment_type == "remote":
            print_info("Network deployment configuration:")
            print()
            
            # Ask for Oscar IP
            oscar_ip = prompt_user(
                "Oscar/Marvin host IP or hostname",
                default="localhost"
            )
            self.config["oscar_ip"] = oscar_ip
            
            # Ports (use defaults if local)
            if oscar_ip not in ["localhost", "127.0.0.1"]:
                oscar_port = prompt_user(
                    "Oscar port",
                    default="1100"
                )
                self.config["oscar_port"] = int(oscar_port)
                
                marvin_port = prompt_user(
                    "Marvin port",
                    default="52001"
                )
                self.config["marvin_port"] = int(marvin_port)
        
        elif deployment_type == "container":
            print_info("Container deployment will use environment variables")
            print_info("Generated configs will read from $(MinionNamespace), $(OscarIP), etc.")
        
        elif deployment_type == "multi":
            print_info("Multi-deployment setup:")
            num_envs = prompt_user(
                "Number of environments to compare",
                default="2"
            )
            self.config["num_deployments"] = int(num_envs)
        
        # Namespace (all types)
        print()
        namespace = prompt_user(
            "Minion namespace (groups collectors)",
            default="QuickStart"
        )
        self.config["minion_namespace"] = namespace
        
        print()
    
    def _select_collectors(self):
        """Let user choose which collectors to include"""
        deployment_type = self.config["deployment_type"]
        
        print_info("Select collectors to include:")
        print()
        
        # Pre-defined collector presets
        if deployment_type == "local":
            presets = {
                "demo": ["RandomVal", "Timer", "CPU"],
                "monitoring": ["CPU", "Memory", "Network", "Storage"],
                "minimal": ["RandomVal"]
            }
        else:
            presets = {
                "demo": ["RandomVal", "Timer"],
                "monitoring": ["CPU", "Memory", "Network"],
                "minimal": ["RandomVal"]
            }
        
        print("Available presets:")
        for name, collectors in presets.items():
            print(f"  - {name}: {', '.join(collectors)}")
        print()
        
        preset = select_from_menu(
            list(presets.keys()) + ["custom"],
            "Choose collector preset"
        )
        
        if preset == "custom":
            print_info("Custom collector selection coming soon...")
            print_info("Using 'demo' preset for now")
            preset = "demo"
        
        self.config["collectors"] = presets[preset]
        print_success(f"Selected collectors: {', '.join(self.config['collectors'])}")
        print()
    
    def _select_output_directory(self):
        """Choose where to generate configs"""
        print_info("Output directory configuration:")
        print()
        
        default_dir = Path.cwd() / "biff-quickstart"
        output = prompt_user(
            "Output directory for generated files",
            default=str(default_dir)
        )
        
        self.config["output_dir"] = Path(output)
        
        if self.config["output_dir"].exists():
            print_warning(f"Directory already exists: {self.config['output_dir']}")
            overwrite = confirm_action("Overwrite existing files?", default=False)
            if not overwrite:
                print_error("Setup cancelled - please choose a different directory")
                return None
        
        print()
    
    def _confirm_configuration(self) -> bool:
        """Show summary and ask for confirmation"""
        print_header("Configuration Summary")
        print()
        
        print(f"Deployment Type:  {self.config['deployment_type']}")
        print(f"Output Directory: {self.config['output_dir']}")
        print(f"Minion Namespace: {self.config['minion_namespace']}")
        print(f"Oscar Address:    {self.config['oscar_ip']}:{self.config['oscar_port']}")
        print(f"Marvin Port:      {self.config['marvin_port']}")
        print(f"Collectors:       {', '.join(self.config['collectors'])}")
        
        if self.config["use_existing"]:
            print(f"BIFF Root:        {self.config['biff_root']}")
        
        print()
        
        return confirm_action("Proceed with this configuration?", default=True)
    
    def get_config(self) -> Dict:
        """Get the configuration dict"""
        return self.config
