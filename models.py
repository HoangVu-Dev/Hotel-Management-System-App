import datetime

class LoaiPhongConfig:
    def __init__(self, ma_loai, ten_loai, gia_co_ban, phi_don_dep=0, phi_minibar=0):
        self.ma_loai = ma_loai
        self.ten_loai = ten_loai
        self.gia_co_ban = int(gia_co_ban)
        self.phi_don_dep = int(phi_don_dep)
        self.phi_minibar = int(phi_minibar)

    def to_dict(self):
        return {
            "ma_loai": self.ma_loai,
            "ten_loai": self.ten_loai,
            "gia_co_ban": self.gia_co_ban,
            "phi_don_dep": self.phi_don_dep,
            "phi_minibar": self.phi_minibar
        }


class DichVu:
    def __init__(self, ma_dv, ten_dv, gia_dv):
        self.ma_dv = ma_dv
        self.ten_dv = ten_dv
        self.gia_dv = int(gia_dv)

    def to_dict(self):
        return {"ma_dv": self.ma_dv, "ten_dv": self.ten_dv, "gia_dv": self.gia_dv}


class SuDungDichVu:
    def __init__(self, cccd, ten_khach, ma_phong, ma_dv, ten_dv, gia_dv, so_luong, ngay_su_dung=None, da_thanh_toan=False):
        self.cccd = cccd
        self.ten_khach = ten_khach
        self.ma_phong = ma_phong
        self.ma_dv = ma_dv
        self.ten_dv = ten_dv
        self.gia_dv = int(gia_dv)
        self.so_luong = int(so_luong)
        self.ngay_su_dung = ngay_su_dung or datetime.date.today().strftime("%Y-%m-%d")
        self.da_thanh_toan = da_thanh_toan

    def tinh_thanh_tien(self):
        return self.gia_dv * self.so_luong

    def to_dict(self):
        return {
            "cccd": self.cccd,
            "ten_khach": self.ten_khach,
            "ma_phong": self.ma_phong,
            "ma_dv": self.ma_dv,
            "ten_dv": self.ten_dv,
            "gia_dv": self.gia_dv,
            "so_luong": self.so_luong,
            "ngay_su_dung": self.ngay_su_dung,
            "da_thanh_toan": self.da_thanh_toan
        }


class Phong:
    def __init__(self, ma_phong, ten_phong, ma_loai, gia_co_ban, phi_don_dep=0, phi_minibar=0, trang_thai="Trống"):
        self.ma_phong = ma_phong
        self.ten_phong = ten_phong
        self.ma_loai = ma_loai
        self.gia_co_ban = int(gia_co_ban)
        self.phi_don_dep = int(phi_don_dep)
        self.phi_minibar = int(phi_minibar)
        self._trang_thai = trang_thai

    @property
    def trang_thai(self):
        return self._trang_thai

    def dat_phong(self):
        self._trang_thai = "Đã thuê"

    def tra_phong(self):
        self._trang_thai = "Trống"

    def tinh_tien_phong(self, so_ngay):
        return (self.gia_co_ban * so_ngay) + self.phi_don_dep + self.phi_minibar

    def to_dict(self):
        return {
            "ma_phong": self.ma_phong,
            "ten_phong": self.ten_phong,
            "ma_loai": self.ma_loai,
            "gia_co_ban": self.gia_co_ban,
            "phi_don_dep": self.phi_don_dep,
            "phi_minibar": self.phi_minibar,
            "trang_thai": self._trang_thai
        }


class KhachHang:
    def __init__(self, cccd, ten):
        self.cccd = cccd
        self.ten = ten

    def to_dict(self):
        return {"cccd": self.cccd, "ten": self.ten}


class PhieuThue:
    def __init__(self, khach_hang: KhachHang, phong: Phong, ngay_checkin, ngay_checkout, trang_thai_pay="Chưa thanh toán"):
        self.khach_hang = khach_hang
        self.phong = phong
        self.ngay_checkin = ngay_checkin
        self.ngay_checkout = ngay_checkout
        self.trang_thai_pay = trang_thai_pay

    def tinh_trang_thai_luu_tru(self):
        hom_nay = datetime.date.today().strftime("%Y-%m-%d")
        if self.ngay_checkin <= hom_nay <= self.ngay_checkout:
            return "Đang ở"
        elif self.ngay_checkin > hom_nay:
            return "Đặt trước"
        else:
            return "Đã quá hạn"

    def tinh_so_ngay(self):
        try:
            d_in = datetime.datetime.strptime(self.ngay_checkin, "%Y-%m-%d").date()
            d_out = datetime.datetime.strptime(self.ngay_checkout, "%Y-%m-%d").date()
            return max(1, (d_out - d_in).days)
        except Exception:
            return 1

    def tinh_tien_phong(self):
        return self.phong.tinh_tien_phong(self.tinh_so_ngay())

    def to_dict(self):
        return {
            "khach_hang": self.khach_hang.to_dict(),
            "ma_phong": self.phong.ma_phong,
            "ngay_checkin": self.ngay_checkin,
            "ngay_checkout": self.ngay_checkout,
            "trang_thai_pay": self.trang_thai_pay
        }