# -*- coding-utf-8 -*-
# CHƯƠNG TRÌNH MINH HỌA THUẬT TOÁN TRAO ĐỔI KHÓA DIFFIE-HELLMAN

# --- 1. KHAI BÁO CÁC THƯ VIỆN ---
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import math
import secrets

# --- 2. LỚP CHÍNH CỦA ỨNG DỤNG ---
class DiffieHellmanApp:
    # Hàm khởi tạo lớp ứng dụng
    def __init__(self, root):
        self.root = root
        self.root.title("Minh Họa Thuật Toán Trao Đổi Khóa Diffie-Hellman")

        # Cài đặt logo (nếu có file)
        try:
            self.root.iconbitmap('logo.ico')
        except tk.TclError:
            print("Lưu ý: Không tìm thấy file 'logo.ico'.")

        # Dữ liệu các cặp (p, g) có sẵn
        self.prime_data = {
            23: [5, 7, 10, 11, 14, 15, 17, 19, 20],
            97: [5, 7, 10, 13, 14, 15, 17, 21, 23],
            991: [6, 7, 11, 12, 22, 23, 28, 34, 41],
            2287: [19, 21, 33, 35, 38, 39, 42, 53, 55],
            7919: [7, 13, 14, 17, 21, 26, 28, 29, 31],
            104743: [3, 6, 7, 11, 22, 24, 28, 31, 43],
            1299709: [6, 10, 18, 19, 21, 22, 24, 30, 34],
            15485863: [6, 7, 12, 14, 20, 39, 46, 48, 51],
            2147483647: [7, 11, 14, 22, 28, 31, 39, 44, 45]
        }

        # Biến lưu trữ widget
        self.private_entries = {}
        self.public_entries = {}
        self.p_var = tk.StringVar()
        self.g_var = tk.StringVar()

        # Tạo giao diện và căn giữa
        self.create_widgets()
        self.center_window()

    # --- 2.1. HÀM TẠO GIAO DIỆN CHÍNH ---
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Tạo các phần giao diện con
        self._create_params_section(main_frame)
        self._create_parties_section(main_frame)
        self._create_results_section(main_frame)
        self._create_control_buttons(main_frame)

        # Tải giá trị mặc định
        self.p_combo.current(0)
        self.update_g_options(None)

    # --- 2.2. CÁC HÀM TẠO GIAO DIỆN PHỤ ---
    def _create_params_section(self, parent_frame):
        # Tạo khu vực chọn/nhập p và g
        params_frame = ttk.LabelFrame(parent_frame, text="1. Tham Số Công Khai (p, g)", padding="15")
        params_frame.pack(fill=tk.X, pady=(0, 10))
        params_frame.columnconfigure(1, weight=3)
        params_frame.columnconfigure(3, weight=2)

        ttk.Label(params_frame, text="Chọn/Nhập p:").grid(row=0, column=0, padx=(0,5), pady=5, sticky="w")
        self.p_combo = ttk.Combobox(params_frame, textvariable=self.p_var, values=list(self.prime_data.keys()), bootstyle="primary")
        self.p_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.p_combo.bind("<<ComboboxSelected>>", self.update_g_options)
        self.p_combo.bind("<KeyRelease>", self.update_g_options)
        self.p_combo.bind("<Button-1>", lambda e: self.root.after(10, lambda: self.p_combo.event_generate('<Down>')))

        ttk.Label(params_frame, text="Chọn/Nhập g:").grid(row=0, column=2, padx=(10,5), pady=5, sticky="w")
        self.g_combo = ttk.Combobox(params_frame, textvariable=self.g_var, bootstyle="primary")
        self.g_combo.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        self.g_combo.bind("<Button-1>", lambda e: self.root.after(10, lambda: self.g_combo.event_generate('<Down>')))

    def _create_parties_section(self, parent_frame):
        # Tạo khu vực nhập liệu cho Bên A và Bên B
        parties_frame = ttk.Frame(parent_frame)
        parties_frame.pack(fill=tk.X, pady=10)
        parties_frame.columnconfigure(0, weight=1)
        parties_frame.columnconfigure(1, weight=1)

        # Tạo giao diện A và B bằng hàm trợ giúp
        self._create_single_party_frame(parties_frame, 'a', "2. Bên A", 0, (0, 10))
        self._create_single_party_frame(parties_frame, 'b', "3. Bên B", 1, (10, 0))

    def _create_single_party_frame(self, parent_frame, party_letter, frame_text, grid_column, padx_config):
        # Hàm trợ giúp: Tạo khung giao diện cho một bên
        frame = ttk.LabelFrame(parent_frame, text=frame_text, padding="15")
        frame.grid(row=0, column=grid_column, padx=padx_config, sticky="nsew")

        ttk.Label(frame, text=f"Nhập hoặc tạo khóa bí mật ({party_letter}):").pack(anchor="w", pady=(0, 2))
        input_frame = ttk.Frame(frame)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        private_entry = ttk.Entry(input_frame)
        private_entry.pack(side="left", expand=True, fill=tk.X)
        self.private_entries[party_letter] = private_entry

        random_btn = ttk.Button(input_frame, text="Ngẫu nhiên", command=lambda p=party_letter: self.generate_and_set_random_key(p), bootstyle="secondary")
        random_btn.pack(side="left", padx=(5, 0))

        ttk.Label(frame, text=f"Khóa công khai ({party_letter.upper()}):").pack(anchor="w", pady=(0, 2))
        public_entry = ttk.Entry(frame, state="readonly")
        public_entry.pack(fill=tk.X)
        self.public_entries[party_letter] = public_entry

    def _create_results_section(self, parent_frame):
        # Tạo khu vực hiển thị kết quả khóa chung và nút tính toán
        result_frame = ttk.LabelFrame(parent_frame, text="4. Khóa Chung Bí Mật", padding="15")
        result_frame.pack(fill=tk.X, pady=10)

        self.calc_button = ttk.Button(result_frame, text="Thực Hiện Trao Đổi & Tính Khóa Chung", command=self.calculate_shared_key, bootstyle="primary")
        self.calc_button.pack(fill=tk.X, ipady=5, pady=5)

        ttk.Label(result_frame, text="Khóa chung (Shared Secret K):").pack(anchor="w", pady=(10,2))
        self.shared_key_val = ttk.Entry(result_frame, state="readonly")
        self.shared_key_val.pack(fill=tk.X)

    def _create_control_buttons(self, parent_frame):
        # Tạo nút 'Xóa & Làm Lại'
        self.clear_button = ttk.Button(parent_frame, text="Xóa & Làm Lại", command=self.clear_fields, bootstyle="danger-outline")
        self.clear_button.pack(fill=tk.X, ipady=5, pady=(20,0))

    # --- 2.3. CÁC HÀM XỬ LÝ SỰ KIỆN VÀ LOGIC ---

    # Hàm cập nhật danh sách g khi p thay đổi
    def update_g_options(self, event):
        suggested_g_values = []
        try:
            p_text = self.p_var.get().strip()
            if not p_text:
                 self.g_combo['values'] = []; self.g_var.set(""); return
            p = int(p_text)

            if p in self.prime_data: # Tìm trong danh sách có sẵn
                suggested_g_values = self.prime_data[p]
            elif self.is_prime(p) and p > 2 and p < 50000: # Tự tính gợi ý nếu p hợp lệ
                count = 0
                for g_candidate in range(2, 51):
                    if self.is_primitive_root(g_candidate, p):
                        suggested_g_values.append(g_candidate)
                        count += 1
                        if count >= 5: break

            # Cập nhật Combobox của g
            current_g = self.g_var.get()
            self.g_combo['values'] = suggested_g_values
            if suggested_g_values:
                 if (event and event.widget == self.p_combo and event.type == tk.EventType.ComboboxSelected) or not current_g:
                    self.g_var.set(suggested_g_values[0])
            else:
                 if not self.is_prime(p): self.g_var.set("")
        except (ValueError, tk.TclError):
            self.g_combo['values'] = []; self.g_var.set("")

    # Hàm tạo số ngẫu nhiên cho khóa bí mật a hoặc b
    def generate_and_set_random_key(self, party):
        try:
            p = int(self.p_var.get())
            if p <= 3: messagebox.showwarning("Giá trị không hợp lệ", "Giá trị p phải lớn hơn 3."); return
            random_key = secrets.randbelow(p - 3) + 2 # Số ngẫu nhiên an toàn
            entry_widget = self.private_entries[party]
            entry_widget.delete(0, tk.END); entry_widget.insert(0, str(random_key))
        except (ValueError, tk.TclError):
            messagebox.showerror("Lỗi", "Vui lòng nhập giá trị p hợp lệ trước.")

    # Hàm kiểm tra số nguyên tố
    def is_prime(self, n):
        if n < 2: return False
        if n in (2, 3): return True
        if n % 2 == 0 or n % 3 == 0: return False
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0: return False
            i += 6
        return True

    # Hàm tìm các thừa số nguyên tố riêng biệt của n
    def _get_prime_factors(self, n):
        factors = set(); d = 2
        temp_n = n
        while d * d <= temp_n:
            while (temp_n % d) == 0: factors.add(d); temp_n //= d
            d += 1
        if temp_n > 1: factors.add(temp_n)
        return list(factors)

    # Hàm kiểm tra g có phải là căn nguyên thủy của p
    def is_primitive_root(self, g, p):
        if not self.is_prime(p): return False
        if not (1 < g < p): return False
        phi = p - 1; factors = self._get_prime_factors(phi)
        if not factors and phi > 0: return True # Trường hợp p=3
        if not factors and phi == 0: return False # Trường hợp p=2
        for factor in factors:
            try:
                # Điều kiện kiểm tra căn nguyên thủy
                if pow(g, phi // factor, p) == 1: return False
            except OverflowError:
                 print(f"Cảnh báo: Lỗi tràn số khi kiểm tra g={g}, p={p}.")
                 return False
        return True

    # Hàm hiển thị hộp thoại cảnh báo với lựa chọn Yes/No
    def _show_validation_warning(self, title, error_msg, condition_msg, reason_msg):
        full_message = f"{error_msg}\n\n{condition_msg}\n\n{reason_msg}\n\nBạn có muốn tiếp tục không?"
        return messagebox.askyesno(title, full_message, icon='warning')

    # Hàm kiểm tra tất cả các điều kiện đầu vào p, g, a, b
    def validate_inputs(self, p, g, a, b):
        # Kiểm tra p
        if not self.is_prime(p):
            if not self._show_validation_warning("Cảnh Báo: p không hợp lệ", f"Giá trị p = {p} không phải là số nguyên tố.", "Giá trị của p phải là một số nguyên tố.", "Đây là yêu cầu cơ bản của thuật toán."): return False
        # Kiểm tra g
        if p > 2 and p < 10**7: # Chỉ kiểm tra căn nguyên thủy nếu p không quá lớn
             if not self.is_primitive_root(g, p):
                 if not self._show_validation_warning("Cảnh Báo: g không hợp lệ", f"Giá trị g = {g} không phải là căn nguyên thủy của p = {p}.", "Giá trị của g phải là căn nguyên thủy modulo p.", "Nếu không, độ an toàn sẽ giảm."): return False
        elif not (1 < g < p): # Kiểm tra khoảng giá trị nếu p lớn
             if not self._show_validation_warning("Cảnh Báo: g không hợp lệ", f"Giá trị g = {g} nằm ngoài khoảng (1, {p}).", f"Giá trị của g phải thỏa mãn 1 < g < {p}.", "Đảm bảo g nằm trong nhóm toán học."): return False
        # Kiểm tra a
        if not (1 < a < p - 1):
            if not self._show_validation_warning("Cảnh Báo: Khóa 'a' không an toàn", f"Khóa bí mật a = {a} nằm ngoài khoảng khuyến nghị.", f"Giá trị của a nên thỏa mãn 1 < a < {p-1}.", "Chọn khóa ngoài khoảng này có thể giảm độ an toàn."): return False
        # Kiểm tra b
        if not (1 < b < p - 1):
            if not self._show_validation_warning("Cảnh Báo: Khóa 'b' không an toàn", f"Khóa bí mật b = {b} nằm ngoài khoảng khuyến nghị.", f"Giá trị của b nên thỏa mãn 1 < b < {p-1}.", "Chọn khóa ngoài khoảng này có thể giảm độ an toàn."): return False
        return True

    # Hàm chính, thực hiện tính toán trao đổi khóa Diffie-Hellman
    def calculate_shared_key(self):
        try:
            p = int(self.p_var.get()); g = int(self.g_var.get())
            a = int(self.private_entries['a'].get()); b = int(self.private_entries['b'].get())

            if not self.validate_inputs(p, g, a, b): return

            # Bước 1: Tính khóa công khai A = g^a mod p
            A = pow(g, a, p)
            # Bước 2: Tính khóa công khai B = g^b mod p
            B = pow(g, b, p)
            # Bước 3: Tính khóa chung K = B^a mod p (hoặc K = A^b mod p)
            K = pow(B, a, p)

            # Hiển thị kết quả A, B, K
            self._update_readonly_entry(self.public_entries['a'], str(A))
            self._update_readonly_entry(self.public_entries['b'], str(B))
            self._update_readonly_entry(self.shared_key_val, str(K))
            messagebox.showinfo("Thành công", f"Trao đổi khóa thành công!\nKhóa chung là: {K}")

        except ValueError: # Xử lý lỗi nhập sai định dạng số
            messagebox.showerror("Lỗi Đầu Vào", "Vui lòng nhập đầy đủ p, g, a, b dưới dạng số nguyên.")
        except OverflowError: # Xử lý lỗi tràn số
             messagebox.showerror("Lỗi Tính Toán", "Giá trị p hoặc các khóa quá lớn dẫn đến tràn số.")
        except Exception as e: # Xử lý các lỗi khác
            messagebox.showerror("Lỗi Không Xác Định", f"Đã có lỗi xảy ra: {e}")

    # Hàm cập nhật nội dung ô chỉ đọc
    def _update_readonly_entry(self, entry_widget, text):
        entry_widget.config(state="normal")
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, text)
        entry_widget.config(state="readonly")

    # Hàm xóa toàn bộ dữ liệu trên giao diện
    def clear_fields(self):
        self.private_entries['a'].delete(0, tk.END); self.private_entries['b'].delete(0, tk.END)
        self._update_readonly_entry(self.public_entries['a'], ""); self._update_readonly_entry(self.public_entries['b'], "")
        self._update_readonly_entry(self.shared_key_val, "")
        self.p_combo.current(0); self.update_g_options(None) # Reset về giá trị mặc định
        self.private_entries['a'].focus() # Đặt con trỏ vào ô nhập a

    # Hàm đặt cửa sổ ra giữa màn hình
    def center_window(self):
        self.root.update_idletasks() # Cập nhật để lấy kích thước đúng
        width = self.root.winfo_reqwidth(); height = self.root.winfo_reqheight()
        screen_width = self.root.winfo_screenwidth(); screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2)); y = int((screen_height / 2) - (height / 2))
        self.root.geometry(f"{width}x{height}+{x}+{y}"); self.root.minsize(width, height)

# --- 3. ĐIỂM KHỞI CHẠY CỦA CHƯƠNG TRÌNH ---
if __name__ == "__main__":
    # Khởi tạo cửa sổ chính với theme "litera"
    root = ttk.Window(themename="litera")
    app = DiffieHellmanApp(root)
    # Bắt đầu vòng lặp sự kiện chính của giao diện
    root.mainloop()