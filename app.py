from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from functools import wraps
import datetime
from services import QuanLyKhachSan

app = Flask(__name__)
app.secret_key = "hotel_vietinbank_key"
qlks = QuanLyKhachSan()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "logged_in" not in session: 
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "123":
            session["logged_in"] = True
            return redirect(url_for("index"))
        flash("Sai tên đăng nhập hoặc mật khẩu!", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# --- 1. SƠ ĐỒ PHÒNG KHÁCH SẠN ---
@app.route("/")
@login_required
def index():
    hom_nay = datetime.date.today().strftime("%d/%m/%Y")
    return render_template("index.html", 
                           danh_sach_phong=qlks.danh_sach_phong, 
                           hom_nay=hom_nay)

# --- 2. SƠ ĐỒ GANTT TIMELINE ---
@app.route("/so-do-gantt")
@login_required
def trang_so_do_gantt():
    hom_nay_obj = datetime.date.today()
    ds_ngay = [(hom_nay_obj + datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(14)]
    phieu_hien_tai = [pt for pt in qlks.danh_sach_phieu if pt.trang_thai_pay == "Chưa thanh toán"]

    return render_template("gantt.html", 
                           danh_sach_phong=qlks.danh_sach_phong, 
                           phieu_hien_tai=phieu_hien_tai, 
                           ds_ngay=ds_ngay,
                           hom_nay=hom_nay_obj.strftime("%Y-%m-%d"))

# API Xem chi tiết phòng cho Pop-up Modal ở trang Sơ đồ
@app.route("/api/phong/<ma_phong>")
@login_required
def api_phong_detail(ma_phong):
    try:
        phong = qlks.tim_phong(ma_phong)
        if not phong: 
            return jsonify({"status": "error", "message": "Không tìm thấy phòng"}), 404

        phieu = qlks.tim_phieu_hien_tai(ma_phong)
        res = {
            "ma_phong": phong.ma_phong,
            "ten_phong": phong.ten_phong,
            "gia_co_ban": phong.gia_co_ban,
            "phi_don_dep": phong.phi_don_dep,
            "phi_minibar": phong.phi_minibar,
            "trang_thai": phong.trang_thai
        }
        
        if phieu:
            ds_dv_dung = [sd.to_dict() for sd in qlks.lich_su_su_dung_dv if sd.cccd == phieu.khach_hang.cccd and sd.ma_phong == ma_phong and not sd.da_thanh_toan]
            res["khach_hang"] = phieu.khach_hang.ten
            res["cccd"] = phieu.khach_hang.cccd
            res["ngay_checkin"] = phieu.ngay_checkin
            res["ngay_checkout"] = phieu.ngay_checkout
            res["so_ngay"] = phieu.tinh_so_ngay()
            res["trang_thai_luu_tru"] = phieu.tinh_trang_thai_luu_tru()
            res["dich_vu"] = ds_dv_dung

        return jsonify({"status": "success", "data": res})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- 3. CẤU HÌNH LOẠI PHÒNG GỐC ---
@app.route("/loai-phong")
@login_required
def trang_loai_phong():
    return render_template("loaiphong.html", danh_sach_loai=qlks.danh_sach_loai_phong)

@app.route("/loai-phong/them", methods=["POST"])
@login_required
def them_loai_phong():
    ok, msg = qlks.them_loai_phong(request.form["ma_loai"].strip(), request.form["ten_loai"].strip(), int(request.form["gia_co_ban"]), int(request.form.get("phi_don_dep", 0) or 0), int(request.form.get("phi_minibar", 0) or 0))
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("trang_loai_phong"))

@app.route("/loai-phong/sua", methods=["POST"])
@login_required
def sua_loai_phong():
    ok, msg = qlks.sua_loai_phong(request.form["ma_loai"].strip(), request.form["ten_loai"].strip(), int(request.form["gia_co_ban"]), int(request.form.get("phi_don_dep", 0) or 0), int(request.form.get("phi_minibar", 0) or 0))
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("trang_loai_phong"))

@app.route("/loai-phong/xoa/<ma_loai>", methods=["POST"])
@login_required
def xoa_loai_phong(ma_loai):
    ok, msg = qlks.xoa_loai_phong(ma_loai)
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("trang_loai_phong"))

