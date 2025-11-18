import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import requests
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import os
from datetime import datetime
import subprocess
import sys
import winreg
import json
import platform
import re
import ctypes
import socket
import socks
from urllib.parse import urlparse
import random

class ProxyClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Proxy Client - Windows 11")
        self.root.geometry("1200x850")
        self.root.configure(bg='#f0f0f0')
        
        # Current proxy settings
        self.current_proxy = None
        self.system_proxy_enabled = False
        self.proxy_active = False
        
        # Initialize checking_active early to prevent AttributeError
        self.checking_active = False
        self.stop_checking_flag = False
        
        # Modern styling
        self.style = ttk.Style()
        self.style.theme_use('vista')
        
        self.proxies = []
        self.checker_proxies = []
        self.settings_file = "proxy_settings.json"
        
        # NEW: Auto-rotation variables
        self.auto_rotate_active = False
        self.rotate_timer = None
        self.rotation_proxies = []
        
        # Load saved data
        self.load_data()
        
        self.setup_ui()
        
        # Initial IP check
        self.check_current_ip()
        
    def load_data(self):
        """Load proxies and settings from JSON file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    # Convert old format to new format if needed
                    self.proxies = self._convert_old_proxy_format(data.get('proxies', []))
                    self.current_proxy = data.get('current_proxy')
        except Exception as e:
            print(f"Error loading data: {e}")
            self.proxies = []
    
    def _convert_old_proxy_format(self, proxies):
        """Convert old proxy format to new format with 'ip' key"""
        converted = []
        for proxy in proxies:
            # If proxy uses 'host' instead of 'ip', convert it
            if 'host' in proxy and 'ip' not in proxy:
                proxy['ip'] = proxy['host']
                del proxy['host']
            converted.append(proxy)
        return converted
    
    def save_data(self):
        """Save proxies and settings to JSON file"""
        try:
            data = {
                'proxies': self.proxies,
                'current_proxy': self.current_proxy
            }
            with open(self.settings_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
        
    def setup_ui(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Proxy Client
        self.client_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.client_frame, text="🌐 Proxy Client")
        
        # Tab 2: Proxy Checker
        self.checker_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.checker_frame, text="⚡ Proxy Checker")
        
        # Tab 3: Bulk Import
        self.import_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.import_frame, text="📥 Bulk Import")
        
        # Tab 4: IP Information
        self.info_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.info_frame, text="🌍 IP Information")
        
        self.setup_client_tab()
        self.setup_checker_tab()
        self.setup_import_tab()
        self.setup_info_tab()
        
        # Initial IP check
        self.check_current_ip()
        
    def setup_client_tab(self):
        # Main container for client tab
        main_frame = ttk.Frame(self.client_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title section
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="🌐 Proxy Client", font=('Segoe UI', 18, 'bold'), 
                 background='#f0f0f0').pack(side=tk.LEFT)
        
        # Current status frame
        status_frame = ttk.LabelFrame(main_frame, text="Current Connection Status", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        status_inner = ttk.Frame(status_frame)
        status_inner.pack(fill=tk.X)
        
        self.status_label = ttk.Label(status_inner, text="❌ Proxy Disabled", 
                                     font=('Segoe UI', 12, 'bold'), foreground='red')
        self.status_label.pack(side=tk.LEFT)
        
        self.current_ip_label = ttk.Label(status_inner, text="Your IP: Checking...", 
                                         font=('Segoe UI', 10))
        self.current_ip_label.pack(side=tk.LEFT, padx=(20, 0))
        
        self.proxy_ip_label = ttk.Label(status_inner, text="Proxy IP: None", 
                                       font=('Segoe UI', 10))
        self.proxy_ip_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Control buttons frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Proxy control buttons - ALWAYS VISIBLE
        self.enable_btn = ttk.Button(control_frame, text="✅ Enable Proxy", 
                                   command=self.enable_proxy)
        self.enable_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.disable_btn = ttk.Button(control_frame, text="🛑 Disable Proxy", 
                                    command=self.disable_proxy)
        self.disable_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(control_frame, text="🔄 Check My IP", 
                  command=self.check_current_ip).pack(side=tk.LEFT, padx=(0, 5))
        
        # System proxy toggle
        self.system_proxy_var = tk.BooleanVar()
        self.system_proxy_cb = ttk.Checkbutton(control_frame, text="Set System Proxy (for ALL applications)", 
                       variable=self.system_proxy_var,
                       command=self.toggle_system_proxy)
        self.system_proxy_cb.pack(side=tk.LEFT, padx=(20, 0))
        
        # NEW: Auto Rotate Proxy Feature
        self.auto_rotate_var = tk.BooleanVar()
        self.auto_rotate_cb = ttk.Checkbutton(control_frame, text="🔄 Auto Rotate Proxies", 
                                            variable=self.auto_rotate_var,
                                            command=self.toggle_auto_rotate)
        self.auto_rotate_cb.pack(side=tk.LEFT, padx=(20, 0))
        
        # NEW: Rotation interval
        ttk.Label(control_frame, text="Rotate every:").pack(side=tk.LEFT, padx=(20, 5))
        self.rotate_interval_var = tk.StringVar(value="30")
        rotate_spin = ttk.Spinbox(control_frame, from_=5, to=300, width=5, 
                                textvariable=self.rotate_interval_var)
        rotate_spin.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(control_frame, text="sec").pack(side=tk.LEFT)
        
        # Proxy management frame
        mgmt_frame = ttk.Frame(main_frame)
        mgmt_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(mgmt_frame, text="📁 Load Proxies", 
                  command=self.load_proxies).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(mgmt_frame, text="✏️ Add Manually", 
                  command=self.add_manual_proxy).pack(side=tk.LEFT, padx=(0, 5))
        
        # NEW: Random Proxy Button
        ttk.Button(mgmt_frame, text="🎲 Random Proxy", 
                  command=self.enable_random_proxy).pack(side=tk.LEFT, padx=(0, 5))
        
        # NEW: One-Click Test & Enable
        ttk.Button(mgmt_frame, text="⚡ Test & Enable", 
                  command=self.quick_test_and_enable).pack(side=tk.LEFT, padx=(0, 5))
        
        # Simple checker in client tab
        ttk.Button(mgmt_frame, text="🔍 Check Selected", 
                  command=self.quick_check_selected).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(mgmt_frame, text="🔍 Check All Proxies", 
                  command=self.check_all_proxies).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(mgmt_frame, text="💾 Export Working", 
                  command=self.export_working).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(mgmt_frame, text="🗑️ Clear List", 
                  command=self.clear_list).pack(side=tk.LEFT)
        
        # NEW: Backup/Restore buttons
        ttk.Button(mgmt_frame, text="💾 Backup", 
                  command=self.backup_config).pack(side=tk.LEFT, padx=(20, 5))
        ttk.Button(mgmt_frame, text="📂 Restore", 
                  command=self.restore_config).pack(side=tk.LEFT, padx=(0, 5))
        
        # Progress section for client tab
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.client_progress_var = tk.DoubleVar()
        self.client_progress_bar = ttk.Progressbar(progress_frame, variable=self.client_progress_var, maximum=100)
        self.client_progress_bar.pack(fill=tk.X, side=tk.LEFT, expand=True)
        
        self.client_progress_label = ttk.Label(progress_frame, text="Ready")
        self.client_progress_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Statistics frame for client tab
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.total_client_label = ttk.Label(stats_frame, text="Total: 0", font=('Segoe UI', 9))
        self.total_client_label.pack(side=tk.LEFT, padx=(0, 15))
        
        self.working_client_label = ttk.Label(stats_frame, text="Working: 0", font=('Segoe UI', 9), foreground='green')
        self.working_client_label.pack(side=tk.LEFT, padx=(0, 15))
        
        self.failed_client_label = ttk.Label(stats_frame, text="Failed: 0", font=('Segoe UI', 9), foreground='red')
        self.failed_client_label.pack(side=tk.LEFT)
        
        # NEW: Auto-rotate status
        self.rotate_status_label = ttk.Label(stats_frame, text="Auto-Rotate: Off", font=('Segoe UI', 9), foreground='orange')
        self.rotate_status_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Table frame
        table_frame = ttk.LabelFrame(main_frame, text="Available Proxies - Right-click for options", padding="5")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create treeview (table)
        columns = ('#', 'Type', 'IP', 'Port', 'Username', 'Password', 'Status', 'Response Time', 'Country')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)
        
        # Configure columns
        column_widths = {
            '#': 40, 'Type': 80, 'IP': 130, 'Port': 70, 'Username': 100, 
            'Password': 100, 'Status': 100, 'Response Time': 90, 'Country': 120
        }
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout for table and scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Enhanced Right-click context menu
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="🚀 Enable Proxy", command=self.context_enable_proxy)
        self.context_menu.add_command(label="⚡ Test Proxy", command=self.context_test_proxy)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📋 Copy Proxy", command=self.context_copy_proxy)
        # NEW: Copy username and password options
        self.context_menu.add_command(label="👤 Copy Username", command=self.context_copy_username)
        self.context_menu.add_command(label="🔒 Copy Password", command=self.context_copy_password)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🔄 Set as Rotating Proxy", command=self.context_set_rotate_proxy)
        self.context_menu.add_command(label="📊 Test Speed", command=self.context_test_speed)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="❌ Remove Proxy", command=self.context_remove_proxy)
        self.context_menu.add_command(label="🛑 Disable Proxy", command=self.context_disable_proxy)
        
        # Bind right-click
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # Double click to enable proxy
        self.tree.bind('<Double-1>', self.on_double_click)
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=6, font=('Consolas', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Initialize button states for client tab only
        self.update_client_button_states()
        
        # Update table with loaded data
        self.update_table()
        self.update_client_stats()

    def setup_import_tab(self):
        """Setup bulk import tab"""
        main_frame = ttk.Frame(self.import_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="📥 Bulk Proxy Import", font=('Segoe UI', 16, 'bold'), 
                 background='#f0f0f0').pack(pady=(0, 10))
        
        # Import text area
        ttk.Label(main_frame, text="Paste proxies (one per line):", 
                 font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=5)
        
        self.import_text = scrolledtext.ScrolledText(main_frame, height=15, 
                                                   bg='white', fg='black')
        self.import_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Format examples
        examples = """Supported formats:
