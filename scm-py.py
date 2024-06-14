import os
import platform
import subprocess
import sys
import termios
import tty
import requests
from tqdm import tqdm

def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

# Check if required modules are installed, and install them if necessary
def check_and_install_module(module_name):
    try:
        __import__(module_name)
    except ImportError:
        print(f"{module_name} is not installed.")
        print(f"Do you want to install {module_name}? (Y/N): ", end='', flush=True)
        choice = get_key().lower()
        print(choice.upper())  # Show the key press for clarity
        if choice == 'y':
            subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])
            print(f"{module_name} installed successfully. Restarting script...")
            os.execv(sys.executable, ['python'] + sys.argv)
        else:
            print(f"{module_name} is required for this script to run.")
            sys.exit()

def check_and_install_modules():
    check_and_install_module("requests")
    check_and_install_module("PIL")
    check_and_install_module("tqdm")

check_and_install_modules()

from PIL import Image
from io import BytesIO

ASCII_ART = r"""

  /$$$$$$$  /$$$$$$$ /$$$$$$/$$$$           /$$$$$$  /$$   /$$
 /$$_____/ /$$_____/| $$_  $$_  $$ /$$$$$$ /$$__  $$| $$  | $$
|  $$$$$$ | $$      | $$ \ $$ \ $$|______/| $$  \ $$| $$  | $$
 \____  $$| $$      | $$ | $$ | $$        | $$  | $$| $$  | $$
 /$$$$$$$/|  $$$$$$$| $$ | $$ | $$        | $$$$$$$/|  $$$$$$$
|_______/  \_______/|__/ |__/ |__/        | $$____/  \____  $$
                                          | $$       /$$  | $$
                                          | $$      |  $$$$$$/
by lexi/rekushi <3                        |__/       \______/ 

------------------------------------------------------------"""

BASE_URL = "https://www.smashcustommusic.net/json"
HEADERS = {"User-Agent": "scm-py/0.1"}

def clear_console():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def display_ascii_art():
    clear_console()
    print(ASCII_ART)
    print("")

def offer_install_scm_cli():
    message = """You are using scm-py on a Unix-based operating system, which supports scm-cli. scm-cli is recommended, since it receives updates and new features, while also not depending on Python to run.

scm-py is only suggested for use on Windows operating systems.

Would you like to install scm-cli? Y/N
"""
    print(message)
    choice = get_key().lower()
    print(choice.upper())  # Show the key press for clarity
    if choice == 'y':
        subprocess.run("curl -sL https://raw.githubusercontent.com/RekuNote/scm-cli/main/install.sh | bash", shell=True)
        print("\nTo run scm-cli, run the command:\nscm-cli")
        sys.exit(0)
    elif choice == 'n':
        return

