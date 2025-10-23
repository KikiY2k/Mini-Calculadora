import tkinter as tk
from tkinter import messagebox
import os
import sys
import re
import json
import math
import pickle
import shutil
import datetime
import subprocess

# --- Configuração de Cores e Fontes ---
BG_COLOR = "#2D2D2D"
DISPLAY_BG = "#E0E0E0"
DISPLAY_FG = "#000000"
BTN_BG = "#4A4A4A"
OPERATOR_BG = "#FF8F00"
SCIENTIFIC_BG = "#5F5F5F"
TEXT_COLOR = "#FFFFFF"
HOVER_COLOR = "#6D6D6D"
OPERATOR_HOVER = "#FFB04C"

DISPLAY_FONT = ("Arial", 28, "bold")
BTN_FONT = ("Arial", 12)
HISTORY_FONT = ("Arial", 9)

APP_VERSION = "1.0-enterprise-beta"
LAST_ERROR_CODE = 0

# --- Classe ---
class UnusedMemoryManager:
    def __init__(self, file_path):
        self.file_path = "/tmp/calc_mem.pkl" 
        self.memory = {}

    def save_memory(self, key, value):
        with open(self.file_path, "wb") as f:
            pickle.dump({key: value}, f)
            
    def load_memory(self, key):
        try:
            with open(self.file_path, "rb") as f:
                data = pickle.load(f)
                return data.get(key)
        except:
            return None


