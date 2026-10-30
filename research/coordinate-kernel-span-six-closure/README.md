# 剩余 24 类坐标核结构的八调用不可能性

结论：在 PR5231 指定的四寄存器形式阿贝尔 BIT 模型中，剩余 24 类
坐标核结构均不能在地址张成维数为 6 时，以 8 次秩一调用实现三个
可逆的 3×3 有理地址矩阵目标。辅助输入任意，辅助输出允许任意对角单项式。

核心是一个保留原坐标的 3+1 分块，而不是继续扩大搜索。
代表结构的三个非坐标投影都在第四行和第四列为零，所有允许的坐标
投影也保持这一分块。三寄存器子词的关系空间通过补零嵌入原关系空间，
故关系秩至多为 2。由 PR720 第 1—4 节的互不相交子集引理，三块输出的
地址秩之和不超过该子词调用数；孤立坐标的地址秩不超过其调用数。
因此总秩 ≤8，与三个满秩目标所需的总秩 ≥9 矛盾。

完整英文证明见 PROOF.md，依赖来源及当前主分支快照见 SOURCES.json
。沿用的引理归 David Govea / PR720 及其 PR468、PR288、
PR203 前驱工作；24/48 分类和题目来源归 woklerx、unpaidmoon 和
Nick Petalas。新贡献仅为坐标隔离归约及相应检查。

运行（仅 Python 标准库，无网络、无第三方依赖）：

```sh
python3 -I -B verify.py
python3 -I -O -B verify.py
```

检查覆盖全部 24 个坐标置换池、96 种数据寄存器位置组合、七字母表中
长度 1—4 的全部 2800 个形式词、逆元抵消、模型边界反例，以及一个
地址维数为 6 的九调用正例。有限检查不是八调用全枚举；普遍结论由
PROOF.md 的推导及明确引用的前驱引理支持。没有重新证明该引理、执行
原有完整分类程序或进行证明助手核验。

结果待维护者审阅；没有修改乘法指数 κ。
跨度 5 的一般耦合结构与更多辅助寄存器的情况仍不在此结果内。

Nicholas Stone，OpenAI Codex 提供实质性证明、代码及整理协助。
新材料采用 Apache-2.0；前驱来源及其署名已在 PROOF.md 和 SOURCES.json 中注明。

## Open next questions

See TASK.json: frame-span five with one dirty auxiliary remains outside this proof. Its relation rank is three; begin with three-dimensional off-diagonal pattern spaces and exact chronological endpoints.
