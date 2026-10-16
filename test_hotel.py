import unittest
from models import PhongThuong, PhongVIP, KhachHang, PhieuThue

class TestHotelManagement(unittest.TestCase):

    def test_tinh_tien_phong_thuong(self):
        phong = PhongThuong("P101", "Phong Thuong", 500000)
        tong_tien = phong.tinh_tien(2)
        self.assertEqual(tong_tien, 1000000)

    def test_tinh_tien_phong_vip(self):
        # Kiểm tra tính đa hình của PhongVIP
        phong_vip = PhongVIP("P102", "Phong VIP", 1000000, phi_don_dep=100000, phi_minibar=50000)
        tong_tien = phong_vip.tinh_tien(3)
        self.assertEqual(tong_tien, 3150000)

    def test_dong_goi_trang_thai_phong(self):
        phong = PhongThuong("P103", "Phong Standard", 400000)
        self.assertEqual(phong.trang_thai, "Trống")
        
        phong.dat_phong()
        self.assertEqual(phong.trang_thai, "Đã thuê")
        
        phong.tra_phong()
        self.assertEqual(phong.trang_thai, "Trống")

if __name__ == "__main__":
    unittest.main()