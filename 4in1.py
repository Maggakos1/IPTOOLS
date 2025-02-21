import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import socket
import threading
import requests

# Global variables
scanning = False
open_ports = []

# Function to scan ports (Public IP Port Scanner)
def public_port_scan(ip, port):
    if stop_event.is_set():
        return
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            result = s.connect_ex((ip, port))
            if result == 0:
                open_ports.append(port)
    except:
        pass

# Function to start scanning (Public IP Port Scanner)
def start_public_scan():
    global scanning, stop_event
    target_ip = public_ip_entry.get()
    if not target_ip:
        messagebox.showerror("Error", "Please enter a valid IP address")
        return

    scanning = True
    stop_event = threading.Event()
    open_ports.clear()
    total_ports = 65535
    public_progress["maximum"] = total_ports

    def scan_ports():
        for port in range(0, total_ports + 1):
            if stop_event.is_set():
                break
            public_progress["value"] = port
            public_result_text.insert(tk.END, f"Scanning port {port}\n")
            public_result_text.see(tk.END)
            thread = threading.Thread(target=public_port_scan, args=(target_ip, port))
            thread.start()
        stop_public_scan()
        messagebox.showinfo("Scan Complete", f"Found {len(open_ports)} open ports")

    public_scan_button.config(state=tk.DISABLED)
    public_terminate_button.config(state=tk.NORMAL)
    threading.Thread(target=scan_ports).start()

# Function to stop scanning (Public IP Port Scanner)
def stop_public_scan():
    global scanning
    stop_event.set()
    scanning = False
    public_scan_button.config(state=tk.NORMAL)
    public_terminate_button.config(state=tk.DISABLED)

# Function to show open ports (Public IP Port Scanner)
def show_public_open_ports():
    if not open_ports:
        messagebox.showinfo("Open Ports", "No open ports found.")
        return
    open_ports_window = tk.Toplevel(root)
    open_ports_window.title("Open Ports")
    listbox = tk.Listbox(open_ports_window, width=50, height=20)
    listbox.pack(padx=10, pady=10)
    for port in open_ports:
        listbox.insert(tk.END, f"Port {port} - OPEN")

# Function to scan ports (Local IP Port Scanner)
def scan_ports(ip, start_port, end_port, result_text, progress_bar):
    global scanning, open_ports
    open_ports = []
    for port in range(start_port, end_port + 1):
        if not scanning:
            break
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            result = sock.connect_ex((ip, port))
            if result == 0:
                open_ports.append(port)
                result_text.insert(tk.END, f"Port {port} is open\n")
            sock.close()
        except Exception as e:
            result_text.insert(tk.END, f"Error scanning port {port}: {e}\n")
        progress_bar['value'] = ((port - start_port) / (end_port - start_port)) * 100
        root.update_idletasks()
    scanning = False
    scan_button.config(state=tk.NORMAL)
    terminate_button.config(state=tk.DISABLED)
    if open_ports:
        messagebox.showinfo("Scan Complete", f"Scan completed. Open ports: {open_ports}")
    else:
        messagebox.showinfo("Scan Complete", "Scan completed. No open ports found.")

# Function to start scanning (Local IP Port Scanner)
def start_scan():
    global scanning
    ip = local_ip_entry.get()
    if not ip:
        messagebox.showerror("Error", "Please enter a valid IP address")
        return
    scanning = True
    scan_button.config(state=tk.DISABLED)
    terminate_button.config(state=tk.NORMAL)
    local_result_text.delete(1.0, tk.END)
    local_progress_bar['value'] = 0
    threading.Thread(target=scan_ports, args=(ip, 0, 65535, local_result_text, local_progress_bar)).start()

# Function to terminate scanning (Local IP Port Scanner)
def terminate_scan():
    global scanning
    scanning = False
    scan_button.config(state=tk.NORMAL)
    terminate_button.config(state=tk.DISABLED)

# Function to show open ports (Local IP Port Scanner)
def show_open_ports():
    if not open_ports:
        messagebox.showinfo("Open Ports", "No open ports found.")
        return
    open_ports_window = tk.Toplevel(root)
    open_ports_window.title("Open Ports")
    open_ports_label = tk.Label(open_ports_window, text="Open Ports:", font=("Arial", 14))
    open_ports_label.pack(pady=10)
    open_ports_text = scrolledtext.ScrolledText(open_ports_window, width=50, height=20)
    open_ports_text.pack(padx=10, pady=10)
    for port in open_ports:
        open_ports_text.insert(tk.END, f"Port {port} is open\n")

