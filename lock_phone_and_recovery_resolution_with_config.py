import subprocess
from time import sleep
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime
import configparser

# 读取配置文件
config = configparser.ConfigParser()
config.read("config.ini")


def send_error_email(error_message):
    """Send error notification email"""
    try:
        # Email settings
        smtp_server = config["Email"]["smtp_server"]
        smtp_port = int(config["Email"]["smtp_port"])
        sender = config["Email"]["sender"]
        receiver = config["Email"]["receiver"]
        password = config["Email"]["password"]

        # Create message
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subject = f"MAA Task Failed - {current_time}"
        content = f"""
        Task execution failed at {current_time}

        Error details:
        {error_message}
        """

        msg = MIMEText(content, "plain", "utf-8")
        msg["Subject"] = Header(subject, "utf-8")
        msg["From"] = sender
        msg["To"] = receiver

        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, [receiver], msg.as_string())
            print("Error notification email sent successfully")
    except Exception as e:
        print(f"Failed to send error email: {str(e)}")


def check_adb_device():
    """Check if any ADB device is connected and authorized"""
    try:
        # Kill existing ADB server to ensure fresh start
        subprocess.run("adb kill-server", shell=True, check=True)
        sleep(2)
        # Start ADB server
        subprocess.run("adb start-server", shell=True, check=True)
        sleep(2)

        # Try to connect via IP
        device_ip = config["ADB"]["device_ip"]
        print(f"Trying to connect via IP: {device_ip}...")
        connect_result = subprocess.run(
            f"adb connect {device_ip}",
            shell=True,
            capture_output=True,
            text=True,
        )
        print(f"Connect result: {connect_result.stdout}")
        sleep(2)

        # Get device list
        result = subprocess.run(
            "adb devices", shell=True, capture_output=True, text=True, check=True
        )

        # Parse the output
        lines = result.stdout.strip().split("\n")
        if len(lines) <= 1:  # Only has the "List of devices attached" header
            error_msg = "No ADB devices found. Please check your connection."
            print(error_msg)
            send_error_email(error_msg)
            return False

        # Check if any device is properly authorized
        for line in lines[1:]:  # Skip the header line
            if line.strip() and not line.strip().endswith("unauthorized"):
                print("Found connected device:", line.strip())
                return True

        error_msg = "Found device but it's not authorized. Please check your phone and accept the debugging prompt."
        print(error_msg)
        send_error_email(error_msg)
        return False

    except subprocess.CalledProcessError as e:
        error_msg = f"Error checking ADB devices: {e}"
        print(error_msg)
        send_error_email(error_msg)
        return False


def set_resolution_and_launch_app():
    try:
        # First check ADB device connection
        if not check_adb_device():
            print("Please connect your device and try again.")
            return

        print("Setting screen resolution to 2400x1080...")
        # Set screen resolution
        subprocess.run("adb shell wm size 1080x2400", check=True)
        sleep(2)

        # 从 config.ini 中读取包名和应用名称
        package_name = config["App"]["package_name"]
        app_name = config["App"]["app_name"]
        print(f"Checking for package: {package_name}")

        # First, list all packages and print the grep result for debugging
        print(f"Searching for {app_name} package...")
        list_result = subprocess.run(
            "adb shell pm list packages",
            shell=True,
            capture_output=True,
            text=True,
        )
        print("All packages:", list_result.stdout)

        # Direct check if the package exists
        check_result = subprocess.run(
            f"adb shell pm path {package_name}",
            shell=True,
            capture_output=True,
            text=True,
        )

        if check_result.returncode == 0 and check_result.stdout.strip():
            print(f"Found {app_name} package: {package_name}")
            print(f"Package path: {check_result.stdout.strip()}")

            # Try to launch directly with known activity
            print(f"Attempting to launch {app_name}...")
            launch_result = subprocess.run(
                f"adb shell am start -n {package_name}/.DroidCamActivity",
                shell=True,
                capture_output=True,
                text=True,
            )

            if launch_result.returncode == 0:
                print(f"{app_name} launched successfully!")
            else:
                error_msg = f"Failed to launch {app_name} with main activity, trying fallback method..."
                print(error_msg)
                # Fallback to monkey
                monkey_result = subprocess.run(
                    f"adb shell monkey -p {package_name} 1",
                    shell=True,
                    capture_output=True,
                    text=True,
                )
                if monkey_result.returncode == 0:
                    print(f"{app_name} launched using fallback method")
                else:
                    error_msg = f"Fallback launch failed: {monkey_result.stdout}"
                    print(error_msg)
                    send_error_email(error_msg)
        else:
            error_msg = f"{app_name} is not installed on the device\npm path result: {check_result.stdout}\npm path return code: {check_result.returncode}"
            print(error_msg)
            send_error_email(error_msg)

    except subprocess.CalledProcessError as e:
        error_msg = f"Error executing ADB command: {e}\nCommand output: {e.output.decode() if e.output else 'No output'}"
        print(error_msg)
        send_error_email(error_msg)
    except Exception as e:
        error_msg = f"An error occurred: {e}"
        print(error_msg)
        send_error_email(error_msg)


if __name__ == "__main__":
    try:
        set_resolution_and_launch_app()
        print("\nProgram success")
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
