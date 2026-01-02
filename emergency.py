import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import pandas as pd
import os, random
from datetime import datetime

# ================= FILE PATHS =================
ADMIN_FILE = 'admins.csv'
USERS_FILE = 'users.csv'
VOLUNTEERS_FILE = 'volunteers.csv'
EMERGENCIES_FILE = 'emergencies.csv'
RESOURCES_FILE = 'resources.csv'

# ================= GUI CONSOLE =================
class GUIConsole:
    def __init__(self, widget):
        self.widget = widget
    def write(self, msg):
        self.widget.insert(tk.END, str(msg) + "\n")
        self.widget.see(tk.END)
    def clear(self):
        self.widget.delete('1.0', tk.END)

console = None

def print_gui(msg):
    console.write(msg)

# ================= SAFE INPUT =================
def safe_input(prompt, default=None):
    val = simpledialog.askstring('Input', prompt)
    if val is None or val == '':
        return default if default is not None else ''
    return val

# ================= DATA =================
def ensure_tables():
    global admins, users, volunteers, emergencies, resources
    admins = pd.read_csv(ADMIN_FILE) if os.path.exists(ADMIN_FILE) else pd.DataFrame([[1,'Admin','admin@mail.com','admin123']], columns=['admin_id','name','email','password'])
    users = pd.read_csv(USERS_FILE) if os.path.exists(USERS_FILE) else pd.DataFrame(columns=['user_id','name','email','phone','location','password'])
    volunteers = pd.read_csv(VOLUNTEERS_FILE) if os.path.exists(VOLUNTEERS_FILE) else pd.DataFrame(columns=['volunteer_id','name','email','phone','location','password','status','assigned_emergency_id'])
    emergencies = pd.read_csv(EMERGENCIES_FILE) if os.path.exists(EMERGENCIES_FILE) else pd.DataFrame(columns=['emergency_id','user_id','type','description','location','time','date','status','assigned_volunteer_id'])
    resources = pd.read_csv(RESOURCES_FILE) if os.path.exists(RESOURCES_FILE) else pd.DataFrame(columns=['resource_id','name','quantity','status','location','assigned_emergency_id'])

ensure_tables()


def save_all():
    admins.to_csv(ADMIN_FILE, index=False)
    users.to_csv(USERS_FILE, index=False)
    volunteers.to_csv(VOLUNTEERS_FILE, index=False)
    emergencies.to_csv(EMERGENCIES_FILE, index=False)
    resources.to_csv(RESOURCES_FILE, index=False)


def next_id(df, col):
    return 1 if df.empty else int(df[col].max()) + 1

# ================= ORIGINAL OPERATIONS =================
def register_user():
    uid = next_id(users, 'user_id')
    name = safe_input('Name')
    if not name: return
    email = safe_input('Email')
    if not email: return
    phone = safe_input('Phone')
    if not phone: return
    location = safe_input('Location')
    if not location: return
    password = safe_input('Password')
    if not password: return
    
    users.loc[len(users)] = [uid, name, email, phone, location, password]
    save_all()
    print_gui(f'User registered successfully! ID={uid}')
    messagebox.showinfo('Success', f'User registered with ID: {uid}')


def register_volunteer():
    vid = next_id(volunteers, 'volunteer_id')
    name = safe_input('Name')
    if not name: return
    email = safe_input('Email')
    if not email: return
    phone = safe_input('Phone')
    if not phone: return
    location = safe_input('Location')
    if not location: return
    password = safe_input('Password')
    if not password: return
    
    volunteers.loc[len(volunteers)] = [vid, name, email, phone, location, password, 'Available', None]
    save_all()
    print_gui(f'Volunteer registered successfully! ID={vid}')
    messagebox.showinfo('Success', f'Volunteer registered with ID: {vid}')


def login(df, role):
    email = safe_input('Email')
    if not email: return None
    password = safe_input('Password')
    if not password: return None
    
    row = df[(df['email']==email) & (df['password']==password)]
    if row.empty:
        messagebox.showerror('Login Failed', 'Invalid credentials')
        return None
    print_gui(f'Welcome {role}: {row.iloc[0]["name"]}')
    return int(row.iloc[0][0])


def add_emergency(admin_mode=False, user_id=0):
    eid = next_id(emergencies, 'emergency_id')
    
    etype = safe_input('Emergency Type (Fire/Flood/Accident/Medical/Other)', 'Other')
    if not etype: return
    description = safe_input('Description', '')
    location = safe_input('Location', '')
    if not location: return
    time = safe_input('Time (HH:MM)', datetime.now().strftime('%H:%M'))
    date = safe_input('Date (YYYY-MM-DD)', datetime.now().strftime('%Y-%m-%d'))
    
    assigned = None
    available = volunteers[volunteers['status']=='Available']
    if not available.empty:
        assigned = int(random.choice(available['volunteer_id'].tolist()))
        volunteers.loc[volunteers['volunteer_id']==assigned,'status']='Busy'
        volunteers.loc[volunteers['volunteer_id']==assigned,'assigned_emergency_id']=eid
    
    emergencies.loc[len(emergencies)] = [eid, user_id, etype, description, location, time, date, 'Pending', assigned]
    save_all()
    
    msg = f'Emergency added! ID={eid}'
    if assigned:
        msg += f', Assigned to Volunteer ID={assigned}'
    else:
        msg += ', No volunteers available at the moment'
    
    print_gui(msg)
    messagebox.showinfo('Success', msg)


