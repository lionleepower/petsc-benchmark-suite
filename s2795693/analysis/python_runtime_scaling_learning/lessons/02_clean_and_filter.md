# 02 Clean and Filter: 哪些数据可以用于画图？

本节目标：把原始 CSV 变成适合 Runtime Scaling 图的数据。

## 核心问题

画图前要明确：

- 只用成功完成的实验：`status == "completed"`
- 只比较指定线程数：`T = 1, 2, 4, 8`
- 确认数值列确实是 numeric
- 验证 `total_cores = nodes x ppn x threads`

## 运行

```bash
python scripts/02_clean_and_filter.py
```

## 关键概念

`pandas` 常见过滤写法：

```python
completed = df[df["status"] == "completed"]
selected = completed[completed["threads"].isin([1, 2, 4, 8])]
```

常见类型转换写法：

```python
df["runtime_seconds"] = pd.to_numeric(df["runtime_seconds"], errors="coerce")
```

`errors="coerce"` 的意思是：如果某个值无法转换成数字，就变成 `NaN`，方便之后检查和过滤。

## 检查点

脚本会打印：

- 清洗前后行数
- 保留下来的 `threads`
- 保留下来的 `scale`
- `total_cores` 验证是否通过
