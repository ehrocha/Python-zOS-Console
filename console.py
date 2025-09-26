import readline
import os
from zosmf import ZOSMFClient
from uss import USSClient

class SessionContext:
    def session_info(self):
        return f"\033[96mUserID: {self.system['user']} | Profile: {self.system['name']} | IP: {self.system['host']}\033[0m"
    def __init__(self, system):
        self.system = system
        user = system['user']
        password = system['password']
        ssh_port = system.get('ssh_port', 22)
        zosmf_port = system.get('zosmf_port', 443)
        self.zosmf = ZOSMFClient(
            system['host'],
            user,
            password,
            zosmf_port
        )
        self.uss = USSClient(
            system['host'],
            user,
            password,
            ssh_port
        )


def main_menu(systems):
    print("Select a system:")
    for idx, sys in enumerate(systems):
        print(f"{idx+1}. {sys['name']}")
    choice = int(input("Select System: ")) - 1
    selected = systems[choice]
    return selected


def command_loop(context, systems):
    def print_session_info():
        print(context.session_info())
    os.system('clear')
    print_session_info()

    # Enable command history and arrow key navigation
    histfile = os.path.expanduser('~/.console_history')
    try:
        readline.read_history_file(histfile)
    except FileNotFoundError:
        pass
    import atexit
    atexit.register(readline.write_history_file, histfile)

    while True:
        lpar_prompt = f"\033[1;33m{context.system['name']}\033[0m> "
        cmd = input(lpar_prompt)
        cmd_strip = cmd.strip()
        if not cmd_strip:
            continue
        cmd_upper = cmd_strip.upper()
        if cmd_upper.startswith("START "):
            subcmd = cmd_strip[6:].strip().upper()
            import subprocess
            sys = context.system
            ssh_port = sys.get('ssh_port', 22)
            port_3270 = sys.get('3270_port', 23)
            if subcmd == "3270":
                if sys.get('secure_3270', False):
                    cmdline = [
                        "x3270",
                        "-title", f"{sys['name']}",
                        f"L:Y:{sys['host']}:{port_3270}"
                    ]
                else:
                    cmdline = [
                        "x3270",
                        "-title", f"{sys['name']}",
                        f"{sys['host']}:{port_3270}"
                    ]
                subprocess.Popen(cmdline)
            elif subcmd == "SSH":
                wt_path = "/mnt/c/Users/EduardoHenriqueRocha/AppData/Local/Microsoft/WindowsApps/wt.exe"
                cmdline = [
                    wt_path,
                    "--window", "new",
                    "--profile", "Ubuntu",
                    "bash", "-ic",
                    f"ssh {sys['user']}@{sys['host']} -p {ssh_port}"
                ]
                subprocess.Popen(cmdline)
            elif subcmd == "SFTP":
                wt_path = "/mnt/c/Users/EduardoHenriqueRocha/AppData/Local/Microsoft/WindowsApps/wt.exe"
                cmdline = [
                    wt_path,
                    "--window", "new",
                    "--profile", "Ubuntu",
                    "bash", "-ic",
                    f"sftp -P {ssh_port} {sys['user']}@{sys['host']}"
                ]
                subprocess.Popen(cmdline)
            else:
                print("Unknown START subcommand. Use: START 3270, START SSH, START SFTP")
        elif cmd_upper.startswith("TSO "):
            tso_cmd = cmd_strip[4:].strip()
            try:
                result = context.zosmf.tso_command(tso_cmd)
                print(f"\033[96m{result}\033[0m")
            except Exception as e:
                print(f"TSO command error: {e}")
        elif cmd_upper.startswith("ZOS "):
            zos_cmd = cmd_strip[4:].strip()
            try:
                result = context.zosmf.zos_command(zos_cmd)
                print(f"\033[92m{result}\033[0m")
            except Exception as e:
                print(f"ZOS command error: {e}")
        elif cmd_upper.startswith("USS "):
            uss_cmd = cmd_strip[4:].strip()
            try:
                stdout, stderr = context.uss.run_command(uss_cmd)
                if stdout:
                    print(f"\033[95m{stdout}\033[0m", end='')  # Magenta for stdout
                if stderr:
                    print(f"\033[91m{stderr}\033[0m", end='')  # Red for stderr
            except Exception as e:
                print(f"USS command error: {e}")
        elif cmd_upper == "SWITCH":
            system = main_menu(systems)
            context = SessionContext(system)
            os.system('clear')
            print_session_info()
        elif cmd_upper.startswith("=G"):
            sysname = cmd_strip[2:].strip()
            found = next((s for s in systems if s['name'].lower() == sysname.lower()), None)
            if found:
                context = SessionContext(found)
                os.system('clear')
                print_session_info()
                print(f"Switched to system: {found['name']}")
            else:
                print(f"System '{sysname}' not found.")
        elif cmd_upper == "CLEAR":
            os.system('clear')
            print_session_info()
        elif cmd_upper == "EXIT":
            break
        else:
            print("Unknown command. Use TSO, ZOS, USS, START, switch, clear, or exit.")
