#!/bin/bash

echo "========== Start Orchestration Process =========="

# Virtual Environment Path
VENV_PATH="/Users/dilafaradisa/Documents/disa/05_pacmann/03_into_to_devops/storage/pactravel-dataset/pactravel/bin/activate"

# Activate Virtual Environment
source "$VENV_PATH"

# Set Python script
PYTHON_SCRIPT="/Users/dilafaradisa/Documents/disa/05_pacmann/03_into_to_devops/storage/pactravel-dataset/main_elt.py"

# Run Python Script 
python "$PYTHON_SCRIPT"

echo "========== End of Orchestration Process =========="