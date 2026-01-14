# PXE Server Configuration

This repository contains the configuration files for a comprehensive PXE (Pre-boot Execution Environment) server. The setup uses `dnsmasq` for DHCP and TFTP, and `nginx` for HTTP to serve boot files for multiple operating systems.

## Architecture

The environment is designed to boot clients via UEFI PXE. The process is as follows:

1.  **Client PXE Boot**: The client broadcasts a DHCP request.
2.  **dnsmasq (DHCP/TFTP)**: `dnsmasq` responds with an IP address and provides the `ipxe.efi` bootloader via TFTP.
3.  **iPXE Execution**: The client loads `ipxe.efi`, which then makes another DHCP request.
4.  **iPXE DHCP Detection**: `dnsmasq` detects the iPXE client (using DHCP option 175) and instructs it to download the `boot.ipxe` script via HTTP.
5.  **iPXE Menu**: The `boot.ipxe` script is executed, which can present a menu for booting into different operating systems (e.g., Ubuntu, Windows PE).

- **DHCP/PXE/TFTP**: `dnsmasq`
- **HTTP**: `nginx`
- **Bootloader**: iPXE
- **Windows Chainloader**: wimboot

## Configuration Details

### `dnsmasq`

The `dnsmasq` configuration is split into two main files.

**`services/dhcp-tftp/pxe-interface.conf`**:
```
listen-address=192.168.1.1
```

**`services/dhcp-tftp/pxe.conf`**:
```conf
# Disable DNS functionality
port=0

# DHCP Range
dhcp-range=192.168.1.50,192.168.1.150,255.255.255.0,12h

# Legacy BIOS boot file
dhcp-boot=undionly.kpxe

# UEFI boot file
dhcp-match=set:efi64,option:client-arch,7
dhcp-match=set:efi64,option:client-arch,9
dhcp-boot=tag:efi64,ipxe.efi

# iPXE detection and script
dhcp-match=set:ipxe,175
dhcp-boot=tag:ipxe,boot.ipxe

# Enable TFTP
enable-tftp
tftp-root=/var/lib/tftpboot
```

This configuration correctly handles the iPXE boot loop by detecting the iPXE client and serving a different boot file.

### `nginx`

The `nginx` configuration serves the files needed for the iPXE script and the OS installers.

**`services/http/default.conf`**:
```nginx
server {
        listen 80 default_server;
        listen [::]:80 default_server;

        root /var/www/html;
        index index.html index.htm index.nginx-debian.html;
        server_name _;

        location / {
                autoindex on;
                try_files $uri $uri/ =404;
        }
}
```

### iPXE Script

The `boot.ipxe` script is the entry point for iPXE clients. This example shows how to chainload the Ubuntu installer.

**`boot.ipxe`**:
```ipxe
#!ipxe

echo Booting into Ubuntu 22.04 Installer...

chain --autofree http://192.168.1.1/ubuntu-installer/EFI/boot/grubx64.efi
boot
```

## Deployment Notes

- **OS Files**: Ensure the OS installer files are extracted to the correct location within the `nginx` root (`/var/www/html`). For example, the Ubuntu files should be in `/var/www/html/ubuntu-installer/`.
- **Secure Boot**: Client machines must have **Secure Boot disabled** to boot custom `efi` files like `ipxe.efi`.
- **Network**: The server must have a static IP address configured that matches the `listen-address` in the `dnsmasq` configuration.

## Summary

This configuration provides a fully functional UEFI PXE + iPXE + HTTP boot environment. It resolves common issues like the iPXE DHCP loop and provides a solid foundation for booting multiple operating systems.
