import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from store import JsonStore
from auth import Auth
from gui_admin import AdminApp
from gui_customer import CustomerApp

class LoginWindow(tk.Tk):
    def __init__(self, store_nv, store_sp, store_kh):
        super().__init__()
        self.title("Hệ thống quản lý bán vợt cầu lông")
        self.geometry("420x380")
        self.configure(bg="#f0f2f5")
        self.store_nv = store_nv
        self.store_sp = store_sp
        self.store_kh = store_kh
        self.auth = Auth(store_nv, store_kh)
        self._build()

    def _build(self):
        # Frame tổng
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True)

        # Logo + tiêu đề
        top = ttk.Frame(main_frame)
        top.grid(row=0, column=0, pady=(15, 5))

        try:
            img = Image.open("1.png").resize((100, 100))
            self.logo = ImageTk.PhotoImage(img)
            ttk.Label(top, image=self.logo).grid(row=0, column=0, pady=5)
        except:
            ttk.Label(top, text="[Logo không tìm thấy]", font=("Segoe UI", 10, "italic")).grid(row=0, column=0, pady=5)

        ttk.Label(top, text="DT CREATIVE HOUSE", font=("Segoe UI", 12, "bold")).grid(row=1, column=0, pady=2)
        ttk.Label(top, text="Đăng nhập hệ thống", font=("Segoe UI", 14)).grid(row=2, column=0, pady=5)

        # Khung đăng nhập
        frm = ttk.LabelFrame(main_frame, text="Thông tin đăng nhập", padding=20)
        frm.grid(row=1, column=0, padx=20, pady=15)

        ttk.Label(frm, text="Tên đăng nhập:").grid(row=0, column=0, sticky="w", pady=5)
        self.ent_user = ttk.Entry(frm, width=30)
        self.ent_user.grid(row=0, column=1, pady=5)

        ttk.Label(frm, text="Mật khẩu:").grid(row=1, column=0, sticky="w", pady=5)
        self.ent_pass = ttk.Entry(frm, show="*", width=30)
        self.ent_pass.grid(row=1, column=1, pady=5)

        ttk.Button(frm, text="Đăng nhập", command=self.on_login).grid(row=2, column=0, columnspan=2, pady=15)

    def on_login(self):
        username = self.ent_user.get().strip()
        password = self.ent_pass.get().strip()
        if not username or not password:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.")
            return

        if self.auth.login(username, password):
            role = self.auth.role()
            name = self.auth.current.get("HO_TEN", username)
            messagebox.showinfo("Thành công", f"Xin chào {name} ({role})")
            self.destroy()
            if self.auth.loai_tai_khoan == "nhanvien":
                app = AdminApp(self.store_sp, self.auth)
            else:
                app = CustomerApp(self.store_sp, self.auth)
            app.mainloop()
        else:
            messagebox.showerror("Lỗi", "Sai tên đăng nhập hoặc mật khẩu")

def main():
    store_sp = JsonStore("data/sanpham.json")
    store_nv = JsonStore("data/nhanvien.json")
    store_kh = JsonStore("data/khachhang.json")
    login = LoginWindow(store_nv, store_sp, store_kh)
    login.mainloop()

if __name__ == "__main__":
    main()