# Function to gather IP information (Public IP Info)
def gather_ip_info():
    ip = public_ip_entry.get()
    if not ip:
        messagebox.showerror("Error", "Please enter a valid IP address")
        return

    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        data = response.json()

        provider = data.get("org", "N/A")
        hostname = data.get("hostname", "N/A")
        organization = data.get("org", "N/A").split()[0] if data.get("org") else "N/A"
        country = data.get("country", "N/A")
        city = data.get("city", "N/A")
        location = data.get("loc", "N/A")
        ip_type = data.get("type", "N/A")
        vpn = "Yes" if data.get("vpn", False) else "No"
        satellite = "Yes" if data.get("satellite", False) else "No"
        anonymous = "Yes" if data.get("anonymous", False) else "No"
        hosting = "Yes" if data.get("hosting", False) else "No"
        proxy = "Yes" if data.get("proxy", False) else "No"
        tor = "Yes" if data.get("tor", False) else "No"
        relay = "Yes" if data.get("relay", False) else "No"
        service = data.get("service", "N/A")

        public_result_text.delete(1.0, tk.END)
        public_result_text.insert(tk.END, f"Provider: {provider}\n")
        public_result_text.insert(tk.END, f"Hostname: {hostname}\n")
        public_result_text.insert(tk.END, f"Organization: {organization}\n")
        public_result_text.insert(tk.END, f"Country: {country}\n")
        public_result_text.insert(tk.END, f"City: {city}\n")
        public_result_text.insert(tk.END, f"Location: {location}\n")
        public_result_text.insert(tk.END, f"Type: {ip_type}\n")
        public_result_text.insert(tk.END, f"VPN: {vpn}\n")
        public_result_text.insert(tk.END, f"Satellite: {satellite}\n")
        public_result_text.insert(tk.END, f"Anonymous: {anonymous}\n")
        public_result_text.insert(tk.END, f"Hosting: {hosting}\n")
        public_result_text.insert(tk.END, f"Proxy: {proxy}\n")
        public_result_text.insert(tk.END, f"Tor Browser: {tor}\n")
        public_result_text.insert(tk.END, f"Relay: {relay}\n")
        public_result_text.insert(tk.END, f"Service: {service}\n")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to gather IP information: {e}")

