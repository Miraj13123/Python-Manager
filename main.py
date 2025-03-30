import os
import subprocess
import sys
from datetime import datetime

def get_pip_package_times():
    try:
        result = subprocess.check_output([sys.executable, "-m", "pip", "list", "--format=freeze"], text=True)
        packages = {}
        for line in result.split('\n'):
            if line.strip():
                pkg_name = line.split('==')[0]
                try:
                    pkg_info = subprocess.check_output([sys.executable, "-m", "pip", "show", pkg_name], text=True)
                    for info_line in pkg_info.split('\n'):
                        if info_line.startswith('Location:'):
                            location = info_line.split(':', 1)[1].strip()
                            pkg_path = os.path.join(location, pkg_name.lower().replace('-', '_') + '*.dist-info')
                            import glob
                            dist_info = glob.glob(pkg_path)
                            if dist_info:
                                install_time = os.path.getctime(dist_info[0])
                                packages[pkg_name] = install_time
                            else:
                                packages[pkg_name] = 0  # Default time if no metadata
                            break
                except:
                    packages[pkg_name] = 0  # Default time if error
        return packages
    except:
        return {}

def get_apt_package_times():
    try:
        result = subprocess.check_output(["dpkg", "-l"], text=True)
        packages = {}
        for line in result.split('\n'):
            if line.strip() and 'python3-' in line.lower():
                parts = line.split()
                if len(parts) > 1 and parts[0] == 'ii':  # Installed packages only
                    pkg_name = parts[1]
                    try:
                        pkg_info = subprocess.check_output(["dpkg-query", "-s", pkg_name], text=True)
                        for info_line in pkg_info.split('\n'):
                            if info_line.startswith('Installed-Time:'):
                                install_time = float(info_line.split(':')[1].strip())
                                packages[pkg_name] = install_time
                                break
                        else:
                            packages[pkg_name] = 0  # Default time if no Installed-Time
                    except:
                        packages[pkg_name] = 0  # Default time if error
        return packages
    except:
        return {}

def get_brew_package_times():
    try:
        result = subprocess.check_output(["brew", "list"], text=True)
        packages = {}
        for line in result.split('\n'):
            if line.strip() and 'python' in line.lower():
                pkg_name = line.strip()
                try:
                    install_time = os.path.getctime(f"/usr/local/Cellar/{pkg_name}")
                    packages[pkg_name] = install_time
                except:
                    packages[pkg_name] = 0  # Default time if error
        return packages
    except:
        return {}

def list_packages(os_choice, sort_type):
    try:
        if os_choice == "1":  # Linux
            packages = get_apt_package_times()
            if not packages:
                print("No Python3 packages found.")
                return []
            if sort_type == "1":  # Time sorting
                sorted_packages = sorted(packages.items(), key=lambda x: x[1])
                print("\nInstalled Linux (apt) packages (time sorted - latest at bottom):")
            else:  # Alphabetical sorting
                sorted_packages = sorted(packages.items(), key=lambda x: x[0])
                print("\nInstalled Linux (apt) packages (alphabetical):")
        
        elif os_choice == "2":  # Windows
            packages = get_pip_package_times()
            if not packages:
                print("No pip packages found.")
                return []
            if sort_type == "1":  # Time sorting
                sorted_packages = sorted(packages.items(), key=lambda x: x[1])
                print("\nInstalled Windows (pip) packages (time sorted - latest at bottom):")
            else:  # Alphabetical sorting
                sorted_packages = sorted(packages.items(), key=lambda x: x[0])
                print("\nInstalled Windows (pip) packages (alphabetical):")
        
        elif os_choice == "3":  # Mac
            packages = get_brew_package_times()
            if not packages:
                print("No Python-related brew packages found.")
                return []
            if sort_type == "1":  # Time sorting
                sorted_packages = sorted(packages.items(), key=lambda x: x[1])
                print("\nInstalled Mac (brew) packages (time sorted - latest at bottom):")
            else:  # Alphabetical sorting
                sorted_packages = sorted(packages.items(), key=lambda x: x[0])
                print("\nInstalled Mac (brew) packages (alphabetical):")
        
        pkg_list = []
        for i, (pkg, install_time) in enumerate(sorted_packages, 1):
            time_str = datetime.fromtimestamp(install_time).strftime('%Y-%m-%d %H:%M:%S') if install_time else "Unknown"
            print(f"{i}. {pkg} (Installed: {time_str})")
            pkg_list.append(pkg)
        return pkg_list
    except Exception as e:
        print(f"Error listing packages: {e}")
        return []

def search_pip_package(search_term):
    try:
        result = subprocess.check_output([sys.executable, "-m", "pip", "search", search_term], text=True)
        packages = []
        for line in result.split('\n'):
            if line.strip() and '(' in line:
                package_name = line.split()[0]
                packages.append(package_name)
        return packages[:15]
    except:
        return []