# --- 4. QUẢN LÝ PHÒNG ---
@app.route("/phong")
@login_required
def trang_phong():
    return render_template("phong.html", danh_sach_phong=qlks.danh_sach_phong, danh_sach_loai=qlks.danh_sach_loai_phong)

@app.route("/phong/them", methods=["POST"])
@login_required
def them_phong():
    ok, msg = qlks.them_phong(request.form["ma_phong"].strip(), request.form["ten_phong"].strip(), request.form["ma_loai"])
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("trang_phong"))

@app.route("/phong/xoa/<ma_phong>", methods=["POST"])
@login_required
def xoa_phong(ma_phong):
    ok, msg = qlks.xoa_phong(ma_phong)
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("trang_phong"))

# --- 5. DỊCH VỤ KHÁCH SẠN GỐC ---
@app.route("/dich-vu")
@login_required
def trang_dich_vu():
    return render_template("dichvu.html", danh_sach_dv=qlks.danh_sach_dv)

@app.route("/dich-vu/them", methods=["POST"])
@login_required
def them_dich_vu():
    ok, msg = qlks.them_dich_vu(request.form["ma_dv"].strip(), request.form["ten_dv"].strip(), int(request.form["gia_dv"]))
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("trang_dich_vu"))

@app.route("/dich-vu/sua", methods=["POST"])
@login_required
def sua_dich_vu():
    ok, msg = qlks.sua_dich_vu(request.form["ma_dv"].strip(), request.form["ten_dv"].strip(), int(request.form["gia_dv"]))
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("trang_dich_vu"))

@app.route("/dich-vu/xoa/<ma_dv>", methods=["POST"])
@login_required
def xoa_dich_vu(ma_dv):
    ok, msg = qlks.xoa_dich_vu(ma_dv)
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("trang_dich_vu"))

# --- 6. ĐẶT PHÒNG HIỆN TẠI (CRUD) ---
@app.route("/hientai-datphong")
@login_required
def trang_hientai_datphong():
    kw = request.args.get("kw", "").strip()
    ds_hien_tai = [pt for pt in qlks.danh_sach_phieu if pt.trang_thai_pay == "Chưa thanh toán"]
    if kw:
        ds_hien_tai = [pt for pt in ds_hien_tai if kw.lower() in pt.khach_hang.ten.lower() or kw in pt.khach_hang.cccd or kw in pt.phong.ma_phong]

    phong_trong = [p for p in qlks.danh_sach_phong if p.trang_thai == "Trống"]
    return render_template("hientai_datphong.html", danh_sach_phieu=ds_hien_tai, phong_trong=phong_trong, kw=kw)

@app.route("/dat-phong/them", methods=["POST"])
@login_required
def them_dat_phong():
    ok, msg = qlks.dat_phong_truoc(request.form["ma_phong"].strip(), request.form["ten_khach"].strip(), request.form["cccd"].strip(), request.form["ngay_in"], request.form["ngay_out"])
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("trang_hientai_datphong"))

@app.route("/hientai-datphong/sua", methods=["POST"])
@login_required
def sua_hientai_datphong():
    ok, msg = qlks.sua_dat_phong_hien_tai(
        request.form["ma_phong"].strip(),
        request.form["cccd_cu"].strip(),
        request.form["ten_khach"].strip(),
        request.form["cccd_moi"].strip(),
        request.form["ngay_in"],
        request.form["ngay_out"]
    )
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("trang_hientai_datphong"))

@app.route("/hientai-datphong/xoa", methods=["POST"])
@login_required
def xoa_hientai_datphong():
    ok, msg = qlks.xoa_dat_phong_hien_tai(request.form["ma_phong"].strip(), request.form["cccd"].strip())
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("trang_hientai_datphong"))

