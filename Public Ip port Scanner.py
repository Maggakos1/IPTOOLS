import socket
import threading
import tkinter as tk
from tkinter import ttk, messagebox

class PortScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Port Scanner")
        self.root.geometry("600x400")

        # Scan control variables
        self.scan_active = False
        self.stop_event = threading.Event()

        # Main UI components
        self.create_main_interface()

    def create_main_interface(self):
        # IP Address Input
        ttk.Label(self.root, text="Public IP Address:").pack(pady=5)
        self.ip_entry = ttk.Entry(self.root, width=25)
        self.ip_entry.pack(pady=5)

        # Scan Controls
        self.scan_button = ttk.Button(self.root, text="Scan Ports", command=self.start_scan)
        self.scan_button.pack(pady=5)

        self.terminate_button = ttk.Button(self.root, text="Terminate",
                                         command=self.stop_scan, state=tk.DISABLED)
        self.terminate_button.pack(pady=5)

        # Progress bar
        self.progress = ttk.Progressbar(self.root, orient='horizontal',
                                      length=400, mode='determinate')
        self.progress.pack(pady=10)

        # Results display
        self.results_text = tk.Text(self.root, height=10, width=70)
        self.results_text.pack(pady=5)

        # Navigation buttons
        nav_frame = ttk.Frame(self.root)
        nav_frame.pack(pady=10)

        ttk.Button(nav_frame, text="Open Ports",
                 command=self.show_open_ports).grid(row=0, column=0, padx=5)
        ttk.Button(nav_frame, text="Credits",
                 command=self.show_credits).grid(row=0, column=1, padx=5)

        # Open ports storage
        self.open_ports = []

    def port_scan(self, ip, port):
        if self.stop_event.is_set():
            return
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                result = s.connect_ex((ip, port))
                if result == 0:
                    self.open_ports.append(port)
        except:
            pass

    def scan_ports(self):
        target_ip = self.ip_entry.get()
        if not target_ip:
            messagebox.showerror("Error", "Please enter a valid IP address")
            return

        self.open_ports.clear()
        total_ports = 65535
        self.progress["maximum"] = total_ports

        try:
            for port in range(0, total_ports + 1):
                if self.stop_event.is_set():
                    break
                self.progress["value"] = port
                self.results_text.insert(tk.END, f"Scanning port {port}\n")
                self.results_text.see(tk.END)
                thread = threading.Thread(target=self.port_scan, args=(target_ip, port))
                thread.start()
        finally:
            self.stop_scan()
            messagebox.showinfo("Scan Complete",
                              f"Found {len(self.open_ports)} open ports")

    def start_scan(self):
        self.scan_active = True
        self.stop_event.clear()
        self.scan_button.config(state=tk.DISABLED)
        self.terminate_button.config(state=tk.NORMAL)
        scan_thread = threading.Thread(target=self.scan_ports)
        scan_thread.start()

    def stop_scan(self):
        self.stop_event.set()
        self.scan_active = False
        self.scan_button.config(state=tk.NORMAL)
        self.terminate_button.config(state=tk.DISABLED)

    def show_open_ports(self):
        open_ports_window = tk.Toplevel(self.root)
        open_ports_window.title("Open Ports")

        listbox = tk.Listbox(open_ports_window, width=50, height=20)
        listbox.pack(padx=10, pady=10)

        for port in self.open_ports:
            listbox.insert(tk.END, f"Port {port} - OPEN")

    def show_credits(self):
        credits_window = tk.Toplevel(self.root)
        credits_window.title("Credits")
        ttk.Label(credits_window, text="Developer:", font=('Arial', 12, 'bold')).pack(pady=5)
        ttk.Label(credits_window, text="Panos Daflos", font=('Arial', 14)).pack(pady=10)
        ttk.Label(credits_window, text="This tool is for educational purposes only",
                font=('Arial', 10)).pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = PortScannerApp(root)
    root.mainloop()