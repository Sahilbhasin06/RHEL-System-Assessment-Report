from unittest.mock import patch, MagicMock
from src.checkers import InsightsChecker
import psutil

@patch('subprocess.run')
def test_check_selinux_status_enforcing(mock_run):
    """
    Test that our checker correctly extracts 'enabled' when 
    sestatus outputs standard RHEL enforcing details.
    """
    # We mock out what a RHEL system would actually return in the terminal.
    mock_proc = MagicMock()
    mock_proc.stdout = "SELinux status: enabled\nCurrent mode:  enforcing"
    mock_run.return_value = mock_proc
    
    # We will call our function(Yet to be created)
    status = InsightsChecker.check_selinux_status()
    
    # We assert that our function correctly parses the terminal output
    assert status == "enabled"

@patch('subprocess.run')
def test_check_selinux_status_disabled(mock_run):
    """Test the fallback behavior if 'sestatus' fails or isn't found."""
    # Setup: Force the mocked command to raise an error
    mock_run.side_effect = FileNotFoundError
    
    #Execution
    status = InsightsChecker.check_selinux_status()
    
    #Assertion
    assert status == "Disabled/Not Found"
    
@patch('psutil.cpu_percent')
def test_get_cpu_usage(mock_cpu):
    # Setting up Mock CPU utilization at 45.5%
    mock_cpu.return_value = 45.5
    
    # Execution
    cpu = InsightsChecker.get_cpu_usage()
    
    # Assertion
    assert cpu == 45.5
    
@patch('psutil.virtual_memory')
def test_get_ram_usage(mock_ram):
    # Setting up Mock virtual memory to return an object where .percent is 70.2
    mock_mem_obj = MagicMock()
    mock_mem_obj.percent = 70.2
    mock_ram.return_value = mock_mem_obj
    
    # Execution
    ram = InsightsChecker.get_ram_usage()
    
    # Assertion
    assert ram == 70.2
    
@patch('psutil.disk_usage')
def test_get_disk_usage(mock_disk):
    # Setting up Mock disk usage to return an object where .percent is 12.4%
    mock_disk_obj = MagicMock()
    mock_disk_obj.percent = 12.4
    mock_disk.return_value = mock_disk_obj
    
    # Execution
    disk = InsightsChecker.get_disk_usage()
    
    # Assertion
    assert disk == 12.4

@patch('subprocess.run')
def test_check_subscription_status_registered_classic(mock_run):
    # Simulating a successfully registered system
    mock_proc = MagicMock()
    mock_proc.stdout = "Overall Status: Current\nContent Access Mode: org"
    mock_run.return_value = mock_proc
    
    # Execution
    status = InsightsChecker.check_subscription_status()
    
    # Assertion
    assert status == "Registered"

@patch('subprocess.run')
def test_check_subscription_status_registered_sca(mock_run):
    # Simulating a successfully registered system with SCA
    mock_proc = MagicMock()
    mock_proc.stdout = "Overall Status: Disabled\nContent Access Mode is set to Simple Content Access. This host has access to content"
    mock_run.return_value = mock_proc
    
    # Execution
    status = InsightsChecker.check_subscription_status()
    
    # Assertion
    assert status == "Registered (SCA Active)"
    
@patch('subprocess.run')
def test_check_subscription_status_unregistered(mock_run):
    # Simulating an unregistered system
    mock_proc = MagicMock()
    mock_proc.stdout = "Overall Status: Unknown\nSystem is not registered."
    mock_run.return_value = mock_proc
    
    # Execution
    status = InsightsChecker.check_subscription_status()
    
    # Assertion
    assert status == "Unregistered / Issue Detected"

@patch('subprocess.run')
def test_check_package_up_to_date(mock_run):
    # Simulating exit code 0 (System is fully patched)
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_run.return_value = mock_proc
    
    # Execution
    status = InsightsChecker.check_outdated_packages()
    
    # Assertion
    assert status == "Up to Date"
    
@patch('subprocess.run')
def test_check_packages_update_available(mock_run):
    # Simulating exit code 100 (DNF indicates updates are ready)
    mock_proc = MagicMock()
    mock_proc.returncode = 100
    mock_run.return_value = mock_proc
    
    # Execution
    status = InsightsChecker.check_outdated_packages()
    
    # Assertion
    assert status == "Updates Available"
    
@patch('os.path.exists')
@patch('os.stat')
def test_check_file_permissions_secure(mock_stat, mock_exists):
    # Simulating /etc/shadow exists and has 0o600 secure permissions
    mock_exists.return_value = True
    mock_stat.return_value.st_mode = 33152 # Integer mappint to 0o600 standard file permissions
    
    # Execution
    perms = InsightsChecker.check_file_permissions("/etc/shadow")
    
    # Assertion
    assert perms == "0o600"

@patch('psutil.process_iter')
def test_detect_zombie_processes_found(mock_process_iter):
    # Mock a process list containing exactly 1 running task and 1 zombie task
    proc_running = MagicMock()
    proc_running.info = {'status': psutil.STATUS_RUNNING}
    
    proc_zombie = MagicMock()
    proc_zombie.info = {'status': psutil.STATUS_ZOMBIE}
    
    mock_process_iter.return_value = [proc_running, proc_zombie]
    
    # Execution
    zombies = InsightsChecker.detect_zombie_processes()
    
    # Assertion
    assert zombies == 1