def list_games():
    page = 0
    per_page = 20
    while True:
        offset = page * per_page
        response = requests.get(f"{BASE_URL}/gamelist/", headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            game_count = data['game_count']
            total_pages = (game_count + per_page - 1) // per_page  # Calculate total pages
            games = data['games'][offset:offset + per_page]
            
            if not games:
                print("No more games to display.")
                break
            
            display_ascii_art()
            print(f"Total games available: {game_count}\n")
            print(f"Games (Page {page + 1} of {total_pages}):\n")
            for game in games:
                print(f"{game['game_id']}: {game['game_name']} ({game['song_count']} songs)")
            
            print("\nX to Exit")
            print("N to show Next Entries")
            print("B to show Previous Entries")
            print("G to Select Game")
            print("S to Search Game")
            print()

            next_page_key = get_key().upper()
            
            if next_page_key == "N" and page + 1 < total_pages:
                page += 1
            elif next_page_key == "B" and page > 0:
                page -= 1
            elif next_page_key == "G":
                game_id = input("Insert Game ID, or leave blank to cancel: ").strip()
                if game_id:
                    search_songs(game_id)
            elif next_page_key == "S":
                display_ascii_art()
                print("Type the name of the game you would like to search for, or leave empty to cancel: ")
                search_games()
            elif next_page_key == "X":
                exit(0)
            else:
                print("Invalid option. Please try again.")
        else:
            print("Error: Unable to fetch data from the server.")
            break

def search_games():
    response = requests.get(f"{BASE_URL}/gamelist/", headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        game_list = data['games']
        search_term = input().strip()
        if search_term:
            search_results = [game for game in game_list if search_term.lower() in game['game_name'].lower()]
            search_count = len(search_results)
            page = 0
            per_page = 20
            total_pages = (search_count + per_page - 1) // per_page  # Calculate total pages
            while True:
                offset = page * per_page
                display_ascii_art()
                print(f"{search_count} results for \"{search_term}\":\n")
                print(f"Results (Page {page + 1} of {total_pages}):\n")
                for game in search_results[offset:offset + per_page]:
                    print(f"{game['game_id']}: {game['game_name']} ({game['song_count']} songs)")
                
                print("\nX to Exit")
                print("R to Return")
                print("N to show Next Entries")
                print("B to show Previous Entries")
                print("G to Select Game")
                print()

                search_page_key = get_key().upper()
                
                if search_page_key == "N" and page + 1 < total_pages:
                    page += 1
                elif search_page_key == "B" and page > 0:
                    page -= 1
                elif search_page_key == "G":
                    game_id = input("Insert Game ID, or leave blank to return to the game list: ").strip()
                    if game_id:
                        search_songs(game_id)
                        break
                elif search_page_key == "R":
                    list_games()
                    return
                elif search_page_key == "X":
                    exit(0)
                else:
                    print("Invalid option. Please try again.")
    else:
        print("Error: Unable to fetch data from the server.")

def search_songs(game_id):
    page = 0
    per_page = 20
    while True:
        offset = page * per_page
        response = requests.get(f"{BASE_URL}/game/{game_id}", headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            game_name = data['game_name']
            songs = data['songs'][offset:offset + per_page]
            song_count = len(data['songs'])
            total_pages = (song_count + per_page - 1) // per_page  # Calculate total pages
            
            display_ascii_art()
            print(f"Game: {game_name}\n")
            print(f"Songs (Page {page + 1} of {total_pages}):\n")
            for song in songs:
                song_length = song.get('song_length', 'N/A')
                print(f"{song['song_id']}: {song['song_name']} ({song_length} seconds)")
            
            print("\nX to Exit")
            print("R to Return")
            print("N to Show Next Entries")
            print("B to Show Previous Entries")
            print("S to Select Song")
            print()

            next_page_key = get_key().upper()
            
            if next_page_key == "N" and page + 1 < total_pages:
                page += 1
            elif next_page_key == "B" and page > 0:
                page -= 1
            elif next_page_key == "S":
                song_id = input("Insert Song ID, or leave blank to cancel: ").strip()
                if song_id:
                    show_track_info(song_id)
            elif next_page_key == "R":
                list_games()
            elif next_page_key == "X":
                exit(0)
            else:
                print("Invalid option. Please try again.")
        else:
            print("Error: Unable to fetch data from the server.")
            break

def show_track_info(song_id):
    response = requests.get(f"{BASE_URL}/song/{song_id}", headers=HEADERS)
    
    if response.status_code == 200:
        data = response.json()
        song_name = data['name']
        description = data['description']
        game_name = data['game_name']
        theme_type = data.get('theme_type', 'N/A')
        uploader = data['uploader']
        length = data['length']
        size = data['size']
        downloads = data['downloads']
        loop_type = data['loop_type']
        start_loop_point = data['start_loop_point']
        end_loop_point = data['end_loop_point']
        sample_rate = data['sample_rate']

        length_minutes = int(length) // 60
        length_seconds = int(length) % 60
        size_mb = int(size) / 1048576

        display_ascii_art()
        print(f"\nSong Name: {song_name}\n{description}\n")
        print(f"Game: {game_name}")
        print(f"Song Type: {theme_type}")
        print(f"Song ID: {song_id}")
        print(f"Uploaded By: {uploader}")
        print(f"Length: {length_minutes}m {length_seconds}s")
        print(f"BRSTM Size: {size_mb:.2f}MB")
        print(f"Downloads: {downloads}")
        print(f"Loop Type: {loop_type}")
        print(f"Start Loop Point: {start_loop_point}")
        print(f"End Loop Point: {end_loop_point}")
        print(f"Sample Rate: {sample_rate}\n")

        print("X to Exit")
        print("R to Return")
        print("D for Download Options")
        print()

        user_input = get_key().upper()

        if user_input == "D":
            display_ascii_art()
            print("Download Options:\n")
            print("1 to Download BRSTM")
            print("2 to Download BCSTM")
            print("3 to Download BFSTM (Wii U)")
            print("4 to Download BFSTM (Switch)")
            print("5 to Download BWAV")
            print("6 to Download NUS3Audio")
            print("R to Return")
            print("X to Exit")
            print()

            download_option = get_key().upper()

            download_formats = {
                "1": "brstm",
                "2": "bcstm",
                "3": "bfstm",
                "4": "sw_bfstm",
                "5": "bwav",
                "6": "nus3audio"
            }

            if download_option in download_formats:
                download_file(song_id, download_formats[download_option])
            elif download_option == "R":
                return
            elif download_option == "X":
                exit(0)
            else:
                print("Invalid option. Please try again.")
        elif user_input == "R":
            search_songs(song_id)
        elif user_input == "X":
            exit(0)
    else:
        print("Error: Unable to fetch data from the server.")

def download_file(song_id, download_format):
    output_paths = {
        "brstm": "brstm",
        "bcstm": "bcstm",
        "bfstm": "bfstm/wiiu",
        "sw_bfstm": "bfstm/switch",
        "bwav": "bwav",
        "nus3audio": "nus3audio"
    }

    output_path = os.path.join(os.getcwd(), output_paths[download_format])
    os.makedirs(output_path, exist_ok=True)

    download_url = f"https://www.smashcustommusic.net/{download_format}/{song_id}"

    try:
        with requests.get(download_url, stream=True, headers=HEADERS, timeout=10) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            block_size = 1024
            output_file = os.path.join(output_path, f"{song_id}.{download_format}")
            with open(output_file, 'wb') as f, tqdm(
                desc=output_file,
                total=total_size,
                unit='iB',
                unit_scale=True,
            ) as bar:
                for data in r.iter_content(block_size):
                    bar.update(len(data))
                    f.write(data)
        
        # Rename .sw_bfstm files to .bfstm in /switch directory
        if download_format == "sw_bfstm":
            new_output_file = output_file.replace(".sw_bfstm", ".bfstm")
            os.rename(output_file, new_output_file)
            output_file = new_output_file
        
        print(f"File downloaded successfully to {output_file}. Press any key to return.")
        get_key()
        show_track_info(song_id)
    except requests.exceptions.RequestException as e:
        print(f"Download failed: {e}")

# Main script logic
if __name__ == "__main__":
    if platform.system() in ["Linux", "Darwin"]:  # Unix-based systems: Linux and macOS
        display_ascii_art()
        offer_install_scm_cli()
    list_games()