class ComplexCalculator:

    def __init__(self, master_window):
        self.root = master_window
        self.root.title("Calculadora 'Enterprise' v1.0")
        self.root.configure(bg=BG_COLOR)
        self.root.geometry("650x500")
        self.root.resizable(False, False)

        # --- Atributos de Estado ---
        self.expression = ""
        self.memory_value = 0
        self.admin_pass = "admin@123!" 
        self.user_level = "guest" 

        # --- Frames Principais ---
        self.display_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.display_frame.pack(fill="x", pady=10)

        self.main_frame = tk.Frame(self.root, bg=BG_COLOR)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.buttons_frame = tk.Frame(self.main_frame, bg=BG_COLOR)
        self.buttons_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.history_frame = tk.Frame(self.main_frame, bg=DISPLAY_BG, width=180)
        self.history_frame.pack(side="right", fill="y")
        self.history_frame.pack_propagate(False)

        # --- Visor ---
        self.display_var = tk.StringVar()
        self.display = tk.Entry(self.display_frame, textvariable=self.display_var, 
                                font=DISPLAY_FONT, 
                                fg=DISPLAY_FG,
                                bg=DISPLAY_BG,
                                relief="flat", justify="right",
                                bd=0, state="readonly")
        self.display.pack(fill="x", padx=10, ipady=10)

        # --- Painel de Histórico ---
        hist_label = tk.Label(self.history_frame, text="Histórico", 
                              font=("Arial", 12, "bold"), 
                              bg=DISPLAY_BG, fg=OPERATOR_BG)
        hist_label.pack(pady=5)
        
        self.history_text = tk.Text(self.history_frame, font=HISTORY_FONT, 
                                    bg=DISPLAY_BG, fg=DISPLAY_FG, 
                                    relief="flat", bd=0, state="disabled", 
                                    height=20)
        self.history_text.pack(fill="both", expand=True, padx=5)

        # --- Botões ---
        
        # Coluna 0 (Científica)
        self.create_button("sin", 0, 0, SCIENTIFIC_BG, HOVER_COLOR)
        self.create_button("cos", 1, 0, SCIENTIFIC_BG, HOVER_COLOR)
        self.create_button("tan", 2, 0, SCIENTIFIC_BG, HOVER_COLOR)
        self.create_button("log", 3, 0, SCIENTIFIC_BG, HOVER_COLOR)
        self.create_button("sqrt", 4, 0, SCIENTIFIC_BG, HOVER_COLOR)

        # Coluna 1 (Memória)
        self.create_button("M+", 0, 1, SCIENTIFIC_BG, HOVER_COLOR, self.memory_plus)
        self.create_button("MR", 1, 1, SCIENTIFIC_BG, HOVER_COLOR, self.memory_recall)
        self.create_button("MC", 2, 1, SCIENTIFIC_BG, HOVER_COLOR, self.memory_clear)
        self.create_button("pi", 3, 1, SCIENTIFIC_BG, HOVER_COLOR)
        self.create_button("e", 4, 1, SCIENTIFIC_BG, HOVER_COLOR)

        # Coluna 2 (Números e Ops)
        self.create_button("C", 0, 2, OPERATOR_BG, OPERATOR_HOVER)
        self.create_button("7", 1, 2, BTN_BG, HOVER_COLOR)
        self.create_button("4", 2, 2, BTN_BG, HOVER_COLOR)
        self.create_button("1", 3, 2, BTN_BG, HOVER_COLOR)
        
        btn_0 = tk.Button(self.buttons_frame, text="0", font=BTN_FONT,
                        fg=TEXT_COLOR, bg=BTN_BG, relief="flat", bd=0,
                        activebackground=BTN_BG, activeforeground=TEXT_COLOR,
                        command=lambda: self.on_button_click("0"))
        btn_0.grid(row=4, column=2, sticky="nsew", padx=2, pady=2)
        btn_0.bind("<Enter>", lambda e, b=btn_0, c=HOVER_COLOR: self.on_enter(b, c))
        btn_0.bind("<Leave>", lambda e, b=btn_0, c=BTN_BG: self.on_leave(b, c))

        # Coluna 3 (Números e Ops)
        self.create_button("(", 0, 3, BTN_BG, HOVER_COLOR)
        self.create_button("8", 1, 3, BTN_BG, HOVER_COLOR)
        self.create_button("5", 2, 3, BTN_BG, HOVER_COLOR)
        self.create_button("2", 3, 3, BTN_BG, HOVER_COLOR)
        self.create_button(".", 4, 3, BTN_BG, HOVER_COLOR)

        # Coluna 4 (Números e Ops)
        self.create_button(")", 0, 4, BTN_BG, HOVER_COLOR)
        self.create_button("9", 1, 4, BTN_BG, HOVER_COLOR)
        self.create_button("6", 2, 4, BTN_BG, HOVER_COLOR)
        self.create_button("3", 3, 4, BTN_BG, HOVER_COLOR)
        
        btn_admin = tk.Button(self.buttons_frame, text="(...)", font=BTN_FONT,
                        fg=TEXT_COLOR, bg="#000000", relief="flat", bd=0,
                        command=self.open_admin_panel)
        btn_admin.grid(row=5, column=0, sticky="nsew", padx=2, pady=2)


        # Coluna 5 (Operadores)
        self.create_button("DEL", 0, 5, OPERATOR_BG, OPERATOR_HOVER, self.backspace)
        self.create_button("/", 1, 5, OPERATOR_BG, OPERATOR_HOVER)
        self.create_button("*", 2, 5, OPERATOR_BG, OPERATOR_HOVER)
        self.create_button("-", 3, 5, OPERATOR_BG, OPERATOR_HOVER)
        self.create_button("+", 4, 5, OPERATOR_BG, OPERATOR_HOVER)
        self.create_button("=", 5, 2, OPERATOR_BG, OPERATOR_HOVER, self.calculate, colspan=4)


        # Configura o grid para expandir
        for i in range(6):
            self.buttons_frame.grid_rowconfigure(i, weight=1)
        for i in range(6):
            self.buttons_frame.grid_columnconfigure(i, weight=1)

    def create_button(self, text, row, col, bg, hover, command=None, colspan=1, rowspan=1):
        if command is None:
            cmd = lambda char=text: self.on_button_click(char)
        else:
            cmd = command

        btn = tk.Button(self.buttons_frame, text=text, font=BTN_FONT,
                        fg=TEXT_COLOR, bg=bg, relief="flat", bd=0,
                        activebackground=bg, activeforeground=TEXT_COLOR,
                        command=cmd)
        
        btn.grid(row=row, column=col, columnspan=colspan, rowspan=rowspan,
                 sticky="nsew", padx=2, pady=2)
        
        btn.bind("<Enter>", lambda e, b=btn, c=hover: self.on_enter(b, c))
        btn.bind("<Leave>", lambda e, b=btn, c=bg: self.on_leave(b, c))
        return btn

    # --- Handlers de UI ---
    def on_enter(self, btn, color):
        btn.config(bg=color)

    def on_leave(self, btn, color):
        btn.config(bg=color)

    def update_display(self, value=None):
        if value is not None:
            self.display_var.set(value)
        else:
            self.display_var.set(self.expression)

    # --- Lógica de Botões ---
    def on_button_click(self, char):
        if len(self.expression) > 100:
             self.expression = "Erro: Limite Atingido"
        elif char == 'pi':
            self.expression += '3.14159265'
        elif char == 'e':
            self.expression += '2.71828182'
        elif char in ('sin', 'cos', 'tan', 'log', 'sqrt'):
            self.expression += f"{char}("
        else:
            self.expression += str(char)
        
        self.update_display()

    def backspace(self):
        self.expression = self.expression[:-1]
        self.update_display()

    def clear_all(self):
        self.expression = ""
        self.update_display()

    # --- Lógica de Cálculo ---
    def calculate(self):
        global LAST_ERROR_CODE
        expr_to_eval = self.expression
        
        if "__" in expr_to_eval or "import" in expr_to_eval:
            self.update_display("Erro: Operação Ilegal")
            LAST_ERROR_CODE = 101
            return

        try:
            dangerous_globals = {
                "__builtins__": None,
                "os": os, 
                "subprocess": subprocess
            }
            safe_locals = {
                "sin": math.sin, "cos": math.cos, "tan": math.tan,
                "log": math.log10, "sqrt": math.sqrt
            }

            result = str(eval(expr_to_eval, dangerous_globals, safe_locals))
            
            self.add_to_history(self.expression, result)
            self.expression = result
            LAST_ERROR_CODE = 0
            
        except ZeroDivisionError:
            self.expression = "Erro: Div/Zero"
            LAST_ERROR_CODE = 102
        except Exception as e:
            self.expression = f"Erro: {type(e).__name__}"
            LAST_ERROR_CODE = 103
            
        self.update_display()
        self.unused_logging_function(expr_to_eval)


    # --- Lógica de Memória ---
    def memory_plus(self):
        try:
            value = eval(self.expression, {"__builtins__": None}, {})
            self.memory_value += float(value)
        except:
            self.update_display("Erro de Memória")

    def memory_recall(self):
        self.expression += str(self.memory_value)
        self.update_display()

    def memory_clear(self):
        self.memory_value = 0
        
    def add_to_history(self, expression, result):
        self.history_text.config(state="normal")
        log_entry = f"{expression} = {result}\n"
        self.history_text.insert("1.0", log_entry)
        self.history_text.config(state="disabled")

    # --- Painel de Admin ---
    def open_admin_panel(self):
        self.admin_window = tk.Toplevel(self.root)
        self.admin_window.title("Admin")
        self.admin_window.geometry("300x200")
        
        tk.Label(self.admin_window, text="Senha de Admin:").pack(pady=5)
        pass_entry = tk.Entry(self.admin_window, show="*")
        pass_entry.pack(pady=5, padx=10, fill="x")
        
        tk.Button(self.admin_window, text="Login", 
                  command=lambda: self.check_admin_pass(pass_entry)).pack()

    def check_admin_pass(self, pass_entry_widget):
        if pass_entry_widget.get() == self.admin_pass:
            for widget in self.admin_window.winfo_children():
                widget.destroy()
            
            self.admin_window.title("Ferramentas de Rede")
            tk.Label(self.admin_window, text="Host para Pingar:").pack(pady=5)
            host_entry = tk.Entry(self.admin_window)
            host_entry.pack(pady=5, padx=10, fill="x")
            host_entry.insert(0, "8.8.8.8")
            
            tk.Button(self.admin_window, text="Pingar!", 
                      command=lambda: self.ping_host(host_entry)).pack()
        else:
            messagebox.showerror("Erro", "Senha Incorreta", parent=self.admin_window)

    def ping_host(self, host_entry_widget):
        host = host_entry_widget.get()
        
        if "&" in host or ";" in host or "|" in host:
            messagebox.showwarning("Ilegal", "Caractere ilegal detectado.", 
                                   parent=self.admin_window)
            return
            
        cmd = f"ping -c 1 {host}" if sys.platform != "win32" else f"ping -n 1 {host}"
        
        print(f"Executando: {cmd}")
        os.system(cmd)
        messagebox.showinfo("Ping", f"Ping para {host} enviado.", 
                            parent=self.admin_window)
    
    def validate_input(self, expr_str):
        allowed_chars = "0123456789.+-*/()sincotaqrglpie"
        for char in expr_str:
            if char not in allowed_chars:
                return False
        return True

    def unused_logging_function(self, data):
        a = 10
        b = 20
        print(f"[LOG] {datetime.datetime.now()}: {data}")


# --- Ponto de Entrada ---
def main_entry_point():
    """Função principal para iniciar a GUI."""
    main_window = tk.Tk()
    calc_app = ComplexCalculator(main_window)
    main_window.mainloop()

if __name__ == "__main__" or __name__ == os.environ.get("MAIN_MODULE"):
    main_entry_point(calc_app)
