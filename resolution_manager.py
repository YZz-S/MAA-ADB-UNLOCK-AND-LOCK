import subprocess
import os
import configparser
from typing import Optional, Tuple


class ResolutionManager:
    """Manages screen resolution for ADB operations"""
    
    def __init__(self, config_file: str = "config.ini"):
        self.config = configparser.ConfigParser()
        self.config.read(config_file, encoding='utf-8')
        
        # Get configuration values
        self.unlock_resolution = self.config.get("Resolution", "unlock_resolution", fallback="720x1280")
        self.lock_resolution = self.config.get("Resolution", "lock_resolution", fallback="1080x2400")
        self.save_original = self.config.getboolean("Resolution", "save_original_resolution", fallback=True)
        self.original_file = self.config.get("Resolution", "original_resolution_file", fallback="original_resolution.txt")
    
    def get_current_resolution(self) -> Optional[str]:
        """Get current screen resolution from device"""
        try:
            result = subprocess.run(
                "adb shell wm size",
                shell=True,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse output like "Physical size: 1080x2400"
            output = result.stdout.strip()
            if "Physical size:" in output:
                resolution = output.split("Physical size:")[-1].strip()
                print(f"Current resolution: {resolution}")
                return resolution
            elif "Override size:" in output:
                # If there's an override, get that instead
                lines = output.split('\n')
                for line in lines:
                    if "Override size:" in line:
                        resolution = line.split("Override size:")[-1].strip()
                        print(f"Current override resolution: {resolution}")
                        return resolution
            else:
                # Try to extract resolution from any format
                words = output.split()
                for word in words:
                    if 'x' in word and word.replace('x', '').replace('0', '').replace('1', '').replace('2', '').replace('3', '').replace('4', '').replace('5', '').replace('6', '').replace('7', '').replace('8', '').replace('9', '') == '':
                        print(f"Extracted resolution: {word}")
                        return word
                        
            print(f"Could not parse resolution from: {output}")
            return None
            
        except subprocess.CalledProcessError as e:
            print(f"Error getting current resolution: {e}")
            return None
    
    def save_original_resolution(self) -> bool:
        """Save current resolution to file for later restoration"""
        if not self.save_original:
            print("Original resolution saving is disabled in config")
            return True
            
        current_res = self.get_current_resolution()
        if current_res:
            try:
                with open(self.original_file, 'w', encoding='utf-8') as f:
                    f.write(current_res)
                print(f"Original resolution {current_res} saved to {self.original_file}")
                return True
            except Exception as e:
                print(f"Error saving original resolution: {e}")
                return False
        else:
            print("Could not get current resolution to save")
            return False
    
    def load_original_resolution(self) -> Optional[str]:
        """Load original resolution from file"""
        if not os.path.exists(self.original_file):
            print(f"Original resolution file {self.original_file} not found")
            return None
            
        try:
            with open(self.original_file, 'r', encoding='utf-8') as f:
                resolution = f.read().strip()
                print(f"Loaded original resolution: {resolution}")
                return resolution
        except Exception as e:
            print(f"Error loading original resolution: {e}")
            return None
    
    def set_resolution(self, resolution: str) -> bool:
        """Set screen resolution"""
        try:
            cmd = f"adb shell wm size {resolution}"
            subprocess.run(cmd, shell=True, check=True)
            print(f"Resolution set to: {resolution}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error setting resolution to {resolution}: {e}")
            return False
    
    def reset_resolution(self) -> bool:
        """Reset resolution to device default"""
        try:
            subprocess.run("adb shell wm size reset", shell=True, check=True)
            print("Resolution reset to device default")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error resetting resolution: {e}")
            return False
    
    def set_unlock_resolution(self) -> bool:
        """Set resolution for unlock operation"""
        print(f"Setting unlock resolution: {self.unlock_resolution}")
        return self.set_resolution(self.unlock_resolution)
    
    def set_lock_resolution(self) -> bool:
        """Set resolution for lock operation"""
        print(f"Setting lock resolution: {self.lock_resolution}")
        return self.set_resolution(self.lock_resolution)
    
    def restore_original_resolution(self) -> bool:
        """Restore the original resolution from saved file"""
        if not self.save_original:
            print("Original resolution restoration is disabled in config")
            # Fallback to configured lock resolution
            return self.set_lock_resolution()
            
        original_res = self.load_original_resolution()
        if original_res:
            return self.set_resolution(original_res)
        else:
            print("Could not load original resolution, using configured lock resolution")
            return self.set_lock_resolution()
    
    def cleanup_resolution_file(self) -> bool:
        """Remove the original resolution file"""
        try:
            if os.path.exists(self.original_file):
                os.remove(self.original_file)
                print(f"Cleaned up resolution file: {self.original_file}")
            return True
        except Exception as e:
            print(f"Error cleaning up resolution file: {e}")
            return False


# Convenience functions for backward compatibility
def save_current_resolution(config_file: str = "config.ini") -> bool:
    """Save current resolution (convenience function)"""
    manager = ResolutionManager(config_file)
    return manager.save_original_resolution()


def restore_original_resolution(config_file: str = "config.ini") -> bool:
    """Restore original resolution (convenience function)"""
    manager = ResolutionManager(config_file)
    return manager.restore_original_resolution()


def set_unlock_resolution(config_file: str = "config.ini") -> bool:
    """Set unlock resolution (convenience function)"""
    manager = ResolutionManager(config_file)
    return manager.set_unlock_resolution()


def set_lock_resolution(config_file: str = "config.ini") -> bool:
    """Set lock resolution (convenience function)"""
    manager = ResolutionManager(config_file)
    return manager.set_lock_resolution()


if __name__ == "__main__":
    # Test the resolution manager
    manager = ResolutionManager()
    
    print("Current resolution:")
    current = manager.get_current_resolution()
    
    print("\nSaving original resolution...")
    manager.save_original_resolution()
    
    print("\nTesting unlock resolution...")
    manager.set_unlock_resolution()
    
    print("\nTesting lock resolution...")
    manager.set_lock_resolution()
    
    print("\nRestoring original resolution...")
    manager.restore_original_resolution() 