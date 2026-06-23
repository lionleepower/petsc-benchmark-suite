# 03 GroupBy Aggregate: 重复实验怎么合并？

本节目标：把重复实验合并成每个配置一个点。

## 为什么要聚合？

`runtime_results.csv` 中，同一个 `(scale, total_cores, threads)` 可能有多次运行。画线图时，如果直接画所有重复点，会让图变乱。

这里选择 median runtime 作为主值：

```text
median_runtime_seconds
```

同时保留：

- `mean_runtime_seconds`
- `min_runtime_seconds`
- `max_runtime_seconds`
- `repeat_count`

这样既能画清楚主趋势，也能知道重复实验是否稳定。

## 运行

```bash
python scripts/03_groupby_aggregate.py
```

## 核心代码形状

```python
aggregated = (
    clean_df
    .groupby(["scale", "unknowns", "total_cores", "threads"], as_index=False)
    .agg(
        median_runtime_seconds=("runtime_seconds", "median"),
        mean_runtime_seconds=("runtime_seconds", "mean"),
        min_runtime_seconds=("runtime_seconds", "min"),
        max_runtime_seconds=("runtime_seconds", "max"),
        repeat_count=("runtime_seconds", "count"),
    )
)
```

## 输出

```text
outputs/runtime_scaling_aggregated_pandas.csv
```
