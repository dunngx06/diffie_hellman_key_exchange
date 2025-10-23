import math

def get_prime_factors(n):
    """
    Hàm này trả về một tập hợp (set) các thừa số nguyên tố
    phân biệt của n.
    """
    factors = set()
    
    # Kiểm tra số 2
    while n % 2 == 0:
        factors.add(2)
        n //= 2
        
    # Kiểm tra các số lẻ từ 3 trở đi
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        while n % i == 0:
            factors.add(i)
            n //= i
            
    # Nếu n vẫn còn là một số lớn hơn 2
    if n > 2:
        factors.add(n)
        
    return factors

def find_limited_primitive_roots(p, max_g=100, count_limit=10):
    """
    Tìm căn nguyên thủy cho p, kiểm tra từ 2 đến max_g,
    và dừng lại khi tìm thấy 'count_limit' số.
    """
    
    if p == 2:
        return [1] # Trường hợp đặc biệt

    phi = p - 1
    prime_factors = get_prime_factors(phi)
    
    primitive_roots = [] 
    
    # Bắt đầu kiểm tra từ g = 2 đến max_g (vì 1 không phải căn)
    for g in range(2, max_g + 1):
        is_primitive = True
        
        for q in prime_factors:
            if pow(g, phi // q, p) == 1:
                is_primitive = False
                break 
        
        if is_primitive:
            primitive_roots.append(g)
            
            # --- ĐIỀU KIỆN DỪNG MỚI ---
            # Nếu đã đủ số lượng, dừng tìm kiếm cho số p này
            if len(primitive_roots) >= count_limit:
                break # Thoát khỏi vòng lặp 'for g'
            
    return primitive_roots

# --- CHƯƠNG TRÌNH CHÍNH ---

# Danh sách các số nguyên tố cần kiểm tra
primes_to_check = [
    23, 
    97, 
    991, 
    2287, 
    7919, 
    104743, 
    1299709, 
    15485863, 
    2147483647 
]

# Cập nhật các biến điều khiển
max_check_range = 100  # Kiểm tra đến 100
max_results_count = 10 # Dừng khi tìm thấy 10

print(f"--- Kiểm tra căn nguyên thủy (từ 2 đến {max_check_range}) ---")
print(f"--- Dừng khi tìm thấy {max_results_count} giá trị đầu tiên cho mỗi số ---")
print("-" * 75)

for p in primes_to_check:
    results = find_limited_primitive_roots(p, max_check_range, max_results_count)
    
    if results:
        roots_str = ", ".join(map(str, results))
        print(f"Số nguyên tố {p:>10}: {len(results)} căn tìm thấy: {roots_str}")
    else:
        # Trường hợp này gần như không xảy ra với p lớn
        print(f"Số nguyên tố {p:>10}: KHÔNG tìm thấy trong khoảng [2, {max_check_range}]")

print("-" * 75)