# --- 7. KHÁCH DÙNG DỊCH VỤ HIỆN TẠI (CRUD) ---
@app.route("/hientai-sudung-dv")
@login_required
def trang_hientai_sudung_dv():
    kw = request.args.get("kw", "").strip()
    ds_hien_tai = [sd for sd in qlks.lich_su_su_dung_dv if not sd.da_thanh_toan]
    if kw:
        ds_hien_tai = [sd for sd in ds_hien_tai if kw.lower() in sd.ten_khach.lower() or kw in sd.cccd or kw in sd.ma_phong or kw.lower() in sd.ten_dv.lower()]

    phong_da_thue = [p for p in qlks.danh_sach_phong if p.trang_thai == "Đã thuê"]
    hom_nay = datetime.date.today().strftime("%Y-%m-%d")
    return render_template("hientai_sudung_dv.html", ds_dv=ds_hien_tai, phong_da_thue=phong_da_thue, danh_sach_dv=qlks.danh_sach_dv, kw=kw, hom_nay=hom_nay)

@app.route("/su-dung-dich-vu/them-hang-loat", methods=["POST"])
@login_required
def them_hang_loat_dich_vu():
    data = request.json
    ma_phong = data.get("ma_phong")
    ngay_su_dung = data.get("ngay_su_dung", datetime.date.today().strftime("%Y-%m-%d"))
    ds_dv = data.get("dich_vu_list", [])
    ok, msg = qlks.them_nhieu_dich_vu_cho_khach(ma_phong, ngay_su_dung, ds_dv)
    return jsonify({"status": "success" if ok else "error", "message": msg})

@app.route("/su-dung-dich-vu/sua", methods=["POST"])
@login_required
def sua_su_dung_dich_vu():
    ok, msg = qlks.sua_so_luong_dv_hien_tai(
        request.form["cccd"].strip(),
        request.form["ma_phong"].strip(),
        request.form["ma_dv"].strip(),
        request.form["ngay_su_dung"].strip(),
        request.form["so_luong"]
    )
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("trang_hientai_sudung_dv"))

@app.route("/su-dung-dich-vu/xoa", methods=["POST"])
@login_required
def xoa_su_dung_dich_vu():
    ok, msg = qlks.xoa_dv_hien_tai(
        request.form["cccd"].strip(),
        request.form["ma_phong"].strip(),
        request.form["ma_dv"].strip(),
        request.form["ngay_su_dung"].strip()
    )
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("trang_hientai_sudung_dv"))

# --- 8. TRẢ PHÒNG & THANH TOÁN ---
@app.route("/tra-phong")
@login_required
def trang_tra_phong():
    phong_da_thue = [p for p in qlks.danh_sach_phong if p.trang_thai == "Đã thuê"]
    return render_template("traphong.html", phong_da_thue=phong_da_thue)

@app.route("/api/invoice/<ma_phong>")
@login_required
def api_invoice(ma_phong):
    phieu = qlks.tim_phieu_hien_tai(ma_phong)
    if not phieu: return jsonify({"status": "error", "message": "Không tìm thấy thông tin phòng!"})

    ds_dv_dung = [sd for sd in qlks.lich_su_su_dung_dv if sd.cccd == phieu.khach_hang.cccd and sd.ma_phong == ma_phong and not sd.da_thanh_toan]
    tien_dv = sum(sd.tinh_thanh_tien() for sd in ds_dv_dung)
    tien_phong = phieu.tinh_tien_phong()
    tong_tien = tien_phong + tien_dv
    
    ma_hd = f"HD{int(datetime.datetime.now().timestamp())}"
    qr_url, noi_dung_ck = qlks.tao_qr_sepay(ma_hd, tong_tien)

    return jsonify({
        "status": "success",
        "ma_hd": ma_hd,
        "ma_phong": ma_phong,
        "ten_khach": phieu.khach_hang.ten,
        "cccd": phieu.khach_hang.cccd,
        "ngay_in": phieu.ngay_checkin,
        "ngay_out": phieu.ngay_checkout,
        "so_ngay": phieu.tinh_so_ngay(),
        "tien_phong": tien_phong,
        "dich_vu": [sd.to_dict() for sd in ds_dv_dung],
        "tong_tien": tong_tien,
        "qr_url": qr_url,
        "noi_dung_ck": noi_dung_ck
    })

@app.route("/api/thanh-toan-xac-nhan", methods=["POST"])
@login_required
def api_thanh_toan_xac_nhan():
    data = request.json
    ok, msg, hd = qlks.xac_nhan_thanh_toan(data["ma_phong"], data["phuong_thuc"])
    return jsonify({"status": "success" if ok else "error", "message": msg, "hoa_don": hd})

