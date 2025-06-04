import subprocess
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime
from time import sleep
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
        subject = f"Phone Unlock Failed - {current_time}"
        content = f"""
        Phone unlock task failed at {current_time}

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


print("start unlock")


def check_adb_device():
    """Check if any ADB device is connected and authorized"""
    try:
        # Kill existing ADB server to ensure fresh start
        subprocess.run("adb kill-server", shell=True, check=True)
        sleep(5)
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


try:
    # First check ADB device connection
    if not check_adb_device():
        error_msg = "Please connect your device and try again."
        print(error_msg)
        send_error_email(error_msg)
        raise Exception("ADB device not found")

    # Check if unlock is required
    require_unlock = config["ADB"].getboolean("require_unlock", True)
    if not require_unlock:
        print("Unlock step skipped as per configuration")
        # 跳过后续解锁步骤
        exit()

    print("Setting screen resolution to 1280x720...")
    # Set screen resolution
    subprocess.run("adb shell wm size 720x1280", check=True)
    sleep(2)
    subprocess.Popen("adb shell input keyevent 26")
    sleep(3)
    subprocess.Popen("adb shell input swipe 400 1000 400 300")
    sleep(3)
    # Get unlock password from config
    lock_password = config["ADB"]["lock_password"]
    subprocess.Popen(f"adb shell input text {lock_password}")
    sleep(3)

    # Check if screen is unlocked using dumpsys
    try:
        # Get full window state
        window_state = subprocess.check_output(
            "adb shell dumpsys window", shell=True
        ).decode()

        # Check multiple indicators
        if (
            "mDreamingLockscreen=false" in window_state
            or "mKeyguardShowing=false" in window_state
            or "isStatusBarKeyguard=false" in window_state
        ):
            print("Screen is unlocked!")
        else:
            error_msg = "Screen might still be locked! Trying unlock again..."
            print(error_msg)
            # Try unlock again
            lock_password = config["ADB"]["lock_password"]
            subprocess.Popen(f"adb shell input text {lock_password}")
            sleep(3)

            # Check again
            window_state = subprocess.check_output(
                "adb shell dumpsys window", shell=True
            ).decode()
            if (
                "mDreamingLockscreen=false" in window_state
                or "mKeyguardShowing=false" in window_state
                or "isStatusBarKeyguard=false" in window_state
            ):
                print("Screen is now unlocked!")
            else:
                error_msg = "Failed to unlock screen after retry"
                print(error_msg)
                send_error_email(error_msg)

    except subprocess.CalledProcessError as e:
        error_msg = f"Could not determine screen lock state: {str(e)}\nReturn code: {e.returncode}\nOutput: {e.output.decode() if e.output else 'No output'}"
        print(error_msg)
        send_error_email(error_msg)

except Exception as e:
    error_msg = f"Error: {str(e)}"
    print(error_msg)
    send_error_email(error_msg)
