"""Python 3.12-compatible OS-Ken launcher for this OpenFlow application."""
from os_ken.base import app_manager
if __name__ == '__main__':
    app_manager.AppManager.run_apps(['os_ken.controller.ofp_handler','controller.sdn_controller'])
