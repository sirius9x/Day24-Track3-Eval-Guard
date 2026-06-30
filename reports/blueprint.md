# CI/CD Blueprint: RAG Eval + Guardrail Stack

**Sinh viên:** Sirius
**Ngày:** 30/06/2026

---

## Guard Stack Architecture

```
User Input
    │
    ▼ (~2ms P95)
[Presidio PII Scan]
    │ block if: VN_CCCD / VN_PHONE / EMAIL detected
    │ action:   return 400 + "PII detected in query"
    ▼ (~250ms P95)
[NeMo Input Rail]
    │ block if: off-topic / jailbreak / prompt injection
    │ action:   return 503 + refuse message
    ▼
[RAG Pipeline (Day 18)]
    │ M1 Chunk → M2 Search → M3 Rerank → GPT-4o-mini
    ▼
[NeMo Output Rail]
    │ flag if:  PII in response / sensitive content
    │ action:   replace with safe response
    ▼
User Response
```

---

## Latency Budget

*(Điền từ kết quả Task 12 — measure_p95_latency())*

| Layer | P50 (ms) | P95 (ms) | P99 (ms) | Budget |
|---|---|---|---|---|
| Presidio PII | 1638.0 | 3319.3 | 3319.3 | <10ms |
| NeMo Input Rail | 143.3 | 291.1 | 291.1 | <300ms |
| RAG Pipeline | 1200 | 1800 | 2200 | <2000ms |
| NeMo Output Rail | 210 | 290 | 360 | <300ms |
| **Total Guard** | 1779.4 | **3496.6** | 3496.6 | **<500ms** |

**Budget OK?** [ ] Yes / [x] No  
**Comment:** Việc sử dụng API LLM (GPT-4o-mini) cho cả Input và Output Rail làm tăng độ trễ đáng kể. Điểm nghẽn (bottleneck) nằm ở thời gian chờ network API. Cần tự host mô hình nhỏ hơn (như Llama-3-8B với vLLM) chuyên cho Guardrails để giảm latency, hoặc song song hóa (parallelize) các bước không phụ thuộc nhau.

---

## CI/CD Gates (phải pass trước khi merge to main)

```yaml
# .github/workflows/rag_eval.yml
- name: RAGAS Quality Gate
  run: python src/phase_a_ragas.py
  env:
    MIN_FAITHFULNESS: 0.75
    MIN_AVG_SCORE: 0.65

- name: Guardrail Gate
  run: pytest tests/test_phase_c.py -k "test_adversarial_suite_pass_rate"
  # phải ≥ 15/20 (75%)

- name: Latency Gate
  run: python -c "from src.phase_c_guard import measure_p95_latency; ..."
  # P95 total < 500ms
```

---

## Monitoring Dashboard (production)

| Metric | Alert Threshold | Action |
|---|---|---|
| RAGAS faithfulness (daily sample) | < 0.70 | Page on-call |
| Adversarial block rate | < 80% | Review new attack patterns |
| Guard P95 latency | > 600ms | Scale NeMo model |
| PII detected count | spike >10/hour | Security alert |

---

## Kết quả thực tế từ Lab

| | Kết quả |
|---|---|
| RAGAS avg_score (50q) | 0.85 |
| Worst metric | Faithfulness |
| Dominant failure distribution | Factual (Câu hỏi tra cứu thực tế) |
| Cohen's κ | 0.167 |
| Adversarial pass rate | 20 / 20 |
| Guard P95 latency | 3496.6 ms |

---

## Nhận xét & Cải tiến

> Hệ thống Guardrail bằng Presidio và NeMo hoạt động hiệu quả trong việc chặn lộ lọt thông tin cá nhân (PII) và các câu hỏi jailbreak cơ bản. Tuy nhiên, P95 latency đã vượt quá ngân sách cho phép (572ms > 500ms) do độ trễ lớn khi phải gọi qua LLM API hai vòng. Ngoài ra, module sinh RAG (Phase A) đang bộc lộ điểm yếu lớn nhất ở "Faithfulness" với các câu hỏi tra cứu thông tin tĩnh. Nếu lên production, tôi sẽ áp dụng "self-correction" ở khâu tạo RAG để cải thiện Faithfulness và host một mô hình nhỏ chuyên cho Guardrails ngay tại local để đảm bảo thời gian phản hồi ở mức dưới 500ms.
