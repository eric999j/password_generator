"""
GUI 應用程式主模組
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as ttb
from datetime import datetime

from src.config import Config
from src.database import PasswordRepository
from src.services import PasswordGenerator
from src.crypto.secure_string import SecureString


class PasswordGeneratorApp:
    """應用程式主類"""
    
    def __init__(self, root):
        self.root = root
        self.root.title(Config.APP_NAME)
        self.root.geometry(Config.WINDOW_SIZE)
        
        self.repo = PasswordRepository()
        self._build_ui()
    
    def _build_ui(self):
        """建立 UI"""
        # 標題與工具列
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(header_frame, text='🔐 強密碼產生器', font=('Arial', 16, 'bold')).pack(side='left', padx=(40, 0), expand=True)
        
        # 主題切換按鈕
        current_theme = Config.get_theme()
        self.theme_btn = ttb.Button(header_frame, text='', command=self._toggle_theme, bootstyle='link')
        self._update_theme_button(current_theme)
        self.theme_btn.pack(side='right')
        
        # 選項卡
        self.notebook = ttb.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 生成頁籤
        self.gen_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.gen_tab, text='生成密碼')
        self._build_generate_tab()
        
        # 管理頁籤
        self.manage_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.manage_tab, text='密碼管理')
        self._build_manage_tab()
    
    def _build_generate_tab(self):
        """生成密碼頁籤"""
        # 強度選擇
        frame1 = ttk.LabelFrame(self.gen_tab, text='密碼強度等級', padding=10)
        frame1.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(frame1, text='選擇強度:').pack(side='left', padx=5)
        self.strength_var = tk.StringVar(value='中')
        ttb.Combobox(frame1, textvariable=self.strength_var,
                     values=['低 (8字元)', '中 (10字元)', '高 (12字元)'],
                     state='readonly', width=20).pack(side='left', padx=5)
        
        # 生成按鈕
        ttb.Button(self.gen_tab, text='生成密碼', command=self._on_generate,
                   bootstyle='primary').pack(pady=10)
        
        # 密碼顯示
        frame2 = ttk.LabelFrame(self.gen_tab, text='生成的密碼', padding=10)
        frame2.pack(fill='x', padx=10, pady=10)
        
        btn_frame = ttk.Frame(frame2)
        btn_frame.pack(side='right', padx=(5, 0))
        ttb.Button(btn_frame, text='複製', command=self._on_copy,
                   bootstyle='secondary', width=6).pack(side='left', padx=2)
        ttb.Button(btn_frame, text='評估', command=self._on_evaluate,
                   bootstyle='info', width=6).pack(side='left', padx=2)
        
        self.password_text = tk.Text(frame2, height=2, width=20, font=('Courier', 11))
        self.password_text.pack(side='left', fill='both', expand=True)
        
        # 強度評估
        frame3 = ttk.LabelFrame(self.gen_tab, text='強度評估', padding=10)
        frame3.pack(fill='x', padx=10, pady=10)
        
        self.strength_bar = ttb.Progressbar(frame3, length=300, mode='determinate',
                                            value=0, bootstyle='danger')
        self.strength_bar.pack(fill='x', padx=5, pady=5)
        self.strength_label = ttk.Label(frame3, text='強度: ---', font=('Arial', 10))
        self.strength_label.pack(padx=5)
        
        # 儲存區域
        frame4 = ttk.LabelFrame(self.gen_tab, text='儲存密碼', padding=10)
        frame4.pack(fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(frame4, text='使用該密碼的服務名稱:').pack(anchor='w', pady=(0, 5))
        self.service_entry = ttk.Entry(frame4, width=40)
        self.service_entry.pack(fill='x', pady=(0, 10))
        
        ttk.Label(frame4, text='用戶名:').pack(anchor='w', pady=(0, 5))
        self.username_entry = ttk.Entry(frame4, width=40)
        self.username_entry.pack(fill='x', pady=(0, 10))
        
        ttb.Button(frame4, text='儲存密碼', command=self._on_save,
                   bootstyle='success').pack(fill='x')
    
    def _build_manage_tab(self):
        """密碼管理頁籤"""
        # 按鈕列
        btn_frame = ttk.Frame(self.manage_tab)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        ttb.Button(btn_frame, text='刷新', command=self._refresh_list,
                   bootstyle='primary').pack(side='left', padx=5)
        ttb.Button(btn_frame, text='導出為 CSV', command=self._on_export,
                   bootstyle='success').pack(side='left', padx=5)
        
        # 列表
        tree_frame = ttk.Frame(self.manage_tab)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        cols = ('服務名稱', '用戶名', '最後修改日期')
        self.tree = ttb.Treeview(tree_frame, columns=cols, height=15, show='headings')
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        scrollbar = ttb.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 操作按鈕
        action_frame = ttk.Frame(self.manage_tab)
        action_frame.pack(fill='x', padx=10, pady=10)
        
        ttb.Button(action_frame, text='查看', command=self._on_view,
                   bootstyle='info').pack(side='left', padx=5)
        ttb.Button(action_frame, text='編輯', command=self._on_edit,
                   bootstyle='warning').pack(side='left', padx=5)
        ttb.Button(action_frame, text='刪除', command=self._on_delete,
                   bootstyle='danger').pack(side='left', padx=5)
        
        self._refresh_list()
    
    # === 事件處理 ===
    
    def _on_generate(self):
        level = self.strength_var.get().split()[0]
        password = PasswordGenerator.generate(level)
        self.password_text.delete('1.0', 'end')
        self.password_text.insert('1.0', password)
        self._update_strength(password)
    
    def _on_evaluate(self):
        password = self.password_text.get('1.0', 'end-1c').strip()
        self._update_strength(password)
    
    def _update_strength(self, password: str):
        score, color, level = PasswordGenerator.evaluate(password)
        self.strength_bar['value'] = score
        self.strength_bar.configure(bootstyle='danger' if score <= 33 else ('warning' if score <= 66 else 'success'))
        self.strength_label.config(text=f'強度: {level} ({score}/100)')
    
    def _on_copy(self):
        password = self.password_text.get('1.0', 'end-1c')
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            self.root.update()
            messagebox.showinfo('成功', '密碼已複製到剪貼板')
    
    def _on_save(self):
        service = self.service_entry.get().strip()
        username = self.username_entry.get().strip()
        raw_password = self.password_text.get('1.0', 'end-1c').strip()
        
        if not service or not username or not raw_password:
            messagebox.showwarning('警告', '請填寫所有欄位')
            return
        
        # 使用 SecureString 處理密碼
        with SecureString(raw_password) as sec_pwd:
            if self.repo.add(service, username, sec_pwd.get_value()):
                messagebox.showinfo('成功', f'密碼已儲存: {service}')
                self.service_entry.delete(0, 'end')
                self.username_entry.delete(0, 'end')
                self.password_text.delete('1.0', 'end')
            else:
                messagebox.showerror('錯誤', f'服務 "{service}" 已存在')
    
    def _refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for pwd in self.repo.get_all():
            self.tree.insert('', 'end', iid=pwd['id'],
                             values=(pwd['service'], pwd['username'], pwd['updated_at']))
    
    def _get_selected_service(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning('警告', '請選擇一條記錄')
            return None
        return self.tree.item(selected[0], 'values')[0]
    
    def _on_view(self):
        service = self._get_selected_service()
        if not service:
            return
        
        info = self.repo.get(service)
        if info:
            win = tk.Toplevel(self.root)
            win.title(f'查看密碼 - {service}')
            win.geometry('400x220')
            
            for label, value in [('服務名稱:', info['service']),
                                  ('用戶名:', info['username'])]:
                ttk.Label(win, text=label, font=('Arial', 10, 'bold')).pack(anchor='w', padx=10, pady=(10, 0))
                ttk.Label(win, text=value, font=('Courier', 10)).pack(anchor='w', padx=20)
            
            ttk.Label(win, text='密碼:', font=('Arial', 10, 'bold')).pack(anchor='w', padx=10, pady=(10, 0))
            pwd_text = tk.Text(win, height=2, width=40, font=('Courier', 10))
            pwd_text.insert('1.0', info['password'])
            pwd_text.config(state='disabled')
            pwd_text.pack(padx=10, pady=5)
            
            def copy():
                self.root.clipboard_clear()
                self.root.clipboard_append(info['password'])
                self.root.update()
                messagebox.showinfo('成功', '密碼已複製')
            
            ttb.Button(win, text='複製密碼', command=copy, bootstyle='primary').pack(pady=10)
    
    def _on_edit(self):
        service = self._get_selected_service()
        if not service:
            return
        
        info = self.repo.get(service)
        if info:
            win = tk.Toplevel(self.root)
            win.title(f'編輯密碼 - {service}')
            win.geometry('400x280')
            
            ttk.Label(win, text='用戶名:').pack(anchor='w', padx=10, pady=(10, 0))
            username_entry = ttk.Entry(win, width=40)
            username_entry.insert(0, info['username'])
            username_entry.pack(fill='x', padx=10, pady=(0, 10))
            
            ttk.Label(win, text='密碼:').pack(anchor='w', padx=10, pady=(10, 0))
            pwd_text = tk.Text(win, height=3, width=40, font=('Courier', 10))
            pwd_text.insert('1.0', info['password'])
            pwd_text.pack(fill='x', padx=10, pady=(0, 10))
            
            def save():
                new_user = username_entry.get().strip()
                new_pwd = pwd_text.get('1.0', 'end-1c').strip()
                if new_user and new_pwd:
                    if self.repo.update(service, new_user, new_pwd):
                        messagebox.showinfo('成功', '密碼已更新')
                        win.destroy()
                        self._refresh_list()
            
            ttb.Button(win, text='保存', command=save, bootstyle='success').pack(fill='x', padx=10, pady=10)
    
    def _on_delete(self):
        service = self._get_selected_service()
        if not service:
            return
        
        if messagebox.askyesno('確認刪除', f'確定要刪除 "{service}" 的密碼嗎？'):
            if self.repo.delete(service):
                messagebox.showinfo('成功', '密碼已刪除')
                self._refresh_list()
    
    def _on_export(self):
        path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[('CSV 檔案', '*.csv')],
            initialfile=f'passwords_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
        if path:
            if self.repo.export_csv(path):
                messagebox.showinfo('成功', f'密碼已導出到:\n{path}')

    def _toggle_theme(self):
        """切換深色/淺色模式"""
        try:
            # 獲取當前主題名稱 - 確保從 style 獲取準確狀態
            current_theme = self.root.style.theme.name
            
            # 在 darkly (深色) 和 flatly (淺色) 之間切換
            # 如果當前是 darkly，則切換為 flatly；否則切換為 darkly
            new_theme = 'flatly' if current_theme == 'darkly' else 'darkly'
            
            print(f"Theme toggle: {current_theme} -> {new_theme}")
            
            # 應用新主題
            self.root.style.theme_use(new_theme)
            
            # 儲存設定
            Config.save_theme(new_theme)
            
            # 更新按鈕文字
            self._update_theme_button(new_theme)
            
        except Exception as e:
            print(f"Theme toggle error: {e}")
            messagebox.showerror('錯誤', f'切換主題失敗: {str(e)}')

    def _update_theme_button(self, theme_name):
        """更新主題切換按鈕的文字"""
        # 若當前是深色，顯示太陽(提示切換到淺色)
        theme_text = '切換模式 ☀️' if theme_name == 'darkly' else '切換模式 🌙'
        self.theme_btn.configure(text=theme_text)

def run_app():
    """運行應用程式"""
    # 讀取儲存的主題，默認為 darkly
    theme = Config.get_theme()
    print(f"Starting app with theme: {theme}")
    
    root = ttb.Window(themename=theme)
    
    # 雙重確認主題是否正確應用
    try:
        current = root.style.theme.name
        if current != theme:
            print(f"Theme mismatch detected! Expected {theme}, got {current}. Enforcing...")
            root.style.theme_use(theme)
    except Exception as e:
        print(f"Theme validation error: {e}")
            
    try:
        PasswordGeneratorApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("程式啟動錯誤", f"初始化失敗：\n{str(e)}")
        root.destroy()
