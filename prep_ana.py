#!/home/tono/python-mess-organised/scb_analysis/.venv/bin/python3
"""
CLI tool to prepare analysis directories by copying templates.
Usage: ./prep_ana.py <template> <new_dir_name>
Example: ./prep_ana.py scba 01-01-2026_blahblah
"""

import argparse
import shutil
from pathlib import Path

try:
    import tomlkit
except ImportError:
    print("Error: tomlkit is required. Install with: pip install tomlkit")
    exit(1)


# Configuration: map template names to their source directories
TEMPLATES = {
    "scba": "default_scba",
    # Add more templates as needed:
    # "hcl": "default_hcl",
    # "other": "default_other",
}

# Base analysis directory
ANALYSIS_DIR = Path(__file__).parent / "Analysis"


def copy_and_rename_template(template_name: str, new_dir_name: str, force: bool = False) -> None:
    """
    Copy the template directory and rename it to new_dir_name.
    
    Args:
        template_name: Name of the template (key in TEMPLATES dict)
        new_dir_name: Name of the new directory to create
        force: If True, overwrite existing directory
        
    Raises:
        ValueError: If template not found or new directory already exists (unless force=True)
    """
    # Validate template exists
    if template_name not in TEMPLATES:
        raise ValueError(
            f"Template '{template_name}' not found. "
            f"Available templates: {', '.join(TEMPLATES.keys())}"
        )
    
    # Get template source path
    template_dir = ANALYSIS_DIR / TEMPLATES[template_name]
    if not template_dir.exists():
        raise ValueError(f"Template directory not found: {template_dir}")
    
    # Define destination path
    dest_dir = ANALYSIS_DIR / new_dir_name
    if dest_dir.exists():
        if not force:
            raise ValueError(f"Directory already exists: {dest_dir}")
        print(f"Removing existing directory: {dest_dir}")
        shutil.rmtree(dest_dir)
    
    # Copy template
    print(f"Copying template '{template_name}' from {template_dir}")
    shutil.copytree(template_dir, dest_dir)
    print(f"✓ Created new directory: {dest_dir}")
    
    # Update info.toml with new directory name
    update_info_toml(dest_dir, new_dir_name)
    return dest_dir


def update_info_toml(dest_dir: Path, new_dir_name: str) -> None:
    """
    Update the remote_path in info.toml [[mounts]] section with the new directory name.
    Preserves all comments and formatting.
    
    Args:
        dest_dir: Path to the newly created directory
        new_dir_name: Name to set as remote_path
    """
    info_file = dest_dir / "info.toml"
    if not info_file.exists():
        print(f"Warning: info.toml not found in {dest_dir}")
        return
    
    # Read TOML file with tomlkit to preserve comments
    with open(info_file, "r") as f:
        data = tomlkit.parse(f.read())
    
    # Update remote_path in mounts section
    if "mounts" in data and isinstance(data["mounts"], list) and len(data["mounts"]) > 0:
        data["mounts"][0]["remote_path"] = new_dir_name
        print(f"  Updated remote_path to: {new_dir_name}")
    else:
        print(f"Warning: [[mounts]] section not found in {info_file}")
        return
    
    # Write updated TOML back, preserving comments
    with open(info_file, "w") as f:
        f.write(tomlkit.dumps(data))
    
    print(f"✓ Updated info.toml")


def main():
    """Parse arguments and execute template copy."""
    parser = argparse.ArgumentParser(
        description="Prepare analysis directories by copying templates"
    )
    parser.add_argument(
        "template",
        help=f"Template to use. Options: {', '.join(TEMPLATES.keys())}",
    )
    parser.add_argument(
        "new_dir_name",
        help="Name of the new analysis directory to create",
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Overwrite existing directory if it already exists",
    )
    parser.add_argument(
        "-r", "--run",
        action="store_true",
        help="Run Analysis/analysis.py after creating the directory",
    )
    
    args = parser.parse_args()
    
    try:
        dest_dir = copy_and_rename_template(args.template, args.new_dir_name, force=args.force)

        if args.run:
            analysis_script = dest_dir / "analysis.py"
            if not analysis_script.exists():
                raise FileNotFoundError(f"analysis.py not found in {dest_dir}")
            print(f"Running {analysis_script}...")
            ret =  __import__('subprocess').run([str(dest_dir / 'analysis.py')], cwd=str(dest_dir), check=False)
            if ret.returncode != 0:
                raise RuntimeError(f"analysis.py exited with {ret.returncode}")
            print("✓ analysis.py completed successfully")

    except ValueError as e:
        print(f"Error: {e}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit(1)


if __name__ == "__main__":
    main()

