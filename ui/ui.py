import os
import sys
import threading
from tkinter import *
from tkinter import ttk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import search

root = Tk()
root.title('Jira Agent')
root.geometry("1280x720")
root.minsize(320, 240)

frm = ttk.Frame(root, padding=10)
frm.grid(row=0, column=0, sticky="nsew")
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)
frm.rowconfigure(0, weight=1)
frm.columnconfigure(0, weight=1)

log = Text(frm, state="disabled", wrap="word")
log.grid(row=0, column=0, columnspan=2, sticky="nsew")

scrollbar = ttk.Scrollbar(frm, command=log.yview)
scrollbar.grid(row=0, column=2, sticky="ns")
log.configure(yscrollcommand=scrollbar.set)

entry = ttk.Entry(frm)
entry.grid(row=1, column=0, sticky="ew", pady=(10, 0))
frm.columnconfigure(0, weight=1)

def append_log(text):
    log.configure(state="normal")
    log.insert(END, text + "\n\n")
    log.configure(state="disabled")
    log.see(END)

def on_reply(reply):
    append_log(f"Agent: {reply}")
    entry.configure(state="normal")
    send_btn.configure(state="normal")
    entry.focus_set()

def run_agent(content):
    try:
        reply = search.jira_agent(content)
    except Exception as e:
        reply = f"Error: {e}"
    root.after(0, on_reply, reply)

def send(event=None):
    content = entry.get().strip()
    if not content:
        return
    append_log(f"You: {content}")
    entry.delete(0, END)
    entry.configure(state="disabled")
    send_btn.configure(state="disabled")
    threading.Thread(target=run_agent, args=(content,), daemon=True).start()

send_btn = ttk.Button(frm, text="Send", command=send)
send_btn.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(10, 0))

entry.bind("<Return>", send)
entry.focus_set()

root.mainloop()
