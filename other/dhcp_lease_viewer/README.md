# Web-Based DHCP Lease Viewer

This directory contains the components for a simple web-based system to view and interact with DHCP leases provided by Dnsmasq.

## Architecture

This system consists of three main parts:

1.  **Scheduled Script (`cron`)**: A cron job runs periodically to generate a static HTML page of the current DHCP leases.
2.  **Frontend (Nginx)**: The generated `leases.html` page is served by Nginx, providing a user-friendly, searchable table of leases.
3.  **Backend API (Flask)**: A simple Python Flask service runs in the background to provide a `ping` API, allowing users to check the status of a leased IP directly from the web page.

## Component Breakdown

### 1. `generate_lease_html.py`
*   **Language:** Python 3
*   **Purpose:** This script reads the raw Dnsmasq lease file, parses it, and injects the data into an HTML template.
*   **Process:**
    1.  Reads lease data from `/var/lib/misc/dnsmasq.leases`.
    2.  Reads an HTML template from `leases_template.html`.
    3.  Injects the formatted lease information and an "Last Updated" timestamp into the template.
    4.  Writes the final, complete page to `/var/www/html/leases.html`.

### 2. `ping_api.py`
*   **Language:** Python 3 with Flask
*   **Purpose:** Provides a backend API to safely execute `ping` commands.
*   **Functionality:**
    *   Starts a web server listening on port `5000`.
    *   Exposes a single endpoint: `/api/ping/<ip_address>`.
    *   When called, it validates that the requested IP is on the `192.168.1.0/24` subnet to prevent misuse.
    *   It executes the system's `ping` command and returns the output as a JSON response.
*   **Integration:** Nginx is configured to proxy any requests for `/api/` to this service running on `http://127.0.0.1:5000`.

### 3. `lease-updater`
*   **Type:** Cron Job File
*   **Location:** `/etc/cron.d/lease-updater`
*   **Schedule:** `* * * * *` (Every minute).
*   **Action:** Executes `generate_lease_html.py` as the `root` user, ensuring the `leases.html` page is kept up-to-date.

### 4. `leases_template.html`
*   **Type:** HTML Template
*   **Purpose:** This is the master template for the lease viewer page. It contains all the static HTML, CSS, and JavaScript. The `generate_lease_html.py` script replaces placeholder comments (`<!--LEASE_ROWS-->` and `<!--LAST_UPDATED-->`) with dynamic content.

## How it Works (Flow)

1.  The `lease-updater` cron job triggers `generate_lease_html.py` every minute.
2.  The Python script generates a fresh `leases.html` file and saves it in `/var/www/html/`.
3.  A user navigates to `http://<server_ip>/leases.html`.
4.  Nginx serves the static `leases.html` file.
5.  The user clicks a "Ping" button on the page for a specific IP.
6.  JavaScript on the page sends a `fetch` request to `/api/ping/<ip>`.
7.  Nginx receives the request and, due to its proxy configuration, forwards it to the `ping_api.py` service on port 5000.
8.  The Flask service executes the ping, captures the result, and sends it back as JSON.
9.  The JavaScript on the page receives the JSON and displays the ping result to the user.
