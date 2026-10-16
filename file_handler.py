import json, os
from models import LoaiPhongConfig, Phong, KhachHang, PhieuThue, DichVu, SuDungDichVu

FILE_NAME = "khachsan_data.json"

def save_data(danh_sach_loai_phong, danh_sach_phong, danh_sach_phieu, danh_sach_dv, lich_su_su_dung_dv, lich_su_hoa_don):
    data = {
        "danh_sach_loai_phong": [lp.to_dict() for lp in danh_sach_loai_phong],
        "danh_sach_phong": [p.to_dict() for p in danh_sach_phong],
        "danh_sach_phieu": [pt.to_dict() for pt in danh_sach_phieu],
        "danh_sach_dv": [dv.to_dict() for dv in danh_sach_dv],
        "lich_su_su_dung_dv": [sd.to_dict() for sd in lich_su_su_dung_dv],
        "lich_su_hoa_don": lich_su_hoa_don
    }
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_data():
    if not os.path.exists(FILE_NAME):
        # Mặc định tạo 2 loại phòng cấu hình chuẩn
        default_loai = [
            LoaiPhongConfig("STD", "Phòng Thường (Standard)", 500000, 0, 0),
            LoaiPhongConfig("VIP", "Phòng VIP Cao Cấp", 1000000, 100000, 50000)
        ]
        return default_loai, [], [], [], [], []

    try:
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            data = json.load(f)

        danh_sach_loai_phong = [
            LoaiPhongConfig(lp["ma_loai"], lp["ten_loai"], lp["gia_co_ban"], lp.get("phi_don_dep", 0), lp.get("phi_minibar", 0))
            for lp in data.get("danh_sach_loai_phong", [])
        ]
        if not danh_sach_loai_phong:
            danh_sach_loai_phong = [
                LoaiPhongConfig("STD", "Phòng Thường (Standard)", 500000, 0, 0),
                LoaiPhongConfig("VIP", "Phòng VIP Cao Cấp", 1000000, 100000, 50000)
            ]

        danh_sach_dv = [DichVu(d["ma_dv"], d["ten_dv"], d["gia_dv"]) for d in data.get("danh_sach_dv", [])]
        
        lich_su_su_dung_dv = [
            SuDungDichVu(s["cccd"], s["ten_khach"], s["ma_phong"], s["ma_dv"], s["ten_dv"], s["gia_dv"], s["so_luong"], s.get("ngay_su_dung"), s.get("da_thanh_toan", False))
            for s in data.get("lich_su_su_dung_dv", [])
        ]
        
        lich_su_hoa_don = data.get("lich_su_hoa_don", [])

        danh_sach_phong = []
        dict_phong = {}
        for item in data.get("danh_sach_phong", []):
            p = Phong(item["ma_phong"], item["ten_phong"], item.get("ma_loai", "STD"), item["gia_co_ban"], item.get("phi_don_dep", 0), item.get("phi_minibar", 0), item["trang_thai"])
            danh_sach_phong.append(p)
            dict_phong[p.ma_phong] = p

        danh_sach_phieu = []
        for pt in data.get("danh_sach_phieu", []):
            kh = KhachHang(pt["khach_hang"]["cccd"], pt["khach_hang"]["ten"])
            ma_p = pt["ma_phong"]
            if ma_p in dict_phong:
                phieu = PhieuThue(kh, dict_phong[ma_p], pt["ngay_checkin"], pt["ngay_checkout"], pt.get("trang_thai_pay", "Chưa thanh toán"))
                danh_sach_phieu.append(phieu)

        return danh_sach_loai_phong, danh_sach_phong, danh_sach_phieu, danh_sach_dv, lich_su_su_dung_dv, lich_su_hoa_don
    except Exception:
        return [], [], [], [], [], []