def search_apt_package(search_term):
    try:
        result = subprocess.check_output(["apt-cache", "search", search_term], text=True)
        packages = []
        for line in result.split('\n'):
            if line.strip():
                package_name = line.split()[0]
                if package_name.startswith('python3-'):
                    packages.append(package_name)
        return packages[:15]
    except:
        return []

def search_brew_package(search_term):
    try:
        result = subprocess.check_output(["brew", "search", search_term], text=True)
        packages = []
        for line in result.split('\n'):
            if line.strip() and 'python' in line.lower():
                packages.append(line.strip())
        return packages[:15]
    except:
        return []

def install_linux(package):
    os.system(f"sudo apt-get install {package} -y")

def install_windows(package):
    os.system(f"pip install {package}")

def install_mac(package):
    os.system(f"brew install {package}")

def uninstall_linux(package):
    os.system(f"sudo apt-get remove {package} -y")

def uninstall_windows(package):
    os.system(f"pip uninstall {package} -y")

def uninstall_mac(package):
    os.system(f"brew uninstall {package}")

def display_search_results(packages, os_type):
    if not packages:
        print(f"No {os_type} packages found.")
        return None
    
    print(f"\nFound {os_type} packages:")
    for i, pkg in enumerate(packages, 1):
        print(f"{i}. {pkg}")
    
    choice = input("Enter the number of the package to install (or 0 to skip): ")
    if choice == "0":
        return None
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(packages):
            return packages[idx]
        else:
            print("Invalid selection.")
            return None
    except ValueError:
        print("Invalid input.")
        return None

def handle_package_removal(os_choice, pkg_list):
    while True:
        print("\nPackage options:")
        print("1. Delete/Remove package")
        print("0. Go back")
        choice = input("Enter your choice (0-1): ")
        
        if choice == "0":
            break
        elif choice == "1":
            pkg_num = input("Enter the package number to remove (or 0 to cancel): ")
            if pkg_num == "0":
                continue
            try:
                idx = int(pkg_num) - 1
                if 0 <= idx < len(pkg_list):
                    pkg_to_remove = pkg_list[idx]
                    if os_choice == "1":
                        uninstall_linux(pkg_to_remove)
                    elif os_choice == "2":
                        uninstall_windows(pkg_to_remove)
                    elif os_choice == "3":
                        uninstall_mac(pkg_to_remove)
                    print(f"Removed {pkg_to_remove}")
                else:
                    print("Invalid package number.")
            except ValueError:
                print("Invalid input.")
        else:
            print("Invalid choice. Please select 0 or 1.")

def list_and_manage_packages(os_choice):
    while True:
        print("\nSelect sort type:")
        print("1. Sort by installation time (latest at bottom)")
        print("2. Sort alphabetically")
        print("0. Back")
        sort_type = input("Enter your choice (0-2): ")
        
        if sort_type == "0":
            break
            
        if sort_type in ["1", "2"]:
            pkg_list = list_packages(os_choice, sort_type)
            if pkg_list:
                handle_package_removal(os_choice, pkg_list)
        else:
            print("Invalid choice. Please select 0, 1, or 2.")

def handle_os_choice(os_choice):
    while True:
        print(f"\nSelected OS: {'Linux' if os_choice == '1' else 'Windows' if os_choice == '2' else 'Mac'}")
        print("1. List installed packages")
        print("2. Download new packages")
        print("0. Back to OS selection")
        action = input("Enter your choice (0-2): ")
        
        if action == "0":
            break
            
        elif action == "1":
            list_and_manage_packages(os_choice)
                
        elif action == "2":
            search_term = input("Enter what you want to search for: ")
            if os_choice == "1":
                packages = search_apt_package(search_term)
                selected_package = display_search_results(packages, "Linux")
                if selected_package:
                    install_linux(selected_package)
            elif os_choice == "2":
                packages = search_pip_package(search_term)
                selected_package = display_search_results(packages, "Windows")
                if selected_package:
                    install_windows(selected_package)
            elif os_choice == "3":
                packages = search_brew_package(search_term)
                selected_package = display_search_results(packages, "Mac")
                if selected_package:
                    install_mac(selected_package)
        else:
            print("Invalid choice. Please select 0, 1, or 2.")

def main():
    while True:
        print("\nSelect your operating system:")
        print("1. Linux")
        print("2. Windows")
        print("3. Mac")
        print("0. Exit")
        choice = input("Enter the number corresponding to your OS (0-3): ")
        
        if choice == "0":
            print("Goodbye!")
            break
            
        if choice in ["1", "2", "3"]:
            handle_os_choice(choice)
        else:
            print("Invalid choice. Please select a valid option (0-3).")

if __name__ == "__main__":
    main()
