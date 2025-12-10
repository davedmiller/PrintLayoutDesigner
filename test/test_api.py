# ABOUTME: Test script for the PrintLayoutDesigner API functions.
# ABOUTME: Exercises list_layouts, list_themes, get_layout_spec, and get_html_template.

import sys
import os
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PrintLayoutDesigner import (
    list_layouts,
    list_themes,
    get_layout_spec,
    get_html_template,
)


def test_discovery(base_dir):
    """Test the discovery functions."""
    print("=" * 60)
    print("Testing Discovery Functions")
    print("=" * 60)

    # Test list_layouts
    layouts = list_layouts(base_dir)
    print(f"\nFound {len(layouts)} layouts:")
    for layout in layouts[:5]:  # Show first 5
        print(f"  - {layout['name']}: {layout['title']} ({layout['paper_size']})")
    if len(layouts) > 5:
        print(f"  ... and {len(layouts) - 5} more")

    # Test list_themes
    themes = list_themes(base_dir)
    print(f"\nFound {len(themes)} themes:")
    for theme in themes[:5]:  # Show first 5
        print(f"  - {theme['name']} ({theme['mode']})")
    if len(themes) > 5:
        print(f"  ... and {len(themes) - 5} more")

    return layouts, themes


def test_layout_spec(base_dir, layout_name, front_theme, back_theme):
    """Test get_layout_spec function."""
    print("\n" + "=" * 60)
    print("Testing get_layout_spec()")
    print("=" * 60)

    spec = get_layout_spec(layout_name, front_theme, back_theme, base_dir)

    print(f"\nLayout: {layout_name}")
    print(f"Front theme: {front_theme}")
    print(f"Back theme: {back_theme}")
    print(f"\nSpec structure:")
    print(json.dumps(spec, indent=2))

    return spec


def test_html_template(base_dir, layout_name, front_theme, back_theme, output_dir):
    """Test get_html_template function."""
    print("\n" + "=" * 60)
    print("Testing get_html_template()")
    print("=" * 60)

    template = get_html_template(layout_name, front_theme, back_theme, base_dir)

    # Check for placeholders
    placeholders = ['{{IMAGE}}', '{{CAPTION}}', '{{NOTE}}', '{{FONT_FAMILY}}']
    print(f"\nPlaceholder check:")
    for ph in placeholders:
        found = ph in template
        status = "✓" if found else "✗"
        print(f"  {status} {ph}")

    # Write template with dummy content for visual inspection
    os.makedirs(output_dir, exist_ok=True)
    filled = template.replace('{{IMAGE}}', '<p style="text-align:center; padding-top: 2in;">[IMAGE PLACEHOLDER]</p>')
    filled = filled.replace('{{CAPTION}}', '<p>This is a sample caption with <strong>bold</strong> and <em>italic</em> text.</p>')
    filled = filled.replace('{{NOTE}}', '<p>This is a sample personal note.</p><p>It can have multiple paragraphs.</p>')
    filled = filled.replace('{{FONT_FAMILY}}', 'Georgia, serif')

    output_path = os.path.join(output_dir, 'template_test.html')
    with open(output_path, 'w') as f:
        f.write(filled)
    print(f"\nTemplate written to: {output_path}")

    return template


def main():
    """Run all API tests."""
    # Use production directory for testing
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    production_dir = os.path.join(project_dir, 'production')
    output_dir = os.path.join(script_dir, 'output')

    # Check if production directory exists
    if not os.path.exists(production_dir):
        print(f"Error: Production directory not found: {production_dir}")
        print("Using test directory instead...")
        production_dir = script_dir

    print(f"Base directory: {production_dir}")
    print(f"Output directory: {output_dir}")

    # Run tests
    layouts, themes = test_discovery(production_dir)

    if layouts and themes:
        # Pick a layout and themes for detailed testing
        layout_name = layouts[0]['name']
        front_theme = themes[0]['name']
        back_theme = themes[0]['name']

        test_layout_spec(production_dir, layout_name, front_theme, back_theme)
        test_html_template(production_dir, layout_name, front_theme, back_theme, output_dir)

    print("\n" + "=" * 60)
    print("API Tests Complete")
    print("=" * 60)


if __name__ == '__main__':
    main()
