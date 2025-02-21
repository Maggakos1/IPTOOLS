import tkinter as tk #line:1
from tkinter import ttk ,messagebox ,scrolledtext #line:2
import socket #line:3
import threading #line:4
import requests #line:5
scanning =False #line:8
open_ports =[]#line:9
def public_port_scan (O0O000O0OO00000OO ,OOO0O0OO00000O0OO ):#line:12
    if stop_event .is_set ():#line:13
        return #line:14
    try :#line:15
        with socket .socket (socket .AF_INET ,socket .SOCK_STREAM )as OOOOOO00OO0O0OO00 :#line:16
            OOOOOO00OO0O0OO00 .settimeout (0.5 )#line:17
            OO0000OO000OO000O =OOOOOO00OO0O0OO00 .connect_ex ((O0O000O0OO00000OO ,OOO0O0OO00000O0OO ))#line:18
            if OO0000OO000OO000O ==0 :#line:19
                open_ports .append (OOO0O0OO00000O0OO )#line:20
    except :#line:21
        pass #line:22
def start_public_scan ():#line:25
    global scanning ,stop_event #line:26
    O0OO0O0O00O0OOO0O =public_ip_entry .get ()#line:27
    if not O0OO0O0O00O0OOO0O :#line:28
        messagebox .showerror ("Error","Please enter a valid IP address")#line:29
        return #line:30
    scanning =True #line:32
    stop_event =threading .Event ()#line:33
    open_ports .clear ()#line:34
    O00OO00O0OOOOO0OO =65535 #line:35
    public_progress ["maximum"]=O00OO00O0OOOOO0OO #line:36
    def OOO000O0000O0OO0O ():#line:38
        for OO000OO0OOOO0OO00 in range (0 ,O00OO00O0OOOOO0OO +1 ):#line:39
            if stop_event .is_set ():#line:40
                break #line:41
            public_progress ["value"]=OO000OO0OOOO0OO00 #line:42
            public_result_text .insert (tk .END ,f"Scanning port {OO000OO0OOOO0OO00}\n")#line:43
            public_result_text .see (tk .END )#line:44
            O0O0OOO0000OO000O =threading .Thread (target =public_port_scan ,args =(O0OO0O0O00O0OOO0O ,OO000OO0OOOO0OO00 ))#line:45
            O0O0OOO0000OO000O .start ()#line:46
        stop_public_scan ()#line:47
        messagebox .showinfo ("Scan Complete",f"Found {len(open_ports)} open ports")#line:48
    public_scan_button .config (state =tk .DISABLED )#line:50
    public_terminate_button .config (state =tk .NORMAL )#line:51
    threading .Thread (target =OOO000O0000O0OO0O ).start ()#line:52
def stop_public_scan ():#line:55
    global scanning #line:56
    stop_event .set ()#line:57
    scanning =False #line:58
    public_scan_button .config (state =tk .NORMAL )#line:59
    public_terminate_button .config (state =tk .DISABLED )#line:60
def show_public_open_ports ():#line:63
    if not open_ports :#line:64
        messagebox .showinfo ("Open Ports","No open ports found.")#line:65
        return #line:66
    O0O0O0000000OO0OO =tk .Toplevel (root )#line:67
    O0O0O0000000OO0OO .title ("Open Ports")#line:68
    O0OO000O00O000O00 =tk .Listbox (O0O0O0000000OO0OO ,width =50 ,height =20 )#line:69
    O0OO000O00O000O00 .pack (padx =10 ,pady =10 )#line:70
    for O0O0OOO0O0O00OO00 in open_ports :#line:71
        O0OO000O00O000O00 .insert (tk .END ,f"Port {O0O0OOO0O0O00OO00} - OPEN")#line:72
