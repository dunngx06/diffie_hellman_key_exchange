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
    # Hàm khởi tạo, thiết lập các thuộc tính và giao diện ban đầu
    def __init__(self, root):
        self.root = root
        self.root.title("Minh Họa Thuật Toán Trao Đổi Khóa Diffie-Hellman")

        try:
            self.root.iconbitmap('logo.ico')
        except tk.TclError:
            print("Lưu ý: Không tìm thấy file 'logo.ico'.")
        
        # Mở rộng đáng kể danh sách p và các căn nguyên thủy g tương ứng
        self.prime_data = {
            23: [5, 7, 10, 11],
            97: [5, 7, 10, 13],
            991: [6, 7, 11, 13],
            2287: [2, 10, 11, 13],
            7919: [3, 6, 7, 11],  # Số nguyên tố thứ 1000
            48611: [19, 20, 21, 23],
            104743: [2, 3, 5, 6], # Số nguyên tố thứ 10,000
            1299709: [2, 5, 8, 10] # Số nguyên tố thứ 100,000
        }
        
        self.create_widgets()
        self.center_window()
        
    # Hàm tạo tất cả các thành phần giao diện
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Thiết kế lại giao diện chọn và nhập p, g trên một hàng
        params_frame = ttk.LabelFrame(main_frame, text="1. Tham Số Công Khai (p, g)", padding="15")
        params_frame.pack(fill=tk.X, pady=(0, 10))
        params_frame.columnconfigure(1, weight=1) # Cho phép cột của p co giãn
        params_frame.columnconfigure(3, weight=1) # Cho phép cột của g co giãn
        
        ttk.Label(params_frame, text="Chọn p:").grid(row=0, column=0, padx=(0,5), pady=5, sticky="w")
        self.p_var = tk.StringVar()
        # --- THAY ĐỔI: Thêm bootstyle="primary" ---
        self.p_combo = ttk.Combobox(params_frame, textvariable=self.p_var, values=list(self.prime_data.keys()), bootstyle="primary")
        self.p_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.p_combo.bind("<<ComboboxSelected>>", self.on_p_selected)
        self.p_combo.bind("<KeyRelease>", self.on_p_manual_input) # Bắt sự kiện người dùng gõ phím

        ttk.Label(params_frame, text="Chọn g:").grid(row=0, column=2, padx=(10,5), pady=5, sticky="w")
        self.g_var = tk.StringVar()
        # --- THAY ĐỔI: Thêm bootstyle="primary" ---
        self.g_combo = ttk.Combobox(params_frame, textvariable=self.g_var, bootstyle="primary")
        self.g_combo.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # Phần 2 & 3: Giao diện nhập khóa bí mật cho Bên A và Bên B
        parties_frame = ttk.Frame(main_frame)
        parties_frame.pack(fill=tk.X, pady=10)
        parties_frame.columnconfigure(0, weight=1)
        parties_frame.columnconfigure(1, weight=1)
        
        # Giao diện bên A
        frame_a = ttk.LabelFrame(parties_frame, text="2. Bên A", padding="15")
        frame_a.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        ttk.Label(frame_a, text="Nhập hoặc tạo khóa bí mật (a):").pack(anchor="w", pady=(0, 2))
        input_a_frame = ttk.Frame(frame_a)
        input_a_frame.pack(fill=tk.X, pady=(0, 10))
        self.private_a_entry = ttk.Entry(input_a_frame)
        self.private_a_entry.pack(side="left", expand=True, fill=tk.X)
        self.random_a_btn = ttk.Button(input_a_frame, text="Ngẫu nhiên", command=lambda: self.generate_and_set_random_key('a'), bootstyle="secondary")
        self.random_a_btn.pack(side="left", padx=(5,0))
        ttk.Label(frame_a, text="Khóa công khai (A):").pack(anchor="w", pady=(0, 2))
        self.public_a_val = ttk.Entry(frame_a, state="readonly")
        self.public_a_val.pack(fill=tk.X)
        
        # Giao diện bên B
        frame_b = ttk.LabelFrame(parties_frame, text="3. Bên B", padding="15")
        frame_b.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        ttk.Label(frame_b, text="Nhập hoặc tạo khóa bí mật (b):").pack(anchor="w", pady=(0, 2))
        input_b_frame = ttk.Frame(frame_b)
        input_b_frame.pack(fill=tk.X, pady=(0, 10))
        self.private_b_entry = ttk.Entry(input_b_frame)
        self.private_b_entry.pack(side="left", expand=True, fill=tk.X)
        self.random_b_btn = ttk.Button(input_b_frame, text="Ngẫu nhiên", command=lambda: self.generate_and_set_random_key('b'), bootstyle="secondary")
        self.random_b_btn.pack(side="left", padx=(5,0))
        ttk.Label(frame_b, text="Khóa công khai (B):").pack(anchor="w", pady=(0, 2))
        self.public_b_val = ttk.Entry(frame_b, state="readonly")
        self.public_b_val.pack(fill=tk.X)
        
        # Phần 4: Giao diện hiển thị kết quả và các nút chức năng
        result_frame = ttk.LabelFrame(main_frame, text="4. Khóa Chung Bí Mật", padding="15")
        result_frame.pack(fill=tk.X, pady=10)
        self.calc_button = ttk.Button(result_frame, text="Thực Hiện Trao Đổi & Tính Khóa Chung", command=self.calculate_shared_key, bootstyle="primary")
        self.calc_button.pack(fill=tk.X, ipady=5, pady=5)
        ttk.Label(result_frame, text="Khóa chung (Shared Secret K):").pack(anchor="w", pady=(10,2))
        self.shared_key_val = ttk.Entry(result_frame, state="readonly")
        self.shared_key_val.pack(fill=tk.X)
        
        self.clear_button = ttk.Button(main_frame, text="Xóa & Làm Lại", command=self.clear_fields, bootstyle="danger-outline")
        self.clear_button.pack(fill=tk.X, ipady=5, pady=(20,0))
        
        # Tải giá trị mặc định khi khởi động
        self.p_combo.current(0)
        self.on_p_selected(None)

    # --- CÁC HÀM XỬ LÝ SỰ KIỆN VÀ LOGIC ---

    # Cập nhật logic xử lý sự kiện
    def on_p_selected(self, event):
        """Hàm được gọi khi người dùng chọn một giá trị p từ danh sách."""
        try:
            p = int(self.p_combo.get())
            if p in self.prime_data:
                g_values = self.prime_data[p]
                self.g_combo['values'] = g_values
                self.g_var.set(g_values[0]) # Tự động chọn giá trị g đầu tiên
        except (ValueError, tk.TclError):
            self.g_combo['values'] = []
            self.g_var.set("")

    def on_p_manual_input(self, event):
        """Hàm được gọi khi người dùng tự gõ vào ô p."""
        # Khi người dùng tự gõ, chúng ta xóa danh sách của g vì không biết p có hợp lệ không
        self.g_combo['values'] = []
        
    def generate_and_set_random_key(self, party):
        try:
            p = int(self.p_var.get())
            if p <= 3:
                messagebox.showwarning("Giá trị không hợp lệ", "Giá trị p phải là số nguyên tố lớn hơn 3 để tạo khóa ngẫu nhiên.")
                return
            random_key = secrets.randbelow(p - 3) + 2
            entry_widget = self.private_a_entry if party == 'a' else self.private_b_entry
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, str(random_key))
        except (ValueError, tk.TclError):
            messagebox.showerror("Lỗi", "Vui lòng nhập một giá trị p là số nguyên tố hợp lệ trước.")

    def is_prime(self, n):
        if n < 2: return False
        if n in (2, 3): return True
        if n % 2 == 0 or n % 3 == 0: return False
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0: return False
            i += 6
        return True
    
    def _get_prime_factors(self, n):
        factors = set(); d = 2
        while d * d <= n:
            while (n % d) == 0: factors.add(d); n //= d
            d += 1
        if n > 1: factors.add(n)
        return list(factors)

    def is_primitive_root(self, g, p):
        if not self.is_prime(p): return False
        phi = p - 1; factors = self._get_prime_factors(phi)
        for factor in factors:
            if pow(g, phi // factor, p) == 1: return False
        return True

    def _show_validation_warning(self, title, message):
        full_message = f"{message}\n\nBạn có muốn tiếp tục không?"
        return messagebox.askyesno(title, full_message, icon='warning')

    def validate_inputs(self, p, g, a, b):
        if not self.is_prime(p):
            if not self._show_validation_warning("Cảnh Báo: p không hợp lệ", f"Giá trị p = {p} không phải là số nguyên tố."): return False
        if not self.is_primitive_root(g, p):
            if not self._show_validation_warning("Cảnh Báo: g không hợp lệ", f"Giá trị g = {g} không phải là căn nguyên thủy của p = {p}."): return False
        if not (1 < a < p - 1):
            if not self._show_validation_warning("Cảnh Báo: Khóa 'a' không an toàn", f"Khóa bí mật a = {a} nằm ngoài khoảng khuyến nghị (1 < a < p-1)."): return False
        if not (1 < b < p - 1):
            if not self._show_validation_warning("Cảnh Báo: Khóa 'b' không an toàn", f"Khóa bí mật b = {b} nằm ngoài khoảng khuyến nghị (1 < b < p-1)."): return False
        return True

    def calculate_shared_key(self):
        try:
            p = int(self.p_var.get()); g = int(self.g_var.get())
            a = int(self.private_a_entry.get()); b = int(self.private_b_entry.get())
            if not self.validate_inputs(p, g, a, b): return
            A = pow(g, a, p); B = pow(g, b, p); K = pow(B, a, p)
            self._update_readonly_entry(self.public_a_val, str(A))
            self._update_readonly_entry(self.public_b_val, str(B))
            self._update_readonly_entry(self.shared_key_val, str(K))
            messagebox.showinfo("Thành công", f"Trao đổi khóa thành công!\nKhóa chung là: {K}")
        except ValueError:
            messagebox.showerror("Lỗi Đầu Vào", "Vui lòng nhập đầy đủ các giá trị p, g, a, b dưới dạng số nguyên.")
        except Exception as e:
            messagebox.showerror("Lỗi Không Xác Định", f"Đã có lỗi xảy ra: {e}")
            
    def _update_readonly_entry(self, entry_widget, text):
        entry_widget.config(state="normal"); entry_widget.delete(0, tk.END); entry_widget.insert(0, text); entry_widget.config(state="readonly")

    def clear_fields(self):
        self.private_a_entry.delete(0, tk.END); self.private_b_entry.delete(0, tk.END)
        self._update_readonly_entry(self.public_a_val, ""); self._update_readonly_entry(self.public_b_val, "")
        self._update_readonly_entry(self.shared_key_val, "")
        self.p_combo.current(0); self.on_p_selected(None)
        
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_reqwidth(); height = self.root.winfo_reqheight()
        screen_width = self.root.winfo_screenwidth(); screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2)); y = int((screen_height / 2) - (height / 2))
        self.root.geometry(f"{width}x{height}+{x}+{y}"); self.root.minsize(width, height)

# --- 3. ĐIỂM KHỞI CHẠY CỦA CHƯƠNG TRÌNH ---
if __name__ == "__main__":
    root = ttk.Window(themename="litera") 
    app = DiffieHellmanApp(root)
    root.mainloop()