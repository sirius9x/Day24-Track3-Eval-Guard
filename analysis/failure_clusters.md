# Failure Cluster Analysis — Phase A

**Sinh viên:** Đoàn Xuân Thạch
**Mã số sinh viên:** 2A202600950
**Ngày:** 30/06/2026

---

## 1. Aggregate RAGAS Scores theo Distribution

| Metric | factual | multi_hop | adversarial |
|---|---|---|---|
| faithfulness | 0.753 | 0.476 | 0.500 |
| answer_relevancy | 0.663 | 0.457 | 0.376 |
| context_precision | 0.771 | 0.871 | 0.700 |
| context_recall | 0.800 | 0.604 | 0.517 |
| **avg_score** | 0.747 | 0.602 | 0.523 |

---

## 2. Bottom 10 Questions

| Rank | Distribution | Question | avg_score | worst_metric |
|---|---|---|---|---|
| 1 | factual | Nhân viên được nghỉ bao nhiêu ngày khi kết hôn? | 0.000 | faithfulness |
| 2 | factual | Nhân viên được nghỉ bao nhiêu ngày khi cha hoặc mẹ mất? | 0.000 | faithfulness |
| 3 | factual | Nam nhân viên được nghỉ bao nhiêu ngày khi vợ sinh con? | 0.000 | faithfulness |
| 4 | adversarial | Theo chính sách nghỉ phép cũ (v2023), nhân viên được nghỉ... | 0.000 | faithfulness |
| 5 | multi_hop | Lương thử việc của nhân viên Junior mức cao nhất là bao nhiêu? | 0.146 | faithfulness |
| 6 | multi_hop | Nếu cần mua một chiếc laptop 30 triệu cho nhân viên mới... | 0.208 | faithfulness |
| 7 | multi_hop | Nhân viên vừa kết hôn và cùng tuần đó có con kết hôn... | 0.208 | faithfulness |
| 8 | adversarial | Nhân viên Manager có thể dùng VPN cá nhân khi WFH... | 0.208 | faithfulness |
| 9 | adversarial | Nhân viên được nghỉ bao nhiêu ngày phép năm? | 0.250 | faithfulness |
| 10 | multi_hop | Một nhân viên Senior có 9 năm thâm niên được nghỉ... | 0.333 | faithfulness |

---

## 3. Failure Cluster Matrix

*(Mỗi ô = số câu có worst_metric = row, thuộc distribution = col)*

| worst_metric | factual | multi_hop | adversarial | Total |
|---|---|---|---|---|
| faithfulness | 4 | 11 | 5 | 20 |
| answer_relevancy | 13 | 4 | 1 | 18 |
| context_precision | 2 | 0 | 1 | 3 |
| context_recall | 1 | 5 | 3 | 9 |

---

## 4. Dominant Failure Analysis

**Dominant distribution:** factual
**Dominant metric:** faithfulness

**Lý do phân tích:**

> Nhóm factual lại dễ bị lỗi `answer_relevancy` và `faithfulness` nhất. Điều này thường do chunking cắt không đúng ngữ cảnh làm LLM không lấy được câu trả lời chính xác, hoặc LLM tự suy diễn thay vì bám sát 100% vào policy (do policy tiếng Việt dễ có cách diễn đạt vòng vo). Đặc biệt `faithfulness` cực kỳ thấp ở multi_hop (11 câu) vì LLM phải tổng hợp nhiều chunk nhưng lại ghép nối sai logic.

---

## 5. Suggested Fixes

| Metric yếu | Root cause | Suggested fix |
|---|---|---|
| faithfulness | LLM tự suy diễn (hallucination) | Giảm temperature của LLM về 0, áp dụng kỹ thuật Self-Correction trong prompt. |
| context_recall | Thiếu đoạn văn bản liên quan | Tăng hệ số Top-K khi retrieval, hoặc áp dụng thêm Semantic Search bên cạnh BM25. |
| context_precision | Chunk bị nhiễu quá nhiều | Cấu hình lại Cross-Encoder reranker chặt chẽ hơn để loại bỏ nhiễu. |
| answer_relevancy | Trả lời không đúng trọng tâm | Yêu cầu LLM thực hiện bước suy luận Chain-of-Thought (CoT) trước khi chốt câu trả lời cuối cùng. |

---

## 6. Nhận xét về Adversarial Distribution

> Adversarial là distribution có điểm số `avg_score` thấp nhất (0.523) so với Factual (0.747) và Multi-hop (0.602). Pipeline đặc biệt bối rối với các bẫy hỏi về chính sách cũ (v2023) so với hiện hành (v2024), hoặc các câu hỏi phủ định (như hỏi về VPN cá nhân). Trong top 10 câu tệ nhất, có tới 3 câu rơi vào nhóm Adversarial và tất cả đều chết ở lỗi `faithfulness`. Do đó, cần bổ sung metadata mapping version của policy vào chunk để Reranker có thể lọc bớt chính sách lỗi thời.