def scan_ports (O0OOOOOOOO0OO0000 ,O0OOO0O0OOOOO0O00 ,O0OO000OO0O0O00OO ,OO0OOOOOO0OOO000O ,O000OO00O00OO00OO ):#line:75
    global scanning ,open_ports #line:76
    open_ports =[]#line:77
    for OOOO000O0O0OOO00O in range (O0OOO0O0OOOOO0O00 ,O0OO000OO0O0O00OO +1 ):#line:78
        if not scanning :#line:79
            break #line:80
        try :#line:81
            OOOO0O00O0O0O0O00 =socket .socket (socket .AF_INET ,socket .SOCK_STREAM )#line:82
            OOOO0O00O0O0O0O00 .settimeout (0.1 )#line:83
            O00O00OO0O000O0O0 =OOOO0O00O0O0O0O00 .connect_ex ((O0OOOOOOOO0OO0000 ,OOOO000O0O0OOO00O ))#line:84
            if O00O00OO0O000O0O0 ==0 :#line:85
                open_ports .append (OOOO000O0O0OOO00O )#line:86
                OO0OOOOOO0OOO000O .insert (tk .END ,f"Port {OOOO000O0O0OOO00O} is open\n")#line:87
            OOOO0O00O0O0O0O00 .close ()#line:88
        except Exception as O0000OO0000OO0000 :#line:89
            OO0OOOOOO0OOO000O .insert (tk .END ,f"Error scanning port {OOOO000O0O0OOO00O}: {O0000OO0000OO0000}\n")#line:90
        O000OO00O00OO00OO ['value']=((OOOO000O0O0OOO00O -O0OOO0O0OOOOO0O00 )/(O0OO000OO0O0O00OO -O0OOO0O0OOOOO0O00 ))*100 #line:91
        root .update_idletasks ()#line:92
    scanning =False #line:93
    scan_button .config (state =tk .NORMAL )#line:94
    terminate_button .config (state =tk .DISABLED )#line:95
    if open_ports :#line:96
        messagebox .showinfo ("Scan Complete",f"Scan completed. Open ports: {open_ports}")#line:97
    else :#line:98
        messagebox .showinfo ("Scan Complete","Scan completed. No open ports found.")#line:99
def start_scan ():#line:102
    global scanning #line:103
    OO0O00O00O0000O0O =local_ip_entry .get ()#line:104
    if not OO0O00O00O0000O0O :#line:105
        messagebox .showerror ("Error","Please enter a valid IP address")#line:106
        return #line:107
    scanning =True #line:108
    scan_button .config (state =tk .DISABLED )#line:109
    terminate_button .config (state =tk .NORMAL )#line:110
    local_result_text .delete (1.0 ,tk .END )#line:111
    local_progress_bar ['value']=0 #line:112
    threading .Thread (target =scan_ports ,args =(OO0O00O00O0000O0O ,0 ,65535 ,local_result_text ,local_progress_bar )).start ()#line:113
def terminate_scan ():#line:116
    global scanning #line:117
    scanning =False #line:118
    scan_button .config (state =tk .NORMAL )#line:119
    terminate_button .config (state =tk .DISABLED )#line:120
def show_open_ports ():#line:123
    if not open_ports :#line:124
        messagebox .showinfo ("Open Ports","No open ports found.")#line:125
        return #line:126
    OO000O00O0OO000OO =tk .Toplevel (root )#line:127
    OO000O00O0OO000OO .title ("Open Ports")#line:128
    O0OO0O0OO00000000 =tk .Label (OO000O00O0OO000OO ,text ="Open Ports:",font =("Arial",14 ))#line:129
    O0OO0O0OO00000000 .pack (pady =10 )#line:130
    O000000O0O00OOOO0 =scrolledtext .ScrolledText (OO000O00O0OO000OO ,width =50 ,height =20 )#line:131
    O000000O0O00OOOO0 .pack (padx =10 ,pady =10 )#line:132
    for O0O00O0O0O0OOO000 in open_ports :#line:133
        O000000O0O00OOOO0 .insert (tk .END ,f"Port {O0O00O0O0O0OOO000} is open\n")#line:134
