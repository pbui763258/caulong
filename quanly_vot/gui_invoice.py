import tkinter as tk
from tkinter import ttk, messagebox
import json, os

class InvoiceWindow(tk.Toplevel):
    def __init__(self, auth, mode="customer"):
        super().__init__()
        self.title("📄 Quản lý hóa đơn")
        self.geometry("900x600")
        self.auth = auth
        self.mode = mode  # "customer" hoặc "admin"
        self._build()
        self._load_orders()

    def _build(self):
        # Tiêu đề
        ttk.Label(self, text="📦 Danh sách hóa đơn", font=("Segoe UI", 16, "bold")).pack(pady=10)

        # Bộ lọc trạng thái
        filter_frame = ttk.Frame(self)
        filter_frame.pack(padx=20, pady=5, fill="x")
        ttk.Label(filter_frame, text="Lọc theo trạng thái:").pack(side="left")
        self.cbo_filter = ttk.Combobox(filter_frame,
                                       values=["Tất cả", "Đang giao", "Đã giao", "Đã hủy"],
                                       state="readonly", width=20)
        self.cbo_filter.current(0)
        self.cbo_filter.pack(side="left", padx=10)
        self.cbo_filter.bind("<<ComboboxSelected>>", self._filter_orders)

        # Bảng hóa đơn + scrollbar
        frame = ttk.Frame(self)
        frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.tree = ttk.Treeview(frame,
                                 columns=("MA_DH", "NGAY_DAT", "TONG_TIEN", "TRANG_THAI_DH"),
                                 show="headings", height=9)
        self.tree.heading("MA_DH", text="Mã đơn")
        self.tree.heading("NGAY_DAT", text="Ngày đặt")
        self.tree.heading("TONG_TIEN", text="Tổng tiền (VNĐ)")
        self.tree.heading("TRANG_THAI_DH", text="Trạng thái")
        self.tree.column("MA_DH", width=100, anchor="center")
        self.tree.column("NGAY_DAT", width=120, anchor="center")
        self.tree.column("TONG_TIEN", width=160, anchor="e")
        self.tree.column("TRANG_THAI_DH", width=180, anchor="center")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Khung chi tiết
        self.detail = ttk.LabelFrame(self, text="Chi tiết hóa đơn", padding=10)
        self.detail.pack(padx=20, pady=10, fill="x")
        self.lbl_info = ttk.Label(self.detail, text="Chọn hóa đơn để xem chi tiết", font=("Segoe UI", 11))
        self.lbl_info.pack(anchor="w")

        # Nút chức năng
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="🗑️ Hủy đơn", command=self._cancel_order, width=15).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="💾 Xuất hóa đơn", command=self._export_invoice, width=15).pack(side="left", padx=10)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _load_orders(self):
        self.tree.delete(*self.tree.get_children())
        try:
            with open("data/donhang.json", "r", encoding="utf-8") as f:
                don_hang = json.load(f)
        except:
            don_hang = []

        for dh in don_hang:
            if self.mode == "customer":
                ma_kh = self.auth.current.get("MA_KH", "")
                if dh.get("khach_hang", {}).get("MA_KH") != ma_kh:
                    continue
            self.tree.insert("", "end", iid=dh["MA_DH"],
                             values=(dh["MA_DH"], dh["NGAY_DAT"], f"{dh['TONG_TIEN']:,}", dh["TRANG_THAI_DH"]))

    def _filter_orders(self, _):
        selected = self.cbo_filter.get()
        self.tree.delete(*self.tree.get_children())
        try:
            with open("data/donhang.json", "r", encoding="utf-8") as f:
                don_hang = json.load(f)
        except:
            don_hang = []

        for dh in don_hang:
            if self.mode == "customer":
                ma_kh = self.auth.current.get("MA_KH", "")
                if dh.get("khach_hang", {}).get("MA_KH") != ma_kh:
                    continue
            if selected != "Tất cả" and dh["TRANG_THAI_DH"] != selected:
                continue
            self.tree.insert("", "end", iid=dh["MA_DH"],
                             values=(dh["MA_DH"], dh["NGAY_DAT"], f"{dh['TONG_TIEN']:,}", dh["TRANG_THAI_DH"]))

    def _on_select(self, _):
        sel = self.tree.selection()
        if not sel: return
        ma_dh = sel[0]
        try:
            with open("data/donhang.json", "r", encoding="utf-8") as f:
                don_hang = json.load(f)
            for dh in don_hang:
                if dh["MA_DH"] == ma_dh:
                    text = f"Đơn hàng {ma_dh} ({dh['NGAY_DAT']})\n"
                    text += f"Tổng tiền: {dh['TONG_TIEN']:,} VNĐ\n"
                    text += f"Trạng thái: {dh['TRANG_THAI_DH']}\n"
                    text += f"Phí vận chuyển: {dh['PHI_VAN_CHUYEN']:,} VNĐ\n"
                    text += "Sản phẩm:\n"
                    for sp in dh.get("san_pham_dat", []):
                        text += f"- {sp['TEN_VOT']} x{sp['SO_LUONG']} = {sp['THANH_TIEN']:,} VNĐ\n"
                    self.lbl_info.config(text=text)
                    break
        except:
            self.lbl_info.config(text="Không thể đọc chi tiết hóa đơn.")

    def _cancel_order(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Chưa chọn", "Vui lòng chọn một hóa đơn để hủy.")
        ma_dh = sel[0]
        try:
            with open("data/donhang.json", "r", encoding="utf-8") as f:
                don_hang = json.load(f)
            for dh in don_hang:
                if dh["MA_DH"] == ma_dh:
                    if dh["TRANG_THAI_DH"] == "Đã hủy":
                        return messagebox.showinfo("Thông báo", "Đơn hàng này đã bị hủy trước đó.")
                    dh["TRANG_THAI_DH"] = "Đã hủy"
                    break
            with open("data/donhang.json", "w", encoding="utf-8") as f:
                json.dump(don_hang, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Thành công", f"Đơn hàng {ma_dh} đã được hủy.")
            self._filter_orders(None)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể hủy đơn hàng: {e}")

    def _export_invoice(self):
        sel = self.tree.selection()
        if not sel:
            return messagebox.showwarning("Chưa chọn", "Vui lòng chọn một hóa đơn để xuất.")
        ma_dh = sel[0]
        try:
            with open("data/donhang.json", "r", encoding="utf-8") as f:
                don_hang = json.load(f)
            for dh in don_hang:
                if dh["MA_DH"] == ma_dh:
                    filename = f"data/hoadon_{ma_dh}.json"
                    with open(filename, "w", encoding="utf-8") as f_out:
                        json.dump(dh, f_out, ensure_ascii=False, indent=2)
                    messagebox.showinfo("Xuất hóa đơn", f"Hóa đơn {ma_dh} đã được lưu vào file:\n{filename}")
                    break
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất hóa đơn: {e}")