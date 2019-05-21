import unittest
import sys, os, time
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
import bloom_filter, black_list
import logging, time

import random
import string
def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

class TestCorrectness(unittest.TestCase):
    def init_logging(self, name='testname', log_level=logging.WARNING):
        fileh = logging.FileHandler(f'./log/{name}-{logging.getLevelName(log_level)}.log', 'w', encoding='utf-8')
        # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter('%(message)s')
        fileh.setFormatter(formatter)

        log = logging.getLogger()  # root logger
        for hdlr in log.handlers[:]:  # remove all old handlers
            log.removeHandler(hdlr)
        log.addHandler(fileh)      # set the new handler
        log.setLevel(log_level)

        return fileh


    def test_correctness(self):
        fileh = self.init_logging('correctness', logging.DEBUG)
        b = bloom_filter.BloomFilter(capacity=100)
        added = b.add('Hello')
        logging.info(f'added Hello: {added}')
        
        added = b.add('Hello')
        logging.info(f'added Hello: {added}')
        
        logging.info(f'b.count: {b.count}')

        logging.info(f'Hello in b: {"Hello" in b}')

        logging.info(f'Hola in b: {"Hola" in b}')

        logging.info(f'remove Hola: {b.remove("Hola")}')

        logging.info(f'remove Hello: {b.remove("Hello")}')

        logging.info(f'b.count: {b.count}')

        fileh.close()
    
    def test_benchmark(self):
        fileh = self.init_logging('benchmark', logging.INFO)
        capacity=10000
        arrayBL = black_list.ArrayBasedBlackList()
        bloomBL = black_list.BloomFilterBlackList(capacity=capacity)
        logging.info(f'===== Benchmark =====')
        logging.info(str(bloomBL.bloomfilter))
        logging.info(f'===== Benchmark =====\n')
        
        logging.info(f'Benchmarking add into array...')
        begin = time.time()
        for i in range(capacity):
            string = randomString()
            arrayBL.add(string)
        end = time.time()
        logging.info(f'Time used: {end-begin}\n')

        logging.info(f'Benchmarking add into bloom filter...')
        begin = time.time()
        for i in range(capacity):
            string = randomString()
            bloomBL.add(string)
        end = time.time()
        logging.info(f'Time used: {end-begin}\n')

        arrayBL.clear()
        bloomBL.clear()
        for i in range(capacity):
            string = randomString()
            arrayBL.add(string)
            bloomBL.add(string)
        
        correct_cnt = 0
        logging.info(f'Benchmarking contains for array...')
        begin = time.time()
        for i in range(capacity):
            # 本来应该在其中
            if arrayBL.array[i] in arrayBL:
                correct_cnt += 1
            # 本来应该不在其中
            if not randomString(11) in arrayBL:
                correct_cnt += 1
        end = time.time()
        assert correct_cnt == 2 * capacity
        logging.info(f'Time used: {end-begin}\n')

        
        correct_cnt = 0
        logging.info(f'Benchmarking contains for bloom filter...')
        begin = time.time()
        for i in range(capacity):
            if arrayBL.array[i] in bloomBL:
                correct_cnt += 1
            if not randomString(11) in bloomBL:
                correct_cnt += 1
        end = time.time()
        logging.info(f'Time used: {end-begin}\n')
        
        correct_rate = correct_cnt / (2 * capacity)

        logging.info(f'Correct rate of the bloom filter: {correct_rate * 100}%')

        fileh.close()

if __name__ == "__main__":
    unittest.main()
