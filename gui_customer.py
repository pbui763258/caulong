import tkinter as tk
from tkinter import ttk, messagebox

class CustomerApp(tk.Tk):
    def __init__(self, store, auth):
        super().__init__()
        self.title("Quản lý bán vợt cầu lông - Khách hàng")
        self.geometry("980x620")
        self.store = store
        self.auth = auth
        self.selected_product = None
        self._build()
        self._load()

    def _build(self):
        ttk.Label(self, text="🛒 Danh sách sản phẩm", font=("Segoe UI", 16, "bold")).pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("MA_VOT","TEN_VOT","GIA_BAN"), show="headings", height=15)
        self.tree.heading("MA_VOT", text="Mã vợt")
        self.tree.heading("TEN_VOT", text="Tên vợt")
        self.tree.heading("GIA_BAN", text="Giá bán (VNĐ)")
        self.tree.column("MA_VOT", width=120, anchor="center")
        self.tree.column("TEN_VOT", width=560, anchor="w")
        self.tree.column("GIA_BAN", width=180, anchor="e")
        self.tree.pack(padx=20, pady=10, fill="x")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        info = ttk.LabelFrame(self, text="Thông tin sản phẩm đã chọn", padding=10)
        info.pack(padx=20, pady=10, fill="x")
        self.lbl_ma = ttk.Label(info, text="Mã vợt: -", font=("Segoe UI", 11)); self.lbl_ma.grid(row=0, column=0, sticky="w", pady=4)
        self.lbl_ten = ttk.Label(info, text="Tên vợt: -", font=("Segoe UI", 11)); self.lbl_ten.grid(row=1, column=0, sticky="w", pady=4)
        self.lbl_gia = ttk.Label(info, text="Giá bán: -", font=("Segoe UI", 11)); self.lbl_gia.grid(row=2, column=0, sticky="w", pady=4)

        self.btn_buy = ttk.Button(self, text="🛍️ Mua vợt này", command=self._buy, width=20)
        self.btn_buy.pack(pady=10)

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        for sp in self.store.list_all():
            self.tree.insert("", "end", iid=sp["MA_VOT"], values=(sp["MA_VOT"], sp["TEN_VOT"], f"{sp['GIA_BAN']:,}"))

    def _on_select(self, _):
        sel = self.tree.selection()
        if not sel: return
        ma = sel[0]
        for sp in self.store.list_all():
            if sp["MA_VOT"] == ma:
                self.selected_product = sp
                self.lbl_ma.config(text=f"Mã vợt: {sp['MA_VOT']}")
                self.lbl_ten.config(text=f"Tên vợt: {sp['TEN_VOT']}")
                self.lbl_gia.config(text=f"Giá bán: {sp['GIA_BAN']:,} VNĐ")
                break

    def _buy(self):
        if not self.selected_product:
            return messagebox.showwarning("Chưa chọn", "Vui lòng chọn một sản phẩm để mua.")
        ten = self.selected_product["TEN_VOT"]
        gia = self.selected_product["GIA_BAN"]
        messagebox.showinfo("Đặt mua", f"Bạn đã chọn mua vợt:\n{ten}\nGiá: {gia:,} VNĐ\nCảm ơn bạn!")


