import typer
from rich.console import Console
from rich.table import Table
from checkers import InsightsChecker

app = typer.Typer()
console = Console()

@app.command()
def headline(name: str = "Admin"):
    console.print("[bold green]Success![/bold green] Welcome to rhcheck.")

@app.command()
def report():
    
    """Generate a system health and security report for RHEL"""
    
    # Creating the Table:
    table = Table(title="System Assessment Report")
    table.add_column("Category", style="cyan", no_wrap=True)
    table.add_column("Assessment", style="magenta")
    table.add_column("Status / Value", style="green")

    ##### Security Check #####
    selinux_status = InsightsChecker.check_selinux_status()
    # Applying color coding based on selinux configuration.
    if selinux_status == "enabled":
        status_style = "green"
    elif selinux_status == "Unknown":
        status_style = "yellow"
    else:
        status_style = "red"
    
    table.add_row("Security", "SELinux Status", selinux_status, style=status_style)
    
    ##### Hardware Metrics #####
    cpu = InsightsChecker.get_cpu_usage()
 
    if cpu < 80:
        cpu_style = "green"
    elif cpu >= 90:
        cpu_style = "red"
    elif cpu >= 80:
        cpu_style = "yellow"
    
    table.add_row("Hardware", "CPU Utilization", f"{cpu}%", style=cpu_style)
    
    ram = InsightsChecker.get_ram_usage()
    
    if ram < 80:
        ram_style = "green"
    elif ram >= 90:
        ram_style = "red"
    elif ram >= 80:
        ram_style = "yellow"
    
    table.add_row("Hardware", "RAM Utilization", f"{ram}%", style=ram_style)
    
    disk = InsightsChecker.get_disk_usage()

    if disk < 85:
        disk_style = "green"
    elif disk < 95:
        disk_style = "red"
    else:
        disk_style = "yellow"
    
    table.add_row("Hardware", "Disk Utilization (/)", f"{disk}%", style=disk_style)
    
    ##### Subscription Status Check #####
    
    sub_status = InsightsChecker.check_subscription_status()
    if sub_status =="Registered" or sub_status == "Registered (SCA Active)":
        sub_style = "green"
    else:
        sub_style = "red"
    
    table.add_row("RHSM", "Subscription Status", sub_status, style=sub_style)
    
    ##### Package Check #####
    pkg_status = InsightsChecker.check_outdated_packages()
    if pkg_status == "Up to Date":
        pkg_style = "green"
    elif pkg_status == "Updates Available":
        pkg_style = "yellow"
    else:
        pkg_style = "red"
    
    table.add_row("Software", "Package Status", pkg_status, style=pkg_style)
    
    ##### File Permission Check #####
    shadow_perms = InsightsChecker.check_file_permissions("/etc/shadow")
    # 0o600 or 0o000 are standard secure compliance baselines for /etc/shadow
    if shadow_perms == 0o600 or shadow_perms == 0o000 or shadow_perms == 0o0:
        shadow_style = "green"
    else:
        shadow_style = "red"
    
    table.add_row("Security", "Perms (/etc/shadow)", shadow_perms, style=shadow_style)
    
    ##### Zombie Process Check #####
    zombies = InsightsChecker.detect_zombie_processes()
    if zombies == 0:
        zombies_style = "green"
    else:
        zombies_style = "red"
    
    table.add_row("Diagnostics", "Zombie Processes", str(zombies), style=zombies_style)
    
    
    ####Print the finished table to the screen.
    console.print(table)
    
if __name__ == "__main__":
    app()