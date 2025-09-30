# Alvik Robot Initialization Scripts

This repository contains a set of scripts for initializing and synchronizing Alvik robots with a local source directory. The system is designed to be efficient, only deleting files from the robot that are no longer present locally and only copying new or changed files.

## Core Concepts

The initialization process is built around a simple but powerful idea: a local directory on your computer acts as a "source of truth" that mirrors the desired state of the robot's filesystem.

* **Source Directory:** You provide a directory (e.g., `nhs_robot/`) that contains all the files and folders you want on the robot.

* **Intelligent Sync:** The script compares the remote robot's filesystem with your local source directory.

  * It **deletes** any files on the robot that are not in your source directory.

  * It **copies** only the new or changed files from your source directory to the robot.

* **Protected Workspace:** The `/workspace` directory on the robot is **always protected**. The scripts will never delete this directory or its contents, making it a safe place for user-specific scripts and data.

* **Ignore File (`.robotignore`):** You can place a `.robotignore` file in your source directory to specify files or directories that should be completely ignored by the synchronization process. These files will not be copied to the robot, nor will they be deleted from the robot if they already exist.

## Scripts

### `initialize_robot.sh`

This is the core script that synchronizes a **single robot**.

**Usage:**

```
./initialize_robot.sh -d <source_directory> [-p <port>]
```

**Arguments:**

* `-d, --dir`: (Required) The path to the local source directory that should be mirrored on the robot.

* `-p, --port`: (Optional) The specific port of the robot to initialize. If omitted, the script will automatically detect the first connected Alvik.

### `initialize_all.sh`

This is a wrapper script that finds **all connected Alvik robots** and runs `initialize_robot.sh` for each one.

**Usage:**

```
./initialize_all.sh -d <source_directory>
```

**Arguments:**

* `-d, --dir`: (Required) The path to the local source directory that will be mirrored on all connected robots.

## The `.robotignore` File

To prevent certain files from being part of the sync process, create a file named `.robotignore` inside your source directory. List the files or directories you wish to ignore, one per line.

**Example `nhs_robot/.robotignore`:**

```
# This is a comment and will be ignored
# Protect the hello.py file on the robot from deletion
hello.py

# Protect the entire solutions directory
solutions/
```

In this example:

* `hello.py` will not be copied from the local directory if it exists there.

* `hello.py` will not be deleted from the robot if it exists there.

* The `solutions/` directory will be similarly protected.

## Typical Workflow

1. **Arrange Files:** Place all the files and directories you want on the robot inside a single source directory (e.g., `nhs_robot`).

2. **Configure Ignore List:** Create or edit the `.robotignore` file within your source directory to list any files you want the process to ignore.

3. **Connect Robot(s):** Connect one or more Alvik robots to your computer via USB.

4. **Run Sync:**

   * To update a single, specific robot: ` ./initialize_robot.sh -d nhs_robot -p /dev/cu.usbmodem1234561`

   * To update all connected robots: ` ./initialize_all.sh -d nhs_robot`