def add_resource():
    rid = next_id(resources, 'resource_id')
    name = safe_input('Resource Name')
    if not name: return
    quantity = safe_input('Quantity', '1')
    status = safe_input('Status (Available/In Use/Reserved)', 'Available')
    location = safe_input('Location', '')
    
    resources.loc[len(resources)] = [rid, name, quantity, status, location, None]
    save_all()
    print_gui(f'Resource added! ID={rid}')
    messagebox.showinfo('Success', f'Resource added with ID: {rid}')


def update_emergency_status():
    eid = safe_input('Enter Emergency ID to update')
    if not eid: return
    
    try:
        eid = int(eid)
        if eid not in emergencies['emergency_id'].values:
            messagebox.showerror('Error', 'Emergency ID not found')
            return
        
        new_status = safe_input('New Status (Pending/In Progress/Resolved/Closed)', 'In Progress')
        emergencies.loc[emergencies['emergency_id']==eid, 'status'] = new_status
        
        # If resolved, free up the volunteer
        if new_status in ['Resolved', 'Closed']:
            vid = emergencies.loc[emergencies['emergency_id']==eid, 'assigned_volunteer_id'].values[0]
            if pd.notna(vid):
                volunteers.loc[volunteers['volunteer_id']==vid, 'status'] = 'Available'
                volunteers.loc[volunteers['volunteer_id']==vid, 'assigned_emergency_id'] = None
        
        save_all()
        print_gui(f'Emergency {eid} status updated to: {new_status}')
        messagebox.showinfo('Success', f'Emergency status updated to: {new_status}')
    except ValueError:
        messagebox.showerror('Error', 'Invalid Emergency ID')


