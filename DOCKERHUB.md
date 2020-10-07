# Docker container for Clutch

This is a Docker container for Clutch.

Clutch provides a bridge between a DVR which outputs EDL files such as [Channels-DVR](https://channels.com) and an automated version of [Handbrake](https://github.com/jlesage/docker-handbrake).

The GUI provides only status information through a web-based VNC session.

The fully automated functionality provides watch folders: drop files into a watch folder and let Clutch process them without any user interaction.

---
[![Clutch logo](https://images.weserv.nl/?url=raw.githubusercontent.com/mtlott/Clutch/master/images/clutch-logo.jpg&w=400)](https://github.com/mtlott/clutch/)[![Clutch](https://dummyimage.com/300x110/ffffff/575757&text=Clutch)](https://github.com/mtlott/clutch/)

Clutch is an EDL (Edit Decision List) splicer tool which utilizes ffmpeg to cut segments from a video file without reencoding.

Clutch is based on the amazing work of jlesage on [docker-handbrake](https://github.com/jlesage/docker-handbrake)

---

## Quick Start

**NOTE**: The Docker command provided in this quick start is given as an example
and parameters should be adjusted to your need.

Launch the HandBrake docker container with the following command:
```
docker run -d \
    --name=clutch \
    -p 5800:5800 \
    -v /docker/appdata/clutch:/config:rw \
    -v $HOME:/storage:ro \
    -v $HOME/Clutch/watch:/watch:rw \
    -v $HOME/Clutch/output:/output:rw \
    mtlott/clutch
```

Where:
  - `/docker/appdata/handbrake`: This is where the application stores its configuration, log and any files needing persistency.
  - `$HOME`: This location contains files from your host that need to be accessible by the application.
  - `$HOME/Clutch/watch`: This is where videos to be automatically converted are located.
  - `$HOME/Clutch/output`: This is where automatically converted video files are written.

Browse to `http://your-host-ip:5800` to view Clutch status.
Files from the host appear under the `/storage` folder in the container.

## Documentation

Full documentation is available at https://github.com/mtlott/Clutch.

## Support or Contact

Having troubles with the container or have questions?  Please
[create a new issue].

[create a new issue]: https://github.com/mtlott/Clutch/issues
