import os
import json
import random
import requests
from datetime import datetime, timedelta

TELEGRAM_TOKEN   = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]
ANTHROPIC_KEY    = os.environ["ANTHROPIC_KEY"]

# ── Thông tin cá nhân ────────────────────────────────────────────────────────
HO_TEN    = "Trương Minh Trí"
NGAY_SINH = "08/04/2006"

# ── Bộ bài Tarot (22 lá Major Arcana) ───────────────────────────────────────
TAROT = [
    "The Fool (Kẻ Ngốc)", "The Magician (Nhà Ảo Thuật)", "The High Priestess (Nữ Tư Tế)",
    "The Empress (Hoàng Hậu)", "The Emperor (Hoàng Đế)", "The Hierophant (Giáo Hoàng)",
    "The Lovers (Đôi Tình Nhân)", "The Chariot (Cỗ Xe)", "Strength (Sức Mạnh)",
    "The Hermit (Ẩn Sĩ)", "Wheel of Fortune (Bánh Xe Số Phận)", "Justice (Công Lý)",
    "The Hanged Man (Người Treo Ngược)", "Death (Cái Chết)", "Temperance (Điều Độ)",
    "The Devil (Ác Quỷ)", "The Tower (Tháp)", "The Star (Ngôi Sao)",
    "The Moon (Mặt Trăng)", "The Sun (Mặt Trời)", "Judgement (Phán Xét)",
    "The World (Thế Giới)"
]

# ── Bộ bài Lenormand (36 lá) ─────────────────────────────────────────────────
LENORMAND = [
    "Kỵ Sĩ (Tin tức đến)", "Cỏ Ba Lá (May mắn nhỏ)", "Con Tàu (Hành trình)",
    "Ngôi Nhà (Ổn định)", "Cây (Sức khỏe)", "Đám Mây (Sự mơ hồ)",
    "Con Rắn (Cám dỗ)", "Quan Tài (Kết thúc)", "Bó Hoa (Niềm vui)",
    "Lưỡi Hái (Mất mát)", "Cái Roi (Xung đột)", "Chim (Trò chuyện)",
    "Đứa Trẻ (Mới mẻ)", "Con Cáo (Khôn ngoan)", "Gấu (Sức mạnh)",
    "Ngôi Sao (Hy vọng)", "Cò (Thay đổi)", "Chó (Trung thành)",
    "Tháp (Cô đơn)", "Vườn (Xã hội)", "Núi (Trở ngại)",
    "Ngã Tư (Quyết định)", "Chuột (Hao mòn)", "Tim (Tình cảm)",
    "Chiếc Nhẫn (Cam kết)", "Cuốn Sách (Bí ẩn)", "Bức Thư (Tin nhắn)",
    "Người Đàn Ông (Nam giới)", "Người Phụ Nữ (Nữ giới)", "Hoa Lily (Bình yên)",
    "Mặt Trời (Thành công)", "Mặt Trăng (Cảm xúc)", "Chìa Khóa (Giải pháp)",
    "Cá (Tài chính)", "Neo (Ổn định lâu dài)", "Thập Tự (Thử thách)"
]

# ── Bộ bài Mặt Trăng (13 pha) ───────────────────────────────────────────────
MOON_CARDS = [
    "🌑 Trăng Mới – Khởi đầu, gieo hạt ý tưởng mới",
    "🌒 Trăng Lưỡi Liềm Đầu – Hành động, tiến về phía trước",
    "🌓 Bán Nguyệt Đầu – Quyết định, vượt qua thách thức",
    "🌔 Trăng Khuyết Đầu – Phát triển, tích lũy năng lượng",
    "🌕 Trăng Tròn – Viên mãn, thu hoạch, soi sáng sự thật",
    "🌖 Trăng Khuyết Cuối – Biết ơn, chia sẻ thành quả",
    "🌗 Bán Nguyệt Cuối – Buông bỏ, tái cấu trúc",
    "🌘 Trăng Lưỡi Liềm Cuối – Nghỉ ngơi, nội tâm",
    "🌙 Trăng Đen – Bí ẩn, năng lượng ẩn sâu",
    "🌛 Trăng Nữ Thần – Trực giác mạnh, lắng nghe nội tâm",
    "🌜 Trăng Crone – Trí tuệ, nhìn thấu bản chất",
    "⭐ Trăng Sao – Ước mơ, kết nối vũ trụ",
    "🌌 Trăng Huyền Bí – Chuyển hóa sâu sắc, thức tỉnh"
]

# ── Âm lịch đơn giản (can chi) ───────────────────────────────────────────────
CAN  = ["Giáp","Ất","Bính","Đinh","Mậu","Kỷ","Canh","Tân","Nhâm","Quý"]
CHI  = ["Tý","Sửu","Dần","Mão","Thìn","Tỵ","Ngọ","Mùi","Thân","Dậu","Tuất","Hợi"]
NGU_HANH = {
    "Giáp":"Mộc 🌿","Ất":"Mộc 🌿","Bính":"Hỏa 🔥","Đinh":"Hỏa 🔥",
    "Mậu":"Thổ 🌍","Kỷ":"Thổ 🌍","Canh":"Kim ⚡","Tân":"Kim ⚡",
    "Nhâm":"Thủy 💧","Quý":"Thủy 💧"
}

