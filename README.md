# PXE Server Setup and Troubleshooting / PXE 伺服器設定與問題排除

This document summarizes the steps taken to set up and troubleshoot the PXE (Preboot Execution Environment) server, including its DHCP, TFTP, and HTTP services, and to ensure its network configuration persists across reboots.

這份文件總結了設定和排除 PXE (預啟動執行環境) 伺服器問題的步驟，包括其 DHCP、TFTP 和 HTTP 服務，並確保其網路配置在重新開機後仍然有效。

---

### PXE Environment Setup and Troubleshooting Summary (English)

#### 1. Initial Problem Diagnosis:
*   **Problem Description:** The user initially reported issues with the PXE environment and service configuration, specifically that the client could not obtain an IP or boot correctly.
*   **Initial Diagnosis:**
    *   Executing the `Check_PXE.sh` script showed Nginx and Dnsmasq services running, and ports open.
    *   However, the Dnsmasq TFTP self-test failed with a timeout.
    *   Further investigation of the Dnsmasq configuration file (`/etc/dnsmasq.d/pxe-interface.conf`) found `listen-address=192.168.1.1`.
    *   `ip addr` showed that no interface on the server had `192.168.1.1` as its IP address; the main interface (`wlo1`) was `192.168.45.20`.
    *   **Root Cause:** Dnsmasq could not bind to the specified IP address, preventing DHCP and TFTP services from operating correctly.

#### 2. User Goal and Problem Clarification:
*   The user explicitly stated that `enx00e04c369f39` should be the PXE interface and wanted it to provide DHCP services for the `192.168.1.0/24` subnet.
*   The user also highlighted that the `enx00e04c369f39` interface could not automatically set to the static IP `192.168.1.1` after rebooting, which was a core problem.

#### 3. Solution One: Temporary PXE Interface Activation and Service Verification

*   **Problem:** The `enx00e04c369f39` interface was in a `DOWN` state and unconfigured, preventing Dnsmasq from binding.
*   **Solution:**
    *   Manually configured `enx00e04c369f39` with the static IP `192.168.1.1/24` and brought it `UP` (`ip addr add ... && ip link set ... up`).
    *   Restarted the Dnsmasq service (`systemctl restart dnsmasq.service`).
*   **Verification Results:**
    *   DHCP service operated normally (laptop successfully obtained `192.168.1.51`).
    *   TFTP service operated normally, successfully downloading `ipxe.efi` (`tftp 192.168.1.1 -c get ipxe.efi ...`).
    *   HTTP (Nginx) service was also confirmed to be able to serve the `boot.ipxe` script (`curl -I http://192.168.1.1/pxe/boot.ipxe`).

#### 4. Solution Two: Permanent Static IP Configuration (Netplan)

*   **Problem:** The static IP configuration would not persist after reboot. Previous `netplan apply` attempts failed due to incomplete configuration.
*   **Solution:**
    *   Confirmed the system uses `NetworkManager` as its Netplan renderer.
    *   Created a new, minimal Netplan configuration file `/etc/netplan/99-pxe-static.yaml` with the following content:
        ```yaml
        network:
          version: 2
          renderer: NetworkManager
          ethernets:
            enx00e04c369f39:
              dhcp4: no
              addresses:
                - 192.168.1.1/24
        ```
        This configuration exclusively targets the `enx00e04c369f39` interface and explicitly specifies the renderer, avoiding issues with other interface configurations.
    *   Moved the new configuration file to `/etc/netplan/` (`mv /root/99-pxe-static-minimal.yaml /etc/netplan/99-pxe-static.yaml`).
    *   Successfully applied the Netplan configuration (`netplan apply`).
*   **Result:** The `enx00e04c369f39` interface is now permanently configured with `192.168.1.1/24`, ensuring the PXE server's stability across reboots.

#### Further Recommendations:
The server-side PXE environment is now fully configured and verified. If the client still fails to boot, the problem is likely within the `boot.ipxe` script itself, or the operating system files it attempts to load (e.g., kernel, initrd), including their paths, permissions, or existence.

