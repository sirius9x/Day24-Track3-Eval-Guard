import json

try:
    with open('reports/ragas_50q.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    groups = {'factual': [], 'multi_hop': [], 'adversarial': []}
    for item in data:
        if 'distribution' in item:
            groups[item['distribution']].append(item)

    print('AGGREGATE:')
    for k, v in groups.items():
        if not v: continue
        print(f"[{k}]")
        for m in ['faithfulness', 'answer_relevancy', 'context_precision', 'context_recall', 'avg_score']:
            avg = sum(i[m] for i in v) / len(v)
            print(f"  {m}: {avg:.3f}")

    print('\nBOTTOM 10:')
    bottom_10 = sorted(data, key=lambda x: x['avg_score'])[:10]
    for i, item in enumerate(bottom_10, 1):
        print(f"{i}. [{item['distribution']}] {item['question'][:40]}... (avg: {item['avg_score']:.3f}, worst: {item['worst_metric']})")

except Exception as e:
    print("Error:", e)
