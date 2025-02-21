import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import socket
import requests

# Function to check if a port is open and gather information
def check_port():
    ip = ip_entry.get()
    port = port_entry.get()
    if not ip or not port:
        messagebox.showerror("Error", "Please enter a valid IP address and port")
        return

    try:
        port = int(port)

        # Check if the port is open
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        if result == 0:
            port_status = "Open"
        else:
            port_status = "Closed"
        sock.close()

        # Gather information about the service running on the port
        service_info = "N/A"
        try:
            service = socket.getservbyport(port)
            service_info = f"Service: {service}"
        except:
            service_info = "Service: Unknown"

        # Display the information
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"IP: {ip}\n")
        result_text.insert(tk.END, f"Port: {port}\n")
        result_text.insert(tk.END, f"Status: {port_status}\n")
        result_text.insert(tk.END, f"{service_info}\n")

        # Additional information gathering (hypothetical)
        if port_status == "Open":
            try:
                response = requests.get(f"http://{ip}:{port}", timeout=2)
                result_text.insert(tk.END, f"HTTP Response: {response.status_code}\n")
                if response.headers:
                    result_text.insert(tk.END, "Headers:\n")
                    for key, value in response.headers.items():
                        result_text.insert(tk.END, f"{key}: {value}\n")
            except Exception as e:
                result_text.insert(tk.END, f"HTTP Request Error: {e}\n")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to check port: {e}")

# Create the main window
root = tk.Tk()
root.title("Public IP Port Checker")

# Create and place widgets
ip_label = tk.Label(root, text="Target IP Address:")
ip_label.grid(row=0, column=0, padx=10, pady=10)

ip_entry = tk.Entry(root, width=20)
ip_entry.grid(row=0, column=1, padx=10, pady=10)

port_label = tk.Label(root, text="Port:")
port_label.grid(row=1, column=0, padx=10, pady=10)

port_entry = tk.Entry(root, width=20)
port_entry.grid(row=1, column=1, padx=10, pady=10)

check_button = tk.Button(root, text="Check Port", command=check_port)
check_button.grid(row=1, column=2, padx=10, pady=10)

result_text = scrolledtext.ScrolledText(root, height=20, width=70)
result_text.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

# Start the main loop
root.mainloop()