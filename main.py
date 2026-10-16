from services import QuanLyKhachSan

def get_float_input(prompt):
    while True:
        try:
            val = float(input(prompt))
            if val < 0:
                print("[Lỗi] Giá trị phải là số không âm. Vui lòng nhập lại!")
                continue
            return val
        except ValueError:
            print("[Lỗi] Vui lòng nhập số hợp lệ!")

def get_int_input(prompt):
    while True:
        try:
            val = int(input(prompt))
            if val <= 0:
                print("[Lỗi] Số ngày phải lớn hơn 0. Vui lòng nhập lại!")
                continue
            return val
        except ValueError:
            print("[Lỗi] Vui lòng nhập số nguyên hợp lệ!")

def main():
    qlks = QuanLyKhachSan()

    while True:
        print("\n================ HỆ THỐNG QUẢN LÝ KHÁCH SẠN ================")
        print("1. Hiển thị danh sách phòng")
        print("2. Thêm phòng mới")
        print("3. Đặt phòng")
        print("4. Trả phòng & Thanh toán")
        print("5. Xem báo cáo doanh thu")
        print("6. Thoát & Lưu dữ liệu")
        print("============================================================")
        
        luachon = input("Chọn chức năng (1-6): ").strip()

        if luachon == "1":
            qlks.hien_thi_danh_sach_phong()

        elif luachon == "2":
            print("\n--- THÊM PHÒNG MỚI ---")
            ma_phong = input("Nhập mã phòng: ").strip()
            ten_phong = input("Nhập tên phòng: ").strip()
            gia_co_ban = get_float_input("Nhập giá cơ bản (VNĐ/ngày): ")
            
            loai = input("Chọn loại phòng (1: Thường, 2: VIP): ").strip()
            if loai == "2":
                phi_don_dep = get_float_input("Nhập phí dọn dẹp: ")
                phi_minibar = get_float_input("Nhập phí minibar: ")
                qlks.them_phong(ma_phong, ten_phong, gia_co_ban, "VIP", phi_don_dep, phi_minibar)
            else:
                qlks.them_phong(ma_phong, ten_phong, gia_co_ban, "THUONG")

        elif luachon == "3":
            print("\n--- ĐẶT PHÒNG ---")
            ma_phong = input("Nhập mã phòng muốn đặt: ").strip()
            ma_khach = input("Nhập mã khách hàng: ").strip()
            ten_khach = input("Nhập tên khách hàng: ").strip()
            cccd = input("Nhập số CCCD/CMND: ").strip()
            so_ngay = get_int_input("Nhập số ngày thuê: ")

            try:
                qlks.dat_phong(ma_phong, ma_khach, ten_khach, cccd, so_ngay)
            except ValueError as e:
                print(f"\n[Lỗi nghiệp vụ] {e}")

        elif luachon == "4":
            print("\n--- TRẢ PHÒNG & THANH TOÁN ---")
            ma_phong = input("Nhập mã phòng cần trả: ").strip()
            try:
                qlks.tra_phong(ma_phong)
            except ValueError as e:
                print(f"\n[Lỗi nghiệp vụ] {e}")

        elif luachon == "5":
            qlks.bao_cao_doanh_thu()

        elif luachon == "6":
            qlks.luu_du_lieu()
            print("Cảm ơn bạn đã sử dụng hệ thống! Tạm biệt.")
            break

        else:
            print("\n[Lỗi] Lựa chọn không hợp lệ, vui lòng chọn lại từ 1 đến 6.")

if __name__ == "__main__":
    main()