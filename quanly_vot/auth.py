class Auth:
    def __init__(self, store_nv, store_kh):
        self.store_nv = store_nv
        self.store_kh = store_kh
        self.current = None
        self.loai_tai_khoan = None  # "nhanvien" hoặc "khach"

    def login(self, username, password):
        # Kiểm tra nhân viên
        for nv in self.store_nv.list_all():
            tk = nv.get("tai_khoan")
            if tk and tk.get("TEN_DANG_NHAP") == username and tk.get("MAT_KHAU") == password:
                self.current = nv
                self.loai_tai_khoan = "nhanvien"
                return True
        # Kiểm tra khách hàng
        for kh in self.store_kh.list_all():
            tk = kh.get("tai_khoan")
            if tk and tk.get("TEN_DANG_NHAP") == username and tk.get("MAT_KHAU") == password:
                self.current = kh
                self.loai_tai_khoan = "khach"
                return True
        return False

    def role(self):
        if self.loai_tai_khoan == "nhanvien":
            return self.current["vai_tro"]["TEN_VAI_TRO"]
        elif self.loai_tai_khoan == "khach":
            return "Khách hàng"
        return None

    def can(self, action):
        role = self.role()
        perms = {
            "Quản lý Cửa hàng": {"create","read","update","delete"},
            "Nhân viên Bán hàng": {"create","read"},
            "Nhân viên Kho": {"read","update"},
            "Khách hàng": {"read"}
        }
        return action in perms.get(role, set())
