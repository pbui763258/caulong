import tkinter as tk
from tkinter import ttk, messagebox
import json, os
from datetime import datetime
from gui_invoice import InvoiceWindow   # import giao diện hóa đơn riêng

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

        # Bảng sản phẩm
        self.tree = ttk.Treeview(self, columns=("MA_VOT","TEN_VOT","GIA_BAN"), show="headings", height=9)
        self.tree.heading("MA_VOT", text="Mã vợt")
        self.tree.heading("TEN_VOT", text="Tên vợt")
        self.tree.heading("GIA_BAN", text="Giá bán (VNĐ)")
        self.tree.column("MA_VOT", width=120, anchor="center")
        self.tree.column("TEN_VOT", width=560, anchor="w")
        self.tree.column("GIA_BAN", width=180, anchor="e")
        self.tree.pack(padx=20, pady=10, fill="x")
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Khung thông tin sản phẩm
        info = ttk.LabelFrame(self, text="Thông tin sản phẩm đã chọn", padding=10)
        info.pack(padx=20, pady=10, fill="x")
        self.lbl_ma = ttk.Label(info, text="Mã vợt: -", font=("Segoe UI", 11)); self.lbl_ma.grid(row=0, column=0, sticky="w", pady=4)
        self.lbl_ten = ttk.Label(info, text="Tên vợt: -", font=("Segoe UI", 11)); self.lbl_ten.grid(row=1, column=0, sticky="w", pady=4)
        self.lbl_gia = ttk.Label(info, text="Giá bán: -", font=("Segoe UI", 11)); self.lbl_gia.grid(row=2, column=0, sticky="w", pady=4)
        self.lbl_kt = ttk.Label(info, text="Kỹ thuật: -", font=("Segoe UI", 11)); self.lbl_kt.grid(row=3, column=0, sticky="w", pady=4)
        self.lbl_hang = ttk.Label(info, text="Hãng: -", font=("Segoe UI", 11)); self.lbl_hang.grid(row=4, column=0, sticky="w", pady=4)
        self.lbl_ton = ttk.Label(info, text="Tồn kho: -", font=("Segoe UI", 11)); self.lbl_ton.grid(row=5, column=0, sticky="w", pady=4)

        # Nút mua và nút xem hóa đơn
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="🛍️ Mua vợt này", command=self._buy, width=20).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="📄 Xem hóa đơn", command=self._open_invoice_window, width=20).pack(side="left", padx=10)

    def _load(self):
        self.tree.delete(*self.tree.get_children())
        for sp in self.store.list_all():
            self.tree.insert("", "end", values=(sp["MA_VOT"], sp["TEN_VOT"], f"{sp['GIA_BAN']:,}"))

    def _on_select(self, _):
        sel = self.tree.selection()
        if not sel: return
        values = self.tree.item(sel[0])["values"]
        ma = values[0]
        for sp in self.store.list_all():
            if sp["MA_VOT"] == ma:
                self.selected_product = sp
                self.lbl_ma.config(text=f"Mã vợt: {sp['MA_VOT']}")
                self.lbl_ten.config(text=f"Tên vợt: {sp['TEN_VOT']}")
                self.lbl_gia.config(text=f"Giá bán: {sp['GIA_BAN']:,} VNĐ")
                self.lbl_kt.config(text=f"Kỹ thuật: {sp.get('MO_TA_KT', '-')}")
                self.lbl_hang.config(text=f"Hãng: {sp.get('hang_san_xuat', {}).get('TEN_HANG', '-')}")
                self.lbl_ton.config(text=f"Tồn kho: {sp.get('ton_kho', {}).get('SO_LUONG_TON', '-')}")
                break

    def _buy(self):
        if not self.selected_product:
            return messagebox.showwarning("Chưa chọn", "Vui lòng chọn một sản phẩm để mua.")
        
        dh_file = "data/donhang.json"
        if not os.path.exists(dh_file):
            with open(dh_file, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)

        with open(dh_file, "r", encoding="utf-8") as f:
            don_hang = json.load(f)

        ma_dh = f"DH{len(don_hang)+1:03}"
        ngay_dat = datetime.now().strftime("%Y-%m-%d")
        phi_vc = 20000
        gia = self.selected_product["GIA_BAN"]
        tong = gia + phi_vc

        kh = self.auth.current
        thong_tin_kh = {
            "MA_KH": kh.get("MA_KH", "KH000"),
            "HO_TEN": kh.get("HO_TEN", "Khách chưa rõ"),
            "SDT": kh.get("SDT", "Chưa có")
        }

        dh = {
            "MA_DH": ma_dh,
            "NGAY_DAT": ngay_dat,
            "TONG_TIEN": tong,
            "TRANG_THAI_DH": "Đang giao",
            "PHI_VAN_CHUYEN": phi_vc,
            "khach_hang": thong_tin_kh,
            "nhan_vien_ban": {},
            "san_pham_dat": [{
                "MA_VOT": self.selected_product["MA_VOT"],
                "TEN_VOT": self.selected_product["TEN_VOT"],
                "SO_LUONG": 1,
                "DON_GIA_BAN": gia,
                "THANH_TIEN": gia
            }]
        }

        don_hang.append(dh)
        with open(dh_file, "w", encoding="utf-8") as f:
            json.dump(don_hang, f, ensure_ascii=False, indent=2)

        messagebox.showinfo("Đặt mua",
            f"Bạn đã đặt mua vợt:\n{self.selected_product['TEN_VOT']}\nGiá: {gia:,} VNĐ\nMã đơn hàng: {ma_dh}\nĐã lưu vào hóa đơn.")

    def _open_invoice_window(self):
        win = InvoiceWindow(self.auth, mode="customer")
        win.grab_set()