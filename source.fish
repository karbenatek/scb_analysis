#!/usr/bin/env fish

# Get the directory where this script is located (the package dir)
set PACKAGE_PATH (realpath (dirname (status --current-filename)))

# Add it permanently to PATH (for executables)
if not contains $PACKAGE_PATH $PATH
    set -U fish_user_paths $PACKAGE_PATH $fish_user_paths
    echo "✅ Added $PACKAGE_PATH to PATH"
else
    echo "ℹ️ $PACKAGE_PATH already in PATH"
end

# Add it permanently to PYTHONPATH (for Python imports)
if test -z "$PYTHONPATH"
    set -x PYTHONPATH $PACKAGE_PATH
    echo "✅ Set PYTHONPATH to $PACKAGE_PATH"
else if not contains $PACKAGE_PATH (string split ":" $PYTHONPATH)
    set -x PYTHONPATH "$PACKAGE_PATH:$PYTHONPATH"
    echo "✅ Added $PACKAGE_PATH to PYTHONPATH"
else
    echo "ℹ️ $PACKAGE_PATH already in PYTHONPATH"
end
