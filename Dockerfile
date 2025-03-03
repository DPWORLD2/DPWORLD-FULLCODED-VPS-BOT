# Base Image
FROM ubuntu:22.04

# Update System
RUN apt-get update

# Install SSH Server, tmate, and required dependencies
RUN apt-get install -y tmate openssh-server openssh-client

# Enable Root Login for SSH
RUN sed -i 's/^#\?\s*PermitRootLogin\s\+.*/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN echo 'root:root' | chpasswd

# Prevent policy-rc.d from blocking services
RUN printf '#!/bin/sh\nexit 0' > /usr/sbin/policy-rc.d

# Install SystemD and D-Bus
RUN apt-get install -y systemd systemd-sysv dbus dbus-user-session

# Ensure SystemD Logind Starts on Boot
RUN printf "systemctl start systemd-logind" >> /etc/profile

# Install Additional Utilities
RUN apt install -y curl ufw net-tools iproute2 hostname

# Configure Firewall (UFW)
RUN ufw allow 22 && ufw allow 80 && ufw allow 443

# Cleanup APT Cache
RUN rm -rf /var/lib/apt/lists/*

# Set Default Command
CMD ["bash"]

# Enable SystemD
ENTRYPOINT ["/sbin/init"]
