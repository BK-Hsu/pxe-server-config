echo "--- 1. 檢查 Nginx 與 Dnsmasq 服務狀態 ---"
systemctl is-active nginx.service && echo "Nginx 運行正常" || echo "Nginx 異常"
systemctl is-active dnsmasq.service && echo "Dnsmasq 運行正常" || echo "Dnsmasq 異常"

echo -e "\n--- 2. 檢查網路埠監聽 (80, 67, 69) ---"
# 安裝 net-tools 以確保 netstat 可用
apt install net-tools -y > /dev/null
netstat -tulpn | grep -E '(:80|:67|:69)'

echo -e "\n--- 3. Nginx (HTTP) 自我測試 ---"
curl -I http://localhost/pxe/boot.ipxe
# 如果檔案不存在或路徑錯誤，這裡可能會失敗，請確保 boot.ipxe 已經建立

echo -e "\n--- 4. Dnsmasq (TFTP) 自我測試 ---"
# 使用 tftp 客戶端測試下載引導檔
apt install tftp-hpa -y > /dev/null
tftp 192.168.1.1 -c get ipxe.efi /tmp/test_ipxe_check.efi && ls -lh /tmp/test_ipxe_check.efi
# 檢查檔案大小是否大於零
