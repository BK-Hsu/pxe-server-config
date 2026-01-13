# HTTP 服務 (Nginx)

此目錄包含為 PXE 環境提供 HTTP 服務的 Nginx 設定。

## 用途

在 PXE 流程中，HTTP 主要扮演第二階段的角色。當客戶端透過 TFTP 取得並執行 iPXE 開機程式後，iPXE 會轉而使用 HTTP 協定來下載後續的檔案。使用 HTTP 的優點是**速度比 TFTP 快得多**，非常適合用來傳輸大型檔案，例如作業系統的安裝映像檔 (ISO) 或內核檔案。

在此設定中，Nginx 主要用於：
1.  提供 iPXE 開機腳本 (`boot.ipxe`)。
2.  提供完整的作業系統安裝檔案（例如存放在 `/pxe/ubuntu24` 或 `/pxe/windows` 目錄下的檔案）。

## 設定檔說明

### `default.conf`
```
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

        # ... (其他 location 設定)
}
```
*   **`listen 80 default_server`**: 指示 Nginx 在所有 IPv4 和 IPv6 位址的 80 埠上監聽連線。`default_server` 表示這是處理未知主機名稱請求的預設伺服器。
*   **`root /var/www/html`**: 這是 Nginx 的**網站根目錄**。所有透過 HTTP 請求的 URL 路徑，都會對應到這個伺服器檔案系統目錄。
*   **`server_name _`**: 這是一個萬用字元，表示這個 `server` 區塊會處理所有指向此伺服器 IP 的請求，無論 `Host` 標頭是什麼。
*   **`location /`**: 這是處理所有請求的預設區塊。
    *   **`autoindex on`**: 如果請求的路徑是一個目錄，且該目錄下沒有 `index` 指令中定義的檔案（如 `index.html`），Nginx 會自動產生一個包含該目錄所有檔案和子目錄列表的頁面。這在 PXE 環境中非常有用，方便瀏覽可用的安裝資源。
    *   **`try_files $uri $uri/ =404`**: Nginx 會依序嘗試尋找與請求 URI 完全相符的檔案 (`$uri`)，或是一個與請求 URI 同名的目錄 (`$uri/`)。如果都找不到，則返回 404 Not Found 錯誤。

## 運作流程

1.  iPXE 環境啟動後，它會執行 `boot.ipxe` 腳本中的指令。
2.  `boot.ipxe` 腳本中通常會有類似 `chain http://192.168.1.1/pxe/ubuntu24/vmlinuz ...` 的指令。
3.  iPXE 客戶端向 Nginx 伺服器發起一個對 `http://192.168.1.1/pxe/ubuntu24/vmlinuz` 的 GET 請求。
4.  Nginx 收到請求後，根據 `root /var/www/html` 的設定，將 URL 路徑 `/pxe/ubuntu24/vmlinuz` 對應到伺服器上的檔案路徑 `/var/www/html/pxe/ubuntu24/vmlinuz`。
5.  Nginx 找到該檔案，並透過 HTTP 將其內容傳回給 iPXE 客戶端。
6.  iPXE 客戶端接收檔案，繼續執行後續的開機流程。
