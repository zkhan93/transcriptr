# Audio Transcription Service

This project sets up an audio recording service on a Raspberry Pi using `arecord`. The service records audio in specified segments and stores the files in a specified directory. It is configured to run as a systemd service for automatic management.

## Components

- `record.sh`: A Bash script that continuously records audio in specified segments and saves the recordings in a specified directory.
- `transcriptr.service`: A systemd service file that manages the audio transcription service, ensuring it runs continuously and restarts automatically if it fails.

## Setup Instructions

### Step 1: Prepare the Recording Script

1. Create the `record.sh` script and make it executable:

   ```bash
   sudo nano /pi/home/transcriptr/record.sh
   sudo chmod +x /pi/home/transcriptr/record.sh
   ```

2. Copy the contents of `record.sh` into the file and save it.

### Step 2: Configure the Systemd Service

1. Create the systemd service file:

   ```bash
   sudo nano /etc/systemd/system/transcriptr.service
   ```

2. Copy the contents of `transcriptr.service` into the file and save it.

### Step 3: Enable and Start the Service

1. Reload the systemd manager configuration:

   ```bash
   sudo systemctl daemon-reload
   ```

2. Enable the service to start on boot:

   ```bash
   sudo systemctl enable transcriptr.service
   ```

3. Start the service:

   ```bash
   sudo systemctl start transcriptr.service
   ```

### Step 4: Verify the Service

Check the status of the service to ensure it is running correctly:

```bash
sudo systemctl status transcriptr.service
```

## Usage

The `record.sh` script takes two arguments:
- `-d DIRECTORY`: Directory to place the recorded files.
- `-t DURATION`: Duration of each segment in seconds.

The `transcriptr.service` file is configured to run `record.sh` with the desired arguments. Modify the `ExecStart` line in `transcriptr.service` if you need to change these parameters.

## Logging

Logs for the service can be viewed using the `journalctl` command:

```bash
sudo journalctl -u transcriptr.service
```

## License

This project is licensed under the MIT License.
