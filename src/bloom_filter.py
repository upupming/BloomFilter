import logging, math
from struct import unpack, pack, calcsize

class FourBitsVector(object):
    """
    因为 python 实现 4 位的数字似乎没有解决方案
    所以我是用 byte 来存两个 4 位的数字
    """
    def __init__(self, size):
        self.bytes = bytearray(size // 2 + 1)
    def increment(self, index):
        # 0 -> 0, 前 4 位
        # 1 -> 0, 后 4 位
        real_index = index // 2
        is_end = (index % 2 == 1)
        
        logging.debug(f'real_index = {real_index}, is_end = {is_end}')
        logging.debug(f'before increment: {self.bytes[real_index]}')
        if is_end:
            self.bytes[real_index] += 1
        else:
            self.bytes[real_index] += 1 << 4
        logging.debug(f'after increment: {self.bytes[real_index]}')
    def decrement(self, index):
        # 0 -> 0, 前 4 位
        # 1 -> 0, 后 4 位
        real_index = index // 2
        is_end = (index % 2 == 1)
        
        logging.debug(f'real_index = {real_index}, is_end = {is_end}')

        logging.debug(f'before decrement: {self.bytes[real_index]}')
        if is_end:
            self.bytes[real_index] -= 1
        else:
            self.bytes[real_index] -= 1 << 4
        logging.debug(f'after decrement: {self.bytes[real_index]}')
    def has(self, index):
        # 0 -> 0, 前 4 位
        # 1 -> 0, 后 4 位
        real_index = index // 2
        is_end = (index % 2 == 1)
        
        logging.debug(f'real_index = {real_index}, is_end = {is_end}')
        logging.debug(f'has test: {self.bytes[real_index]}')
        if is_end:
            return (self.bytes[real_index] & 0x0F) > 0
        else:
            return (self.bytes[real_index] & 0xF0) > 0

class BloomFilter(object):
    def __init__(self, capacity, error_rate=0.001):
        """BloomFilter 实现

        capacity
            在假阳性概率小于 *error_rate* 的前提下，此 BloomFilter 至少可以存储 *capacity* 个元素
        error_rate
            假阳性概率，这个值决定了 BloomFilter 的大小，如果插入的元素太多，BloomFilter 的错误率会显著增加
        """
        if not (0 < error_rate < 1):
            raise ValueError('error_rate 必须介于 (0, 1) 之间')
        if not capacity > 0:
            raise ValueError('capacity 必须大于 0')
        
        # n = 位向量长度, k = 散列函数个数, f = 假阳性概率, m = 容量
        # TODO: 不按照公式来，错误率是否会上升
        m = capacity
        f = error_rate
        k = int(math.ceil(math.log(1.0 / f, 2)))
        n = int(math.ceil(
            (m * abs(math.log(f))) /
            ((math.log(2) ** 2))
        ))
        logging.debug(f'f = {f}, k = {k}, n = {n}, m = {m}')
        self._setup(f, k, n, m, 0)

    def _get_hash_funcs(self, num_funcs, limit):
        """
        哈希函数值上限，不超过 limit
        """
        
        # 必须层次嵌套，避免返回相同引用
        # 类似 JS 中的闭包
        def get_hash_func(i):
            def hash_func(key):
                # logging.debug(f'Key: {key + str(i)}')
                return hash(key + str(i)) % limit
            return hash_func

        funcs = []
        for i in range(num_funcs):
            funcs.append(get_hash_func(i))
        return funcs

    def _setup(self, error_rate, num_hashfuncs, num_bits, capacity, count=0):
        """
        error_rate
            假阳性概率
        num_hashfunctions
            哈希函数个数
        num_bits
            位向量长度
        capacity
            BloomFilter 的容量
        """
        self.error_rate = error_rate
        self.num_hashfuncs = num_hashfuncs
        self.num_bits = num_bits
        self.capacity = capacity
        self.count = count
        self.bitarray = FourBitsVector(self.num_bits)
        self.hash_funcs = self._get_hash_funcs(num_hashfuncs, num_bits)

        # for hash_func in self.hash_funcs:
        #     hash_func('test')
        # exit()

    def __str__(self):
        res = f'Capacity(m) = {self.capacity}\n' \
            + f'Error rate(f) = {self.error_rate}\n' \
            + f'Number of hash functions(k): {self.num_hashfuncs}\n' \
            + f'Number of bits(n) = {self.num_bits}'
        return res

    def __len__(self):
        return self.count

    def add(self, key):
        """
        新增元素，已经存在的话不添加并返回 False，否则返回 True
        """
        if self.count >= self.capacity:
            raise IndexError('BloomFilter 已满')
        
        found_all_bits = True
        for hash_func in self.hash_funcs:
            if not self.bitarray.has(hash_func(key)):
                found_all_bits = False
                break
        
        # 不在，插入
        if not found_all_bits:
            self.count += 1
            for hash_func in self.hash_funcs:
                index = hash_func(key)
                self.bitarray.increment(index)
            return True
        # 已经存在，不必插入
        else:
            return False
    def remove(self, key):
        """
        删除元素，不存在的话不删除并返回 False，否则返回 True
        """
        if self.count == 0:
            raise IndexError('BloomFilter 已空')
        
        found_some_none_bits = False
        for hash_func in self.hash_funcs:
            if not self.bitarray.has(hash_func(key)):
                found_some_none_bits = True
                break
        # 不在，无法删除
        if found_some_none_bits:
            return False
        else:
            self.count -= 1
            for hash_func in self.hash_funcs:
                self.bitarray.decrement(hash_func(key))
            return True


    def __contains__(self, key):
        for hash_func in self.hash_funcs:
            # 一旦发现了 0，就直接不在了
            if not self.bitarray.has(hash_func(key)):
                return False
        return True
    def __len__(self):
        return self.count