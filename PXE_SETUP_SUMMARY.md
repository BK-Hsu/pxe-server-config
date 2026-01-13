### PXE 環境設定與問題排除總結

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
