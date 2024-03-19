# Coffee machine demo

Keeps an eye on the clover coffee machine in the Groundlight office, and alerts if somebody forgets to rinse.

This demonstrates how to use the Groundlight Python SDK to:
- Set up a simple logic loop to watch for a specific condition
- Fetch images from an RTSP camera
- Run inference on the images
- Send results / status to a Stacklight

![Needs rinsing](./static/coffee-present.png)
![Already rinsed](./static/coffee-not-present.png)

## Running

1. Install poetry.

``` shell
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```

2. Install dependencies.

``` shell
poetry install
```

3. Configure environment variables in `set-environment.sh`

See [manual](https://code.groundlight.ai/python-sdk/docs/getting-started/api-tokens) for instructions on how to get the Groundlight API token.

If you put that code-block into a file called `set-environment` it will be excluded from git and you can load the variables with

```
source ./set-environment.sh
```

1. Run the script.

``` shell
poetry run python coffee_demo.py
```

# Running continuously in the background (on Mac)

To automatically run at boot time in a `tmux` session, use the `com.groundlight.start_coffee.plist` plist to automatically i`start-coffee.sh` script.

## Installing

1. Make sure you have prerequisites such as `tmux` installed, and a `set-environment` file with your secrets.  Instructions for both are below.

2. Modify the `plist` file to replace `/path/to/start-coffee.sh` with the actual full path of your bash script.

3.  Copy the plist file to ~/Library/LaunchAgents/:

``` bash
cp ./com.groundlight.start_coffee.plist ~/Library/LaunchAgents/
```

4.  Load the plist file using launchctl:

``` bash
launchctl load ~/Library/LaunchAgents/com.groundlight.start_coffee.plist
```

Now, whenever your Mac boots up, it will run the bash script, which will start a tmux session, source the environment variables, and run the Python program.


## Verifying it's working

## Testing the plist file

1. Make sure your plist file is loaded by running the following command:

```
launchctl load ~/Library/LaunchAgents/com.groundlight.start_coffee.plist
```

2. Kickstart the service using `launchctl`:

```
launchctl kickstart -k gui/$(id -u)/com.groundlight.start_coffee
```

Replace `com.groundlight.start_coffee` with the label you used in your plist file.

This command will start the service immediately, allowing you to check that it's working correctly. The `-k` flag ensures that if the service is already running, it will be stopped and then started again. The `gui/$(id -u)` part targets your user-specific launchd instance.

To check the status of your service, you can run:

```
launchctl list | grep com.groundlight.start_coffee
```

This will show you if the service is running and its exit code. You can also check the log files specified in your plist file (e.g., `/tmp/com.groundlight.start_coffee.stdout` and `/tmp/com.groundlight.start_coffee.stderr`) for any output or errors from your script.

## Seeing what's happening

To connect to the tmux session and monitor the progress of the Python script, follow these steps:

1. Open a terminal window.

2. Connect to the tmux session by running the following command:

```
tmux attach-session -t coffee
```

Replace `coffee` with the name of the tmux session if you used a different name in your startup script.

3. After connecting, you will see the output of the Python script running inside the tmux session. You can interact with the script as if it were running in a regular terminal window.

4. To disconnect from the tmux session without stopping the Python script, press `Ctrl-b` followed by `d`. This will detach you from the session, leaving it running in the background.

## Uninstalling

1.  To unload the plist file and stop the process from starting at boot, you can run:

``` bash
launchctl unload ~/Library/LaunchAgents/com.groundlight.start_coffee.plist
```

## Pre-requisites

### Installing `tmux` on macOS

To install `tmux` on your macOS system, we'll use Homebrew, a popular package manager for macOS. If you don't have Homebrew installed, follow the steps below.

#### 1. Install Homebrew

Open your terminal and paste the following command:

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

This will download and install Homebrew on your system.

#### 2. Update Homebrew and check its status

Run the following commands to update Homebrew and ensure it's ready to install packages:

```
brew update
brew doctor
```

#### 3. Install tmux

Finally, use Homebrew to install `tmux` with the following command:

```
brew install tmux
```

Now, `tmux` should be installed on your Mac. To verify the installation, run:

```
tmux -V
```

This command should return the version number of the installed `tmux`.
