"""
Button Widget Builder for BIFF Marvin GUI Composer

Creates interactive button widgets that can execute Minion tasks or Marvin actions.
Supports various button styles and task types.

Phase 3 Week 8 Day 5
"""

from .widget_builder import WidgetBuilder
from typing import Optional, List
from pathlib import Path


class ButtonWidgetBuilder(WidgetBuilder):
    """Builder for interactive button widgets"""
    
    def __init__(self, config_file: str):
        super().__init__(str(config_file))
        self.widget_type = 'button'
    
    def build_widget(self) -> str:
        """Build button widget with interactive wizard"""
        print("\n" + "="*70)
        print("Button Widget Builder")
        print("="*70)
        
        # Step 1: Button label and purpose
        print("\nStep 1: Button Configuration")
        print("-" * 70)
        
        label = input("\nButton label: ").strip()
        if not label:
            print("❌ Button label is required")
            return ""
        
        print(f"✅ Label: {label}")
        
        # Step 2: Button style
        print("\n" + "-" * 70)
        print("Step 2: Button Style")
        print("-" * 70)
        print("\nAvailable styles:")
        print("  1. Standard (default rectangular button)")
        print("  2. LCARS (Star Trek style)")
        print("  3. Custom image button")
        
        while True:
            try:
                style_choice = input("\nSelect style (1-3, default=1): ").strip() or "1"
                style_idx = int(style_choice)
                if 1 <= style_idx <= 3:
                    break
                print("❌ Please enter 1-3")
            except (ValueError, EOFError):
                print("❌ Invalid input")
                return ""
        
        style_map = {1: 'standard', 2: 'lcars', 3: 'image'}
        button_style = style_map[style_idx]
        print(f"✅ Style: {button_style}")
        
        # Step 3: Action type
        print("\n" + "-" * 70)
        print("Step 3: Button Action")
        print("-" * 70)
        print("\nAvailable actions:")
        print("  1. Execute Minion task (remote command)")
        print("  2. Open URL/webpage")
        print("  3. Send data value")
        print("  4. Toggle state")
        
        while True:
            try:
                action_choice = input("\nSelect action (1-4, default=1): ").strip() or "1"
                action_idx = int(action_choice)
                if 1 <= action_idx <= 4:
                    break
                print("❌ Please enter 1-4")
            except (ValueError, EOFError):
                print("❌ Invalid input")
                return ""
        
        action_map = {1: 'minion_task', 2: 'url', 3: 'send_value', 4: 'toggle'}
        action_type = action_map[action_idx]
        print(f"✅ Action: {action_type}")
        
        # Step 4: Action-specific configuration
        action_config = self._configure_action(action_type)
        if not action_config:
            return ""
        
        # Step 5: Visual properties
        print("\n" + "-" * 70)
        print("Step 5: Visual Properties")
        print("-" * 70)
        
        width = int(input("\nButton width (default=2): ").strip() or "2")
        height = int(input("Button height (default=1): ").strip() or "1")
        
        # Optional colors
        use_custom_colors = input("Customize colors? (y/N): ").strip().lower()
        fg_color = ""
        bg_color = ""
        if use_custom_colors == 'y':
            fg_color = input("Foreground color (default=white): ").strip() or "white"
            bg_color = input("Background color (default=blue): ").strip() or "blue"
            print(f"✅ Colors: {fg_color} on {bg_color}")
        else:
            print("✅ Using default colors")
        
        # Step 6: Grid position
        print("\n" + "-" * 70)
        print("Step 6: Grid Position")
        print("-" * 70)
        
        row = int(input("\nRow (default=0): ").strip() or "0")
        col = int(input("Column (default=0): ").strip() or "0")
        
        print(f"✅ Position: Row={row}, Col={col}, Size={width}x{height}")
        
        # Generate XML based on configuration
        widget_xml = self._generate_button_xml(
            label, button_style, action_type, action_config,
            row, col, width, height, fg_color, bg_color
        )
        
        print("\n" + "="*70)
        print("✅ Button widget generated successfully!")
        print("="*70)
        
        return widget_xml
    
    def _configure_action(self, action_type: str) -> dict:
        """Configure action-specific parameters"""
        print("\n" + "-" * 70)
        print("Step 4: Action Configuration")
        print("-" * 70)
        
        if action_type == 'minion_task':
            print("\nExecute Minion task (Actor)")
            
            # List available actors from config
            actors = self._discover_actors()
            if actors:
                print(f"\nAvailable Actors ({len(actors)}):")
                for i, (ns, actor_id) in enumerate(actors, 1):
                    print(f"  {i}. {ns}:{actor_id}")
                
                choice = input("\nSelect actor (number) or enter custom namespace:id: ").strip()
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(actors):
                        namespace, actor_id = actors[idx]
                    else:
                        print("❌ Invalid selection")
                        return {}
                except ValueError:
                    # Custom namespace:id
                    if ':' in choice:
                        parts = choice.split(':', 1)
                        namespace, actor_id = parts[0].strip(), parts[1].strip()
                    else:
                        print("❌ Invalid format. Use namespace:id")
                        return {}
            else:
                print("\n⚠️  No actors found in config")
                namespace = input("Namespace: ").strip()
                actor_id = input("Actor ID: ").strip()
            
            # Optional parameters
            params = input("Parameters (comma-separated, optional): ").strip()
            
            return {
                'namespace': namespace,
                'actor_id': actor_id,
                'params': params
            }
        
        elif action_type == 'url':
            url = input("\nURL to open: ").strip()
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            return {'url': url}
        
        elif action_type == 'send_value':
            namespace = input("\nTarget Namespace: ").strip()
            target_id = input("Target ID: ").strip()
            value = input("Value to send: ").strip()
            return {
                'namespace': namespace,
                'target_id': target_id,
                'value': value
            }
        
        elif action_type == 'toggle':
            namespace = input("\nTarget Namespace: ").strip()
            target_id = input("Target ID: ").strip()
            return {
                'namespace': namespace,
                'target_id': target_id
            }
        
        return {}
    
    def _discover_actors(self) -> List[tuple]:
        """Discover available actors from Minion config"""
        actors = []
        try:
            from xml.dom import minidom
            dom = minidom.parse(str(self.minion_config))
            
            for namespace_node in dom.getElementsByTagName('Namespace'):
                ns_name_nodes = namespace_node.getElementsByTagName('Name')
                if not ns_name_nodes:
                    continue
                
                namespace = ns_name_nodes[0].firstChild.nodeValue.strip()
                
                for actor_node in namespace_node.getElementsByTagName('Actor'):
                    actor_id = actor_node.getAttribute('ID')
                    if actor_id:
                        actors.append((namespace, actor_id))
        except Exception as e:
            print(f"⚠️  Could not parse actors: {e}")
        
        return actors
    
    def _generate_button_xml(self, label: str, style: str, action_type: str,
                            action_config: dict, row: int, col: int,
                            width: int, height: int,
                            fg_color: str, bg_color: str) -> str:
        """Generate button widget XML"""
        
        # Build task XML based on action type
        task_xml = self._generate_task_xml(action_type, action_config)
        
        # Build style attributes
        style_attrs = []
        if fg_color:
            style_attrs.append(f'Foreground="{fg_color}"')
        if bg_color:
            style_attrs.append(f'Background="{bg_color}"')
        
        style_str = ' '.join(style_attrs)
        if style_str:
            style_str = ' ' + style_str
        
        # Choose widget file based on style
        widget_file_map = {
            'standard': 'Button/PushButton.xml',
            'lcars': 'LCARS/Button.xml',
            'image': 'Button/ImageButton.xml'
        }
        widget_file = widget_file_map.get(style, 'Button/PushButton.xml')
        
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- Button Widget: {label} -->
<Widget File="{widget_file}" row="{row}" column="{col}" rowSpan="{height}" columnSpan="{width}"{style_str}>
    <Title>{label}</Title>
    {task_xml}
