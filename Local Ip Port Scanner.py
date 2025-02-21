import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import socket
import threading

# Global variable to control the scanning process
scanning = False
open_ports = []

# Function to scan ports
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

# Function to start scanning
def start_scan():
    global scanning
    ip = ip_entry.get()
    if not ip:
        messagebox.showerror("Error", "Please enter a valid IP address")
        return
    scanning = True
    scan_button.config(state=tk.DISABLED)
    terminate_button.config(state=tk.NORMAL)
    result_text.delete(1.0, tk.END)
    progress_bar['value'] = 0
    threading.Thread(target=scan_ports, args=(ip, 0, 65535, result_text, progress_bar)).start()

# Function to terminate scanning
def terminate_scan():
    global scanning
    scanning = False
    scan_button.config(state=tk.NORMAL)
    terminate_button.config(state=tk.DISABLED)

# Function to show open ports
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

# Function to show credits
def show_credits():
    credits_window = tk.Toplevel(root)
    credits_window.title("Credits")
    credits_label = tk.Label(credits_window, text="Created by Panos Daflos", font=("Arial", 14))
    credits_label.pack(pady=20)

# Create the main window
root = tk.Tk()
root.title("Port Scanner")

# Create and place widgets
ip_label = tk.Label(root, text="Local IP Address:")
ip_label.grid(row=0, column=0, padx=10, pady=10)

ip_entry = tk.Entry(root, width=20)
ip_entry.grid(row=0, column=1, padx=10, pady=10)

scan_button = tk.Button(root, text="Scan Ports", command=start_scan)
scan_button.grid(row=0, column=2, padx=10, pady=10)

terminate_button = tk.Button(root, text="Terminate", command=terminate_scan, state=tk.DISABLED)
terminate_button.grid(row=0, column=3, padx=10, pady=10)

result_text = tk.Text(root, height=20, width=80)
result_text.grid(row=1, column=0, columnspan=4, padx=10, pady=10)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=600, mode="determinate")
progress_bar.grid(row=2, column=0, columnspan=4, padx=10, pady=10)

open_ports_button = tk.Button(root, text="Open Ports", command=show_open_ports)
open_ports_button.grid(row=3, column=0, padx=10, pady=10)

credits_button = tk.Button(root, text="Credits", command=show_credits)
credits_button.grid(row=3, column=1, padx=10, pady=10)

# Start the main loop
root.mainloop()