ip:port
ip:port:user:pass
socks4://user:pass@ip:port
socks5://ip:port
http://user:pass@ip:port
https://ip:port"""
        
        example_label = ttk.Label(main_frame, text=examples, justify='left', font=('Consolas', 9))
        example_label.pack(anchor='w', pady=5)
        
        # Import buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="📥 Import to Client", 
                  command=self.import_to_client).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📥 Import to Checker", 
                  command=self.import_to_checker).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📁 Import from File", 
                  command=self.import_from_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Clear Text", 
                  command=self.clear_import_text).pack(side=tk.LEFT, padx=5)

    def setup_info_tab(self):
        """Setup IP information tab"""
        main_frame = ttk.Frame(self.info_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="🌍 IP Information", font=('Segoe UI', 16, 'bold'), 
                 background='#f0f0f0').pack(pady=(0, 10))
        
        # IP information display
        info_frame = ttk.LabelFrame(main_frame, text="Current Connection Details", padding="15")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create info labels
        self.info_labels = {}
        fields = [
            ('Public IP', 'ip'),
            ('Country', 'country'),
            ('Region', 'region'),
            ('City', 'city'),
            ('ISP', 'isp'),
            ('Proxy Type', 'proxy_type'),
            ('Status', 'status')
        ]
        
        for i, (label, key) in enumerate(fields):
            row_frame = ttk.Frame(info_frame)
            row_frame.pack(fill=tk.X, pady=8)
            
            ttk.Label(row_frame, text=f"{label}:", font=('Segoe UI', 10, 'bold'), 
                     width=15, anchor='w').pack(side=tk.LEFT)
            
            value_label = ttk.Label(row_frame, text="Loading...", font=('Segoe UI', 10),
                                  anchor='w')
            value_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
            
            self.info_labels[key] = value_label
        
        # Refresh button
        ttk.Button(main_frame, text="🔄 Refresh IP Info", 
                  command=self.refresh_ip_info, width=20).pack(pady=20)
        
        # Initial refresh
        self.refresh_ip_info()

    def setup_checker_tab(self):
        # Main container for checker tab
        main_frame = ttk.Frame(self.checker_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title section
        ttk.Label(main_frame, text="⚡ Proxy Checker", font=('Segoe UI', 16, 'bold'), 
                 background='#f0f0f0').pack(pady=(0, 10))
        
        # Enhanced control frame for checker
        enhanced_frame = ttk.Frame(main_frame)
        enhanced_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(enhanced_frame, text="🚀 Advanced Testing", 
                  command=self.advanced_proxy_testing).pack(side=tk.LEFT, padx=5)
        ttk.Button(enhanced_frame, text="📊 Speed Test All", 
                  command=self.test_all_speed).pack(side=tk.LEFT, padx=5)
        ttk.Button(enhanced_frame, text="🔗 Proxy Chains", 
                  command=self.setup_proxy_chain).pack(side=tk.LEFT, padx=5)
        
        # Control frame for checker
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(control_frame, text="📁 Load Proxies to Check", 
                  command=self.load_proxies_checker).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(control_frame, text="✏️ Add Proxy to Check", 
                  command=self.add_proxy_checker).pack(side=tk.LEFT, padx=(0, 5))
        
        self.start_check_btn = ttk.Button(control_frame, text="⚡ Start Checking", 
                                        command=self.start_checking)
        self.start_check_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_check_btn = ttk.Button(control_frame, text="🛑 Stop Checking", 
                                       command=self.stop_checking)
        self.stop_check_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(control_frame, text="💾 Export Working", 
                  command=self.export_working_checker).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(control_frame, text="🗑️ Clear", 
                  command=self.clear_checker).pack(side=tk.LEFT)
        
        # Progress section
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.checker_progress_var = tk.DoubleVar()
        self.checker_progress_bar = ttk.Progressbar(progress_frame, variable=self.checker_progress_var, maximum=100)
        self.checker_progress_bar.pack(fill=tk.X, side=tk.LEFT, expand=True)
        
        self.checker_progress_label = ttk.Label(progress_frame, text="Ready to check")
        self.checker_progress_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Statistics frame
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.total_checker_label = ttk.Label(stats_frame, text="Total: 0", font=('Segoe UI', 10, 'bold'))
        self.total_checker_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.working_checker_label = ttk.Label(stats_frame, text="Working: 0", font=('Segoe UI', 10, 'bold'), foreground='green')
        self.working_checker_label.pack(side=tk.LEFT, padx=(0, 20))
        
        self.failed_checker_label = ttk.Label(stats_frame, text="Failed: 0", font=('Segoe UI', 10, 'bold'), foreground='red')
        self.failed_checker_label.pack(side=tk.LEFT)
        
        # Checker table frame
        table_frame = ttk.LabelFrame(main_frame, text="Proxy Check Results", padding="5")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create treeview for checker
        columns = ('#', 'Type', 'IP', 'Port', 'Username', 'Password', 'Status', 'Response Time', 'Country', 'ISP')
        self.checker_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)
        
        # Configure columns
        column_widths = {
            '#': 40, 'Type': 70, 'IP': 120, 'Port': 60, 'Username': 90, 
            'Password': 90, 'Status': 90, 'Response Time': 80, 'Country': 100, 'ISP': 150
        }
        
        for col in columns:
            self.checker_tree.heading(col, text=col)
            self.checker_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbars for checker
        v_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.checker_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.checker_tree.xview)
        self.checker_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.checker_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Checker log
        log_frame = ttk.LabelFrame(main_frame, text="Checking Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.checker_log_text = scrolledtext.ScrolledText(log_frame, height=6, font=('Consolas', 9))
        self.checker_log_text.pack(fill=tk.BOTH, expand=True)
        
        # Update button states for checker tab
        self.update_checker_button_states()

    # NEW FEATURE 1: Auto Proxy Rotation
    def toggle_auto_rotate(self):
        if self.auto_rotate_var.get():
            self.start_auto_rotate()
        else:
            self.stop_auto_rotate()

    def start_auto_rotate(self):
        if not self.rotation_proxies:
            # If no specific rotation proxies set, use all working proxies
            self.rotation_proxies = [p for p in self.proxies if p.get('status') == 'Working']
        
        if not self.rotation_proxies:
            messagebox.showwarning("Warning", "No working proxies available for rotation!")
            self.auto_rotate_var.set(False)
            return
        
        self.auto_rotate_active = True
        self.rotate_status_label.config(text="Auto-Rotate: ON", foreground='green')
        self.log_message("🔄 Auto-rotation started")
        self.rotate_proxy()

    def stop_auto_rotate(self):
        self.auto_rotate_active = False
        if self.rotate_timer:
            self.root.after_cancel(self.rotate_timer)
            self.rotate_timer = None
        self.rotate_status_label.config(text="Auto-Rotate: Off", foreground='orange')
        self.log_message("🛑 Auto-rotation stopped")

    def rotate_proxy(self):
        if not self.auto_rotate_active or not self.rotation_proxies:
            return
        
        # Select random proxy from rotation list
        proxy = random.choice(self.rotation_proxies)
        self.current_proxy = proxy
        self.enable_proxy()
        
        # Schedule next rotation
        try:
            interval = int(self.rotate_interval_var.get()) * 1000  # Convert to milliseconds
        except:
            interval = 30000  # Default 30 seconds
        
        self.rotate_timer = self.root.after(interval, self.rotate_proxy)
        self.log_message(f"🔄 Next rotation in {interval//1000} seconds")

    # NEW FEATURE 2: Random Proxy Selection
    def enable_random_proxy(self):
        working_proxies = [p for p in self.proxies if p.get('status') == 'Working']
        if not working_proxies:
            messagebox.showwarning("Warning", "No working proxies available!")
            return
        
        proxy = random.choice(working_proxies)
        self.current_proxy = proxy
        self.enable_proxy()
        self.log_message(f"🎲 Enabled random proxy: {proxy['ip']}:{proxy['port']}")

    # NEW FEATURE 3 & 4: Copy Username and Password
    def context_copy_username(self):
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            proxy = self.proxies[self.tree.index(item)]
            username = proxy.get('username', '')
            if username:
                self.root.clipboard_clear()
                self.root.clipboard_append(username)
                self.log_message(f"📋 Copied username: {username}")
            else:
                self.log_message("⚠️ No username to copy")

    def context_copy_password(self):
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            proxy = self.proxies[self.tree.index(item)]
            password = proxy.get('password', '')
            if password:
                self.root.clipboard_clear()
                self.root.clipboard_append(password)
                self.log_message("📋 Copied password")
            else:
                self.log_message("⚠️ No password to copy")

    def context_set_rotate_proxy(self):
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            proxy = self.proxies[self.tree.index(item)]
            # Add to rotation list
            if proxy not in self.rotation_proxies:
                self.rotation_proxies.append(proxy)
                self.log_message(f"🔄 Added {proxy['ip']}:{proxy['port']} to rotation list")
            else:
                self.log_message(f"ℹ️ Proxy already in rotation list")

    def context_test_speed(self):
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            proxy = self.proxies[self.tree.index(item)]
            self.log_message(f"📊 Testing speed for {proxy['ip']}:{proxy['port']}...")
            threading.Thread(target=self.speed_test_single, args=(proxy, self.tree.index(item)), daemon=True).start()

    # NEW FEATURE 5: Advanced Proxy Testing
    def test_proxy_advanced(self, proxy):
        """Test proxy with multiple endpoints for better accuracy"""
        test_urls = [
            'https://api.ipify.org?format=json',
            'https://httpbin.org/ip',
            'https://ifconfig.me/all.json'
        ]
        
        for url in test_urls:
            try:
                proxy_url = self.build_proxy_url(proxy)
                proxies = {'http': proxy_url, 'https': proxy_url}
                
                auth = None
                if proxy.get('username') and proxy.get('password'):
                    auth = (proxy['username'], proxy['password'])
                
                response = requests.get(url, proxies=proxies, timeout=10, auth=auth)
                if response.status_code == 200:
                    return True, response.json().get('ip', 'Unknown')
            except:
                continue
        
        return False, 'Unknown'

    def advanced_proxy_testing(self):
        """Advanced proxy testing with multiple endpoints"""
        if not self.checker_proxies:
            messagebox.showwarning("Warning", "No proxies to test!")
            return
        
        self.checker_log_message("🚀 Starting advanced proxy testing...")
        
        def advanced_test_thread():
            for index, proxy in enumerate(self.checker_proxies):
                working, ip = self.test_proxy_advanced(proxy)
                status = 'Working' if working else 'Failed'
                self.root.after(0, self.update_checker_proxy_status, index, status, 'Advanced', ip, '')
            
            self.root.after(0, lambda: self.checker_log_message("✅ Advanced testing completed!"))
        
        threading.Thread(target=advanced_test_thread, daemon=True).start()

    # NEW FEATURE 6: Speed Testing
    def speed_test_proxy(self, proxy):
        """Test proxy speed with multiple requests"""
        try:
            proxy_url = self.build_proxy_url(proxy)
            proxies = {'http': proxy_url, 'https': proxy_url}
            
            auth = None
            if proxy.get('username') and proxy.get('password'):
                auth = (proxy['username'], proxy['password'])
            
            start_time = time.time()
            # Make multiple requests to test speed
            for _ in range(3):
                response = requests.get('https://httpbin.org/bytes/1024', 
                                      proxies=proxies, timeout=10, auth=auth)
                if response.status_code != 200:
                    return 0
            
            total_time = time.time() - start_time
            speed = (3 * 1024) / total_time  # KB/s
            return speed
        except:
            return 0

    def speed_test_single(self, proxy, index):
        speed = self.speed_test_proxy(proxy)
        if speed > 0:
            self.root.after(0, lambda: self.log_message(f"📊 {proxy['ip']}:{proxy['port']} - Speed: {speed:.1f} KB/s"))
            # Update proxy with speed info
            if 0 <= index < len(self.proxies):
                self.proxies[index]['speed'] = f"{speed:.1f} KB/s"
                self.root.after(0, self.update_table)
        else:
            self.root.after(0, lambda: self.log_message(f"❌ {proxy['ip']}:{proxy['port']} - Speed test failed"))

    def test_all_speed(self):
        """Test speed of all working proxies"""
        working_proxies = [p for p in self.proxies if p.get('status') == 'Working']
        if not working_proxies:
            messagebox.showwarning("Warning", "No working proxies to test!")
            return
        
        self.log_message("📊 Starting speed test for all working proxies...")
        
        def speed_test_thread():
            for proxy in working_proxies:
                speed = self.speed_test_proxy(proxy)
                proxy['speed'] = f"{speed:.1f} KB/s" if speed > 0 else "Failed"
            
            self.root.after(0, self.update_table)
            self.root.after(0, lambda: self.log_message("✅ Speed testing completed"))
        
        threading.Thread(target=speed_test_thread, daemon=True).start()

    # NEW FEATURE 7: Proxy Chains (Experimental)
    def setup_proxy_chain(self):
        """Setup multiple proxies in chain (experimental)"""
        working_proxies = [p for p in self.proxies if p.get('status') == 'Working']
        if len(working_proxies) < 2:
            messagebox.showwarning("Warning", "Need at least 2 working proxies for chaining!")
            return
        
        self.log_message("🔗 Proxy chaining setup (experimental feature)")
        # This would require more complex implementation for actual chaining

    # NEW FEATURE 8: Bulk Operations
    def bulk_operations_menu(self):
        """Show bulk operations menu"""
        bulk_menu = tk.Menu(self.root, tearoff=0)
        bulk_menu.add_command(label="Enable All Working", command=self.enable_all_working)
        bulk_menu.add_command(label="Disable All", command=self.disable_all_proxies)
        bulk_menu.add_command(label="Test All Speed", command=self.test_all_speed)
        bulk_menu.add_command(label="Export All", command=self.export_all_proxies)
        bulk_menu.post(self.root.winfo_pointerx(), self.root.winfo_pointery())

    def enable_all_working(self):
        """Enable all working proxies in rotation"""
        working_proxies = [p for p in self.proxies if p.get('status') == 'Working']
        self.rotation_proxies = working_proxies.copy()
        self.log_message(f"🔄 Added {len(working_proxies)} working proxies to rotation")

    def disable_all_proxies(self):
        """Disable all proxies"""
        self.stop_auto_rotate()
        self.disable_proxy()
        self.rotation_proxies.clear()
        self.log_message("🛑 All proxies disabled")

    def export_all_proxies(self):
        """Export all proxies (not just working ones)"""
        if not self.proxies:
            messagebox.showwarning("Warning", "No proxies to export!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export all proxies",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                for proxy in self.proxies:
                    if proxy.get('username') and proxy.get('password'):
                        line = f"{proxy['type']}://{proxy['username']}:{proxy['password']}@{proxy['ip']}:{proxy['port']}\n"
                    else:
                        line = f"{proxy['type']}://{proxy['ip']}:{proxy['port']}\n"
                    file.write(line)
            
            self.log_message(f"💾 Exported {len(self.proxies)} proxies")
            messagebox.showinfo("Success", f"Exported {len(self.proxies)} proxies!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export proxies: {str(e)}")

    # NEW FEATURE 9: Backup & Restore Configuration
    def backup_config(self):
        """Backup all configuration and proxies"""
        backup_data = {
            'proxies': self.proxies,
            'current_proxy': self.current_proxy,
            'rotation_proxies': self.rotation_proxies,
            'settings': {
                'auto_rotate': self.auto_rotate_var.get(),
                'rotate_interval': self.rotate_interval_var.get(),
                'system_proxy': self.system_proxy_var.get()
            }
        }
        
        file_path = filedialog.asksaveasfilename(
            title="Backup configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(backup_data, f, indent=2)
                self.log_message("💾 Configuration backup saved")
            except Exception as e:
                messagebox.showerror("Error", f"Backup failed: {str(e)}")

    def restore_config(self):
        """Restore configuration from backup"""
        file_path = filedialog.askopenfilename(
            title="Restore configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    backup_data = json.load(f)
                
                self.proxies = backup_data.get('proxies', [])
                self.current_proxy = backup_data.get('current_proxy')
                self.rotation_proxies = backup_data.get('rotation_proxies', [])
                
                settings = backup_data.get('settings', {})
                self.auto_rotate_var.set(settings.get('auto_rotate', False))
                self.rotate_interval_var.set(settings.get('rotate_interval', '30'))
                self.system_proxy_var.set(settings.get('system_proxy', False))
                
                self.update_table()
                self.update_client_stats()
                self.save_data()
                self.log_message("🔄 Configuration restored from backup")
                
            except Exception as e:
                messagebox.showerror("Error", f"Restore failed: {str(e)}")

    # NEW FEATURE 10: One-click Test and Enable
    def quick_test_and_enable(self):
        """Test selected proxy and enable if working"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a proxy!")
            return
        
        item = selection[0]
        index = self.tree.index(item)
        proxy = self.proxies[index]
        
        def test_and_enable():
            self.log_message(f"🔍 Quick testing {proxy['ip']}:{proxy['port']}...")
            start_time = time.time()
            
            try:
                proxy_url = self.build_proxy_url(proxy)
                proxies = {'http': proxy_url, 'https': proxy_url}
                
                auth = None
                if proxy.get('username') and proxy.get('password'):
                    auth = (proxy['username'], proxy['password'])
                
                response = requests.get('https://api.ipify.org?format=json', 
                                      proxies=proxies, timeout=10, auth=auth)
                
                response_time = round((time.time() - start_time) * 1000, 2)
                
                if response.status_code == 200:
                    self.root.after(0, self.update_proxy_status, index, 'Working', f"{response_time}ms", 'Unknown')
                    self.root.after(0, lambda: self.log_message(f"✅ Proxy working, enabling..."))
                    self.root.after(0, lambda: setattr(self, 'current_proxy', proxy))
                    self.root.after(0, self.enable_proxy)
                else:
                    raise Exception(f"HTTP {response.status_code}")
                    
            except Exception as e:
                response_time = round((time.time() - start_time) * 1000, 2)
                self.root.after(0, self.update_proxy_status, index, 'Failed', f"{response_time}ms", '')
                self.root.after(0, lambda: self.log_message(f"❌ Proxy test failed"))
        
        threading.Thread(target=test_and_enable, daemon=True).start()

    # ALL ORIGINAL METHODS (keeping everything from your original code)
    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
        
    def context_enable_proxy(self):
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            index = self.tree.index(item)
            if 0 <= index < len(self.proxies):
                proxy = self.proxies[index]
                self.current_proxy = proxy
                self.enable_proxy()
        
    def context_test_proxy(self):
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            index = self.tree.index(item)
            if 0 <= index < len(self.proxies):
                proxy = self.proxies[index]
                self.log_message(f"🔍 Testing {proxy['ip']}:{proxy['port']}...")
                self.quick_check_selected()
        
    def context_disable_proxy(self):
        self.disable_proxy()
        
    def context_copy_proxy(self):
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            proxy = self.proxies[self.tree.index(item)]
            if proxy.get('username') and proxy.get('password'):
                proxy_str = f"{proxy['ip']}:{proxy['port']}:{proxy['username']}:{proxy['password']}"
            else:
                proxy_str = f"{proxy['ip']}:{proxy['port']}"
            
            self.root.clipboard_clear()
            self.root.clipboard_append(proxy_str)
            self.log_message(f"📋 Copied proxy: {proxy_str}")
        
    def context_remove_proxy(self):
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            index = self.tree.index(item)
            if 0 <= index < len(self.proxies):
                proxy = self.proxies[index]
                if messagebox.askyesno("Confirm", f"Remove proxy {proxy['ip']}:{proxy['port']}?"):
                    self.proxies.pop(index)
                    self.update_table()
                    self.update_client_stats()
                    self.save_data()
                    self.log_message(f"🗑️ Removed proxy: {proxy['ip']}:{proxy['port']}")
        
    def update_client_button_states(self):
        """Update button states for client tab only"""
        if self.proxy_active:
            self.enable_btn.config(state='disabled')
            self.disable_btn.config(state='normal')
            self.system_proxy_cb.config(state='normal')
        else:
            self.enable_btn.config(state='normal')
            self.disable_btn.config(state='disabled')
            self.system_proxy_cb.config(state='normal')
        
    def update_checker_button_states(self):
        """Update button states for checker tab only"""
        if hasattr(self, 'start_check_btn') and hasattr(self, 'stop_check_btn'):
            if self.checking_active:
                self.start_check_btn.config(state='disabled')
                self.stop_check_btn.config(state='normal')
            else:
                self.start_check_btn.config(state='normal')
                self.stop_check_btn.config(state='disabled')
        
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def checker_log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.checker_log_text.insert(tk.END, log_entry)
        self.checker_log_text.see(tk.END)
        self.root.update_idletasks()
        
    def update_client_stats(self):
        total = len(self.proxies)
        working = len([p for p in self.proxies if p.get('status') == 'Working'])
        failed = len([p for p in self.proxies if p.get('status') == 'Failed'])
        
        self.total_client_label.config(text=f"Total: {total}")
        self.working_client_label.config(text=f"Working: {working}")
        self.failed_client_label.config(text=f"Failed: {failed}")
        
    def check_current_ip(self):
        def check_ip_thread():
            try:
                # Use proxy if active
                proxies = None
                if self.proxy_active and self.current_proxy:
                    proxy_url = self.build_proxy_url(self.current_proxy)
                    proxies = {'http': proxy_url, 'https': proxy_url}
                    
                    # Add authentication if needed
                    auth = None
                    if self.current_proxy.get('username') and self.current_proxy.get('password'):
                        auth = (self.current_proxy['username'], self.current_proxy['password'])
                    
                    response = requests.get('https://api.ipify.org?format=json', 
                                          proxies=proxies, timeout=10, auth=auth)
                else:
                    response = requests.get('https://api.ipify.org?format=json', timeout=10)
                
                if response.status_code == 200:
                    ip = response.json().get('ip', 'Unknown')
                    status_text = f"Your IP: {ip}"
                    if self.proxy_active and self.current_proxy:
                        status_text += f" (via Proxy)"
                    
                    self.root.after(0, lambda: self.current_ip_label.config(text=status_text))
                    self.root.after(0, lambda: self.log_message(f"🌍 Current IP: {ip}"))
                else:
                    raise Exception(f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.root.after(0, lambda: self.current_ip_label.config(text="Your IP: Failed to check"))
                self.root.after(0, lambda: self.log_message(f"❌ Failed to check IP: {str(e)}"))
        
        threading.Thread(target=check_ip_thread, daemon=True).start()
        
    def add_manual_proxy(self):
        def save_proxy():
            proxy_type = type_var.get()
            ip = ip_entry.get().strip()
            port = port_entry.get().strip()
            username = user_entry.get().strip()
            password = pass_entry.get().strip()
            
            if not ip or not port:
                messagebox.showerror("Error", "IP and Port are required!")
                return
                
            # Validate port
            try:
                port_int = int(port)
                if not (1 <= port_int <= 65535):
                    raise ValueError("Port out of range")
            except ValueError:
                messagebox.showerror("Error", "Port must be a number between 1 and 65535!")
                return
                
            proxy_data = {
                'type': proxy_type,
                'ip': ip,
                'port': port,
                'username': username,
                'password': password,
                'status': 'Not Tested',
                'response_time': '',
                'country': '',
                'isp': ''
            }
            
            self.proxies.append(proxy_data)
            self.update_table()
            self.update_client_stats()
            self.save_data()
            self.log_message(f"➕ Added manual proxy: {proxy_type}://{ip}:{port}")
            add_window.destroy()
        
        # Create add proxy window
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Proxy Manually")
        add_window.geometry("400x300")
        add_window.resizable(False, False)
        add_window.transient(self.root)
        add_window.grab_set()
        
        # Center the window
        add_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - add_window.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - add_window.winfo_height()) // 2
        add_window.geometry(f"+{x}+{y}")
        
        form_frame = ttk.Frame(add_window, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(form_frame, text="Proxy Type:*").grid(row=0, column=0, sticky='w', pady=(0, 5))
        type_var = tk.StringVar(value="http")
        type_combo = ttk.Combobox(form_frame, textvariable=type_var, 
                                 values=["http", "https", "socks4", "socks5"], state="readonly")
        type_combo.grid(row=0, column=1, sticky='ew', pady=(0, 5), padx=(10, 0))
        
        ttk.Label(form_frame, text="IP Address:*").grid(row=1, column=0, sticky='w', pady=5)
        ip_entry = ttk.Entry(form_frame, width=30)
        ip_entry.grid(row=1, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        ttk.Label(form_frame, text="Port:*").grid(row=2, column=0, sticky='w', pady=5)
        port_entry = ttk.Entry(form_frame, width=30)
        port_entry.grid(row=2, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        ttk.Label(form_frame, text="Username:").grid(row=3, column=0, sticky='w', pady=5)
        user_entry = ttk.Entry(form_frame, width=30)
        user_entry.grid(row=3, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        ttk.Label(form_frame, text="Password:").grid(row=4, column=0, sticky='w', pady=5)
        pass_entry = ttk.Entry(form_frame, width=30, show="*")
        pass_entry.grid(row=4, column=1, sticky='ew', pady=5, padx=(10, 0))
        
        # Configure grid weights
        form_frame.columnconfigure(1, weight=1)
        
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(20, 0))
        
        ttk.Button(button_frame, text="Add Proxy", command=save_proxy).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Cancel", command=add_window.destroy).pack(side=tk.LEFT)
        
        ip_entry.focus()
        
    def quick_check_selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a proxy to check!")
            return
            
        item = selection[0]
        index = self.tree.index(item)
        proxy = self.proxies[index]
        
        self.log_message(f"🔍 Quick checking {proxy['ip']}:{proxy['port']}...")
        
        def check_single():
            start_time = time.time()
            try:
                proxy_url = self.build_proxy_url(proxy)
                proxies = {'http': proxy_url, 'https': proxy_url}
                
                auth = None
                if proxy.get('username') and proxy.get('password'):
                    auth = (proxy['username'], proxy['password'])
                
                response = requests.get(
                    'https://api.ipify.org?format=json',
                    proxies=proxies,
                    timeout=10,
                    auth=auth
                )
                
                response_time = round((time.time() - start_time) * 1000, 2)
                
                if response.status_code == 200:
                    result_ip = response.json().get('ip', 'Unknown')
                    
                    # Get country info
                    try:
                        country_response = requests.get(f'http://ip-api.com/json/{result_ip}', timeout=5)
                        if country_response.status_code == 200:
                            country_data = country_response.json()
                            country = country_data.get('country', 'Unknown')
                        else:
                            country = 'Unknown'
                    except:
                        country = 'Unknown'
                    
                    self.root.after(0, self.update_proxy_status, index, 'Working', 
                                  f"{response_time}ms", country)
                    self.root.after(0, lambda: self.log_message(f"✅ {proxy['ip']}:{proxy['port']} - Working ({response_time}ms)"))
                else:
                    raise Exception(f"HTTP {response.status_code}")
                    
            except Exception as e:
                response_time = round((time.time() - start_time) * 1000, 2)
                self.root.after(0, self.update_proxy_status, index, 'Failed', 
                              f"{response_time}ms", '')
                self.root.after(0, lambda: self.log_message(f"❌ {proxy['ip']}:{proxy['port']} - Failed"))
        
        threading.Thread(target=check_single, daemon=True).start()
        
    def check_all_proxies(self):
        if not self.proxies:
            messagebox.showwarning("Warning", "No proxies to check!")
            return
            
        self.log_message("🚀 Starting to check all proxies...")
        
        def check_thread():
            total = len(self.proxies)
            for index, proxy in enumerate(self.proxies):
                start_time = time.time()
                try:
                    proxy_url = self.build_proxy_url(proxy)
                    proxies = {'http': proxy_url, 'https': proxy_url}
                    
                    auth = None
                    if proxy.get('username') and proxy.get('password'):
                        auth = (proxy['username'], proxy['password'])
                    
                    response = requests.get(
                        'https://api.ipify.org?format=json',
                        proxies=proxies,
                        timeout=8,
                        auth=auth
                    )
                    
                    response_time = round((time.time() - start_time) * 1000, 2)
                    
                    if response.status_code == 200:
                        result_ip = response.json().get('ip', 'Unknown')
                        
                        # Get country info
                        try:
                            country_response = requests.get(f'http://ip-api.com/json/{result_ip}', timeout=5)
                            if country_response.status_code == 200:
                                country_data = country_response.json()
                                country = country_data.get('country', 'Unknown')
                            else:
                                country = 'Unknown'
                        except:
                            country = 'Unknown'
                            
                        self.root.after(0, self.update_proxy_status, index, 'Working', 
                                      f"{response_time}ms", country)
                    else:
                        raise Exception(f"HTTP {response.status_code}")
                        
                except Exception as e:
                    response_time = round((time.time() - start_time) * 1000, 2)
                    self.root.after(0, self.update_proxy_status, index, 'Failed', 
                                  f"{response_time}ms", '')
                
                # Update progress
                progress = ((index + 1) / total) * 100
                self.root.after(0, lambda: self.client_progress_var.set(progress))
                self.root.after(0, lambda: self.client_progress_label.config(text=f"{index + 1}/{total}"))
                
            self.root.after(0, lambda: self.log_message("✅ All proxies checked!"))
            self.root.after(0, lambda: self.client_progress_var.set(0))
            self.root.after(0, lambda: self.client_progress_label.config(text="Ready"))
        
        threading.Thread(target=check_thread, daemon=True).start()
        
    def update_proxy_status(self, index, status, response_time, country):
        if 0 <= index < len(self.proxies):
            self.proxies[index].update({
                'status': status,
                'response_time': response_time,
                'country': country
            })
            self.update_table()
            self.update_client_stats()
            self.save_data()
            
    def load_proxies(self):
        file_path = filedialog.askopenfilename(
            title="Select proxies file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        self._load_proxies_from_file(file_path, self.proxies, self.update_table, self.log_message)
        self.update_client_stats()
        self.save_data()
        
    def load_proxies_checker(self):
        file_path = filedialog.askopenfilename(
            title="Select proxies file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        self._load_proxies_from_file(file_path, self.checker_proxies, self.update_checker_table, self.checker_log_message)
        
    def _load_proxies_from_file(self, file_path, proxy_list, update_callback, log_callback):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = file.readlines()
                
            new_proxies = []
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue
                    
                proxy_data = self.parse_proxy_line(line)
                if proxy_data:
                    # Ensure all required fields
                    proxy_data.setdefault('type', 'http')
                    proxy_data.setdefault('username', '')
                    proxy_data.setdefault('password', '')
                    proxy_data.update({
                        'status': 'Not Tested',
                        'response_time': '',
                        'country': '',
                        'isp': ''
                    })
                    new_proxies.append(proxy_data)
                else:
                    log_callback(f"⚠️ Invalid proxy format on line {line_num}: {line}")
            
            proxy_list.extend(new_proxies)
            update_callback()
            log_callback(f"✅ Loaded {len(new_proxies)} proxies from file")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load proxies: {str(e)}")
            log_callback(f"❌ Error loading proxies: {str(e)}")
            
    def update_table(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Add proxies to table
        for idx, proxy in enumerate(self.proxies, 1):
            # Ensure proxy has all required fields
            proxy.setdefault('type', 'http')
            proxy.setdefault('username', '')
            proxy.setdefault('password', '')
            proxy.setdefault('status', 'Not Tested')
            proxy.setdefault('response_time', '')
            proxy.setdefault('country', '')
            
            status = proxy.get('status', 'Not Tested')
            status_display = '✅ Working' if status == 'Working' else '❌ Failed' if status == 'Failed' else '⏳ Not Tested'
            
            # Add speed information if available
            response_display = proxy.get('response_time', '')
            if proxy.get('speed'):
                response_display += f" ({proxy['speed']})"
            
            values = (
                idx,
                proxy.get('type', 'http').upper(),
                proxy['ip'],
                proxy['port'],
                proxy['username'] or '-',
                proxy['password'] or '-',
                status_display,
                response_display,
                proxy.get('country', '')
            )
            item = self.tree.insert('', tk.END, values=values)
            
    def update_checker_table(self):
        # Clear existing items
        for item in self.checker_tree.get_children():
            self.checker_tree.delete(item)
            
        # Add proxies to checker table
        for idx, proxy in enumerate(self.checker_proxies, 1):
            # Ensure proxy has all required fields
            proxy.setdefault('type', 'http')
            proxy.setdefault('username', '')
            proxy.setdefault('password', '')
            proxy.setdefault('status', 'Not Tested')
            proxy.setdefault('response_time', '')
            proxy.setdefault('country', '')
            proxy.setdefault('isp', '')
            
            status = proxy.get('status', 'Not Tested')
            status_display = '✅ Working' if status == 'Working' else '❌ Failed' if status == 'Failed' else '⏳ Not Tested'
            
            values = (
                idx,
                proxy.get('type', 'http').upper(),
                proxy['ip'],
                proxy['port'],
                proxy['username'] or '-',
                proxy['password'] or '-',
                status_display,
                proxy.get('response_time', ''),
                proxy.get('country', ''),
                proxy.get('isp', '')
            )
            item = self.checker_tree.insert('', tk.END, values=values)
            
        self.update_checker_stats()
        
    def update_checker_stats(self):
        total = len(self.checker_proxies)
        working = len([p for p in self.checker_proxies if p.get('status') == 'Working'])
        failed = len([p for p in self.checker_proxies if p.get('status') == 'Failed'])
        
        self.total_checker_label.config(text=f"Total: {total}")
        self.working_checker_label.config(text=f"Working: {working}")
        self.failed_checker_label.config(text=f"Failed: {failed}")
        
    def on_double_click(self, event):
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            index = self.tree.index(item)
            if 0 <= index < len(self.proxies):
                proxy = self.proxies[index]
                self.current_proxy = proxy
                self.enable_proxy()
                
    def enable_proxy(self):
        if not self.current_proxy:
            messagebox.showwarning("Warning", "Please select a proxy first! Right-click on a proxy and choose 'Enable Proxy'")
            return
            
        def enable_thread():
            try:
                self.root.after(0, lambda: self.log_message(f"🔄 Enabling proxy {self.current_proxy['ip']}:{self.current_proxy['port']}..."))
                
                # Test the proxy first
                proxy_url = self.build_proxy_url(self.current_proxy)
                proxies = {'http': proxy_url, 'https': proxy_url}
                
                auth = None
                if self.current_proxy.get('username') and self.current_proxy.get('password'):
                    auth = (self.current_proxy['username'], self.current_proxy['password'])
                
                # Test the proxy connection
                response = requests.get(
                    'https://api.ipify.org?format=json',
                    proxies=proxies,
                    timeout=10,
                    auth=auth
                )
                
                if response.status_code == 200:
                    proxy_ip = response.json().get('ip', 'Unknown')
                    
                    # Set proxy as active
                    self.proxy_active = True
                    
                    self.root.after(0, lambda: self.status_label.config(
                        text=f"✅ Proxy Enabled - {self.current_proxy['ip']}:{self.current_proxy['port']}", 
                        foreground='green'
                    ))
                    self.root.after(0, lambda: self.proxy_ip_label.config(
                        text=f"Proxy IP: {proxy_ip}"
                    ))
                    self.root.after(0, lambda: self.log_message(
                        f"🚀 Proxy enabled! Your IP should now be {proxy_ip}"
                    ))
                    
                    # Set system proxy if enabled
                    if self.system_proxy_var.get():
                        self.set_system_proxy(self.current_proxy['ip'], self.current_proxy['port'], 
                                            self.current_proxy.get('username'), self.current_proxy.get('password'))
                    
                    # Update button states
                    self.root.after(0, self.update_client_button_states)
                    
                    # Force check IP to verify
                    self.root.after(2000, self.check_current_ip)
                    self.root.after(2000, self.refresh_ip_info)
                        
                else:
                    raise Exception(f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.root.after(0, lambda: self.log_message(f"❌ Failed to enable proxy: {str(e)}"))
                messagebox.showerror("Error", f"Failed to enable proxy: {str(e)}")
        
        threading.Thread(target=enable_thread, daemon=True).start()

    def build_proxy_url(self, proxy):
        proxy_type = proxy.get('type', 'http')
        if proxy.get('username') and proxy.get('password'):
            if proxy_type.startswith('socks'):
                return f"{proxy_type}://{proxy['username']}:{proxy['password']}@{proxy['ip']}:{proxy['port']}"
            else:
                return f"http://{proxy['username']}:{proxy['password']}@{proxy['ip']}:{proxy['port']}"
        else:
            if proxy_type.startswith('socks'):
                return f"{proxy_type}://{proxy['ip']}:{proxy['port']}"
            else:
                return f"http://{proxy['ip']}:{proxy['port']}"

    def disable_proxy(self):
        self.proxy_active = False
        self.current_proxy = None
        self.status_label.config(text="❌ Proxy Disabled", foreground='red')
        self.proxy_ip_label.config(text="Proxy IP: None")
        
        # Disable system proxy
        if self.system_proxy_enabled:
            self.disable_system_proxy()
            
        # Update button states
        self.update_client_button_states()
            
        self.log_message("🛑 Proxy disabled - Traffic back to normal")
        self.check_current_ip()
        self.refresh_ip_info()

    def set_system_proxy(self, ip, port, username=None, password=None):
        """Set system-wide proxy that affects ALL applications including browsers"""
        try:
            self.log_message(f"🔄 Setting system proxy to {ip}:{port}...")
            
            # Method 1: Windows Registry (for most applications including browsers)
            try:
                # Open Internet Settings registry key
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 
                                   0, winreg.KEY_SET_VALUE)
                
                # Enable proxy
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
                
                # Set proxy server
                proxy_server = f"{ip}:{port}"
                winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, proxy_server)
                
                # Set proxy override for local addresses (important!)
                winreg.SetValueEx(key, "ProxyOverride", 0, winreg.REG_SZ, 
                                "<local>;localhost;127.*;10.*;172.16.*;172.17.*;172.18.*;172.19.*;172.20.*;172.21.*;172.22.*;172.23.*;172.24.*;172.25.*;172.26.*;172.27.*;172.28.*;172.29.*;172.30.*;172.31.*;192.168.*")
                
                winreg.CloseKey(key)
                self.log_message("✅ Windows Registry proxy settings updated")
                
            except Exception as reg_error:
                self.log_message(f"⚠️ Registry method failed: {str(reg_error)}")
            
            # Method 2: WinHTTP proxy (for system services and command line)
            try:
                # Set WinHTTP proxy
                result = subprocess.run([
                    'netsh', 'winhttp', 'set', 'proxy', 
                    f'{ip}:{port}', 'bypass-list="localhost;127.0.0.1;10.*;172.16.*;172.17.*;172.18.*;172.19.*;172.20.*;172.21.*;172.22.*;172.23.*;172.24.*;172.25.*;172.26.*;172.27.*;172.28.*;172.29.*;172.30.*;172.31.*;192.168.*"'
                ], capture_output=True, text=True, shell=True, timeout=10)
                
                if result.returncode == 0:
                    self.log_message("✅ WinHTTP proxy set successfully")
                else:
                    self.log_message(f"⚠️ WinHTTP proxy failed: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                self.log_message("⚠️ WinHTTP command timed out")
            except Exception as netsh_error:
                self.log_message(f"⚠️ WinHTTP method failed: {str(netsh_error)}")
            
            # Method 3: Refresh system settings to apply immediately
            try:
                # Refresh Internet Settings using Windows API
                refresh_script = """
                Add-Type -TypeDefinition @"
                using System.Runtime.InteropServices;
                public class WinInet {
                    [DllImport("wininet.dll")]
                    public static extern bool InternetSetOption(int hInternet, int dwOption, int lpBuffer, int dwBufferLength);
                }
                "@
                [WinInet]::InternetSetOption(0, 39, 0, 0)  # INTERNET_OPTION_SETTINGS_CHANGED
                [WinInet]::InternetSetOption(0, 37, 0, 0)  # INTERNET_OPTION_REFRESH
                """
                
                result = subprocess.run(['powershell', '-Command', refresh_script], 
                                      capture_output=True, text=True, shell=True, timeout=10)
                self.log_message("✅ System proxy settings refreshed")
                
            except Exception as refresh_error:
                self.log_message(f"⚠️ Could not refresh system settings: {str(refresh_error)}")
            
            # Method 4: Set environment variables (for some applications)
            try:
                proxy_url = f"http://{ip}:{port}"
                os.environ['HTTP_PROXY'] = proxy_url
                os.environ['HTTPS_PROXY'] = proxy_url
                os.environ['http_proxy'] = proxy_url
                os.environ['https_proxy'] = proxy_url
                self.log_message("✅ Environment variables set")
            except Exception as env_error:
                self.log_message(f"⚠️ Environment variables failed: {str(env_error)}")
            
            # Method 5: For authenticated proxies, provide instructions
            if username and password:
                self.log_message("🔐 Authenticated proxy detected")
                self.log_message("💡 For authenticated proxies, browsers will prompt for credentials")
                self.log_message(f"   Username: {username}")
                self.log_message(f"   Password: {password}")
                
                # Try to set credentials in credential manager
                self._cache_proxy_credentials(ip, port, username, password)
            
            self.system_proxy_enabled = True
            
            # Show success message with instructions
            messagebox.showinfo("System Proxy Enabled", 
                              f"✅ System-wide proxy has been set to:\n"
                              f"IP: {ip}\n"
                              f"Port: {port}\n\n"
                              f"🌐 This should affect:\n"
                              f"• Google Chrome\n"
                              f"• Microsoft Edge\n"
                              f"• Mozilla Firefox\n"
                              f"• Command Line (curl, etc.)\n"
                              f"• Most other applications\n\n"
                              f"🔧 If browsers still show real IP:\n"
                              f"1. Completely close and restart browsers\n"
                              f"2. Check browser proxy settings\n"
                              f"3. Some apps may need manual configuration\n\n"
                              f"🔄 Use 'Check My IP' to verify your IP has changed")
            
            self.log_message(f"🌐 System proxy enabled successfully! All traffic should now go through {ip}:{port}")
            
        except Exception as e:
            error_msg = f"❌ Failed to set system proxy: {str(e)}"
            self.log_message(error_msg)
            messagebox.showerror("System Proxy Error", 
                               f"Could not set system proxy automatically.\n\n"
                               f"Manual setup required:\n"
                               f"1. Press Win+R, type 'inetcpl.cpl'\n"
                               f"2. Go to Connections > LAN settings\n"
                               f"3. Check 'Use a proxy server'\n"
                               f"4. Set Address: {ip}, Port: {port}\n"
                               f"5. Check 'Bypass proxy for local addresses'\n\n"
                               f"Error: {str(e)}")

    def disable_system_proxy(self):
        """Disable system-wide proxy completely"""
        try:
            self.log_message("🔄 Disabling system proxy...")
            
            # Method 1: Windows Registry
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", 
                                   0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
                winreg.CloseKey(key)
                self.log_message("✅ Windows Registry proxy disabled")
            except Exception as reg_error:
                self.log_message(f"⚠️ Registry disable failed: {str(reg_error)}")
            
            # Method 2: WinHTTP proxy
            try:
                result = subprocess.run(['netsh', 'winhttp', 'reset', 'proxy'], 
                                      capture_output=True, text=True, shell=True, timeout=10)
                if result.returncode == 0:
                    self.log_message("✅ WinHTTP proxy reset")
                else:
                    self.log_message(f"⚠️ WinHTTP reset failed: {result.stderr}")
            except Exception as netsh_error:
                self.log_message(f"⚠️ WinHTTP reset failed: {str(netsh_error)}")
            
            # Method 3: Refresh system settings
            try:
                refresh_script = """
                Add-Type -TypeDefinition @"
                using System.Runtime.InteropServices;
                public class WinInet {
                    [DllImport("wininet.dll")]
                    public static extern bool InternetSetOption(int hInternet, int dwOption, int lpBuffer, int dwBufferLength);
                }
                "@
                [WinInet]::InternetSetOption(0, 39, 0, 0)
                [WinInet]::InternetSetOption(0, 37, 0, 0)
                """
                subprocess.run(['powershell', '-Command', refresh_script], 
                             capture_output=True, shell=True, timeout=10)
                self.log_message("✅ System settings refreshed")
            except Exception as refresh_error:
                self.log_message(f"⚠️ Could not refresh system: {str(refresh_error)}")
            
            # Method 4: Clear environment variables
            try:
                for var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
                    if var in os.environ:
                        del os.environ[var]
                self.log_message("✅ Environment variables cleared")
            except Exception as env_error:
                self.log_message(f"⚠️ Environment clear failed: {str(env_error)}")
            
            self.system_proxy_enabled = False
            self.log_message("🌐 System-wide proxy disabled - All applications back to normal")
            
        except Exception as e:
            self.log_message(f"❌ Failed to disable system proxy: {str(e)}")

    def _cache_proxy_credentials(self, ip, port, username, password):
        """Attempt to cache proxy credentials in Windows credential manager"""
        try:
            # Method 1: Using cmdkey
            target_name = f"proxy_{ip}_{port}"
            cmdkey_cmd = f'cmdkey /generic:{target_name} /user:{username} /pass:{password}'
            
            result = subprocess.run(cmdkey_cmd, capture_output=True, text=True, shell=True, timeout=10)
            if result.returncode == 0:
                self.log_message("✅ Proxy credentials cached via cmdkey")
                return True
                
        except Exception as e:
            self.log_message(f"⚠️ Credential caching failed: {str(e)}")
        
        return False

    def toggle_system_proxy(self):
        if self.system_proxy_var.get():
            if self.current_proxy and self.proxy_active:
                self.set_system_proxy(self.current_proxy['ip'], self.current_proxy['port'], 
                                    self.current_proxy.get('username'), self.current_proxy.get('password'))
            else:
                self.log_message("ℹ️ Please enable a proxy first to set system proxy")
                self.system_proxy_var.set(False)
        else:
            self.disable_system_proxy()
            
    def add_proxy_checker(self):
        # Same as add_manual_proxy but for checker tab
        self.add_manual_proxy()
        
    def start_checking(self):
        if not self.checker_proxies:
            messagebox.showwarning("Warning", "No proxies to check!")
            return
            
        if self.checking_active:
            messagebox.showwarning("Warning", "Checking already in progress!")
            return
            
        self.checking_active = True
        self.stop_checking_flag = False
        self.update_checker_button_states()
        self.checker_log_message("🚀 Starting proxy checking...")
        
        thread = threading.Thread(target=self.check_proxies_thread, daemon=True)
        thread.start()
        
    def stop_checking(self):
        self.stop_checking_flag = True
        self.checker_log_message("🛑 Stopping proxy check...")
        
    def check_proxies_thread(self):
        try:
            total_proxies = len(self.checker_proxies)
            checked_count = 0
            
            with ThreadPoolExecutor(max_workers=20) as executor:
                futures = {
                    executor.submit(self.check_single_proxy, proxy, index): (proxy, index)
                    for index, proxy in enumerate(self.checker_proxies)
                }
                
                for future in as_completed(futures):
                    if self.stop_checking_flag:
                        break
                        
                    proxy, index = futures[future]
                    try:
                        future.result()
                        checked_count += 1
                        
                        progress = (checked_count / total_proxies) * 100
                        self.root.after(0, lambda: self.checker_progress_var.set(progress))
                        self.root.after(0, lambda: self.checker_progress_label.config(text=f"{checked_count}/{total_proxies}"))
                        
                    except Exception as e:
                        self.checker_log_message(f"❌ Error checking proxy: {str(e)}")
            
            if self.stop_checking_flag:
                self.checker_log_message("✅ Checking stopped by user")
            else:
                self.checker_log_message("✅ Checking completed!")
            
        except Exception as e:
            self.checker_log_message(f"❌ Checking error: {str(e)}")
        finally:
            self.checking_active = False
            self.stop_checking_flag = False
            self.root.after(0, self.update_checker_button_states)
            self.root.after(0, lambda: self.checker_progress_var.set(0))
            self.root.after(0, lambda: self.checker_progress_label.config(text="Ready"))
            
    def check_single_proxy(self, proxy, index):
        if self.stop_checking_flag:
            return
            
        start_time = time.time()
        
        try:
            proxy_url = self.build_proxy_url(proxy)
            proxies = {'http': proxy_url, 'https': proxy_url}
            
            auth = None
            if proxy.get('username') and proxy.get('password'):
                auth = (proxy['username'], proxy['password'])
            
            response = requests.get(
                'https://api.ipify.org?format=json',
                proxies=proxies,
                timeout=10,
                auth=auth
            )
            
            response_time = round((time.time() - start_time) * 1000, 2)
            
            if response.status_code == 200:
                result_ip = response.json().get('ip', 'Unknown')
                
                # Get more info about the IP
                try:
                    ip_info = requests.get(f'http://ip-api.com/json/{result_ip}', timeout=5).json()
                    country = ip_info.get('country', 'Unknown')
                    isp = ip_info.get('isp', 'Unknown')
                except:
                    country = 'Unknown'
                    isp = 'Unknown'
                
                self.root.after(0, self.update_checker_proxy_status, index, 'Working', 
                              f"{response_time}ms", country, isp)
                
                self.root.after(0, lambda: self.checker_log_message(
                    f"✅ {proxy['ip']}:{proxy['port']} - Working ({response_time}ms) - {country}"
                ))
                
            else:
                raise Exception(f"HTTP {response.status_code}")
                
        except Exception as e:
            response_time = round((time.time() - start_time) * 1000, 2)
            self.root.after(0, self.update_checker_proxy_status, index, 'Failed', 
                          f"{response_time}ms", '', '')
            
            self.root.after(0, lambda: self.checker_log_message(
                f"❌ {proxy['ip']}:{proxy['port']} - Failed ({response_time}ms): {str(e)}"
            ))
            
    def update_checker_proxy_status(self, index, status, response_time, country, isp):
        if 0 <= index < len(self.checker_proxies):
            self.checker_proxies[index].update({
                'status': status,
                'response_time': response_time,
                'country': country,
                'isp': isp
            })
            self.update_checker_table()
            
    def export_working(self):
        working_proxies = [p for p in self.proxies if p.get('status') == 'Working']
        self._export_proxies(working_proxies, "client")
        
    def export_working_checker(self):
        working_proxies = [p for p in self.checker_proxies if p.get('status') == 'Working']
        self._export_proxies(working_proxies, "checker")
        
    def _export_proxies(self, proxies, source):
        if not proxies:
            messagebox.showwarning("Warning", "No working proxies to export!")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Export working proxies",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                for proxy in proxies:
                    if proxy.get('username') and proxy.get('password'):
                        line = f"{proxy['ip']}:{proxy['port']}:{proxy['username']}:{proxy['password']}\n"
                    else:
                        line = f"{proxy['ip']}:{proxy['port']}\n"
                    file.write(line)
                    
            if source == "client":
                self.log_message(f"💾 Exported {len(proxies)} working proxies")
            else:
                self.checker_log_message(f"💾 Exported {len(proxies)} working proxies")
                
            messagebox.showinfo("Success", f"Exported {len(proxies)} working proxies!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export proxies: {str(e)}")
            
    def clear_list(self):
        if self.proxies and not messagebox.askyesno("Confirm", "Clear all proxies from client tab?"):
            return
            
        self.proxies.clear()
        self.update_table()
        self.update_client_stats()
        self.save_data()
        self.log_message("🗑️ Cleared all proxies from client tab")
        
    def clear_checker(self):
        if self.checker_proxies and not messagebox.askyesno("Confirm", "Clear all proxies from checker tab?"):
            return
            
        self.checker_proxies.clear()
        self.update_checker_table()
        self.checker_log_message("🗑️ Cleared all proxies from checker tab")

    # Import/Export methods
    def import_to_client(self):
        """Import proxies from text area to client tab"""
        text = self.import_text.get('1.0', tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "No text to import!")
            return
        
        self._import_from_text(text, self.proxies, self.update_table, self.log_message)
        self.update_client_stats()
        self.save_data()

    def import_to_checker(self):
        """Import proxies from text area to checker tab"""
        text = self.import_text.get('1.0', tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "No text to import!")
            return
        
        self._import_from_text(text, self.checker_proxies, self.update_checker_table, self.checker_log_message)

    def import_from_file(self):
        """Import proxies from file to text area"""
        file_path = filedialog.askopenfilename(
            title="Select proxies file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            self.import_text.delete('1.0', tk.END)
            self.import_text.insert('1.0', content)
            self.log_message(f"📁 Loaded file: {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")

    def clear_import_text(self):
        """Clear the import text area"""
        self.import_text.delete('1.0', tk.END)

    def _import_from_text(self, text, proxy_list, update_callback, log_callback):
        """Import proxies from text to specified list"""
        lines = text.split('\n')
        imported_count = 0
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
                
            proxy_data = self.parse_proxy_line(line)
            if proxy_data:
                # Ensure all required fields are present
                proxy_data.setdefault('type', 'http')
                proxy_data.setdefault('username', '')
                proxy_data.setdefault('password', '')
                proxy_data.update({
                    'status': 'Not Tested',
                    'response_time': '',
                    'country': '',
                    'isp': ''
                })
                proxy_list.append(proxy_data)
                imported_count += 1
            else:
                log_callback(f"⚠️ Invalid proxy format on line {line_num}: {line}")
        
        update_callback()
        log_callback(f"✅ Imported {imported_count} proxies")
        messagebox.showinfo("Success", f"Imported {imported_count} proxies!")

    def parse_proxy_line(self, line):
        """Parse proxy line in various formats"""
        line = line.strip()
        
        # Try different formats
        if line.startswith(('socks4://', 'socks5://', 'http://', 'https://')):
            return self._parse_url_format(line)
        else:
            return self._parse_simple_format(line)

    def _parse_url_format(self, proxy_url):
        """Parse URL format: type://user:pass@host:port"""
        try:
            # Extract type
            if proxy_url.startswith('socks4://'):
                proxy_type = 'socks4'
                proxy_url = proxy_url[9:]
            elif proxy_url.startswith('socks5://'):
                proxy_type = 'socks5'
                proxy_url = proxy_url[9:]
            elif proxy_url.startswith('https://'):
                proxy_type = 'https'
                proxy_url = proxy_url[8:]
            else:  # http://
                proxy_type = 'http'
                proxy_url = proxy_url[7:]
            
            # Check for authentication
            if '@' in proxy_url:
                auth_part, server_part = proxy_url.split('@', 1)
                if ':' in auth_part:
                    username, password = auth_part.split(':', 1)
                else:
                    username, password = auth_part, ''
                
                if ':' in server_part:
                    ip, port = server_part.split(':', 1)
                else:
                    ip, port = server_part, '8080'
            else:
                username, password = '', ''
                if ':' in proxy_url:
                    ip, port = proxy_url.split(':', 1)
                else:
                    ip, port = proxy_url, '8080'
            
            return {
                'type': proxy_type,
                'ip': ip,
                'port': port,
                'username': username,
                'password': password
            }
            
        except Exception:
            return None

    def _parse_simple_format(self, line):
        """Parse simple format: ip:port or ip:port:user:pass"""
        try:
            parts = line.split(':')
            
            if len(parts) == 2:
                # IP:PORT format
                ip, port = parts
                return {
                    'type': 'http',
                    'ip': ip.strip(),
                    'port': port.strip(),
                    'username': '',
                    'password': ''
                }
            elif len(parts) == 4:
                # IP:PORT:USERNAME:PASSWORD format
                ip, port, username, password = parts
                return {
                    'type': 'http',
                    'ip': ip.strip(),
                    'port': port.strip(),
                    'username': username.strip(),
                    'password': password.strip()
                }
            else:
                return None
        except:
            return None

    # IP Information methods
    def refresh_ip_info(self):
        """Refresh IP information display"""
        def refresh_thread():
            try:
                # Update status to show we're checking
                self.root.after(0, lambda: self.info_labels['status'].config(text="Checking..."))
                
                # Get current IP information - try multiple services
                ip_services = [
                    'https://api.ipify.org?format=json',
                    'https://api64.ipify.org?format=json',
                    'https://ipinfo.io/json',
                    'https://ipapi.co/json/'
                ]
                
                response = None
                ip_data = {}
                
                # Try with proxy if active
                if self.proxy_active and self.current_proxy:
                    proxy_url = self.build_proxy_url(self.current_proxy)
                    proxies = {'http': proxy_url, 'https': proxy_url}
                    auth = None
                    if self.current_proxy.get('username') and self.current_proxy.get('password'):
                        auth = (self.current_proxy['username'], self.current_proxy['password'])
                    
                    # Try each service with proxy
                    for service in ip_services:
                        try:
                            response = requests.get(service, proxies=proxies, timeout=10, auth=auth)
                            if response.status_code == 200:
                                ip_data = response.json()
                                break
                        except:
                            continue
                else:
                    # Try each service without proxy
                    for service in ip_services:
                        try:
                            response = requests.get(service, timeout=10)
                            if response.status_code == 200:
                                ip_data = response.json()
                                break
                        except:
                            continue
                
                # If we got data, process it
                if ip_data:
                    # Extract IP from different response formats
                    ip_address = ip_data.get('ip') or ip_data.get('ip_addr') or 'Unknown'
                    
                    # Get detailed information using a different service
                    try:
                        if ip_address != 'Unknown':
                            # Use ip-api.com for detailed info (free service)
                            detail_response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=5)
                            if detail_response.status_code == 200:
                                detail_data = detail_response.json()
                                if detail_data.get('status') == 'success':
                                    ip_data['country'] = detail_data.get('country', 'Unknown')
                                    ip_data['region'] = detail_data.get('regionName', 'Unknown')
                                    ip_data['city'] = detail_data.get('city', 'Unknown')
                                    ip_data['isp'] = detail_data.get('isp', 'Unknown')
                    except:
                        pass  # Use whatever data we have
                    
                    # Fallback to ipapi.co format if needed
                    if 'country' not in ip_data:
                        ip_data['country'] = ip_data.get('country_name', 'Unknown')
                    if 'region' not in ip_data:
                        ip_data['region'] = ip_data.get('region', ip_data.get('state', 'Unknown'))
                    if 'city' not in ip_data:
                        ip_data['city'] = ip_data.get('city', 'Unknown')
                    if 'isp' not in ip_data:
                        ip_data['isp'] = ip_data.get('org', ip_data.get('asn', {}).get('org', 'Unknown'))
                    
                    # Update UI in main thread
                    self.root.after(0, lambda: self.update_ip_info_display(ip_data, True))
                    
                else:
                    raise Exception("Could not fetch IP information from any service")
                    
            except Exception as e:
                error_msg = f"Failed: {str(e)}"
                self.root.after(0, lambda: self.update_ip_info_display({}, False, error_msg))
        
        threading.Thread(target=refresh_thread, daemon=True).start()

    def update_ip_info_display(self, data, success=True, error_msg=""):
        """Update IP information labels with data"""
        if success:
            # Extract values with fallbacks
            ip_address = data.get('ip') or data.get('ip_addr') or 'Unknown'
            country = data.get('country', data.get('country_name', 'Unknown'))
            region = data.get('region', data.get('regionName', data.get('state', 'Unknown')))
            city = data.get('city', 'Unknown')
            isp = data.get('isp', data.get('org', data.get('asn', {}).get('org', 'Unknown')))
            
            # Update labels
            self.info_labels['ip'].config(text=ip_address)
            self.info_labels['country'].config(text=country)
            self.info_labels['region'].config(text=region)
            self.info_labels['city'].config(text=city)
            self.info_labels['isp'].config(text=isp)
            
            if self.proxy_active and self.current_proxy:
                self.info_labels['proxy_type'].config(text=self.current_proxy.get('type', 'http').upper())
                self.info_labels['status'].config(text="✅ Proxy Active", foreground='green')
            else:
                self.info_labels['proxy_type'].config(text="Direct")
                self.info_labels['status'].config(text="✅ Direct Connection", foreground='green')
        else:
            # Show error state
            self.info_labels['ip'].config(text="Error")
            self.info_labels['country'].config(text="Error")
            self.info_labels['region'].config(text="Error")
            self.info_labels['city'].config(text="Error")
            self.info_labels['isp'].config(text="Error")
            self.info_labels['proxy_type'].config(text="Error")
            self.info_labels['status'].config(text=f"❌ {error_msg}", foreground='red')

def main():
    # Check if running on Windows
    if platform.system() != 'Windows':
        messagebox.showerror("Error", "This application is designed for Windows only!")
        return
        
    # Check if running as administrator
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            messagebox.showwarning("Administrator Rights", 
                                 "For full system proxy functionality, it's recommended to run this application as Administrator.\n\n"
                                 "Right-click on the application and select 'Run as administrator'.")
    except:
        pass
        
    root = tk.Tk()
    app = ProxyClient(root)
    root.mainloop()

if __name__ == "__main__":
    main()