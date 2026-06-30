# LLM Judge Bias Report — Phase B

**Sinh viên:** Đoàn Xuân Thạch
**Mã số sinh viên:** 2A202600950
**Ngày:** 30/06/2026
**Judge model:** gpt-4o-mini

---

# LLM Judge Bias Report — Phase B

**Sinh viên:** Sirius
**Ngày:** 30/06/2026
**Judge model:** gpt-4o-mini

---

## 1. Pairwise Judge Results

*(Chạy pairwise_judge() trên ít nhất 5 cặp answers)*

| # | Question (tóm tắt) | Winner | Reasoning tóm tắt |
|---|---|---|---|
| 1 | Nhân viên được nghỉ bao nhiêu ngày khi kết hôn? | B | Ground truth (B) chính xác và đầy đủ chi tiết hơn A. |
| 2 | Bảo hiểm sức khỏe PVI có hạn mức bao nhiêu cho nhân viên? | tie | A và B ngang nhau nhưng thiếu tính nhất quán khi swap. |
| 3 | Phụ cấp ăn trưa hàng tháng là bao nhiêu? | B | Ground truth (B) trả lời đúng trọng tâm hơn. |
| 4 | Mentor và buddy của nhân viên mới có thể là cùng một người không? | tie | Mâu thuẫn khi đổi vị trí, LLM không thể quyết định rõ ràng. |
| 5 | Muốn mua thiết bị trị giá 55 triệu cần ai phê duyệt? | B | B đưa ra chính xác thông tin phê duyệt hơn. |

---

## 2. Swap-and-Average Results

*(Chạy swap_and_average() trên cùng các cặp)*

| # | Pass 1 Winner | Pass 2 Winner | Final | Position Consistent? |
|---|---|---|---|---|
| 1 | B | B | B | True |
| 2 | B | tie | tie | False (Position bias) |
| 3 | B | B | B | True |
| 4 | B | A | tie | False (Position bias) |
| 5 | B | B | B | True |

**Position bias rate:** 20% (= 4 case NOT consistent / 20 tổng)

---

## 3. Cohen's κ Analysis

**Human labels:** `human_labels_10q.json` (10 câu, 5 label=1, 5 label=0)  
**Judge labels:** [0, 1, 0, 1, 1, 0, 0, 1, 0, 1]

| Question ID | Human Label | Judge Label | Agree? |
|---|---|---|---|
| 1 | 0 | 0 | Yes |
| 5 | 1 | 1 | Yes |
| 12 | 0 | 0 | Yes |
| 21 | 1 | 1 | Yes |
| 23 | 0 | 1 | No |
| 29 | 0 | 0 | Yes |
| 33 | 1 | 0 | No |
| 41 | 1 | 1 | Yes |
| 46 | 0 | 0 | Yes |
| 50 | 1 | 1 | Yes |

**Cohen's κ:** 0.167  
**Interpretation:** slight agreement

---

## 4. Verbosity Bias

Trong các case có winner rõ ràng (không phải tie):
- A thắng + A dài hơn B: 0 / 12 cases
- B thắng + B dài hơn A: 11 / 12 cases  
- **Verbosity bias rate:** 91.7%

**Kết luận:** LLM có xu hướng nhỏ trong việc thiên vị các câu trả lời dài hơn nếu độ phân giải chất lượng giữa A và B không đủ cao. Việc này là vấn đề lớn vì người dùng RAG ưu tiên sự súc tích ("conciseness"). Nếu LLM Judge bị Verbosity bias, pipeline sẽ bị phạt nhầm các câu trả lời ngắn-gọn-đúng-trọng-tâm.

---

## 5. Nhận xét chung

> - Hệ số κ = 0.167 ở mức *slight*, cho thấy LLM judge khá bất đồng với con người ở các câu hỏi đánh đố.
> - Position bias ở mức 20% (thấp hơn ngưỡng nguy hiểm 30%), tuy nhiên vẫn chứng tỏ LLM có xu hướng "lười" đổi đáp án khi ta đảo vị trí.
> - Swap-and-average cực kỳ hữu ích, giúp loại bỏ các trường hợp LLM không chắc chắn (gây ra position bias) bằng cách chuyển chúng về trạng thái "tie" an toàn. Trong 20 cặp, nó đã chuyển được 8 trường hợp hòa hoặc mâu thuẫn thành `tie` một cách hợp lý.
> - Trong môi trường production, LLM-as-a-judge nên được dùng dưới dạng swap-and-average qua cronjob hàng ngày để kiểm tra một tệp ngẫu nhiên (sample), và cần dùng một model lớn (như GPT-4o thay vì mini) để tối đa hoá điểm Cohen's κ.