</Widget>"""
    
    def _generate_task_xml(self, action_type: str, config: dict) -> str:
        """Generate task XML based on action type"""
        
        if action_type == 'minion_task':
            params_xml = ""
            if config.get('params'):
                param_list = [p.strip() for p in config['params'].split(',')]
                params_xml = '\n'.join(f'        <Param>{p}</Param>' 
                                      for p in param_list if p)
                if params_xml:
                    params_xml = '\n' + params_xml + '\n    '
            
            return f"""<Task Type="MinionTaskLauncher">
        <Namespace>{config['namespace']}</Namespace>
        <ID>{config['actor_id']}</ID>{params_xml}</Task>"""
        
        elif action_type == 'url':
            return f"""<Task Type="OpenURL">
        <URL>{config['url']}</URL>
    </Task>"""
        
        elif action_type == 'send_value':
            return f"""<Task Type="SendMarvinDatapoint">
        <Namespace>{config['namespace']}</Namespace>
        <ID>{config['target_id']}</ID>
        <Value>{config['value']}</Value>
    </Task>"""
        
        elif action_type == 'toggle':
            return f"""<Task Type="ToggleDatapoint">
        <Namespace>{config['namespace']}</Namespace>
        <ID>{config['target_id']}</ID>
    </Task>"""
        
        return ""


def main():
    """Test button widget builder"""
    import sys
    from io import StringIO
    
    config_path = Path("quickstart_configs/MinionConfig.xml")
    if not config_path.exists():
        print("❌ Config file not found")
        return
    
    builder = ButtonWidgetBuilder(str(config_path))
    
    # Simulate input: label, style=1, action=1 (minion task), custom actor, params, no custom colors, position
    inputs = "Restart Service\n1\n1\nMyNamespace:restart_app\nforce=true\nn\n0\n0\n"
    sys.stdin = StringIO(inputs)
    
    xml = builder.build_widget()
    sys.stdin = sys.__stdin__
    
    if xml:
        print("\n" + "="*70)
        print("Generated XML:")
        print("="*70)
        print(xml)


if __name__ == '__main__':
    main()
