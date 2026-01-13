# Utility and Debugging Scripts

This directory contains various utility and debugging scripts related to this PXE server environment.

## Scripts

### `Check_PXE.sh`

*   **Purpose:** This is a diagnostic script for quickly checking the health of the core PXE services on this server.
*   **Applicable Scenario:** Use this script when you need to verify that the server's PXE components are running correctly. It is specifically configured for this server's setup.
*   **What it does:**
    1.  **Checks Service Status:** Verifies that `nginx` and `dnsmasq` services are active.
    2.  **Checks Port Listening:** Ensures that ports `80` (HTTP), `67` (DHCP), and `69` (TFTP) are being listened on by the correct services.
    3.  **HTTP Self-Test:** Runs `curl` against `http://localhost/pxe/boot.ipxe` to confirm Nginx is serving the iPXE script.
    4.  **TFTP Self-Test:** Runs a `tftp` client test against `192.168.1.1` to confirm Dnsmasq can serve the initial UEFI boot file (`ipxe.efi`).