# ================= TABLE VIEW =================
def show_table(df, title):
    if df.empty:
        messagebox.showinfo('No Data', f'No {title} to display')
        return
    
    top = tk.Toplevel(root)
    top.title(title)
    top.geometry('900x400')
    
    tree = ttk.Treeview(top, columns=list(df.columns), show='headings')
    
    # Add scrollbars
    vsb = ttk.Scrollbar(top, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(top, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
    for c in df.columns:
        tree.heading(c, text=c)
        tree.column(c, width=120)
    
    for _, row in df.iterrows():
        tree.insert('', tk.END, values=list(row))
    
    tree.grid(row=0, column=0, sticky='nsew')
    vsb.grid(row=0, column=1, sticky='ns')
    hsb.grid(row=1, column=0, sticky='ew')
    
    top.grid_rowconfigure(0, weight=1)
    top.grid_columnconfigure(0, weight=1)


# ================= MENU SWITCHING =================
def clear_menu():
    for w in menu_frame.winfo_children():
        w.destroy()


def main_menu():
    clear_menu()
    console.clear()
    print_gui('=== Emergency Management System ===')
    print_gui('Welcome! Please select an option from the menu.')
    print_gui('')
    
    tk.Label(menu_frame, text='Emergency Management', font=('Arial',14,'bold'), bg='#2c3e50', fg='white', pady=10).pack(fill=tk.X)
    tk.Label(menu_frame, text='Main Menu', font=('Arial',12,'bold'), pady=5).pack()
    
    tk.Button(menu_frame, text='👤 Register User', width=25, bg='#3498db', fg='white', command=register_user).pack(pady=3)
    tk.Button(menu_frame, text='🙋 Register Volunteer', width=25, bg='#2ecc71', fg='white', command=register_volunteer).pack(pady=3)
    tk.Button(menu_frame, text='🔐 Login Admin', width=25, bg='#e74c3c', fg='white', command=lambda: admin_menu(login(admins,'Admin'))).pack(pady=3)
    tk.Button(menu_frame, text='🔐 Login User', width=25, bg='#9b59b6', fg='white', command=lambda: user_menu(login(users,'User'))).pack(pady=3)
    tk.Button(menu_frame, text='🔐 Login Volunteer', width=25, bg='#f39c12', fg='white', command=lambda: volunteer_menu(login(volunteers,'Volunteer'))).pack(pady=3)
    
    tk.Label(menu_frame, text='', pady=10).pack()
    tk.Label(menu_frame, text='Default Admin Credentials:', font=('Arial',9)).pack()
    tk.Label(menu_frame, text='Email: admin@mail.com', font=('Arial',8)).pack()
    tk.Label(menu_frame, text='Password: admin123', font=('Arial',8)).pack()


def admin_menu(aid):
    if not aid: return
    clear_menu()
    console.clear()
    print_gui(f'=== Admin Dashboard (ID: {aid}) ===')
    print_gui('You have full access to the system.')
    print_gui('')
    
    tk.Label(menu_frame, text='Admin Dashboard', font=('Arial',12,'bold'), bg='#e74c3c', fg='white', pady=10).pack(fill=tk.X)
    
    tk.Button(menu_frame, text='🚨 View All Emergencies', width=25, command=lambda: show_table(emergencies,'All Emergencies')).pack(pady=3)
    tk.Button(menu_frame, text='➕ Add Emergency', width=25, command=lambda: add_emergency(True,0)).pack(pady=3)
    tk.Button(menu_frame, text='🔄 Update Emergency Status', width=25, command=update_emergency_status).pack(pady=3)
    tk.Button(menu_frame, text='👥 View All Volunteers', width=25, command=lambda: show_table(volunteers,'All Volunteers')).pack(pady=3)
    tk.Button(menu_frame, text='📦 View All Resources', width=25, command=lambda: show_table(resources,'All Resources')).pack(pady=3)
    tk.Button(menu_frame, text='➕ Add Resource', width=25, command=add_resource).pack(pady=3)
    tk.Button(menu_frame, text='👤 View All Users', width=25, command=lambda: show_table(users,'All Users')).pack(pady=3)
    tk.Button(menu_frame, text='← Back to Main Menu', width=25, bg='#95a5a6', command=main_menu).pack(pady=10)


def user_menu(uid):
    if not uid: return
    clear_menu()
    console.clear()
    print_gui(f'=== User Dashboard (ID: {uid}) ===')
    print_gui('You can report emergencies and view system information.')
    print_gui('')
    
    tk.Label(menu_frame, text='User Dashboard', font=('Arial',12,'bold'), bg='#9b59b6', fg='white', pady=10).pack(fill=tk.X)
    
    tk.Button(menu_frame, text='🚨 Report Emergency', width=25, bg='#e74c3c', fg='white', command=lambda: add_emergency(False,uid)).pack(pady=3)
    tk.Button(menu_frame, text='📋 View All Emergencies', width=25, command=lambda: show_table(emergencies,'All Emergencies')).pack(pady=3)
    tk.Button(menu_frame, text='📋 My Emergencies', width=25, command=lambda: show_table(emergencies[emergencies['user_id']==uid],'My Emergencies')).pack(pady=3)
    tk.Button(menu_frame, text='📦 View Resources', width=25, command=lambda: show_table(resources,'Resources')).pack(pady=3)
    tk.Button(menu_frame, text='👥 View Volunteers', width=25, command=lambda: show_table(volunteers,'Volunteers')).pack(pady=3)
    tk.Button(menu_frame, text='← Back to Main Menu', width=25, bg='#95a5a6', command=main_menu).pack(pady=10)


def volunteer_menu(vid):
    if not vid: return
    clear_menu()
    console.clear()
    print_gui(f'=== Volunteer Dashboard (ID: {vid}) ===')
    print_gui('View your assigned emergencies and resources.')
    print_gui('')
    
    tk.Label(menu_frame, text='Volunteer Dashboard', font=('Arial',12,'bold'), bg='#f39c12', fg='white', pady=10).pack(fill=tk.X)
    
    my_emergencies = emergencies[emergencies['assigned_volunteer_id']==vid]
    tk.Button(menu_frame, text=f'🚨 My Assigned Emergencies ({len(my_emergencies)})', width=25, bg='#e74c3c', fg='white', command=lambda: show_table(my_emergencies,'My Emergencies')).pack(pady=3)
    tk.Button(menu_frame, text='📋 View All Emergencies', width=25, command=lambda: show_table(emergencies,'All Emergencies')).pack(pady=3)
    tk.Button(menu_frame, text='👥 View All Volunteers', width=25, command=lambda: show_table(volunteers,'All Volunteers')).pack(pady=3)
    tk.Button(menu_frame, text='📦 View Resources', width=25, command=lambda: show_table(resources,'Resources')).pack(pady=3)
    tk.Button(menu_frame, text='← Back to Main Menu', width=25, bg='#95a5a6', command=main_menu).pack(pady=10)


# ================= GUI ROOT =================
root = tk.Tk()
root.title('Emergency Management System')
root.geometry('1000x600')
root.configure(bg='#ecf0f1')

# Menu frame (left side)
menu_frame = tk.Frame(root, width=250, bg='#ecf0f1')
menu_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
menu_frame.pack_propagate(False)

# Output frame (right side)
output_frame = tk.Frame(root, bg='#ecf0f1')
output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

tk.Label(output_frame, text='System Console', font=('Arial',11,'bold'), bg='#ecf0f1').pack(anchor='w', pady=(0,5))

output_text = tk.Text(output_frame, wrap=tk.WORD, bg='#2c3e50', fg='#ecf0f1', font=('Consolas', 10))
output_text.pack(fill=tk.BOTH, expand=True)

console = GUIConsole(output_text)

main_menu()
root.mainloop()