---

### PXE 環境設定與問題排除總結 (Chinese)

#### 1. 初始問題診斷：
*   **問題描述：** 用戶最初回報 PXE 環境和服務配置有問題，尤其是客戶端無法獲取 IP 或無法正確啟動。
*   **初步診斷：**
    *   執行 `Check_PXE.sh` 腳本顯示 Nginx 和 Dnsmasq 服務運行，埠也已打開。
    *   但 Dnsmasq 的 TFTP 自我測試失敗，顯示連線逾時。
    *   進一步調查 Dnsmasq 配置檔 (`/etc/dnsmasq.d/pxe-interface.conf`)，發現 `listen-address=192.168.1.1`。
    *   `ip addr` 顯示伺服器上沒有任何介面擁有 `192.168.1.1` 這個 IP 位址；主要的介面 (`wlo1`) 為 `192.168.45.20`。
    *   **根本原因：** Dnsmasq 無法綁定到指定的 IP 位址，導致 DHCP 和 TFTP 服務無法正常運作。

#### 2. 用戶目標與問題澄清：
*   用戶明確表示 `enx00e04c369f39` 應作為 PXE 介面，並希望其提供 `192.168.1.0/24` 網段的 DHCP 服務。
*   用戶也指出 `enx00e04c369f39` 介面在重開機後無法自動設定為 `192.168.1.1` 的靜態 IP，這是核心問題。

#### 3. 解決方案一：臨時啟用 PXE 介面並驗證服務

*   **問題：** `enx00e04c369f39` 介面處於 `DOWN` 狀態且未配置 IP。
*   **解決方案：**
    *   手動為 `enx00e04c369f39` 介面設定靜態 IP `192.168.1.1/24`，並將其啟用 (`ip addr add ... && ip link set ... up`)。
    *   重新啟動 Dnsmasq 服務 (`systemctl restart dnsmasq.service`)。
*   **驗證結果：**
    *   DHCP 服務正常運作（筆電成功獲取 `192.168.1.51`）。
    *   TFTP 服務正常運作，成功下載 `ipxe.efi` (`tftp 192.168.1.1 -c get ipxe.efi ...`)。
    *   HTTP (Nginx) 服務也確認可正常提供 `boot.ipxe` 腳本 (`curl -I http://192.168.1.1/pxe/boot.ipxe`)。

#### 4. 解決方案二：永久性靜態 IP 配置 (Netplan)

*   **問題：** 靜態 IP 配置在重開機後會失效。之前的 `netplan apply` 嘗試因設定不完整而失敗。
*   **解決方案：**
    *   確認系統使用 `NetworkManager` 作為 Netplan 渲染器。
    *   創建一個新的、精簡的 Netplan 設定檔 `/etc/netplan/99-pxe-static.yaml`，內容如下：
        ```yaml
        network:
          version: 2
          renderer: NetworkManager
          ethernets:
            enx00e04c369f39:
              dhcp4: no
              addresses:
                - 192.168.1.1/24
        ```
        此配置僅針對 `enx00e04c369f39` 介面，並明確指定渲染器，避免了其他介面配置可能導致的問題。
    *   將新的設定檔移動到 `/etc/netplan/` 目錄 (`mv /root/99-pxe-static-minimal.yaml /etc/netplan/99-pxe-static.yaml`)。
    *   成功套用 Netplan 配置 (`netplan apply`)。
*   **結果：** `enx00e04c369f39` 介面現在已永久配置為 `192.168.1.1/24`，確保 PXE 伺服器在每次重開機後都能穩定運作。

#### 後續建議：
目前伺服器端的 PXE 環境已完整配置並驗證。如果客戶端仍然無法成功啟動，問題很可能出在 `boot.ipxe` 腳本本身的內容，或是該腳本所引導的作業系統檔案（如核心、initrd 等）的路徑、權限或存在性問題。