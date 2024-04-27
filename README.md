# ArduRover-Companion

A companion-app for Ardupilot Rovers.

This is ment to run (preferably and for convenience reasons) in a Docker container either on the companion pc (raspberry) on the rover itself or on a high-end hardware somewhere with TCP/IP connection for camera and telemetry.

## Installation

```shell
cd ~
git clone https://github.com/ploeffler/ArduRover-Companion
cd ArduRover-Companion
sudo docker build -t ardurovercompanion .
