import tkinter as tk
from tkinter import ttk, messagebox

class AdminApp(tk.Tk):
    def __init__(self, store, auth):
        super().__init__()
        self.title("Quản lý bán vợt cầu lông - Nhân viên/Quản lý (Modern)")
        self.geometry("980x620")
        self.configure(bg="#1e1e1e")  # nền tối
        self.store = store
        self.auth = auth

        # Style hiện đại cho ttk
        style = ttk.Style(self)
        style.theme_use('default')

        # Treeview style (nền tối)
        style.configure("Treeview",
                        background="#2b2b2b",
                        foreground="white",
                        fieldbackground="#2b2b2b",
                        rowheight=28,
                        borderwidth=0)
        style.configure("Treeview.Heading",
                        background="#333",
                        foreground="white",
                        font=("Segoe UI", 11, "bold"),
                        borderwidth=0)
        style.map("Treeview.Heading",
                  background=[('active', '#3a3a3a')])

        # Button style
        style.configure("Accent.TButton",
                        foreground="white",
                        background="#ff6600",
                        font=("Segoe UI", 11, "bold"),
                        borderwidth=0)
        style.map("Accent.TButton",
                  background=[('active', '#ff7a1a')])

        # Các frame chính dùng tk.Frame để dễ set background
        container = tk.Frame(self, bg="#1e1e1e")
        container.pack(fill="both", expand=True)

        header = tk.Frame(container, bg="#1e1e1e")
        header.pack(fill="x", pady=(10, 0))
        tk.Label(header, text="📋 Danh sách sản phẩm",
                 bg="#1e1e1e", fg="white", font=("Segoe UI", 16, "bold")).pack(pady=10)

        # Bảng sản phẩm
        tree_frame = tk.Frame(container, bg="#1e1e1e")
        tree_frame.pack(fill="x", padx=20)
        self.tree = ttk.Treeview(tree_frame, columns=("MA_VOT","TEN_VOT","GIA_BAN"),
                                 show="headings", height=15, style="Treeview")
        self.tree.heading("MA_VOT", text="Mã vợt")
        self.tree.heading("TEN_VOT", text="Tên vợt")
        self.tree.heading("GIA_BAN", text="Giá bán (VNĐ)")
        self.tree.column("MA_VOT", width=120, anchor="center")
        self.tree.column("TEN_VOT", width=560, anchor="w")
        self.tree.column("GIA_BAN", width=180, anchor="e")
        self.tree.pack(padx=0, pady=10, fill="x")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Khung nhập liệu: dùng tk.LabelFrame với nền tối và border nhỏ
        frm = tk.LabelFrame(container, text="Thông tin vợt", bg="#1e1e1e",
                            fg="white", bd=0, font=("Segoe UI", 10))
        frm.pack(padx=20, pady=10, fill="x")

        # Dùng tk.Label để dễ set màu nền/foreground
        tk.Label(frm, text="Mã vợt:", width=15, bg="#1e1e1e", fg="white", anchor="w").grid(row=0, column=0, sticky="w", padx=4, pady=6)
        self.ent_ma = ttk.Entry(frm, width=30); self.ent_ma.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(frm, text="Tên vợt:", width=15, bg="#1e1e1e", fg="white", anchor="w").grid(row=1, column=0, sticky="w", padx=4, pady=6)
        self.ent_ten = ttk.Entry(frm, width=60); self.ent_ten.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(frm, text="Giá bán:", width=15, bg="#1e1e1e", fg="white", anchor="w").grid(row=2, column=0, sticky="w", padx=4, pady=6)
        self.ent_gia = ttk.Entry(frm, width=20); self.ent_gia.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Nút chức năng: đặt vào frame có cùng nền
        btns = tk.Frame(container, bg="#1e1e1e")
        btns.pack(pady=10)
        if self.auth.can("create"):
            ttk.Button(btns, text="➕ Thêm", width=15, command=self._add, style="Accent.TButton").pack(side="left", padx=10)
        if self.auth.can("update"):
            ttk.Button(btns, text="✏️ Sửa", width=15, command=self._update, style="Accent.TButton").pack(side="left", padx=10)
        if self.auth.can("delete"):
            ttk.Button(btns, text="🗑️ Xóa", width=15, command=self._delete, style="Accent.TButton").pack(side="left", padx=10)

        # Loại bỏ viền mặc định của một số widget (nếu cần)
        self.configure(highlightthickness=0)

        self._load()

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        for sp in self.store.list_all():
            self.tree.insert("", "end", values=(sp["MA_VOT"], sp["TEN_VOT"], f"{sp['GIA_BAN']:,}"))

    def _on_select(self, _):
        sel = self.tree.selection()
        if not sel: return
        values = self.tree.item(sel[0])["values"]
        if not values: return
        self.ent_ma.delete(0, tk.END); self.ent_ma.insert(0, values[0])
        self.ent_ten.delete(0, tk.END); self.ent_ten.insert(0, values[1])
        self.ent_gia.delete(0, tk.END); self.ent_gia.insert(0, str(values[2]).replace(",", ""))

    def _add(self):
        if not self.auth.can("create"):
            return messagebox.showwarning("Quyền", "Bạn không có quyền thêm.")
        ma = self.ent_ma.get().strip()
        ten = self.ent_ten.get().strip()
        gia_text = self.ent_gia.get().strip()
        if not ma or not ten or not gia_text:
            return messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập đầy đủ Mã vợt, Tên vợt và Giá bán.")
        if not gia_text.isdigit():
            return messagebox.showerror("Sai dữ liệu", "Giá bán phải là số nguyên.")
        sp = {"MA_VOT": ma, "TEN_VOT": ten, "GIA_BAN": int(gia_text)}
        self.store.create(sp)
        self._load()

    def _update(self):
        if not self.auth.can("update"):
            return messagebox.showwarning("Quyền", "Bạn không có quyền sửa.")
        sel = self.tree.selection()
        if not sel: return
        ma = self.tree.item(sel[0])["values"][0]
        ten = self.ent_ten.get().strip()
        gia_text = self.ent_gia.get().strip()
        if not gia_text.isdigit():
            return messagebox.showerror("Sai dữ liệu", "Giá bán phải là số nguyên.")
        fields = {"TEN_VOT": ten, "GIA_BAN": int(gia_text)}
        self.store.update("MA_VOT", ma, fields)
        self._load()

    def _delete(self):
        if not self.auth.can("delete"):
            return messagebox.showwarning("Quyền", "Bạn không có quyền xóa.")
        sel = self.tree.selection()
        if not sel: return
        ma = self.tree.item(sel[0])["values"][0]
        self.store.delete("MA_VOT", ma)
        self._load()
