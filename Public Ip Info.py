import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests

# Function to gather IP information
def gather_ip_info():
    ip = ip_entry.get()
    if not ip:
        messagebox.showerror("Error", "Please enter a valid IP address")
        return

    try:
        # Get IP information from ipinfo.io
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        data = response.json()

        # Extract relevant information
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

        # Display the information
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, f"Provider: {provider}\n")
        result_text.insert(tk.END, f"Hostname: {hostname}\n")
        result_text.insert(tk.END, f"Organization: {organization}\n")
        result_text.insert(tk.END, f"Country: {country}\n")
        result_text.insert(tk.END, f"City: {city}\n")
        result_text.insert(tk.END, f"Location: {location}\n")
        result_text.insert(tk.END, f"Type: {ip_type}\n")
        result_text.insert(tk.END, f"VPN: {vpn}\n")
        result_text.insert(tk.END, f"Satellite: {satellite}\n")
        result_text.insert(tk.END, f"Anonymous: {anonymous}\n")
        result_text.insert(tk.END, f"Hosting: {hosting}\n")
        result_text.insert(tk.END, f"Proxy: {proxy}\n")
        result_text.insert(tk.END, f"Tor Browser: {tor}\n")
        result_text.insert(tk.END, f"Relay: {relay}\n")
        result_text.insert(tk.END, f"Service: {service}\n")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to gather IP information: {e}")

# Create the main window
root = tk.Tk()
root.title("IP Info Gather Tool")

# Create and place widgets
ip_label = tk.Label(root, text="Target IP Address:")
ip_label.grid(row=0, column=0, padx=10, pady=10)

ip_entry = tk.Entry(root, width=20)
ip_entry.grid(row=0, column=1, padx=10, pady=10)

gather_button = tk.Button(root, text="Gather Info", command=gather_ip_info)
gather_button.grid(row=0, column=2, padx=10, pady=10)

result_text = scrolledtext.ScrolledText(root, height=20, width=70)
result_text.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

# Start the main loop
root.mainloop()