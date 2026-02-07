import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os

# ---------- GLOBAL VARIABLES ----------
process_counter = 1
processes = {}
system_health = 100
score = 0
freeze_active = False
slow_active = False
spawn_interval = 1500
level = 1

congrats_shown = False
game_active = True   # MAIN CONTROL FLAG

# ---------- MAIN WINDOW ----------
root = tk.Tk()
root.title("Process Creation & Termination")
root.geometry("800x700")
root.resizable(True, True)

# ---------- HEALTH BAR ----------
health_label = tk.Label(root, text=f"System Health: {system_health}", font=("Arial", 14))
health_label.pack(pady=5)

health_bar = ttk.Progressbar(root, length=700, maximum=100)
health_bar['value'] = system_health
health_bar.pack(pady=5)

# ---------- SCORE & LEVEL ----------
score_label = tk.Label(root, text=f"Score: {score}", font=("Arial", 14))
score_label.pack(pady=2)

level_label = tk.Label(root, text=f"Level: {level}", font=("Arial", 14))
level_label.pack(pady=2)

# ---------- ARENA CANVAS ----------
canvas = tk.Canvas(root, width=750, height=400, highlightthickness=0)
canvas.pack(pady=10)

# Gradient background
for i in range(400):
    color = "#%02x%02x%02x" % (34 + i//4, 34 + i//4, 50 + i//2)
    canvas.create_line(0, i, 750, i, fill=color)

# ---------- LOG BOX ----------
log_box = tk.Text(root, height=10, width=95, state='disabled', bg="#f0f0f0")
log_box.pack(pady=5)

def log(msg):
    log_box.config(state='normal')
    log_box.insert(tk.END, msg + "\n")
    log_box.see(tk.END)
    log_box.config(state='disabled')

# ---------- PROCESS CLASS ----------
class Process:
    def __init__(self, pid):
        self.pid = pid
        self.x = random.randint(20, 700)
        self.y = random.randint(20, 350)
        self.color = random.choice(["red", "orange"])
        self.speed = random.randint(1, 3) + level

        self.rect = canvas.create_oval(self.x, self.y, self.x+50, self.y+50, fill=self.color)
        self.label = canvas.create_text(self.x+25, self.y+25, text=f"P{self.pid}", fill="white")

        canvas.tag_bind(self.rect, "<Button-1>", lambda e, pid=self.pid: terminate_process(pid))
        canvas.tag_bind(self.label, "<Button-1>", lambda e, pid=self.pid: terminate_process(pid))

    def move(self):
        dx = random.choice([-1,0,1]) * self.speed
        dy = random.choice([-1,0,1]) * self.speed
        self.x = max(0, min(700, self.x + dx))
        self.y = max(0, min(350, self.y + dy))
        canvas.coords(self.rect, self.x, self.y, self.x+50, self.y+50)
        canvas.coords(self.label, self.x+25, self.y+25)

# ---------- CREATE PROCESS ----------
def create_process():
    global process_counter
    if not game_active:
        return

    pid = process_counter
    process = Process(pid)
    processes[pid] = process
    log(f"Process P{pid} created")
    process_counter += 1

    root.after(spawn_interval, create_process)

# ---------- MOVE & HEALTH CHECK ----------
def move_processes():
    global system_health, congrats_shown, game_active

    if not game_active:
        return

    for process in list(processes.values()):
        process.move()

    # Health decreases only if >8 processes
    if len(processes) > 8:
        system_health -= 1
        health_bar['value'] = system_health
        health_label.config(text=f"System Health: {system_health}")
        log("⚠ High Load! Health decreasing")

    # Level up
    if score >= level * 50:
        level_up()

    # Success condition
    if level >= 5 and not congrats_shown:
        congrats_shown = True
        game_active = False
        messagebox.showinfo("Success", "🎉 Congratulations! Your system is safe now!")
        log("System stabilized. No more processes will spawn.")
        root.after(1000, root.destroy)
        return

    # Crash condition
    if system_health <= 0:
        system_crash()
        return

    root.after(100, move_processes)

# ---------- TERMINATE PROCESS ----------
def terminate_process(pid):
    global score
    if pid in processes:
        canvas.delete(processes[pid].rect)
        canvas.delete(processes[pid].label)
        del processes[pid]
        score += 10
        score_label.config(text=f"Score: {score}")
        log(f"Process P{pid} terminated")

# ---------- LEVEL UP ----------
def level_up():
    global level, spawn_interval
    level += 1
    spawn_interval = max(500, spawn_interval - 200)
    level_label.config(text=f"Level: {level}")
    log(f"Level Up! Now Level {level}")

# ---------- SYSTEM CRASH ----------
def system_crash():
    global game_active
    game_active = False
    messagebox.showerror("System Crash", "💥 Your system crashed!")
    log("SYSTEM CRASHED! No more processes will spawn.")
    root.destroy()

# ---------- START ----------
create_process()
move_processes()
root.mainloop()
