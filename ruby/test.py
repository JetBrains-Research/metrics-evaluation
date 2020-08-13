import json

from ruby.similarity import ruby

data = json.load(open('to-grade/all-singles.json', 'r'))
for field in ['baseline', 'tranx-annot', 'best-tranx', 'best-tranx-rerank']:
    print(f'Results for {field}:')
    for d in data[:5]:
        sample = d[field].replace('`', '"')
        reference = d['snippet']
        print(f'Sample: {sample}')
        print(f'Reference: {reference}')
        print(ruby(sample, reference))
        print()

    print('=' * 20)
