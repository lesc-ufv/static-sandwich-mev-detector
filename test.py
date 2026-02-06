import os
import re
import subprocess

def get_solidity_pragma_version(file_path):
    """
    Extracts the Solidity pragma version string from a .sol file using regex.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            f.close()
            # Regex to find the pragma solidity line and capture the version part
            # It handles various spacing and version range operators like ^, >=, <, etc.
            match = re.search(r'pragma\s+solidity\s+([^;]+);', content)
            if match:
                # The captured group (index 1) contains the version constraint string
                version_constraint = match.group(1).strip()
                return version_constraint
            else:
                return "Pragma not found"
    except FileNotFoundError:
        return f"Error: The file {file_path} was not found."
    except Exception as e:
        return f"An error occurred: {e}"

def set_solc_version(sc_path):
    sc_version = get_solidity_pragma_version(sc_path).replace("^", "")
    if ">=" in sc_version:
        sc_version = sc_version.split(" ")[0].replace(">=", "")
    elif "<=" in sc_version:
        sc_version = sc_version.split(" ")[1].replace("<=", "")
    else:
        sc_version = sc_version.replace("=", "")
    
    print("Solidity version:", sc_version)

    # Run the command to install solc and capture output
    try:
        install_command = ["solc-select", "install", f"{sc_version}"]
        result = subprocess.run(install_command, capture_output=True, text=True, check=True)
        use_command = ["solc-select", "use", f"{sc_version}"]
        result = subprocess.run(use_command, capture_output=True, text=True, check=True)
        if result.returncode != 0:
            print("ERROR DURING SOLC INSTALATION!")
            return False
        else:
            print("`solc` successfully installed and changed!")
            return True
    except subprocess.CalledProcessError as e:
        print(f"`solc-select` command failed with return code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def run_slither(sc_name):
    try:
        slither_command = ["slither", f"{sc_name}.sol", "--detect", "static-sandwich"]
        result = subprocess.run(slither_command, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(e.stderr)
        print("Test finished successfully!")


database_path = "smart_contracts_database"
sc_name = "Example"


print(f"Running tests for {sc_name}.sol...")
sc_path = f"{database_path}/{sc_name}.sol"

# Set compiler
set_solc_version(sc_path)

# Run slither
os.chdir(f"{database_path}")
run_slither(sc_name)
os.chdir("..")
