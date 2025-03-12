import argparse
import json
import os
import platform
import shutil
import subprocess
import sys


def RED(text):
    return "\033[91m" + text + "\033[0m"


def GREEN(text):
    return "\033[92m" + text + "\033[0m"


def YELLOW(text):
    return "\033[93m" + text + "\033[0m"


def CYAN(text):
    return "\033[96m" + text + "\033[0m"


# === BEGIN: Platform-specific code ===
# To deploy to a CircuitPython board masquerading as a USB drive with a certain name,
# we must be able to find all the mounted USB drives on the system and check their names.
# How this is done depends on the OS on which the script is running. For any OS, the
# `find_mount_points_with_names` function must be implemented for the script to work.
# The function should return a list of tuples, where the first item in each tuple is a
# string which can be supplied to `os.listdir` to find the contents of the root of a USB
# drive. The second item in each tuple should be a string giving the name of the USB
# drive. A tuple should be returned for every USB drive plugged into the system.

# To implement the function for a new platform, simply add a clause to the `if` chain
# below which defines the `find_mount_points_with_names` function.


def find_mount_points_with_names():
    if os.name == "nt":
        drives = []
        drive_list_proc = subprocess.run(
            ["fsutil", "fsinfo", "drives"], stdout=subprocess.PIPE
        )
        for drive in drive_list_proc.stdout.decode().split(" "):
            if len(drive) == 3 and drive[1] == ":" and drive[2] == "\\":
                drive_deets_proc = subprocess.run(
                    ["fsutil", "fsinfo", "volumeInfo", drive[:2]],
                    stdout=subprocess.PIPE,
                )
                drive_name = None
                for drive_kv in drive_deets_proc.stdout.decode().splitlines():
                    if drive_kv.startswith("Volume Name :"):
                        assert drive_name is None
                        drive_name = drive_kv.split(":")[1].strip()
                drives.append((drive, drive_name))
        return drives
    elif platform.system() == "Darwin":
        drives = []
        mount_proc = subprocess.run(["mount"], stdout=subprocess.PIPE)
        for mount_line in mount_proc.stdout.decode().splitlines():
            if mount_line.startswith("/"):
                mount_parts = mount_line.split(" ")
                mount_point = mount_parts[2]
                if mount_point.startswith("/Volumes"):
                    drives.append((mount_point, mount_point.removeprefix("/Volumes/")))
        return drives
    else:
        print(
            RED(
                f"ERROR: Platform-specific functions are not available on your system, which is detected as {os.name}"
            ),
            file=sys.stderr,
        )
        print(
            RED(
                "ERROR: Implement the required platform-specific functions to proceed."
            ),
            file=sys.stderr,
        )
        return None


# === END: Platform-specific code ===

# The rest of the program is implemented using cross-platform functions from the
# Python library, and should work on any system so long as the platform-specific
# functions are implemented with the appropriate contracts.


