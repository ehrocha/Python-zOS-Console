from config import load_config
from console import main_menu, command_loop, SessionContext

def main():
    config = load_config()
    systems = config['systems']
    system = main_menu(systems)
    context = SessionContext(system)
    command_loop(context, systems)

if __name__ == "__main__":
    main()
