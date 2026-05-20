import subprocess
import psutil
import os

class InsightsChecker:
    
    @staticmethod
    def check_selinux_status():
        """Checks SELinux status across RHEL 8, 9 and 10"""
        try:
            result = subprocess.run(
                ['sestatus'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                check=True
            )
            for line in result.stdout.splitlines():
                if "SELinux status:" in line:
                    return line.split(":")[1].strip()
                return "Unknown"
        except(FileNotFoundError, subprocess.CalledProcessError):
            return "Disabled/Not Found"
        
    
    @staticmethod
    def get_cpu_usage():
        """Returns the current CPU usage percentage"""
        # interval = None take an instantaneous reading without blocking execution
        return psutil.cpu_percent(interval=None)
    
    @staticmethod
    def get_ram_usage():
        """Returns the current RAM usage percentage"""
        return psutil.virtual_memory().percent
    
    @staticmethod
    def get_disk_usage():
        """Return the root partition disk usage percentage"""
        return psutil.disk_usage('/').percent
    
    @staticmethod
    def check_subscription_status():
        """Check Subscription Status across RHEL 8,9,10"""
        try:
            result = subprocess.run(
                ['subscription-manager', 'status'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines= True
            )
            if "Overall Status: Current" in result.stdout:
                return "Registered"
            elif "Simple Content Access" in result.stdout:
                return "Registered (SCA Active)"
            return "Unregistered / Issue Detected"
        except FileNotFoundError:
            return "RHSM Not Installed"
    
    @staticmethod
    def check_outdated_packages():
        """Checks for outdated packages via DNF exit codes across RHEL 8/9/10"""
        try:
            result = subprocess.run(
                ['dnf', 'check-update', '--quiet'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines= True
            )
            if result.returncode == 0:
                return "Up to Date"
            elif result.returncode == 100:
                return "Updates Available"
            else:
                return "Check Failed (Repo Issue?)"
        except FileNotFoundError:
            return "DNF not found."
        
    @staticmethod
    def check_file_permissions(filepath):
        """Safely extracts octal file permissions for RHEL Compliance mapping"""
        if not os.path.exists(filepath):
            return "File Not Found"
        try:
            mode = os.stat(filepath).st_mode
            # Extract only the lower 3 octal permission bits (e.g '0o600')
            return oct(mode & 0o777)
        except PermissionError:
            return "Permission Denied"
    
    @staticmethod
    def detect_zombie_processes():
        """Count active zombie acriss the system"""
        zombie_count = 0
        # process_iter parses kernel maps efficiently across RHEL 8,9 and 10
        for proc in psutil.process_iter(['status']):
            try:
                if proc.info['status'] == psutil.STATUS_ZOMBIE:
                    zombie_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return zombie_count