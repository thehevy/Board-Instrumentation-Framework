"""
Base Widget Builder

Abstract base class for all Marvin widget builders with common functionality.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import sys

from ..utils.minion_discovery import MinionDataSourceDiscovery, DataSource


class WidgetBuilder(ABC):
    """Base class for all widget builders"""
    
    def __init__(self, minion_config: Optional[Path] = None):
        """
        Initialize widget builder.
        
        Args:
            minion_config: Path to MinionConfig.xml for data source discovery
        """
        self.minion_config = Path(minion_config) if minion_config else None
        self.discovery = None
        self.data_sources: List[DataSource] = []
        
        if self.minion_config and self.minion_config.exists():
            self.discovery = MinionDataSourceDiscovery(str(self.minion_config))
            self.data_sources = self.discovery.discover()
    
    def _prompt(self, question: str, default: Optional[str] = None) -> str:
        """
        Prompt user for input with optional default.
        
        Args:
            question: Question to ask
            default: Default value (optional)
            
        Returns:
            User input (or default)
        """
        if default:
            prompt = f"{question} [{default}]: "
        else:
            prompt = f"{question}: "
        
        try:
            response = input(prompt).strip()
            
            # Strip BOM if present (Windows PowerShell compatibility)
            if response.startswith('\ufeff'):
                response = response[1:]
            elif response.startswith('ï»¿'):
                response = response[3:]
            
            if not response and default:
                return default
            
            return response
            
        except (EOFError, KeyboardInterrupt):
            print("\n\nOperation cancelled by user")
            sys.exit(0)
    
    def _prompt_choice(self, question: str, options: List[str], default: int = 1) -> int:
        """
        Prompt user to select from a list of options.
        
        Args:
            question: Question to ask
            options: List of options
            default: Default choice (1-indexed)
            
        Returns:
            Selected index (0-based)
        """
        print(f"\n{question}")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        
        while True:
            choice = self._prompt(f"Choose (1-{len(options)})", str(default))
            
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    return idx
                else:
                    print(f"Invalid choice. Please enter 1-{len(options)}")
            except ValueError:
                print(f"Invalid input. Please enter a number 1-{len(options)}")
    
    def select_data_source(self, hint: str = "") -> Optional[DataSource]:
        """
        Interactive data source selection with search.
        
        Args:
            hint: Keyword hint to filter sources
            
        Returns:
            Selected DataSource or None
        """
        if not self.data_sources:
            print("⚠ No data sources found. Run with --config <MinionConfig.xml>")
            return None
        
        # Filter by hint if provided
        sources = self.data_sources
        if hint:
            sources = self.discovery.search(hint)
            if not sources:
                print(f"No sources matching '{hint}'. Showing all sources.")
                sources = self.data_sources
        
        print(f"\n📊 Available Data Sources ({len(sources)} found):")
        print("=" * 80)
        
        # Display sources
        display_sources = sources[:10]  # Limit to first 10
        for i, source in enumerate(display_sources, 1):
            unit = source.suggested_unit
            min_val, max_val = source.suggested_min_max
            
            print(f"{i:2}. {source.display_name}")
            print(f"    {source.description}")
            if unit:
                print(f"    Range: {min_val}-{max_val} {unit}")
        
        if len(sources) > 10:
            print(f"\n... and {len(sources) - 10} more")
            print("Tip: Use search to filter sources")
        
        print("\n0. Skip (no data binding)")
        print("s. Search for specific source")
        
        while True:
            choice = self._prompt("Select source (or 's' to search)", "1")
            
            if choice.lower() == 's':
                search_query = self._prompt("Search query")
                return self.select_data_source(search_query)
            
            try:
                idx = int(choice)
                if idx == 0:
                    return None
                elif 1 <= idx <= len(display_sources):
                    return display_sources[idx - 1]
                else:
                    print(f"Invalid choice. Enter 0-{len(display_sources)} or 's'")
            except ValueError:
                print("Invalid input. Enter a number or 's' to search")
    
    def _generate_minion_src(self, source: Optional[DataSource]) -> str:
        """
        Generate <MinionSrc> XML element.
        
        Args:
            source: Data source (or None for static widget)
            
        Returns:
            XML string
        """
        if source is None:
            return ""
        
        return f'<MinionSrc Namespace="{source.namespace}" ID="{source.collector_id}"/>'
    
    def _generate_position(self, row: int = 1, column: int = 1, 
                          row_span: int = 1, col_span: int = 1) -> str:
        """
        Generate position attributes.
        
        Args:
            row: Grid row (1-based)
            column: Grid column (1-based)
            row_span: Row span
            col_span: Column span
            
        Returns:
            XML attributes string
        """
        attrs = [f'row="{row}"', f'column="{column}"']
        
        if row_span > 1:
            attrs.append(f'rowSpan="{row_span}"')
        if col_span > 1:
            attrs.append(f'columnSpan="{col_span}"')
        
        return ' '.join(attrs)
    
    @abstractmethod
    def build_widget(self) -> str:
        """
        Interactive wizard to build widget XML.
        
        Returns:
            Widget XML string
        """
        raise NotImplementedError("Subclasses must implement build_widget()")
    
    def validate_widget(self, xml: str) -> Tuple[bool, List[str]]:
        """
        Basic validation of widget XML.
        
        Args:
            xml: Widget XML string
            
        Returns:
            (valid, error_messages)
        """
        errors = []
        
        # Check for required elements
        if '<Widget' not in xml:
            errors.append("Missing <Widget> element")
        
        # Check for balanced tags
        open_tags = xml.count('<')
        close_tags = xml.count('>')
        if open_tags != close_tags:
            errors.append("Unbalanced XML tags")
        
        # Check for common mistakes
        if '<MinionSrc' in xml:
            if 'Namespace=' not in xml or 'ID=' not in xml:
                errors.append("<MinionSrc> missing Namespace or ID attribute")
        
        return len(errors) == 0, errors
    
    def save_widget(self, xml: str, output_path: Path) -> bool:
        """
        Save widget XML to file.
        
        Args:
            xml: Widget XML string
            output_path: Output file path
            
        Returns:
            Success boolean
        """
        try:
            # Ensure directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write XML
            output_path.write_text(xml, encoding='utf-8')
            
            return True
            
        except Exception as e:
            print(f"Error saving widget: {e}")
            return False
    
    def create_widget(self, output_path: Optional[Path] = None) -> Optional[str]:
        """
        Complete workflow: build, validate, and optionally save widget.
        
        Args:
            output_path: Optional path to save widget XML
            
        Returns:
            Widget XML string or None if failed
        """
        print(f"\n{'='*70}")
        print(f"  {self.__class__.__name__}")
        print(f"{'='*70}\n")
        
        # Build widget via interactive wizard
        xml = self.build_widget()
        
        # Validate
        valid, errors = self.validate_widget(xml)
        if not valid:
            print("\n❌ Widget validation failed:")
            for error in errors:
                print(f"  • {error}")
            return None
        
        # Save if path provided
        if output_path:
            if self.save_widget(xml, output_path):
                print(f"\n✓ Widget saved: {output_path}")
            else:
                print(f"\n❌ Failed to save widget to {output_path}")
                return None
        
        return xml
    
    def print_summary(self, widget_type: str, config: Dict[str, any]):
        """
        Print widget configuration summary.
        
        Args:
            widget_type: Type of widget
            config: Configuration dictionary
        """
        print(f"\n{'='*70}")
        print(f"  Widget Summary: {widget_type}")
        print(f"{'='*70}")
        
        for key, value in config.items():
            if isinstance(value, DataSource):
                print(f"  • {key}: {value.display_name}")
            else:
                print(f"  • {key}: {value}")
        
        print(f"{'='*70}\n")
