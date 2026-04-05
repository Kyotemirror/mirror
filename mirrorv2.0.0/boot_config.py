import subprocess

def run(cmd):
    subprocess.run(cmd, shell=True, check=True)

# Enable quiet boot
run("sed -i 's/console=tty1/console=tty3 quiet splash loglevel=3 vt.global_cursor_default=0/' /boot/cmdline.txt")

# Install plymouth
run("apt install -y plymouth plymouth-themes")

# Create custom theme directory
run("mkdir -p /usr/share/plymouth/themes/kyote")

# Copy theme files
run("cp /home/pi/mirror/assets/boot/* /usr/share/plymouth/themes/kyote/")

# Register theme
run("plymouth-set-default-theme -R kyote")