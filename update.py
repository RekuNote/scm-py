import os
import platform
import requests
import sys

def clear_console():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def update_scm_py():
    clear_console()
    print("Updating scm-py...\n")

    url = "https://raw.githubusercontent.com/RekuNote/scm-py/main/scm-py.py"
    local_script_path = os.path.realpath(__file__)

    try:
        response = requests.get(url)
        response.raise_for_status()

        with open(local_script_path, 'wb') as file:
            file.write(response.content)
        
        print("scm-py has been updated successfully.")
        print("Restarting the script to apply updates...")
        os.execv(sys.executable, ['python'] + sys.argv)

    except requests.RequestException as e:
        print(f"Error during update: {e}")

if __name__ == "__main__":
    update_scm_py()