# Function to check if a port is open (Public IP Port Checker)
def check_port():
    ip = public_ip_port_entry.get()
    port = public_port_entry.get()
    if not ip or not port:
        messagebox.showerror("Error", "Please enter a valid IP address and port")
        return

    try:
        port = int(port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        if result == 0:
            port_status = "Open"
        else:
            port_status = "Closed"
        sock.close()

        service_info = "N/A"
        try:
            service = socket.getservbyport(port)
            service_info = f"Service: {service}"
        except:
            service_info = "Service: Unknown"

        public_port_result_text.delete(1.0, tk.END)
        public_port_result_text.insert(tk.END, f"IP: {ip}\n")
        public_port_result_text.insert(tk.END, f"Port: {port}\n")
        public_port_result_text.insert(tk.END, f"Status: {port_status}\n")
        public_port_result_text.insert(tk.END, f"{service_info}\n")

        if port_status == "Open":
            try:
                response = requests.get(f"http://{ip}:{port}", timeout=2)
                public_port_result_text.insert(tk.END, f"HTTP Response: {response.status_code}\n")
                if response.headers:
                    public_port_result_text.insert(tk.END, "Headers:\n")
                    for key, value in response.headers.items():
                        public_port_result_text.insert(tk.END, f"{key}: {value}\n")
            except Exception as e:
                public_port_result_text.insert(tk.END, f"HTTP Request Error: {e}\n")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to check port: {e}")

# Create the main window
root = tk.Tk()
root.title("4-in-1 Tool")

# Create a notebook (tabbed interface)
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Public IP Port Scanner Tab
public_port_tab = ttk.Frame(notebook)
notebook.add(public_port_tab, text="Public IP Port Scanner")

public_ip_label = tk.Label(public_port_tab, text="Public IP Address:")
public_ip_label.grid(row=0, column=0, padx=10, pady=10)

public_ip_entry = tk.Entry(public_port_tab, width=20)
public_ip_entry.grid(row=0, column=1, padx=10, pady=10)

public_scan_button = tk.Button(public_port_tab, text="Scan Ports", command=start_public_scan)
public_scan_button.grid(row=0, column=2, padx=10, pady=10)

public_terminate_button = tk.Button(public_port_tab, text="Terminate", command=stop_public_scan, state=tk.DISABLED)
public_terminate_button.grid(row=0, column=3, padx=10, pady=10)

public_result_text = tk.Text(public_port_tab, height=10, width=80)
public_result_text.grid(row=1, column=0, columnspan=4, padx=10, pady=10)

public_progress = ttk.Progressbar(public_port_tab, orient='horizontal', length=600, mode='determinate')
public_progress.grid(row=2, column=0, columnspan=4, padx=10, pady=10)

public_open_ports_button = tk.Button(public_port_tab, text="Open Ports", command=show_public_open_ports)
public_open_ports_button.grid(row=3, column=0, padx=10, pady=10)

# Local IP Port Scanner Tab
local_tab = ttk.Frame(notebook)
notebook.add(local_tab, text="Local IP Port Scanner")

local_ip_label = tk.Label(local_tab, text="Local IP Address:")
local_ip_label.grid(row=0, column=0, padx=10, pady=10)

local_ip_entry = tk.Entry(local_tab, width=20)
local_ip_entry.grid(row=0, column=1, padx=10, pady=10)

scan_button = tk.Button(local_tab, text="Scan Ports", command=start_scan)
scan_button.grid(row=0, column=2, padx=10, pady=10)

terminate_button = tk.Button(local_tab, text="Terminate", command=terminate_scan, state=tk.DISABLED)
terminate_button.grid(row=0, column=3, padx=10, pady=10)

local_result_text = tk.Text(local_tab, height=10, width=80)
local_result_text.grid(row=1, column=0, columnspan=4, padx=10, pady=10)

local_progress_bar = ttk.Progressbar(local_tab, orient="horizontal", length=600, mode="determinate")
local_progress_bar.grid(row=2, column=0, columnspan=4, padx=10, pady=10)

open_ports_button = tk.Button(local_tab, text="Open Ports", command=show_open_ports)
open_ports_button.grid(row=3, column=0, padx=10, pady=10)

# Public IP Info Tab
public_tab = ttk.Frame(notebook)
notebook.add(public_tab, text="Public IP Info")

public_ip_label = tk.Label(public_tab, text="Target IP Address:")
public_ip_label.grid(row=0, column=0, padx=10, pady=10)

public_ip_entry = tk.Entry(public_tab, width=20)
public_ip_entry.grid(row=0, column=1, padx=10, pady=10)

gather_button = tk.Button(public_tab, text="Gather Info", command=gather_ip_info)
gather_button.grid(row=0, column=2, padx=10, pady=10)

public_result_text = scrolledtext.ScrolledText(public_tab, height=20, width=70)
public_result_text.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

# Public IP Port Checker Tab
public_port_tab = ttk.Frame(notebook)
notebook.add(public_port_tab, text="Public IP Port Checker")

public_ip_port_label = tk.Label(public_port_tab, text="Target IP Address:")
public_ip_port_label.grid(row=0, column=0, padx=10, pady=10)

public_ip_port_entry = tk.Entry(public_port_tab, width=20)
public_ip_port_entry.grid(row=0, column=1, padx=10, pady=10)

public_port_label = tk.Label(public_port_tab, text="Port:")
public_port_label.grid(row=1, column=0, padx=10, pady=10)

public_port_entry = tk.Entry(public_port_tab, width=20)
public_port_entry.grid(row=1, column=1, padx=10, pady=10)

check_button = tk.Button(public_port_tab, text="Check Port", command=check_port)
check_button.grid(row=1, column=2, padx=10, pady=10)

public_port_result_text = scrolledtext.ScrolledText(public_port_tab, height=20, width=70)
public_port_result_text.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

# Credits Tab
credits_tab = ttk.Frame(notebook)
notebook.add(credits_tab, text="Credits")

credits_label = tk.Label(credits_tab, text="Created by Panos Daflos", font=("Arial", 14))
credits_label.pack(pady=20)

# Start the main loop
root.mainloop()