def gather_ip_info ():#line:137
    O0O00OOO00OO0OO00 =public_ip_entry .get ()#line:138
    if not O0O00OOO00OO0OO00 :#line:139
        messagebox .showerror ("Error","Please enter a valid IP address")#line:140
        return #line:141
    try :#line:143
        OO00OOOO0O0OO0O00 =requests .get (f"https://ipinfo.io/{O0O00OOO00OO0OO00}/json")#line:144
        O0OOOOOO00OOO0OOO =OO00OOOO0O0OO0O00 .json ()#line:145
        OO0OO00OO0O0OO0OO =O0OOOOOO00OOO0OOO .get ("org","N/A")#line:147
        O000000O0OOOO0O00 =O0OOOOOO00OOO0OOO .get ("hostname","N/A")#line:148
        O00O00000O0OO00OO =O0OOOOOO00OOO0OOO .get ("org","N/A").split ()[0 ]if O0OOOOOO00OOO0OOO .get ("org")else "N/A"#line:149
        O0O0O00O0O0OOOO0O =O0OOOOOO00OOO0OOO .get ("country","N/A")#line:150
        O000O0O0OOO00O0OO =O0OOOOOO00OOO0OOO .get ("city","N/A")#line:151
        OOOO0O000O000OOO0 =O0OOOOOO00OOO0OOO .get ("loc","N/A")#line:152
        OOO0OOOO0O0O00000 =O0OOOOOO00OOO0OOO .get ("type","N/A")#line:153
        OOOO0000OO00000OO ="Yes"if O0OOOOOO00OOO0OOO .get ("vpn",False )else "No"#line:154
        OO00OOO0OO0OO0O0O ="Yes"if O0OOOOOO00OOO0OOO .get ("satellite",False )else "No"#line:155
        OO0OOOOOO0O0OO0O0 ="Yes"if O0OOOOOO00OOO0OOO .get ("anonymous",False )else "No"#line:156
        OO00OO0OOOO0OO0OO ="Yes"if O0OOOOOO00OOO0OOO .get ("hosting",False )else "No"#line:157
        OOOO0O0O0O0O00O00 ="Yes"if O0OOOOOO00OOO0OOO .get ("proxy",False )else "No"#line:158
        OO000OOO0OO00O0OO ="Yes"if O0OOOOOO00OOO0OOO .get ("tor",False )else "No"#line:159
        O0000OO0O0O000000 ="Yes"if O0OOOOOO00OOO0OOO .get ("relay",False )else "No"#line:160
        OO000000O00OOO0OO =O0OOOOOO00OOO0OOO .get ("service","N/A")#line:161
        public_result_text .delete (1.0 ,tk .END )#line:163
        public_result_text .insert (tk .END ,f"Provider: {OO0OO00OO0O0OO0OO}\n")#line:164
        public_result_text .insert (tk .END ,f"Hostname: {O000000O0OOOO0O00}\n")#line:165
        public_result_text .insert (tk .END ,f"Organization: {O00O00000O0OO00OO}\n")#line:166
        public_result_text .insert (tk .END ,f"Country: {O0O0O00O0O0OOOO0O}\n")#line:167
        public_result_text .insert (tk .END ,f"City: {O000O0O0OOO00O0OO}\n")#line:168
        public_result_text .insert (tk .END ,f"Location: {OOOO0O000O000OOO0}\n")#line:169
        public_result_text .insert (tk .END ,f"Type: {OOO0OOOO0O0O00000}\n")#line:170
        public_result_text .insert (tk .END ,f"VPN: {OOOO0000OO00000OO}\n")#line:171
        public_result_text .insert (tk .END ,f"Satellite: {OO00OOO0OO0OO0O0O}\n")#line:172
        public_result_text .insert (tk .END ,f"Anonymous: {OO0OOOOOO0O0OO0O0}\n")#line:173
        public_result_text .insert (tk .END ,f"Hosting: {OO00OO0OOOO0OO0OO}\n")#line:174
        public_result_text .insert (tk .END ,f"Proxy: {OOOO0O0O0O0O00O00}\n")#line:175
        public_result_text .insert (tk .END ,f"Tor Browser: {OO000OOO0OO00O0OO}\n")#line:176
        public_result_text .insert (tk .END ,f"Relay: {O0000OO0O0O000000}\n")#line:177
        public_result_text .insert (tk .END ,f"Service: {OO000000O00OOO0OO}\n")#line:178
    except Exception as OO0O000O00O0O0000 :#line:179
        messagebox .showerror ("Error",f"Failed to gather IP information: {OO0O000O00O0O0000}")#line:180
