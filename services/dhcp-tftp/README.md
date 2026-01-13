# DHCP & TFTP 服務 (Dnsmasq)

此目錄包含 PXE 環境中 DHCP 和 TFTP 服務的設定，這兩項服務都由 `Dnsmasq` 提供。

## 用途

*   **DHCP (動態主機設定協定):** 為 PXE 客戶端分配 IP 位址，並在回應中告訴客戶端下一步要載入哪個開機檔案。
*   **TFTP (小型檔案傳輸協定):** 一個輕量的檔案傳輸服務，用於向客戶端提供最初的開機檔案 (例如 `ipxe.efi`)。

## 設定檔說明

### `pxe-interface.conf`
```
listen-address=192.168.1.1
```
*   **`listen-address`**: 這個重要的指令告訴 Dnsmasq **只在** `192.168.1.1` 這個 IP 位址上監聽請求。這確保了服務只對連接到 `enx00e04c369f39` 介面的 PXE 網路提供服務，而不會干擾到其他網路（例如您的 Wi-Fi）。

### `pxe.conf`
```
# 停用 DNS 功能
port=0

# 設定 DHCP 範圍
dhcp-range=192.168.1.50,192.168.1.150,255.255.255.0,12h

# 指定 PXE 引導檔
dhcp-boot=undionly.kpxe
dhcp-match=set:efi64,option:client-arch,7
dhcp-match=set:efi64,option:client-arch,9
dhcp-boot=tag:efi64,ipxe.efi
dhcp-match=set:ipxe,175
dhcp-boot=tag:ipxe,boot.ipxe

# 啟用 TFTP
enable-tftp
tftp-root=/var/lib/tftpboot
```
*   **`port=0`**: 停用 Dnsmasq 的 DNS 功能，因為我們只將它用作 DHCP 和 TFTP 伺服器。
*   **`dhcp-range`**: 設定 IP 分配範圍為 `192.168.1.50` 到 `192.168.1.150`，子網路遮罩為 `255.255.255.0`，租期為 12 小時。
*   **`dhcp-boot` & `dhcp-match`**: 這是一組條件判斷，用來提供正確的開機檔案：
    *   預設為傳統 BIOS 提供 `undionly.kpxe`。
    *   如果偵測到客戶端是 UEFI 架構 (`option:client-arch,7` 或 `9`)，則提供 `ipxe.efi`。
    *   如果偵測到客戶端本身就是 iPXE (`175`)，則直接告訴它去載入 `boot.ipxe` 腳本（通常是透過 HTTP）。
*   **`enable-tftp`**: 啟用內建的 TFTP 伺服器。
*   **`tftp-root`**: 設定 TFTP 服務的根目錄為 `/var/lib/tftpboot`。客戶端請求的任何檔案都會在這個目錄下尋找。

## 運作流程

1.  PXE 客戶端開機，在區域網路上廣播一個 DHCP 探索封包。
2.  Dnsmasq 服務在 `192.168.1.1` 上收到請求，從 `192.168.1.50-150` 範圍內挑選一個可用的 IP，連同開機檔案的名稱（例如 `ipxe.efi`）一起回應給客戶端。
3.  客戶端設定好 IP 位址後，向 Dnsmasq 的 TFTP 服務請求 `ipxe.efi` 檔案。
4.  Dnsmasq 從 `/var/lib/tftpboot` 目錄中找到並傳送 `ipxe.efi` 給客戶端。
5.  客戶端執行 `ipxe.efi`，進入 iPXE 環境，開始執行下一階段的開機腳本。
