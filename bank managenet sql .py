import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

def connect_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345678",
            database="bankdb"
        )
        return conn
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
        return None

root = tk.Tk()
root.title("🏦 Bank Management System")
root.geometry("1100x620")
root.config(bg="#f5f5f5")
root.rowconfigure(1, weight=1)
root.columnconfigure(0, weight=1)

title = tk.Label(root, text="BANK MANAGEMENT SYSTEM", font=("Segoe UI", 26, "bold"),
                 fg="#2c3e50", bg="#f5f5f5")
title.grid(row=0, column=0, columnspan=2, pady=15, sticky="n")

main_frame = tk.Frame(root, bg="#f5f5f5")
main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
main_frame.columnconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=2)
main_frame.rowconfigure(0, weight=1)

left_frame = tk.LabelFrame(main_frame, text="Account Details", font=("Segoe UI", 16, "bold"),
                           bg="white", fg="#007bff", labelanchor="n")
left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10, ipadx=10, ipady=10)
left_frame.columnconfigure(1, weight=1)

fields = ["Account No", "Name", "Account Type", "Balance"]
entries = {}

for i, field in enumerate(fields):
    tk.Label(left_frame, text=field, font=("Segoe UI", 12), bg="white").grid(row=i, column=0, sticky="w", pady=5, padx=10)
    entry = tk.Entry(left_frame, font=("Segoe UI", 12), width=25, bd=2, relief=tk.SOLID)
    entry.grid(row=i, column=1, sticky="ew", pady=5, padx=10)
    entries[field] = entry

def clear_fields():
    for e in entries.values():
        e.delete(0, tk.END)

def load_data():
    """Load data from MySQL into Treeview"""
    for row in tree.get_children():
        tree.delete(row)
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM accounts")
        for acc in cur.fetchall():
            tree.insert("", tk.END, values=acc)
        conn.close()

def add_account():
    data = [entries[f].get() for f in fields]
    if "" in data:
        messagebox.showwarning("Warning", "Please fill all fields!")
        return
    try:
        float(data[3])
    except ValueError:
        messagebox.showerror("Error", "Balance must be a number!")
        return

    conn = connect_db()
    if conn:
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO accounts VALUES (%s, %s, %s, %s)", data)
            conn.commit()
            messagebox.showinfo("Success", "Account added successfully!")
            load_data()
            clear_fields()
        except mysql.connector.IntegrityError:
            messagebox.showerror("Error", "Account number already exists!")
        finally:
            conn.close()

def delete_account():
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Warning", "Please select a record to delete!")
        return
    acc_no = tree.item(sel)["values"][0]
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM accounts WHERE acc_no=%s", (acc_no,))
        conn.commit()
        conn.close()
        tree.delete(sel)
        messagebox.showinfo("Deleted", "Account deleted successfully!")

def update_account():
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Warning", "Please select a record to update!")
        return
    data = [entries[f].get() for f in fields]
    if "" in data:
        messagebox.showwarning("Warning", "Please fill all fields!")
        return
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute("UPDATE accounts SET name=%s, acc_type=%s, balance=%s WHERE acc_no=%s",
                    (data[1], data[2], data[3], data[0]))
        conn.commit()
        conn.close()
        messagebox.showinfo("Updated", "Account updated successfully!")
        load_data()

def deposit_money():
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Warning", "Please select an account to deposit into!")
        return
    acc_no = tree.item(sel)['values'][0]
    try:
        amount = float(entries["Balance"].get())
    except ValueError:
        messagebox.showerror("Error", "Enter a valid amount!")
        return
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute("UPDATE accounts SET balance = balance + %s WHERE acc_no=%s", (amount, acc_no))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", f"₹{amount:.2f} deposited successfully!")
        load_data()
        clear_fields()

def withdraw_money():
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Warning", "Please select an account to withdraw from!")
        return
    acc_no = tree.item(sel)['values'][0]
    try:
        amount = float(entries["Balance"].get())
    except ValueError:
        messagebox.showerror("Error", "Enter a valid amount!")
        return
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT balance FROM accounts WHERE acc_no=%s", (acc_no,))
        bal = cur.fetchone()[0]
        if bal < amount:
            messagebox.showerror("Error", "Insufficient balance!")
        else:
            cur.execute("UPDATE accounts SET balance = balance - %s WHERE acc_no=%s", (amount, acc_no))
            conn.commit()
            messagebox.showinfo("Success", f"₹{amount:.2f} withdrawn successfully!")
        conn.close()
        load_data()
        clear_fields()

def check_balance():
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Warning", "Please select an account!")
        return
    acc_no = tree.item(sel)['values'][0]
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute("SELECT name, balance FROM accounts WHERE acc_no=%s", (acc_no,))
        name, balance = cur.fetchone()
        messagebox.showinfo("Balance Info", f"Account: {acc_no}\nHolder: {name}\nBalance: ₹{balance:.2f}")
        conn.close()

def on_select(event):
    sel = tree.selection()
    if not sel:
        return
    values = tree.item(sel)['values']
    for i, f in enumerate(fields):
        entries[f].delete(0, tk.END)
        entries[f].insert(0, values[i])
btn_frame = tk.Frame(left_frame, bg="white")
btn_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky="ew")
btn_frame.columnconfigure((0, 1, 2, 3), weight=1)

buttons = [
    ("Add", "#28a745", add_account),
    ("Update", "#f0ad4e", update_account),
    ("Delete", "#dc3545", delete_account),
    ("Clear", "#2c3e50", clear_fields)
]

for i, (text, color, cmd) in enumerate(buttons):
    tk.Button(btn_frame, text=text, bg=color, fg="white", font=("Segoe UI", 11, "bold"),
              command=cmd).grid(row=0, column=i, padx=5, pady=5, sticky="ew")

btn_frame2 = tk.Frame(left_frame, bg="white")
btn_frame2.grid(row=6, column=0, columnspan=2, pady=10, sticky="ew")
btn_frame2.columnconfigure((0, 1, 2), weight=1)

actions = [
    ("Deposit", "#007bff", deposit_money),
    ("Withdraw", "#6f42c1", withdraw_money),
    ("Check Balance", "#17a2b8", check_balance)
]

for i, (text, color, cmd) in enumerate(actions):
    tk.Button(btn_frame2, text=text, bg=color, fg="white", font=("Segoe UI", 11, "bold"),
              command=cmd).grid(row=0, column=i, padx=5, pady=5, sticky="ew")
right_frame = tk.LabelFrame(main_frame, text="Customer Records", font=("Segoe UI", 16, "bold"),
                            bg="white", fg="#28a745", labelanchor="n")
right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
right_frame.rowconfigure(0, weight=1)
right_frame.columnconfigure(0, weight=1)

columns = ("Account No", "Name", "Account Type", "Balance")
tree = ttk.Treeview(right_frame, columns=columns, show="headings")

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor=tk.CENTER)

tree.grid(row=0, column=0, sticky="nsew")
scroll_y = ttk.Scrollbar(right_frame, orient="vertical", command=tree.yview)
tree.configure(yscroll=scroll_y.set)
scroll_y.grid(row=0, column=1, sticky="ns")

tree.bind("<<TreeviewSelect>>", on_select)

load_data()

root.mainloop()