def check_port ():#line:183
    OOO0O0O0O00OO000O =public_ip_port_entry .get ()#line:184
    OO00000OOO0O0OOO0 =public_port_entry .get ()#line:185
    if not OOO0O0O0O00OO000O or not OO00000OOO0O0OOO0 :#line:186
        messagebox .showerror ("Error","Please enter a valid IP address and port")#line:187
        return #line:188
    try :#line:190
        OO00000OOO0O0OOO0 =int (OO00000OOO0O0OOO0 )#line:191
        OOO0O00OOO00O00O0 =socket .socket (socket .AF_INET ,socket .SOCK_STREAM )#line:192
        OOO0O00OOO00O00O0 .settimeout (1 )#line:193
        O0000OOOO00000O00 =OOO0O00OOO00O00O0 .connect_ex ((OOO0O0O0O00OO000O ,OO00000OOO0O0OOO0 ))#line:194
        if O0000OOOO00000O00 ==0 :#line:195
            O00000OO00O000OOO ="Open"#line:196
        else :#line:197
            O00000OO00O000OOO ="Closed"#line:198
        OOO0O00OOO00O00O0 .close ()#line:199
        OO0O00OOOOOO00000 ="N/A"#line:201
        try :#line:202
            O0O00O0OO0000O00O =socket .getservbyport (OO00000OOO0O0OOO0 )#line:203
            OO0O00OOOOOO00000 =f"Service: {O0O00O0OO0000O00O}"#line:204
        except :#line:205
            OO0O00OOOOOO00000 ="Service: Unknown"#line:206
        public_port_result_text .delete (1.0 ,tk .END )#line:208
        public_port_result_text .insert (tk .END ,f"IP: {OOO0O0O0O00OO000O}\n")#line:209
        public_port_result_text .insert (tk .END ,f"Port: {OO00000OOO0O0OOO0}\n")#line:210
        public_port_result_text .insert (tk .END ,f"Status: {O00000OO00O000OOO}\n")#line:211
        public_port_result_text .insert (tk .END ,f"{OO0O00OOOOOO00000}\n")#line:212
        if O00000OO00O000OOO =="Open":#line:214
            try :#line:215
                OOOOOOO0OOO0O00O0 =requests .get (f"http://{OOO0O0O0O00OO000O}:{OO00000OOO0O0OOO0}",timeout =2 )#line:216
                public_port_result_text .insert (tk .END ,f"HTTP Response: {OOOOOOO0OOO0O00O0.status_code}\n")#line:217
                if OOOOOOO0OOO0O00O0 .headers :#line:218
                    public_port_result_text .insert (tk .END ,"Headers:\n")#line:219
                    for OOOO0000O000OO00O ,O0O0O000OO0O0000O in OOOOOOO0OOO0O00O0 .headers .items ():#line:220
                        public_port_result_text .insert (tk .END ,f"{OOOO0000O000OO00O}: {O0O0O000OO0O0000O}\n")#line:221
            except Exception as O0OOO00OO00OO00OO :#line:222
                public_port_result_text .insert (tk .END ,f"HTTP Request Error: {O0OOO00OO00OO00OO}\n")#line:223
    except Exception as O0OOO00OO00OO00OO :#line:224
        messagebox .showerror ("Error",f"Failed to check port: {O0OOO00OO00OO00OO}")#line:225
