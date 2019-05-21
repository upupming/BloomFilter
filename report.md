# 随机算法实验 3 - BloomFilter 的抽象数据类型实现

<center>

主讲教师: 骆吉洲

姓名: 李一鸣    学号: 1160300625    日期: 2019 年 5 月 13 日

</center>

## 一、实验要求

实验目的为：

1. 理解和体会随机数据结构在数据内存管理中的效用
2. 理解用期望复杂性表示的计算效率结果
3. 理解随机数据结构支持确定型算法的效果
4. 规范撰写实验报告

实验内容为：

将 BloomFilter 实现为一种抽象数据类型，并用它支持一种应用。

实验步骤：

1. 将 BloomFilter 实现为一种抽象数据类型，支持按需初始化、元素插入、元素查找、结构销毁等基本操作
2. 将集合存储为整数数组，支持元素插入、元素查找；
3. 分别用上述两种方法管理黑名单（可以选择其他更有趣的应用）
4. 比较两种方案在插入、查找等操作在两种实现方式的性能
5. 思考你实现的BloomFilter能否有效支持集合元素的删除操作
6. 撰写实验报告

## 二、实验原理

### BloomFilter

对于计算问题：现有全集 $U$，其一个子集 $S \subset U$，对于给定的 $x \in U$，快速判断 $x \in S$ 是否成立。（这相当于查找操作）

BloomFilter 的示意图如下：

