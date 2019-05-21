# BloomFilter

Author: Li Yiming

BloomFilter implementation in python, deletion is supported.

See my [report](report.md) (in Chinese) for more technical information.

Run test cases and see the logs under `log` folder (you have to manually create it if not exist):

```bash
python test/test.py
```

The log file with `INFO` is a simple version of log, and `DEBUG` is a more verbose version of log.

For example, the `benchmark-INFO.log` file has only the summary of the algorithm result and time used:

```txt
===== Benchmark =====
Capacity(m) = 10000
Error rate(f) = 0.001
Number of hash functions(k): 10
Number of bits(n) = 143776
===== Benchmark =====

Benchmarking add into array...
Time used: 0.3128187656402588

Benchmarking add into bloom filter...
Time used: 1.3782086372375488

Benchmarking contains for array...
Time used: 5.337045431137085

Benchmarking contains for bloom filter...
Time used: 0.7575616836547852

Correct rate of the bloom filter: 99.955%
```

## Reference

1. Network application of Bloom Filter: A Survey, Internet Mathematics, 1(4): 485-509, 2005.
2. Probability and Computing, section 5.5.3