@app.route("/webhook/sepay", methods=["POST"])
def webhook_sepay():
    data = request.json
    if not data: return jsonify({"status": "error"}), 400
    content = data.get("content", "").upper().strip()
    
    # Kiểm tra nội dung chứa HOTEL hoặc mã HD
    if "HOTEL" in content or "HD" in content:
        for phieu in list(qlks.danh_sach_phieu):
            if phieu.trang_thai_pay == "Chưa thanh toán":
                qlks.xac_nhan_thanh_toan(phieu.phong.ma_phong, phuong_thuc="Chuyển khoản VietinBank (SePay Auto)")
                return jsonify({"status": "success"})
    return jsonify({"status": "ignored"})
# API kiểm tra trạng thái thanh toán realtime cho giao diện Web
@app.route("/api/check-payment-status/<ma_phong>")
def api_check_payment_status(ma_phong):
    # Tìm phiếu thuê của phòng này
    phieu = qlks.tim_phieu_hien_tai(ma_phong)
    
    # Nếu không còn phiếu chưa thanh toán (tức SePay đã gạch nợ thành công) -> Trả về paid: True
    if not phieu:
        return jsonify({"paid": True})
    
    # Nếu vẫn còn phiếu chưa thanh toán -> Trả về paid: False
    return jsonify({"paid": False})
# --- 9. TRA CỨU LỊCH SỬ ---
@app.route("/ls-datphong")
@login_required
def trang_ls_datphong():
    kw = request.args.get("kw", "").strip()
    ngay = request.args.get("ngay", "").strip()
    ds_ls = [pt for pt in qlks.danh_sach_phieu if pt.trang_thai_pay == "Đã thanh toán"]
    if kw:
        ds_ls = [pt for pt in ds_ls if kw.lower() in pt.khach_hang.ten.lower() or kw in pt.khach_hang.cccd or kw in pt.phong.ma_phong]
    if ngay:
        ds_ls = [pt for pt in ds_ls if ngay in pt.ngay_checkin or ngay in pt.ngay_checkout]

    return render_template("ls_datphong.html", danh_sach=ds_ls, kw=kw, ngay=ngay)

@app.route("/ls-sudung-dv")
@login_required
def trang_ls_sudung_dv():
    kw = request.args.get("kw", "").strip()
    ngay = request.args.get("ngay", "").strip()
    ds_ls = [sd for sd in qlks.lich_su_su_dung_dv if sd.da_thanh_toan]
    if kw:
        ds_ls = [sd for sd in ds_ls if kw.lower() in sd.ten_khach.lower() or kw in sd.cccd or kw.lower() in sd.ten_dv.lower()]
    if ngay:
        ds_ls = [sd for sd in ds_ls if ngay in sd.ngay_su_dung]

    return render_template("ls_sudung_dv.html", danh_sach=ds_ls, kw=kw, ngay=ngay)

@app.route("/ls-hoadon")
@login_required
def trang_ls_hoadon():
    kw = request.args.get("kw", "").strip()
    ngay = request.args.get("ngay", "").strip()
    ds_hd = qlks.lich_su_hoa_don
    if kw:
        ds_hd = [h for h in ds_hd if kw.lower() in h["ten_khach"].lower() or kw in h["cccd"] or kw in h["ma_hd"]]
    if ngay:
        ds_hd = [h for h in ds_hd if ngay in h["ngay_thanh_toan"]]

    return render_template("ls_hoadon.html", danh_sach=ds_hd, kw=kw, ngay=ngay)

# --- 10. BÁO CÁO DOANH THỦ ---
@app.route("/bao-cao")
@login_required
def trang_bao_cao():
    thang_query = request.args.get("thang", datetime.date.today().strftime("%Y-%m"))
    nam_query = request.args.get("nam", datetime.date.today().strftime("%Y"))

    labels_ngay, data_ngay, labels_thang, data_thang = qlks.lay_du_lieu_bieu_do(thang_query, nam_query)

    return render_template("baocao.html", 
                           thang_query=thang_query, nam_query=nam_query,
                           labels_ngay=labels_ngay, data_ngay=data_ngay,
                           labels_thang=labels_thang, data_thang=data_thang)

if __name__ == "__main__":
    app.run(debug=True, port=5000)