![20190513202101-2019-5-13.png](https://i.loli.net/2019/05/13/5cd96135be73211473.png)

正式定义如下：

- $n$: BloomFilter 的大小，一般远远小于元素个数
- $A$: BloomFilter 位向量，长度为 $n$
- $m$: 集合大小
- $S$: 元素集合，大小为 $m$
- $k$: 散列函数个数
- $h_i$: 第 $i$ 个散列函数

BloomFilter 由一个 $n$ 个二进制数字组成的数组组成，从 $A[0]$ 到 $A[n-1]$，开始时全都设置为 $0$，一个 Bloom 过滤器利用 $k$ 个值域为 $[0, \cdots, n-1]$ 的独立的散列函数 $h_1, \cdots, h_k$，为便于分析，我们作通常的假定：这些散列函数将全域中的每个元素都映射到值域 $[0, \cdots, n-1]$ 上的均匀随机数。假定用一个 BloomFilter 来表示一个来自全集 $U$ 的 $m$ 个元素的集合 $S = \{s_1, \cdots, s_m\}$，对于每个元素 $s \in S$，二进制数字 $A[h_i(s)]$ 设置为 $1$，其中 $i \in [1, k]$。一个二进制数字的位置可以多次被设置为 1，但只有第一次改变有作用。为了检查一个元素 $x$ 是否在 $S$ 中，我们检查所有数组位置 $A[h_i(x)]=1, i\in(1, k)$ 是否设置为 1。如果不是，那么 $x$ 显然不是 $S$ 的成员，因为 $x$ 如果在 $S$ 中，那么由 BloomFilter 的构造方法，所有位置 $A[h_i(x)], i\in(1,k)$ 都应该设置为 1。如果所有 $A[h_i(x)]$ 都是 $1$，我们就假定 $x$ 在 $S$ 中，虽然这可能是错误的。错误出现的情景是：虽然 $x$ 不在 $S$ 中，但是所有 $A[h_i(x)]$ 都是 $1$，是其他元素将这些位置为 $1$ 的。也就是说 **BloomFilter 可能出现假阳性**。下图是 BloomFilter 构造的一个例子：

![20190513203722-2019-5-13.png](https://i.loli.net/2019/05/13/5cd96505f011382434.png)

#### 假阳性的概率

一个不在集合中的元素的假阳性概率，在散列函数是随机选取的前提下，可以直接计算。

在 $S$ 中所有元素都散列为 BloomFilter 后，某一个二进制数字仍然是 $0$ 的概率为（一直未被散列函数选中）：

$$
p = \left(1-\frac{1}{n}\right)^{km} \approx e^{-km/n}
$$

为简化分析，我们暂且假定将 $S$ 的所有元素都散列为 BloomFilter 后，二进制数字仍然为 0 的比例是 $p$，那么假阳性的概率为（$k$ 个散列函数的结果都是 $1$）：

$$
f = \left(1-\left(1-\frac{1}{n}^{km}\right)\right)^k \approx (1-e^{-km/n})^k = (1-p)^k

\tag{1}
$$

#### 优化散列函数个数 $k$

假定 $m$ 和 $n$ 已知，希望优化散列函数的个数 $k$，从而极小化假阳性概率 $f$。存在两种对抗力量：利用较多的散列函数可以给我们较多的机会，对一个不是 $S$ 成员的元素找到一个二进制数字 $0$；但利用较少的散列函数能增加数组中二进制数字 $0$ 的比例。将假阳性概率视作为 $k$ 的函数，极小化 $f$，即可得到最优的散列函数个数。记 $g= \ln f = k\ln(1-e^{-km/n})$，我们要极小化 $f$，就是要极小化 $g$，将其对 $k$ 求导得到：

$$
\begin{aligned}
\frac{dg}{dk} 
&= \ln(1-e^{-km/n}) + k\frac{1}{1-e^{-km/n}}[-e^{-km/n}(-m/n)] \\
&= \ln(1-e^{-km/n}) + \frac{km}{n}\frac{e^{-km/n}}{1-e^{-km/n}} \\
\end{aligned}
$$

令导数为 $0$，得到 $k^* = \frac{n}{m}\ln 2$，此即极小值点，此时假阳性的概率 $f = (1/2)^{k^*}\approx(0.6185)^{n/m}$。当然 $k$ 必须是整数，所以 $k$ 的最好可能选择会导致一个稍高的假阳性概率。

#### 扩展：添加、删除元素

通过查阅论文发现，要在 BloomFilter 中插入元素非常简单，使用 $k$ 个散列函数对新加入的元素计算散列值并且将相应的位置为 $1$。但是我们无法逆向操作来删除一个元素，如果我们把某个元素 $k$ 个散列值对应的位都置为 $0$ 的话，那集合 $S$ 中其他元素的散列值为 $1$ 代表的位也可能会被置 $0$。这样。BloomFilter 就不能正确反映集合中元素的信息了。

解决办法是，BloomFilter 不再只是使用 $0/1$ 的二进制位，而是使用一个 **counter 计数器**，我们称之为 counting BloomFilter。

- 插入元素：相应的计数器加 $1$
- 删除元素：相应的计数器减 $1$

为了防止计数器上溢，我们可以选比较大的计数器。根据论文分析，每个计数器只需 $w=4$ 位即可应对大多数情况。

现在可以进行具体的分析，用 $c(i)$ 表示第 $i$ 个计数器对应的计数值，其服从二项分布：

$$
P[c(i) = j] = C_{mk}^j\left(\frac{1}{n}\right)^j\left(1-\frac{1}{n}\right)^{mk-j}
$$

任选一个计数器，其至少是 $j$ 的概率的上界是 $nP[c(i)\ge j]$，可以利用上面的公式进行计算，我们将其进行放缩得到：

$$
P[c(i) \ge j] \le C_{mk}^j\left(\frac{1}{n}\right)^j \le \left(\frac{emk}{jn}\right)^j
$$

假定我们控制 $k \le \frac{n}{m}\ln 2$，我们已经证明 $k=\frac{n}{m} \ln 2$ 时，假阳性概率最小，这样就有：

$$
P[\max_ic(i)\ge j] \le n \left(\frac{e \ln2}{j}\right)^j
$$

假设我们选择 $w$ 位作为计数器，有：

$$
P[\max_ic(i)\ge2^w] \le n \left(\frac{e \ln2}{2^w}\right)^{2^w}
$$

令 $w=4$，得到 $P[\max_ic(i)\ge 16] \le 1.37 \times 10^{-15} \times n$

## 三、实验过程

### BloomFilter 初始化

在 BloomFilter 初始化时，用户传入参数 `capacity` 和 `error_rate`，即 $m$ 和 $f$，我们需要根据这两个参数计算其他参数 $k, n$。

根据上面的讨论，散列函数个数 $k$ 满足下面的等式：

$$
k = \ln_{1/2}^f = \frac{-\ln f}{\ln2}
$$

同时又有

$$
k = \frac{n}{m}\ln 2
$$

即

$$
n = \frac{mk}{\ln 2} = \frac{m(-\ln f)}{\ln^2 2}
$$

这样我们就确定了 $k$ 和 $n$。

### BloomFilter 散列函数的生成

实验要求中写道：

> 通过简单的映射管理，黑名单中的每个元素可视为一个整数

但是我认为要实现更加实用的 BloomFilter，应该是支持每个元素是一个**字符串**才比较好。因此我们的散列函数就需要将一个字符串映射到一个下标，[pybloom](https://github.com/jaybaird/python-bloomfilter) 使用的是 `hashlib` 库中的散列函数来做的。我直接使用了 [StackOverflow 上推荐的](https://stackoverflow.com/a/16008760/8242705) `hash` 函数。

```py
>>> # Use hash()
>>> abs(hash(s)) % (10 ** 8)
82148974
```

### 支持删除

每个位上不再是一个位，而是 4 位的数。在此基础上可以进行删除，如前文所介绍的那样将相应的数减 1 即可。

### 正确性测试

对 `add`, `in` 操作进行测试得到下面的 Log 文件：

```txt
added Hello: True
added Hello: False
b.count: 1
Hello in b: True
```

### 性能测试

数据使用 `randomString` 随机生成：

```py
def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))
```

对于容量为 $m$ 的 BloomFilter，测试 $m$ 个所有在其中的元素，和 $m$ 个不在其中的元素，得到如下的测试结果。

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

## 实验感想

1. 实现过程中，遇到了许多困难，通过查阅论文对理论基础进行了夯实。在原来老师讲课的基础上实现了 BloomFilter 的删除操作。
2. 实验中遇到了一个函数数组的问题，不能直接在循环里面定义函数然后 `append` 到数组里面，比如这样：

    ```py
    funcs = []
    for i in range(n):
        def func(i)
            return i
        func.append(func)
    ```

    这样的话最终得到的数组包含的每个函数都是同一个函数，解决的办法可以参考我的代码，使用了一个 `get_hash_func` 来得到一个新的函数，避免所有函数指向同一个内存，而是每次需要的时候新创建一个，互相之间不干扰。

## 参考文献

1. Network application of Bloom Filter: A Survey,
Internet Mathematics, 1(4): 485-509, 2005.
2. P. Almeida, C.Baquero, N. Preguiça, D. Hutchison, Scalable Bloom Filters,
(GLOBECOM 2007), IEEE, 2007.