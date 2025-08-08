#!/bin/bash

# Update system
sudo apt update && sudo apt upgrade -y

# Install VSCode
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
sudo apt update
sudo apt install -y code

# Install additional development tools
sudo apt install -y git vim nano htop tree

# Install Python packages
pip3 install --user jupyter notebook ipython

echo "Setup complete! You can now SSH into the instance:"
echo "gcloud compute ssh nemo-dev-instance --zone=asia-southeast1-a"
echo ""
echo "To run VSCode with X11 forwarding:"
echo "gcloud compute ssh nemo-dev-instance --zone=asia-southeast1-a -- -X"
echo "Then run: code"