# 01 Read CSV: CSV 里到底有什么？

本节目标：用 `pandas` 读取 `runtime_results.csv`，先观察数据，不急着画图。

## 核心问题

我们要先知道：

- 有多少行？
- 有哪些列？
- 每列是什么类型？
- 前几行长什么样？
- 数值列有没有被当成字符串？

## 运行

```bash
python scripts/01_read_csv.py
```

## 你会看到什么

脚本会打印：

- CSV 路径
- `df.shape`
- `df.columns`
- `df.head()`
- `df.info()`
- 关键列的唯一值

## 关键概念

`pd.read_csv(...)` 会返回一个 `DataFrame`。可以把 `DataFrame` 理解成带列名的表格。

常用观察方法：

```python
df.head()
df.columns
df.info()
df.describe()
```

这些方法的目的不是做最终分析，而是避免在不了解数据时直接画图。
