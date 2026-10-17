import datetime
from models import LoaiPhongConfig, Phong, KhachHang, PhieuThue, DichVu, SuDungDichVu
from file_handler import save_data, load_data

BANK_ACC = "100871471728"
BANK_NAME = "VietinBank"
PREFIX_SEPAY = "SEVQR HOTEL"

class QuanLyKhachSan:
    def __init__(self):
        self.danh_sach_loai_phong, self.danh_sach_phong, self.danh_sach_phieu, self.danh_sach_dv, self.lich_su_su_dung_dv, self.lich_su_hoa_don = load_data()

    def tim_loai_phong(self, ma_loai):
        return next((lp for lp in self.danh_sach_loai_phong if lp.ma_loai == ma_loai), None)

    def tim_phong(self, ma_phong):
        return next((p for p in self.danh_sach_phong if p.ma_phong == ma_phong), None)

    def tim_phieu_hien_tai(self, ma_phong):
        return next((pt for pt in self.danh_sach_phieu if pt.phong.ma_phong == ma_phong and pt.trang_thai_pay == "Chưa thanh toán"), None)

    def tim_dich_vu(self, ma_dv):
        return next((dv for dv in self.danh_sach_dv if dv.ma_dv == ma_dv), None)

    # --- 1. SỬA LỖI: BỔ SUNG CÁC HÀM CRUD DỊCH VỤ GỐC KHÁCH SẠN ---
    def them_dich_vu(self, ma_dv, ten_dv, gia_dv):
        if self.tim_dich_vu(ma_dv): 
            return False, "Mã dịch vụ đã tồn tại!"
        self.danh_sach_dv.append(DichVu(ma_dv, ten_dv, gia_dv))
        self.luu_du_lieu()
        return True, "Thêm dịch vụ thành công!"

    def sua_dich_vu(self, ma_dv, ten_dv, gia_dv):
        dv = self.tim_dich_vu(ma_dv)
        if not dv: 
            return False, "Không tìm thấy dịch vụ!"
        dv.ten_dv = ten_dv
        dv.gia_dv = int(gia_dv)
        self.luu_du_lieu()
        return True, "Cập nhật dịch vụ thành công!"

    def xoa_dich_vu(self, ma_dv):
        dv = self.tim_dich_vu(ma_dv)
        if dv:
            self.danh_sach_dv.remove(dv)
            self.luu_du_lieu()
            return True, "Đã xóa dịch vụ!"
        return False, "Không tìm thấy dịch vụ!"

    # --- 2. SỬA LỖI: CRUD LOẠI PHÒNG ---
    def them_loai_phong(self, ma_loai, ten_loai, gia_co_ban, phi_don_dep=0, phi_minibar=0):
        if self.tim_loai_phong(ma_loai): return False, "Mã loại phòng đã tồn tại!"
        self.danh_sach_loai_phong.append(LoaiPhongConfig(ma_loai, ten_loai, gia_co_ban, phi_don_dep, phi_minibar))
        self.luu_du_lieu()
        return True, "Thêm loại phòng thành công!"

    def sua_loai_phong(self, ma_loai, ten_loai, gia_co_ban, phi_don_dep=0, phi_minibar=0):
        lp = self.tim_loai_phong(ma_loai)
        if not lp: return False, "Không tìm thấy loại phòng!"
        lp.ten_loai = ten_loai
        lp.gia_co_ban = int(gia_co_ban)
        lp.phi_don_dep = int(phi_don_dep)
        lp.phi_minibar = int(phi_minibar)
        self.luu_du_lieu()
        return True, "Cập nhật loại phòng thành công!"

    def xoa_loai_phong(self, ma_loai):
        lp = self.tim_loai_phong(ma_loai)
        if lp:
            self.danh_sach_loai_phong.remove(lp)
            self.luu_du_lieu()
            return True, "Đã xóa loại phòng!"
        return False, "Không tìm thấy loại phòng!"

    # --- 3. QUẢN LÝ PHÒNG ---
    def them_phong(self, ma_phong, ten_phong, ma_loai):
        if self.tim_phong(ma_phong): return False, "Mã phòng đã tồn tại!"
        lp = self.tim_loai_phong(ma_loai)
        if not lp: return False, "Loại phòng không hợp lệ!"

        p = Phong(ma_phong, ten_phong, ma_loai, lp.gia_co_ban, lp.phi_don_dep, lp.phi_minibar)
        self.danh_sach_phong.append(p)
        self.luu_du_lieu()
        return True, f"Thêm phòng {ma_phong} thành công!"

    def xoa_phong(self, ma_phong):
        p = self.tim_phong(ma_phong)
        if not p: return False, "Không tìm thấy phòng!"
        if p.trang_thai == "Đã thuê": return False, "Không thể xóa phòng đang có khách!"
        self.danh_sach_phong.remove(p)
        self.luu_du_lieu()
        return True, "Đã xóa phòng thành công!"

    # --- 4. CRUD ĐẶT PHÒNG HIỆN TẠI ---
    def dat_phong_truoc(self, ma_phong, ten_khach, cccd, ngay_in, ngay_out):
        phong = self.tim_phong(ma_phong)
        if not phong: return False, "Phòng không tồn tại!"

        d_in = datetime.datetime.strptime(ngay_in, "%Y-%m-%d").date()
        d_out = datetime.datetime.strptime(ngay_out, "%Y-%m-%d").date()
        if d_out <= d_in: return False, "Ngày đi phải sau ngày đến!"

        for pt in self.danh_sach_phieu:
            if pt.phong.ma_phong == ma_phong and pt.trang_thai_pay == "Chưa thanh toán":
                pt_in = datetime.datetime.strptime(pt.ngay_checkin, "%Y-%m-%d").date()
                pt_out = datetime.datetime.strptime(pt.ngay_checkout, "%Y-%m-%d").date()
                if not (d_out <= pt_in or d_in >= pt_out):
                    return False, f"Phòng {ma_phong} bị trùng lịch từ {pt.ngay_checkin} đến {pt.ngay_checkout}!"

        kh = KhachHang(cccd, ten_khach)
        phieu = PhieuThue(kh, phong, ngay_in, ngay_out)
        if d_in <= datetime.date.today() <= d_out:
            phong.dat_phong()

        self.danh_sach_phieu.append(phieu)
        self.luu_du_lieu()
        return True, "Đặt phòng thành công!"

    def sua_dat_phong_hien_tai(self, ma_phong, cccd_cu, ten_khach, cccd_moi, ngay_in, ngay_out):
        phong = self.tim_phong(ma_phong)
        if not phong:
            return False, "Không tìm thấy thông tin phòng!"

        d_in = datetime.datetime.strptime(ngay_in, "%Y-%m-%d").date()
        d_out = datetime.datetime.strptime(ngay_out, "%Y-%m-%d").date()
        if d_out <= d_in:
            return False, "Ngày trả phòng (Check-out) phải sau ngày nhận phòng (Check-in)!"

        # 1. KIỂM TRA TRÙNG LỊCH VỚI CÁC PHIẾU KHÁC CỦA PHÒNG NÀY
        for pt in self.danh_sach_phieu:
            # Bỏ qua chính phiếu đang sửa
            if pt.phong.ma_phong == ma_phong and pt.khach_hang.cccd == cccd_cu and pt.trang_thai_pay == "Chưa thanh toán":
                continue
            
            # Kiểm tra với các khách khác chưa thanh toán của phòng này
            if pt.phong.ma_phong == ma_phong and pt.trang_thai_pay == "Chưa thanh toán":
                pt_in = datetime.datetime.strptime(pt.ngay_checkin, "%Y-%m-%d").date()
                pt_out = datetime.datetime.strptime(pt.ngay_checkout, "%Y-%m-%d").date()
                
                # Nếu khoảng thời gian mới bị chồng lấp (overlap) với lịch người khác đã đặt
                if not (d_out <= pt_in or d_in >= pt_out):
                    return False, f"Không thể sửa! Khoảng thời gian từ {ngay_in} đến {ngay_out} đã bị trùng với lịch đặt trước của khách khác (từ {pt.ngay_checkin} đến {pt.ngay_checkout}). Vui lòng chọn ngày khác hoặc đặt phòng mới!"

        # 2. NẾU KHÔNG TRÙNG THÌ TIẾN HÀNH CẬP NHẬT
        for pt in self.danh_sach_phieu:
            if pt.phong.ma_phong == ma_phong and pt.khach_hang.cccd == cccd_cu and pt.trang_thai_pay == "Chưa thanh toán":
                pt.khach_hang.ten = ten_khach
                pt.khach_hang.cccd = cccd_moi
                pt.ngay_checkin = ngay_in
                pt.ngay_checkout = ngay_out
                
                # Cập nhật thông tin tương ứng trong danh sách dịch vụ chưa thanh toán
                for sd in self.lich_su_su_dung_dv:
                    if sd.cccd == cccd_cu and sd.ma_phong == ma_phong and not sd.da_thanh_toan:
                        sd.cccd = cccd_moi
                        sd.ten_khach = ten_khach
                        
                self.luu_du_lieu()
                return True, "Cập nhật thông tin đặt phòng thành công!"
                
        return False, "Không tìm thấy phiếu đặt phòng cần sửa!"

    def xoa_dat_phong_hien_tai(self, ma_phong, cccd):
        for pt in list(self.danh_sach_phieu):
            if pt.phong.ma_phong == ma_phong and pt.khach_hang.cccd == cccd and pt.trang_thai_pay == "Chưa thanh toán":
                pt.phong.tra_phong()
                self.danh_sach_phieu.remove(pt)
                self.luu_du_lieu()
                return True, "Đã hủy phiếu đặt phòng!"
        return False, "Không tìm thấy phiếu thuê!"

    # --- 5. BỔ SUNG CHỌN NGÀY THỰC HIỆN DỊCH VỤ TRONG POP-UP ---
    def them_nhieu_dich_vu_cho_khach(self, ma_phong, ngay_su_dung, ds_dv_chon):
        phieu = self.tim_phieu_hien_tai(ma_phong)
        if not phieu: return False, "Phòng này không có khách ở hiện tại!"

        for item in ds_dv_chon:
            ma_dv = item.get("ma_dv")
            so_luong = int(item.get("so_luong", 1))
            dv = self.tim_dich_vu(ma_dv)
            if dv and so_luong > 0:
                sd = SuDungDichVu(phieu.khach_hang.cccd, phieu.khach_hang.ten, ma_phong, dv.ma_dv, dv.ten_dv, dv.gia_dv, so_luong, ngay_su_dung=ngay_su_dung)
                self.lich_su_su_dung_dv.append(sd)

        self.luu_du_lieu()
        return True, f"Đã ghi nhận toàn bộ dịch vụ ngày {ngay_su_dung}!"

    def sua_so_luong_dv_hien_tai(self, cccd, ma_phong, ma_dv, ngay_su_dung, so_luong_moi):
        for sd in self.lich_su_su_dung_dv:
            if sd.cccd == cccd and sd.ma_phong == ma_phong and sd.ma_dv == ma_dv and sd.ngay_su_dung == ngay_su_dung and not sd.da_thanh_toan:
                sd.so_luong = int(so_luong_moi)
                self.luu_du_lieu()
                return True, "Đã cập nhật số lượng dịch vụ thành công!"
        return False, "Không tìm thấy bản ghi dịch vụ cần sửa!"

    def xoa_dv_hien_tai(self, cccd, ma_phong, ma_dv, ngay_su_dung):
        for sd in list(self.lich_su_su_dung_dv):
            if sd.cccd == cccd and sd.ma_phong == ma_phong and sd.ma_dv == ma_dv and sd.ngay_su_dung == ngay_su_dung and not sd.da_thanh_toan:
                self.lich_su_su_dung_dv.remove(sd)
                self.luu_du_lieu()
                return True, "Đã xóa dịch vụ thành công!"
        return False, "Không tìm thấy bản ghi dịch vụ!"

    def tao_qr_sepay(self, ma_hd, tong_tien):
        import urllib.parse
        
        # Cú pháp nội dung chuyển khoản bắt buộc có tiền tố SEVQR HOTEL_ABC
        noi_dung_ck = f"{PREFIX_SEPAY} {ma_hd}"
        
        # Encode nội dung để chuyển khoảng trắng thành %20 giúp URL VietQR nhận chuẩn 100%
        noi_dung_encoded = urllib.parse.quote(noi_dung_ck)
        
        # Link sinh mã QR VietQR chuẩn SePay
        qr_url = f"https://qr.sepay.vn/img?bank={BANK_NAME}&acc={BANK_ACC}&amount={int(tong_tien)}&des={noi_dung_encoded}"
        
        return qr_url, noi_dung_ck

    def xac_nhan_thanh_toan(self, ma_phong, phuong_thuc="Chuyển khoản VietinBank (SePay Auto)"):
        phieu = self.tim_phieu_hien_tai(ma_phong)
        if not phieu: return False, "Không tìm thấy phiếu thuê!", None

        ds_dv_dung = [sd for sd in self.lich_su_su_dung_dv if sd.cccd == phieu.khach_hang.cccd and sd.ma_phong == ma_phong and not sd.da_thanh_toan]
        tien_dv = sum(sd.tinh_thanh_tien() for sd in ds_dv_dung)
        tien_phong = phieu.tinh_tien_phong()
        tong_tien = tien_phong + tien_dv
        ma_hd = f"HD{int(datetime.datetime.now().timestamp())}"

        for sd in ds_dv_dung:
            sd.da_thanh_toan = True

        hoa_don = {
            "ma_hd": ma_hd,
            "ma_phong": ma_phong,
            "ten_khach": phieu.khach_hang.ten,
            "cccd": phieu.khach_hang.cccd,
            "ngay_checkin": phieu.ngay_checkin,
            "ngay_checkout": phieu.ngay_checkout,
            "so_ngay": phieu.tinh_so_ngay(),
            "ngay_thanh_toan": datetime.date.today().strftime("%Y-%m-%d"),
            "tien_phong": tien_phong,
            "tien_dich_vu": tien_dv,
            "dich_vu_su_dung": [sd.to_dict() for sd in ds_dv_dung],
            "tong_tien": tong_tien,
            "phuong_thuc": phuong_thuc,
            "trang_thai": "Thanh toán thành công"
        }

        phieu.trang_thai_pay = "Đã thanh toán"
        phieu.phong.tra_phong()
        self.lich_su_hoa_don.append(hoa_don)
        self.luu_du_lieu()
        return True, "Thanh toán thành công!", hoa_don

    def lay_du_lieu_bieu_do(self, thang_str, nam_str):
        ds_thang = [hd for hd in self.lich_su_hoa_don if hd["ngay_thanh_toan"].startswith(thang_str)]
        ngay_dict = {}
        for hd in ds_thang:
            ngay = hd["ngay_thanh_toan"]
            ngay_dict[ngay] = ngay_dict.get(ngay, 0) + hd["tong_tien"]

        labels_ngay = sorted(list(ngay_dict.keys()))
        data_ngay = [ngay_dict[k] for k in labels_ngay]

        ds_nam = [hd for hd in self.lich_su_hoa_don if hd["ngay_thanh_toan"].startswith(nam_str)]
        thang_dict = {f"{nam_str}-{m:02d}": 0 for m in range(1, 13)}
        for hd in ds_nam:
            thang_key = hd["ngay_thanh_toan"][:7]
            if thang_key in thang_dict:
                thang_dict[thang_key] += hd["tong_tien"]

        labels_thang = list(thang_dict.keys())
        data_thang = [thang_dict[k] for k in labels_thang]

        return labels_ngay, data_ngay, labels_thang, data_thang

    def luu_du_lieu(self):
        save_data(self.danh_sach_loai_phong, self.danh_sach_phong, self.danh_sach_phieu, self.danh_sach_dv, self.lich_su_su_dung_dv, self.lich_su_hoa_don)