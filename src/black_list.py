from bloom_filter import *

class ArrayBasedBlackList(object):
    def __init__(self):
        self.array = []
    def add(self, item):
        self.array.append(item)
    def delete(self, item):
        self.array.remove(item)
    def __contains__(self, item):
        return self.array.count(item) > 0
    def clear(self):
        self.array = []

class BloomFilterBlackList(object):
    def __init__(self, capacity=1000):
        self.bloomfilter = BloomFilter(capacity)
    def add(self, item):
        self.bloomfilter.add(item)
    def delete(self, item):
        self.bloomfilter.remove(item)
    def __contains__(self, item):
        return self.bloomfilter.__contains__(item)
    def clear(self):
        self.bloomfilter = BloomFilter(self.bloomfilter.capacity)