def get_can_chi(year: int, month: int, day: int):
    # Tính can chi năm
    can_nam = CAN[(year - 4) % 10]
    chi_nam = CHI[(year - 4) % 12]
    # Tính can chi ngày (công thức đơn giản)
    jd = day + (month * 30) + (year * 365)
    can_ngay = CAN[jd % 10]
    chi_ngay = CHI[jd % 12]
    ngu_hanh = NGU_HANH.get(can_ngay, "Thổ 🌍")
    return can_nam, chi_nam, can_ngay, chi_ngay, ngu_hanh

def tinh_so_chu_dao(ngay: int, thang: int, nam: int) -> int:
    s = sum(int(c) for c in f"{ngay:02d}{thang:02d}{nam}")
    while s > 9 and s not in [11, 22, 33]:
        s = sum(int(c) for c in str(s))
    return s

def call_claude(prompt: str) -> str:
    headers = {
        "x-api-key":         ANTHROPIC_KEY,
        "anthropic-version": "2023-06-01",
        "content-type":      "application/json",
    }
    body = {
        "model":      "claude-haiku-4-5-20251001",
        "max_tokens": 1000,
        "messages":   [{"role": "user", "content": prompt}]
    }
    r    = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=body, timeout=30)
    data = r.json()
    return data["content"][0]["text"]

def send_telegram(msg: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={
        "chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"
    }, timeout=10)

def main():
    now      = datetime.utcnow() + timedelta(hours=1)  # BST UK
    ngay     = now.day
    thang    = now.month
    nam      = now.year
    thu      = ["Thứ Hai","Thứ Ba","Thứ Tư","Thứ Năm","Thứ Sáu","Thứ Bảy","Chủ Nhật"][now.weekday()]
    hom_nay  = now.strftime("%d/%m/%Y")

    # Rút bài ngẫu nhiên
    tarot      = random.choice(TAROT)
    lenormand  = random.choice(LENORMAND)
    moon       = random.choice(MOON_CARDS)

    # Can chi & ngũ hành
    can_nam, chi_nam, can_ngay, chi_ngay, ngu_hanh = get_can_chi(nam, thang, ngay)
    so_chu_dao = tinh_so_chu_dao(8, 4, 2006)  # ngày sinh Trí

    # Gọi Claude để generate nội dung
    prompt = f"""Bạn là một thầy bói phương Đông kết hợp tarot hiện đại, uyên thâm và hài hước nhẹ nhàng.

Hôm nay là {thu}, ngày {hom_nay}.
- Ngày can chi: {can_ngay} {chi_ngay} | Năm: {can_nam} {chi_nam}
- Ngũ hành ngày: {ngu_hanh}
- Lá Tarot hôm nay: {tarot}
- Lá Lenormand hôm nay: {lenormand}
- Lá Mặt Trăng hôm nay: {moon}
- Người xem: {HO_TEN}, sinh {NGAY_SINH}, số chủ đạo {so_chu_dao}

Hãy viết thông điệp ngày hôm nay cho Trí theo cấu trúc sau (viết bằng tiếng Việt, thân thiện, ngắn gọn, mỗi phần 2-3 câu):

1. ⚡ NĂNG LƯỢNG NGÀY: Giải thích ngũ hành và can chi hôm nay ảnh hưởng thế nào
2. 🃏 TAROT – {tarot}: Ý nghĩa lá bài và thông điệp cho Trí hôm nay
3. 🌿 LENORMAND – {lenormand}: Ý nghĩa và lời khuyên
4. {moon.split('–')[0].strip()} LÁ TRĂNG: Ý nghĩa pha trăng và năng lượng
5. 🔮 DỰ ĐOÁN TỔNG HỢP: Tổng hợp tất cả, dự đoán ngày hôm nay của Trí sẽ như thế nào, lưu ý gì
6. 💫 CÂU THẦN CHÚ HÔM NAY: 1 câu ngắn truyền cảm hứng cho Trí

Viết tự nhiên như người bạn thân đang nhắn tin, không cần format cứng nhắc."""

    reading = call_claude(prompt)

    # Build Telegram message
    msg = (
        f"🌟 *NHẬT KÝ VŨ TRỤ – {thu.upper()} {hom_nay}*\n"
        f"_Dành riêng cho {HO_TEN}_\n\n"
        f"📅 *Can Chi:* {can_ngay} {chi_ngay} | Năm {can_nam} {chi_nam}\n"
        f"🎴 Tarot: *{tarot}*\n"
        f"🌿 Lenormand: *{lenormand}*\n"
        f"{moon}\n\n"
        f"{'─'*30}\n\n"
        f"{reading}"
    )

    send_telegram(msg)
    print(f"✅ Đã gửi nhật ký vũ trụ ngày {hom_nay}")

if __name__ == "__main__":
    main()
