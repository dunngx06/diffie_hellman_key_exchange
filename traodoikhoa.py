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

        # Cài đặt logo cho cửa sổ
        try:
            self.root.iconbitmap('logo.ico')
        except tk.TclError:
            print("Lưu ý: Không tìm thấy file 'logo.ico'.")
        
        # Danh sách các cặp (p, g) có sẵn
        self.preset_groups = {
            "p = 23, g = 5": (23, 5),
            "p = 991, g = 7": (991, 7),
            "p = 2287, g = 2": (2287, 2),
            "p = 48611, g = 19": (48611, 19),
            "p = 1299709, g = 2": (1299709, 2),
        }
        
        self.create_widgets()
        self.center_window()
        
    # Hàm tạo tất cả các thành phần giao diện
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Phần 1: Giao diện chọn và nhập tham số p, g
        params_frame = ttk.LabelFrame(main_frame, text="1. Tham Số Công Khai (p, g)", padding="15")
        params_frame.pack(fill=tk.X, pady=(0, 10))
        params_frame.columnconfigure(2, weight=1)
        
        ttk.Label(params_frame, text="Chọn cặp (p, g) có sẵn:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.group_combo = ttk.Combobox(params_frame, values=list(self.preset_groups.keys()), state="readonly")
        self.group_combo.grid(row=0, column=1, columnspan=4, padx=5, pady=5, sticky="ew")
        self.group_combo.current(0)
        self.group_combo.bind("<<ComboboxSelected>>", self.on_group_select)

        ttk.Label(params_frame, text="Giá trị đang sử dụng:").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        ttk.Label(params_frame, text="p =").grid(row=1, column=1, padx=(5,0), pady=10, sticky="e")
        self.p_var = tk.StringVar()
        self.p_entry = ttk.Entry(params_frame, textvariable=self.p_var, width=15)
        self.p_entry.grid(row=1, column=2, padx=(5,10), pady=10, sticky="ew")

        ttk.Label(params_frame, text="g =").grid(row=1, column=3, padx=(5,0), pady=10, sticky="e")
        self.g_var = tk.StringVar()
        self.g_entry = ttk.Entry(params_frame, textvariable=self.g_var, width=10)
        self.g_entry.grid(row=1, column=4, padx=(5,5), pady=10, sticky="w")

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
        ttk.Label(result_frame, text="Khóa chung (K):").pack(anchor="w", pady=(10,2))
        self.shared_key_val = ttk.Entry(result_frame, state="readonly")
        self.shared_key_val.pack(fill=tk.X)
        
        self.clear_button = ttk.Button(main_frame, text="Xóa & Làm Lại", command=self.clear_fields, bootstyle="danger-outline")
        self.clear_button.pack(fill=tk.X, ipady=5, pady=(20,0))
        
        # Tải giá trị mặc định khi khởi động
        self.on_group_select(None)

    # --- CÁC HÀM XỬ LÝ SỰ KIỆN VÀ LOGIC ---

    # Hàm xử lý sự kiện khi chọn một cặp (p, g) từ danh sách
    def on_group_select(self, event):
        selected_group_name = self.group_combo.get()
        p, g = self.preset_groups[selected_group_name]
        self.p_var.set(str(p))
        self.g_var.set(str(g))

    # Hàm tạo và điền một số ngẫu nhiên an toàn vào ô khóa bí mật
    def generate_and_set_random_key(self, party):
        try:
            p = int(self.p_var.get())
            if p <= 3:
                messagebox.showwarning("Giá trị không hợp lệ", "Giá trị p phải lớn hơn 3 để tạo khóa ngẫu nhiên.")
                return
            
            random_key = secrets.randbelow(p - 3) + 2
            entry_widget = self.private_a_entry if party == 'a' else self.private_b_entry
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, str(random_key))
        except (ValueError, tk.TclError):
            messagebox.showerror("Lỗi", "Vui lòng nhập một giá trị p là số nguyên hợp lệ trước.")

    # Hàm kiểm tra một số có phải là số nguyên tố không
    def is_prime(self, n):
        if n < 2: return False
        if n in (2, 3): return True
        if n % 2 == 0 or n % 3 == 0: return False
        i = 5
        while i * i <= n:
            if n % i == 0 or n % (i + 2) == 0: return False
            i += 6
        return True

    # Hàm hiển thị hộp thoại cảnh báo Yes/No
    def _show_validation_warning(self, title, message):
        full_message = f"{message}\n\nBạn có muốn tiếp tục không?"
        return messagebox.askyesno(title, full_message, icon='warning')

    # Hàm kiểm tra tất cả các điều kiện của p, g, a, b
    def validate_inputs(self, p, g, a, b):
        if not self.is_prime(p):
            if not self._show_validation_warning("Cảnh Báo: p không hợp lệ", f"Giá trị p = {p} không phải là số nguyên tố."):
                return False
        
        if not (1 < g < p):
            if not self._show_validation_warning("Cảnh Báo: g không hợp lệ", f"Giá trị g = {g} nằm ngoài khoảng an toàn (1 < g < p)."):
                return False

        if not (1 < a < p - 1):
            if not self._show_validation_warning("Cảnh Báo: Khóa 'a' không an toàn", f"Khóa bí mật a = {a} nằm ngoài khoảng khuyến nghị (1 < a < p-1)."):
                return False

        if not (1 < b < p - 1):
            if not self._show_validation_warning("Cảnh Báo: Khóa 'b' không an toàn", f"Khóa bí mật b = {b} nằm ngoài khoảng khuyến nghị (1 < b < p-1)."):
                return False
        
        return True

    # Hàm chính, thực hiện toàn bộ quá trình tính toán trao đổi khóa
    def calculate_shared_key(self):
        try:
            p = int(self.p_var.get())
            g = int(self.g_var.get())
            a = int(self.private_a_entry.get())
            b = int(self.private_b_entry.get())
            
            if not self.validate_inputs(p, g, a, b):
                return
            
            # Tính toán các giá trị A, B, và K
            A = pow(g, a, p)
            B = pow(g, b, p)
            K = pow(B, a, p)

            # Cập nhật kết quả lên giao diện
            self._update_readonly_entry(self.public_a_val, str(A))
            self._update_readonly_entry(self.public_b_val, str(B))
            self._update_readonly_entry(self.shared_key_val, str(K))
            messagebox.showinfo("Thành công", f"Trao đổi khóa thành công!\nKhóa chung là: {K}")

        except ValueError:
            messagebox.showerror("Lỗi Đầu Vào", "Vui lòng nhập đầy đủ các giá trị p, g, a, b dưới dạng số nguyên.")
        except Exception as e:
            messagebox.showerror("Lỗi Không Xác Định", f"Đã có lỗi xảy ra: {e}")
            
    # Hàm trợ giúp để cập nhật nội dung cho ô chỉ đọc
    def _update_readonly_entry(self, entry_widget, text):
        entry_widget.config(state="normal")
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, text)
        entry_widget.config(state="readonly")

    # Hàm xóa tất cả dữ liệu trên giao diện để làm lại
    def clear_fields(self):
        self.private_a_entry.delete(0, tk.END)
        self.private_b_entry.delete(0, tk.END)
        self._update_readonly_entry(self.public_a_val, "")
        self._update_readonly_entry(self.public_b_val, "")
        self._update_readonly_entry(self.shared_key_val, "")
        self.group_combo.current(0)
        self.on_group_select(None)
        self.p_entry.focus()
        
    # Hàm đặt cửa sổ ra giữa màn hình khi khởi chạy
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_reqwidth()
        height = self.root.winfo_reqheight()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.minsize(width, height)

# --- 3. ĐIỂM KHỞI CHẠY CỦA CHƯƠNG TRÌNH ---
if __name__ == "__main__":
    # Khởi tạo cửa sổ chính với theme "litera"
    root = ttk.Window(themename="litera") 
    app = DiffieHellmanApp(root)
    # Bắt đầu vòng lặp của giao diện
    root.mainloop()