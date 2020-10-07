#
#  Dockerfile for Clutch
#
# https://github.com/mtlott/clutch
#
# Based on:
# https://github.com/jlesage/handbrake
#

# Pull base image.
FROM jlesage/baseimage-gui:alpine-3.11-v3.5.6

# Docker image version is provided via build arg.
ARG DOCKER_IMAGE_VERSION=unknown

# Define software versions.

# Define software download URLs.

# Other build arguments.

# Define working directory.
WORKDIR /tmp

# Install dependencies.
RUN \
    add-pkg \
        bash \
        python3 \
        ffmpeg \
        xterm \
        yad \
        coreutils \
        # Media codecs:
        libtheora \
        x264-libs \
        lame \
        opus \
        libvorbis \
        # For main, big icons:
        librsvg \
        # For all other small icons:
        adwaita-icon-theme \
        # For watchfolder
        findutils \
        expect

# Adjust the openbox config.
RUN \
    # Maximize only the main/initial window.
    sed-patch 's/<application type="normal">/<application type="normal" title="Clutch">/' \
        /etc/xdg/openbox/rc.xml && \
    # Make sure the main window is always in the background.
    sed-patch '/<application type="normal" title="Clutch">/a \    <layer>below</layer>' \
        /etc/xdg/openbox/rc.xml

# Generate and install favicons.
RUN \
    APP_ICON_URL=https://raw.githubusercontent.com/mtlott/clutch/master/images/clutch-icon.png && \
    install_app_icon.sh "$APP_ICON_URL"

# Add files.
COPY rootfs/ /

# Set environment variables.
ENV APP_NAME="Clutch" \
    AUTOMATED_CONVERSION_INPUT="edl"

# Define mountable directories.
VOLUME ["/config"]
VOLUME ["/storage"]
VOLUME ["/output"]
VOLUME ["/watch"]

# Metadata.
LABEL \
      org.label-schema.name="clutch" \
      org.label-schema.description="Docker container for Clutch" \
      org.label-schema.version="$DOCKER_IMAGE_VERSION" \
      org.label-schema.vcs-url="https://github.com/mtlott/clutch" \
      org.label-schema.schema-version="1.0"