root =tk .Tk ()#line:228
root .title ("4-in-1 Tool")#line:229
notebook =ttk .Notebook (root )#line:232
notebook .pack (fill ="both",expand =True )#line:233
public_port_tab =ttk .Frame (notebook )#line:236
notebook .add (public_port_tab ,text ="Public IP Port Scanner")#line:237
public_ip_label =tk .Label (public_port_tab ,text ="Public IP Address:")#line:239
public_ip_label .grid (row =0 ,column =0 ,padx =10 ,pady =10 )#line:240
public_ip_entry =tk .Entry (public_port_tab ,width =20 )#line:242
public_ip_entry .grid (row =0 ,column =1 ,padx =10 ,pady =10 )#line:243
public_scan_button =tk .Button (public_port_tab ,text ="Scan Ports",command =start_public_scan )#line:245
public_scan_button .grid (row =0 ,column =2 ,padx =10 ,pady =10 )#line:246
public_terminate_button =tk .Button (public_port_tab ,text ="Terminate",command =stop_public_scan ,state =tk .DISABLED )#line:248
public_terminate_button .grid (row =0 ,column =3 ,padx =10 ,pady =10 )#line:249
public_result_text =tk .Text (public_port_tab ,height =10 ,width =80 )#line:251
public_result_text .grid (row =1 ,column =0 ,columnspan =4 ,padx =10 ,pady =10 )#line:252
public_progress =ttk .Progressbar (public_port_tab ,orient ='horizontal',length =600 ,mode ='determinate')#line:254
public_progress .grid (row =2 ,column =0 ,columnspan =4 ,padx =10 ,pady =10 )#line:255
public_open_ports_button =tk .Button (public_port_tab ,text ="Open Ports",command =show_public_open_ports )#line:257
public_open_ports_button .grid (row =3 ,column =0 ,padx =10 ,pady =10 )#line:258
local_tab =ttk .Frame (notebook )#line:261
notebook .add (local_tab ,text ="Local IP Port Scanner")#line:262
local_ip_label =tk .Label (local_tab ,text ="Local IP Address:")#line:264
local_ip_label .grid (row =0 ,column =0 ,padx =10 ,pady =10 )#line:265
local_ip_entry =tk .Entry (local_tab ,width =20 )#line:267
local_ip_entry .grid (row =0 ,column =1 ,padx =10 ,pady =10 )#line:268
scan_button =tk .Button (local_tab ,text ="Scan Ports",command =start_scan )#line:270
scan_button .grid (row =0 ,column =2 ,padx =10 ,pady =10 )#line:271
terminate_button =tk .Button (local_tab ,text ="Terminate",command =terminate_scan ,state =tk .DISABLED )#line:273
terminate_button .grid (row =0 ,column =3 ,padx =10 ,pady =10 )#line:274
local_result_text =tk .Text (local_tab ,height =10 ,width =80 )#line:276
local_result_text .grid (row =1 ,column =0 ,columnspan =4 ,padx =10 ,pady =10 )#line:277
local_progress_bar =ttk .Progressbar (local_tab ,orient ="horizontal",length =600 ,mode ="determinate")#line:279
local_progress_bar .grid (row =2 ,column =0 ,columnspan =4 ,padx =10 ,pady =10 )#line:280
open_ports_button =tk .Button (local_tab ,text ="Open Ports",command =show_open_ports )#line:282
open_ports_button .grid (row =3 ,column =0 ,padx =10 ,pady =10 )#line:283
public_tab =ttk .Frame (notebook )#line:286
notebook .add (public_tab ,text ="Public IP Info")#line:287
public_ip_label =tk .Label (public_tab ,text ="Target IP Address:")#line:289
public_ip_label .grid (row =0 ,column =0 ,padx =10 ,pady =10 )#line:290
public_ip_entry =tk .Entry (public_tab ,width =20 )#line:292
public_ip_entry .grid (row =0 ,column =1 ,padx =10 ,pady =10 )#line:293
gather_button =tk .Button (public_tab ,text ="Gather Info",command =gather_ip_info )#line:295
gather_button .grid (row =0 ,column =2 ,padx =10 ,pady =10 )#line:296
public_result_text =scrolledtext .ScrolledText (public_tab ,height =20 ,width =70 )#line:298
public_result_text .grid (row =1 ,column =0 ,columnspan =3 ,padx =10 ,pady =10 )#line:299
public_port_tab =ttk .Frame (notebook )#line:302
notebook .add (public_port_tab ,text ="Public IP Port Checker")#line:303
public_ip_port_label =tk .Label (public_port_tab ,text ="Target IP Address:")#line:305
public_ip_port_label .grid (row =0 ,column =0 ,padx =10 ,pady =10 )#line:306
public_ip_port_entry =tk .Entry (public_port_tab ,width =20 )#line:308
public_ip_port_entry .grid (row =0 ,column =1 ,padx =10 ,pady =10 )#line:309
public_port_label =tk .Label (public_port_tab ,text ="Port:")#line:311
public_port_label .grid (row =1 ,column =0 ,padx =10 ,pady =10 )#line:312
public_port_entry =tk .Entry (public_port_tab ,width =20 )#line:314
public_port_entry .grid (row =1 ,column =1 ,padx =10 ,pady =10 )#line:315
check_button =tk .Button (public_port_tab ,text ="Check Port",command =check_port )#line:317
check_button .grid (row =1 ,column =2 ,padx =10 ,pady =10 )#line:318
public_port_result_text =scrolledtext .ScrolledText (public_port_tab ,height =20 ,width =70 )#line:320
public_port_result_text .grid (row =2 ,column =0 ,columnspan =3 ,padx =10 ,pady =10 )#line:321
credits_tab =ttk .Frame (notebook )#line:324
notebook .add (credits_tab ,text ="Credits")#line:325
credits_label =tk .Label (credits_tab ,text ="Created by Panos Daflos",font =("Arial",14 ))#line:327
credits_label .pack (pady =20 )#line:328
root .mainloop ()