def deploy_with_settings(deploy_type, target_drive, tmp_folder, include_tests=False):
    if target_drive is None:
        target_drive = "CIRCUITPY"

    if tmp_folder:
        print(CYAN(f"Starting deploy type {deploy_type} to temporary folder..."))
    else:
        print(
            CYAN(
                f"Starting deploy type {deploy_type} to CircuitPython board with name {target_drive}..."
            )
        )

    deploy_types = os.listdir(os.path.join(".", "artifacts"))
    if deploy_type not in deploy_types:
        print(
            RED(f"ERROR: No software found for target {deploy_type}"),
            file=sys.stderr,
        )
        deploy_types_string = filter(
            (lambda x: (len(x) < 8) or (x[-8:] != "_testapp")), deploy_types
        )
        deploy_types_string = list(map((lambda x: YELLOW(x)), deploy_types_string))
        deploy_types_string = (
            ", ".join(deploy_types_string[:-1]) + ", and " + deploy_types_string[-1]
        )
        print(f"Available deploy types are {deploy_types_string}", file=sys.stderr)
        return None

    if tmp_folder:
        import tempfile

        deploy_path = os.path.join(tempfile.gettempdir(), "CIRCUITPY")
        os.makedirs(deploy_path, exist_ok=True)
    else:
        mpwn = find_mount_points_with_names()
        if mpwn is None:
            return None
        target_drives = [
            mp[0] for mp in filter((lambda mp: mp[1] == target_drive), mpwn)
        ]
        if len(target_drives) != 1:
            print(
                RED(
                    f"ERROR: There must be exactly one drive named {target_drive} but {len(target_drives)} were found."
                ),
                file=sys.stderr,
            )
            print(
                RED(
                    "ERROR: Exited without deploying the software. "
                    + "Rename a drive, or target a drive name that is unique and exists."
                ),
                file=sys.stderr,
            )
            return None
        deploy_path = target_drives[0]

    print(
        f"Configuration complete! Loading software for {deploy_type} to {deploy_path}"
    )

    try:
        includejson = json.load(
            open(os.path.join(".", "artifacts", deploy_type, "include.json"))
        )
    except Exception:
        print(
            RED(f"ERROR: Could not parse a valid `include.json` for {deploy_type}"),
            file=sys.stderr,
        )
        return None

    print("Wiping existing software on device...")
    for item in os.listdir(deploy_path):
        item_path = os.path.join(deploy_path, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
        else:
            os.remove(item_path)

    print("Programming included libraries to device...")
    for item in includejson["src"]:
        src_item_path = os.path.join(".", "src", item)
        dst_item_path = os.path.join(deploy_path, item)
        if os.path.isdir(src_item_path):
            shutil.copytree(
                src_item_path, dst_item_path, symlinks=False, dirs_exist_ok=True
            )
        else:
            os.makedirs(os.path.dirname(dst_item_path), exist_ok=True)
            shutil.copyfile(src_item_path, dst_item_path, follow_symlinks=True)

    if include_tests:
        for item in includejson["unit_tests"]:
            src_item_path = os.path.join(".", "unit_tests", item)
            dst_item_path = os.path.join(deploy_path, item)
            if os.path.isdir(src_item_path):
                shutil.copytree(
                    src_item_path, dst_item_path, symlinks=False, dirs_exist_ok=True
                )
            else:
                os.makedirs(os.path.dirname(dst_item_path), exist_ok=True)
                shutil.copyfile(src_item_path, dst_item_path, follow_symlinks=True)
        shutil.copyfile(
            os.path.join(".", "config", "conftest.py"),
            os.path.join(deploy_path, "conftest.py"),
        )

    print("Programming target-specific software to device...")
    for item in os.listdir(os.path.join(".", "artifacts", deploy_type)):
        if item == "include.json":
            continue
        src_item_path = os.path.join(".", "artifacts", deploy_type, item)
        dst_item_path = os.path.join(deploy_path, item)
        if os.path.isdir(src_item_path):
            shutil.copytree(
                src_item_path, dst_item_path, symlinks=False, dirs_exist_ok=True
            )
        else:
            os.makedirs(os.path.dirname(dst_item_path), exist_ok=True)
            shutil.copyfile(src_item_path, dst_item_path, follow_symlinks=True)

    print("Removing any generated __pycache__ directories copied to device...")
    for tree in os.walk(deploy_path, followlinks=True):
        if "__pycache__" in tree[1]:
            shutil.rmtree(os.path.join(tree[0], "__pycache__"))

    print(GREEN(f"Deployment complete for target {deploy_type} to {deploy_path}!"))
    return deploy_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run this script to find a USB drive with a certain name, wipe its "
        + "current contents, and move the appropriate files to the drive so that it runs "
        + "the updated software. Automatically expands through symbolic links and merges "
        + "general lib folders with board-specific lib folders. The program must be run "
        + "from the root directory of a properly-structured spacecraft software project. "
        + "Can also be used to deploy to a temporary folder. Includes the option to also "
        + "deploy unit tests to the target artifact so they can be run."
    )
    parser.add_argument("deploy_type")
    deploy_target = parser.add_mutually_exclusive_group(required=True)
    deploy_target.add_argument("--target_drive", nargs="?", default="CIRCUITPY")
    deploy_target.add_argument("--tmp_folder", action="store_true")
    parser.add_argument("--include_tests", action="store_true")
    args = parser.parse_args()

    deploy_with_settings(
        args.deploy_type, args.target_drive, args.tmp_folder, args.include_tests
    )
