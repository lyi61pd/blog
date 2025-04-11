---
title: Clickhouse
date: 2025-04-11
tags:
    - Clickhouse
---

# ClickHouse的架构与设计理念
## ClickHouse的整体架构概览
ClickHouse 是一个开源的列式数据库，由 Yandex 开发，专为 **在线分析处理（OLAP）** 场景而设计。它的架构设计强调 **高吞吐、低延迟** 和 **可横向扩展**。

**架构核心组件**

1. **Server 节点**
    - ClickHouse 的基本运行单位是一个服务进程（通常是一个 `clickhouse-server` 实例），它负责处理客户端请求、执行查询、管理存储等。
2. **表引擎（Table Engines）**
    - 表的存储和管理依赖引擎，最核心的是 **MergeTree** 及其衍生类型（如 ReplacingMergeTree、SummingMergeTree）。
    - 每种引擎定义了数据如何存储、如何合并、如何处理TTL等规则。
3. **查询引擎（Query Processor）**
    - 查询经过解析器 → 分析器 → 优化器 → 执行器的层层处理。
    - 查询最终会被向量化处理，高效执行。
4. **分布式支持**
    - 通过 `Distributed` 表引擎实现横向扩展，支持分布式存储与查询。
    - 使用 `ZooKeeper` 协调副本、分片、故障恢复。
5. **系统表（system. 系列）**
    - ClickHouse内部维护了大量系统表，可用于监控、诊断、调优。

---

## 列式数据库的设计理念与优势
ClickHouse 是列式存储的数据库，这意味着它将每一列的数据单独存储在磁盘上，而不是传统行式数据库那样按行存储。

**优势包括：**

+ **更高的压缩率**：同一列中的数据类型一致，便于压缩算法发挥最大效能。
+ **更快的读取速度**：只读取查询涉及的列，IO 开销极低。
+ **高效的向量化计算**：将列数据作为批处理单位，提升 CPU 使用效率。

---

## MergeTree 表引擎基础概念
MergeTree 是 ClickHouse 中最重要的表引擎，几乎所有的功能（如排序键、TTL、物化视图）都建立在它之上。

**核心特性：**

+ **分区（partition by）**：将数据按照某个维度分区管理，提高查询效率与数据管理灵活性。
+ **主键（order by）**：数据在写入时按照主键进行有序组织，支持范围查找和跳跃索引,。
+ **数据分片（parts）**：数据不是整体存储，而是以“Part”为单位增量写入。
+ **后台合并（Merge）**：ClickHouse定期将小的Part合并为大的Part，优化读取性能和空间利用率。

---

# Clickhouse的主键与Mysql的主键的区别
在 **ClickHouse** 和 **MySQL** 中，主键的概念有所不同，因为这两个数据库系统的设计目标和架构有所区别。虽然两者的主键都用于唯一标识记录，但它们的实现方式和作用有所不同。

## MySQL 主键
1. **定义**：
    - 在 **MySQL** 中，主键是一个或多个列的组合，用于唯一标识表中的每一行记录。主键必须是唯一的，并且不能为 **NULL**。
2. **存储与索引**：
    - 在 **MySQL** 中，主键不仅是唯一标识符，它还会自动创建一个 **聚簇索引（Clustered Index）**。这意味着数据行会按照主键的顺序存储在磁盘上，主键的顺序决定了物理存储的顺序。
    - 如果主键由多个列组成，那么这些列的组合会共同决定记录在数据库中的存储顺序。
3. **索引类型**：
    - MySQL 的主键通常是基于 **B+树索引**，适合高效的范围查询和单个记录的查找。B+树索引使得在查找时可以快速定位到对应的行。
4. **作用**：
    - **唯一性**：主键确保每一行数据在表中的唯一性。
    - **查询效率**：由于主键是聚簇索引，它可以显著提高查询性能，尤其是通过主键查找记录时。

## ClickHouse 主键
1. **定义**：
    - 在 **ClickHouse** 中，主键并不像传统数据库（如 MySQL）那样是唯一约束的索引。ClickHouse 的主键主要用于数据的 **排序**，而不是用于唯一性约束。
    - 主键是通过 `ORDER BY` 子句定义的，用来指定数据在存储时的排序顺序。数据并不要求唯一，主键更多的是决定存储方式，以优化查询性能。
2. **存储与索引**：
    - 在 **ClickHouse** 中，表中的数据并不按主键的顺序存储，而是按照 **MergeTree** 引擎的排序规则存储。通过主键指定的排序列决定了数据的 **物理存储顺序**，这有助于优化按这些列进行的查询。
    - **ClickHouse** 的主键不会像 MySQL 那样创建聚簇索引。ClickHouse 的 **MergeTree** 引擎使用 **数据部分（parts）** 来存储数据，并通过索引文件（primary key index）来加速查询。
3. **索引类型**：
    - **ClickHouse** 使用的是 **稀疏索引**（Sparse Index），它与 B+ 树的传统索引不同。ClickHouse 通过在数据块中存储列的最小值和最大值来构建索引，以优化范围查询。主键定义了如何在这些数据块中进行查询和定位。
4. **作用**：
    - **排序优化**：主键的定义帮助 ClickHouse 对数据进行排序，这对于按排序列进行的范围查询非常有效。
    - **没有唯一性约束**：与 MySQL 的主键不同，ClickHouse 中的主键并不强制保证唯一性，它仅用于优化查询。
    - **性能优化**：主键列通常是查询中常用的列，特别是当这些列用于 `ORDER BY` 或 `WHERE` 子句时，排序和索引能够大幅提升查询性能。

## 主要区别
1. **唯一性**：
    - **MySQL**：主键必须唯一，并且每个表只能有一个主键。
    - **ClickHouse**：主键不保证唯一性，它只用于数据的排序优化，不强制要求唯一。
2. **物理存储**：
    - **MySQL**：主键对应的列会影响物理存储顺序，因为主键是聚簇索引，数据行存储的顺序与主键顺序一致。
    - **ClickHouse**：主键影响数据的排序顺序，但不控制数据的物理存储顺序。主键只是优化查询的一个手段，数据本身并不要求按照主键排序存储。
3. **索引结构**：
    - **MySQL**：主键使用**聚簇索引**，基于 B+ 树，适用于范围查询和精确查找。
    - **ClickHouse**：主键使用**稀疏索引**，并通过 `MergeTree` 引擎优化数据分布，更多的是用于查询优化而不是唯一性验证。
4. **查询性能**：
    - **MySQL**：由于主键的聚簇索引，MySQL 对主键相关查询非常高效，特别是精确查找。
    - **ClickHouse**：主键通过控制数据的物理排序来优化范围查询和批量数据访问，特别是在按主键排序的查询中，性能有显著提升。

## 总结
+ **MySQL** 的主键主要是用来保证数据的唯一性，并且通过聚簇索引加速查询。
+ **ClickHouse** 的主键并不要求唯一性，而是主要用于 **数据排序** 和 **查询优化**，特别是在使用 `MergeTree` 引擎时，通过主键来定义数据的存储顺序，优化范围查询。

---

# 底层数据结构
## ClickHouse 的列式存储格式
ClickHouse 是原生的列式数据库，它将每一列的数据单独存储为多个文件，而不是一整行。

****

**每列的数据存储结构**

对于每个字段，ClickHouse 可能生成如下几种文件（以 MergeTree 表为例）：

+ `.bin`（或无后缀）：列的实际数据文件（经过编码与压缩）
+ `.mrk3`：**mark文件**，用于快速定位数据块中的位置
+ `.idx`（bitmap索引等引擎特有）：
+ `.default`：记录 default 表达式结果（如果有）

这些文件按列存储，并以 **part** 为单位组织在磁盘上。每个 part 包含所有列的若干数据段。

---

## 数据组织单位：Part
ClickHouse 的写入不是直接追加数据，而是每次写入都会生成一个新的 **Part**。

****

**Part 的核心特点：**

+ 是不可变的（immutable）
+ 存储在磁盘上一个独立的目录中
+ 包含分区信息、索引、数据列文件、元数据文件
+ 文件结构：

```plain
all_0_0_0/
  columns.txt
  primary.idx
  checksums.txt
  data/
    column1.bin, column1.mrk3
    column2.bin, column2.mrk3
```

****

**Part 的命名结构：**

格式为 `{partition}_{min_block}_{max_block}_{level}`，例如：

+ `202404_1_10_1` 表示：
    - 分区是 202404
    - 包含的块号是从1到10
    - 合并层级为1

ClickHouse 会通过后台合并机制把多个 Part 合并成一个更大的 Part，减少碎片、优化查询。

---

## 主键与索引机制
ClickHouse 的主键不是唯一性约束，而是**数据的物理排序依据**，用于范围查找优化。

### 主键索引（primary.idx）
+ 以每 `N` 行（默认8192）为一个数据块，对主键字段建立 min/max 索引。
+ 存储在 `primary.idx` 中，每个 entry 对应一段数据的起始位置。
+ 查询时可快速跳过不匹配的数据块（称为 **粗粒度索引**）。

### Skip Index（二级索引）
ClickHouse 还支持一些可选的辅助索引，用于跳过数据块：

+ `minmax`（最常用）：为某列记录每块的 min/max
+ `set`：记录块中出现过的值集合
+ `bloom_filter`：用于模糊匹配
+ `ngrambf_v1`：支持 LIKE '%xxx%' 模糊匹配优化

这些索引不会影响写入，但能显著提升过滤性能。

---

## 数据压缩与编码策略
ClickHouse 支持非常高效的压缩机制，是其性能的关键之一。

### 压缩流程：
1. 每列数据按 block 写入（默认最大64KB）
2. 每个 block 使用 LZ4（或 ZSTD）压缩
3. 某些数据类型还会使用 **特殊编码策略**：
    - 整型：Delta 编码、Gorilla 编码
    - 字符串：Dictionary 编码
    - Nullable：使用 bitmap 分离空值位图
    - LowCardinality：将字符串字段转为整数字典引用

压缩率常常达到 5～10 倍，远高于行式数据库。

---

## 分区（Partition）与分片（Shard）
ClickHouse 将数据分为多个 **分区（partition）**，每个分区下有多个 part。

+ 分区是逻辑组织单位，如按月、按日划分。
+ 写入新分区的数据不会触发旧分区的合并。
+ 分区字段常设为 `toYYYYMM(date)` 形式。



**分片（shard）**则是跨节点水平分布的数据副本，属于分布式部署概念，不直接影响本地数据结构。分片主要用于 **水平扩展**（Horizontal Scaling），通过将数据分布到不同的节点，来支持大规模数据的处理和存储。**分片** 是水平划分的，每个分片存储整个表的一部分数据，通常是按某种规则（如 `Hash` 或范围划分）将数据均匀分布到多个节点



**分片的特性**

1. **跨节点分布**：
    - 分片是 **跨多个节点的数据分布**，通常是为了提高系统的容量和处理能力。每个节点存储数据的一部分，这些部分被称为 **分片**（shard）。
    - **分片** 是水平划分的，每个分片存储整个表的一部分数据，通常是按某种规则（如 `Hash` 或范围划分）将数据均匀分布到多个节点。
2. **数据副本（Replica）**：
    - **分片** 和 **副本** 是分布式部署的核心概念。每个分片通常会有一个或多个 **副本**，副本用于容错和高可用性。当一个节点或分片出现故障时，系统可以自动从副本中恢复数据，保证服务的可用性。
    - 副本通常是分布式表的一部分，每个副本存储与其他副本相同的数据，但存储在不同的节点上。
3. **分片和查询**：
    - 当查询是针对整个表进行的，`Distributed` 引擎会自动将查询请求分发到相应的分片节点。分片负责处理本地数据并返回查询结果。
    - 通过使用分片，ClickHouse 能够支持大规模数据集的分布式查询，避免单节点过载，同时提高查询吞吐量。

---

## TTL 与数据生命周期
ClickHouse 支持在表级或字段级设置 TTL，用于自动删除或移动数据。

例如：

```sql
TTL event_time + INTERVAL 30 DAY DELETE
```

执行原理：

+ ClickHouse 后台定时任务扫描符合 TTL 条件的数据块
+ 构造新的 Part（删除或迁移）
+ 替换旧 Part，旧数据自动清理

这一机制也依赖 Part 的不可变性与自动合并能力。

---

## 小结
+ 数据是以列为单位存储在磁盘上的，每列有自己的 `.bin` 和 `.mrk3` 文件。
+ 数据写入生成不可变的 Part，后台进行合并优化。
+ 主键索引和辅助索引实现了高效的数据跳过（跳跃式扫描）。
+ 压缩、编码机制帮助 ClickHouse 在磁盘和内存间取得性能平衡。
+ Partition 逻辑管理数据生命周期与并发写入。
+ TTL 自动清理机制基于 Part 和合并逻辑运行。

---

# 分布式查询执行机制
当查询一个 `Distributed` 表时：

+ 查询在本地生成逻辑执行计划
+ 然后分发到每个分片的本地 MergeTree 表执行
+ 每个分片执行完返回结果，主节点进行 **Merge/Aggregate**

ClickHouse 会自动判断是否进行 **聚合下推**、**过滤下推**，从而减少跨网络传输。

---

# 存储引擎与文件系统交互机制
## MergeTree 表引擎的核心机制
MergeTree 是 ClickHouse 中最重要、最通用的表引擎。它支持有序写入、延迟合并、高效读取、TTL 清理等机制。



**设计目标**

+ **高并发写入（append-only + 异步合并）**
+ **快速查询（主键索引 + mark 跳跃）**
+ **灵活数据管理（分区、TTL、物化视图）**

MergeTree 是列式、不可变、基于 LSM 思路的引擎，但不同于 RocksDB 那种 key-value 模型，它以 block 和 column 为单位组织数据。

---

## 数据写入流程详解
1. **写入内存**
    - 接收 insert 数据，形成内存中的 `Block`
2. **数据编码 + 压缩**
    - 对每列进行编码、压缩处理
3. **落盘成 Part**
    - 每次 insert 都生成一个新的 `Part`，保存在磁盘上一个独立目录中
4. **更新元数据**
    - 包括 `columns.txt`, `checksums.txt`, `partition.dat`, `count.txt`
    - 同时更新主键索引文件（如 `primary.idx`）

写入流程采用批量式写入 + 不可变数据块，避免了行级锁和复杂并发控制。

---

## 磁盘文件结构
每个 Part 的文件组织如下：

```plain
202404_1_10_1/
├── columns.txt         -- 记录所有字段
├── checksums.txt       -- 所有文件校验信息
├── count.txt           -- 行数
├── partition.dat       -- 分区值
├── primary.idx         -- 主键索引（粗粒度）
├── column1.bin         -- 实际数据（压缩编码后）
├── column1.mrk3        -- mark 文件（跳跃索引）
├── ...
```

每列对应两个文件：

+ `.bin`：压缩列数据
+ `.mrk3`：跳跃索引（每 N 行标记偏移）

这种结构易于横向扩展（按列、按分区）和快速定位。

---

## mark 文件的作用
Mark 文件（`.mrk3`）用于支持 **跳跃式扫描**，原理是：

+ 每隔 N 行记录一个 “mark”
+ 每个 mark 保存当前列文件偏移位置（如偏移量、压缩块内位置）
+ 查询时可快速 seek 到指定 mark，避免线性扫描

默认一个 mark 间隔 8192 行（可调），决定了 I/O 粒度和内存消耗的权衡。

---

## Part 的合并（Merge）机制
为了防止磁盘碎片和读取效率下降，ClickHouse 会定期触发后台合并任务。

### 合并流程：
1. 挑选多个小 Part（同一分区内）
2. 解压 + 解码后 merge 成一个大 Part
3. 重新编码、压缩、写入新文件
4. 替换旧 Part，更新元数据

合并采用多线程并发执行，支持 IO 限速、按策略排序（如 TTL 优先、大小优先）

可通过 `system.merges` 观察合并状态。

---

## 磁盘空间策略（Disk & Volume）
ClickHouse 从 v20+ 支持将数据分布在多个磁盘/目录上。

### 存储策略（StoragePolicy）
通过定义 `Disk`, `Volume`, `StoragePolicy`：

```xml
<storage_configuration>
  <disks>
    <disk1>
      <path>/var/lib/clickhouse/disk1/</path>
    </disk1>
    <disk2>
      <path>/mnt/nvme/</path>
    </disk2>
  </disks>
  <policies>
    <hot_to_cold>
      <volumes>
        <hot>
          <disk>disk1</disk>
        </hot>
        <cold>
          <disk>disk2</disk>
        </cold>
      </volumes>
    </hot_to_cold>
  </policies>
</storage_configuration>
```

可以实现：

+ 热数据存 NVMe，冷数据归档到 SATA
+ 配合 TTL 进行分级迁移

---

## 缓存机制（Mark Cache、Uncompressed Cache）
ClickHouse 为提高查询性能，设计了两级缓存：

+ **Mark Cache（默认2GB）**
    - 缓存 mark 文件（跳跃索引），避免频繁读取 `.mrk3`
    - 作用：快速定位数据位置
+ **Uncompressed Cache（默认8GB）**
    - 缓存解压后的数据块（Block）
    - 作用：避免重复解压、提高重复查询速度

这两个缓存都驻留内存，可通过配置调整大小，适当扩大可明显提升查询性能。

---

## 其他存储优化技术
+ **Zero Copy Replication**：副本之间通过共享存储（如 S3、NFS）进行数据同步，避免拷贝
+ **分区裁剪**：查询时自动忽略无关分区，减少读取
+ **Compact Part**：小文件写入场景下启用“紧凑格式”Part，适合日志写入
+ **TTL MOVE TO DISK**：数据分层迁移 + 自动清理

---

## 小结
+ MergeTree 的核心机制基于 Part，不可变、易合并、列存
+ Part 文件结构详尽：数据 + 索引 + 校验 + 元数据
+ mark 索引为跳跃式扫描提供支持
+ 后台合并优化性能、释放空间
+ 多磁盘策略与缓存机制提升资源利用效率

---

# **实战分析与源码学习**
## 系统表分析
ClickHouse 提供大量以 `system.` 开头的系统表用于实时观察数据库内部状态，非常适合用于：

+ 查询调优
+ 瓶颈定位
+ 资源消耗监控
+ 数据合并与副本同步监控

****

**常用系统表**

| 表名 | 作用 |
| --- | --- |
| `system.parts` | 查看表中各个 Part 的信息（大小、状态、压缩率等） |
| `system.merges` | 当前正在进行的合并任务 |
| `system.replication_queue` | 副本同步队列，观察主从同步延迟 |
| `system.processes` | 当前正在执行的查询及其资源消耗 |
| `system.query_log` | 所有历史查询的执行日志（可配置保存时间） |
| `system.text_log` | ClickHouse 后台运行日志 |
| `system.metrics` | 实时系统性能指标，如内存、线程、cache 命中率 |
| `system.events` | 查询过程中触发的事件统计，例如 `SelectedParts`, `SelectedRows` |
| `system.trace_log` | CPU 栈追踪信息（用于定位复杂查询中的热点函数） |


通过结合 `EXPLAIN` 和 `system.query_log`，可以完整还原一次查询的执行过程。

---

## **查询慢的问题定位思路**
1. **分析查询计划**

```sql
EXPLAIN PLAN SELECT ...
```

查看是否存在全表扫描、JOIN 不走索引、聚合位置错误等。

2. **查看实际执行信息**

```sql
SELECT * FROM system.query_log WHERE query_id = '...'
```

包括读取的 part 数量、rows read、bytes read、memory usage 等。

3. **检查合并状态**

```sql
SELECT * FROM system.merges WHERE table = 'your_table'
```

频繁合并可能拖慢查询。

4. **辅助索引是否生效** 使用 `EXPLAIN PIPELINE` 查看是否启用了 min-max、bloom 过滤器。

---

## ClickHouse 源码结构总览
ClickHouse 的源码相对庞大，但结构清晰，主要分为以下几个核心模块（位于 `src/` 目录）：

### 核心模块结构
| 路径 | 内容 |
| --- | --- |
| `src/Storages/` | 各种表引擎，如 MergeTree、Kafka、Memory、Distributed |
| `src/Interpreters/` | 查询解析与执行计划生成模块 |
| `src/Processors/` | 执行器中的算子和执行 pipeline 实现 |
| `src/Columns/` | 列类型的实现（支持类型系统、向量化） |
| `src/DataTypes/` | 数据类型定义与转换 |
| `src/IO/` | 文件读写、压缩、缓冲层、缓存策略 |
| `src/Parsers/` | SQL 解析器（AST 构建） |
| `src/Common/` | 公共基础库，包括多线程、锁、内存池等 |
| `src/Core/` | 全局上下文定义、查询 ID 管理等 |


---

# MergeTree 家族
**所有 MergeTree 系列表引擎都有以下共同能力：**

+ 列式存储（高压缩、按需读取）
+ 主键有序（支持范围过滤）
+ 分区写入（支持按时间或字段拆分）
+ 数据 append-only（不可变 Part）
+ 后台合并（异步合并优化读取性能）
+ TTL 支持（按行/列自动清理或迁移）
+ 支持并发读写、高吞吐 insert
+ 支持多副本复制（Replicated 变体）

---

## MergeTree 家族成员一览
| 引擎名称 | 特殊能力 | 典型使用场景 |
| --- | --- | --- |
| `MergeTree` | 无特殊行为 | 通用查询、分析型写入 |
| `ReplacingMergeTree` | 删除重复数据（可选版本字段） | 幂等写入、幂等去重更新 |
| `SummingMergeTree` | 聚合同主键数据 | 实时累计、指标类数据 |
| `AggregatingMergeTree` | 支持复杂状态聚合合并 | 用户自定义聚合（UDF、HLL） |
| `CollapsingMergeTree` | 按标志列合并正负事件 | 日志型数据，标记删除 |
| `VersionedCollapsingMergeTree` | 同上 + 版本控制 | 日志场景下精确回滚 |
| `GraphiteMergeTree` | 针对 Graphite 监控数据设计 | 时间序列归档、聚合、清洗 |


还有对应的副本版本：

+ `ReplicatedMergeTree`（+ 所有以上派生变体都可用 `ReplicatedXXXMergeTree` 实现多副本）

---

## 关键变体深度解析
### ReplacingMergeTree
#### 特点：
+ 根据主键合并 **重复行**（可选提供 `version` 字段）
+ 多条相同主键的记录，保留“最新”版本（如果定义了 `version`）

#### 底层行为：
+ 合并过程中比较是否主键相同：
    - 无版本字段：保留其中任一条（不确定性）
    - 有版本字段：保留最大版本号的数据

#### 用法示例：
```sql
ENGINE = ReplacingMergeTree(version)
ORDER BY (id)
```

#### 场景：
+ 日志幂等写入（如 Kafka 重放）
+ 状态表更新（如最后一次登录记录）

---

### SummingMergeTree
#### 特点：
+ 对于主键相同的记录，在合并时自动进行 **数值字段求和**
+ 非数值字段将被忽略合并（丢弃）

#### 用法示例：
```sql
ENGINE = SummingMergeTree
ORDER BY (uid, date)
```

#### 注意：
+ 合并只在后台发生，查询时仍可能看到重复数据
+ 需要定期执行 `OPTIMIZE TABLE` 保证合并完成

#### 场景：
+ 实时流量统计、PV/UV 累计、财务计量汇总

---

### AggregatingMergeTree
#### 特点：
+ 专门支持 `AggregateFunction` 类型字段的合并
+ 合并时执行函数级别的聚合（如 `uniqState`、`avgState`）

#### 用法示例：
```sql
ENGINE = AggregatingMergeTree
ORDER BY (app, date)
```

字段定义示例：

```sql
AggregateFunction(uniq, UInt64) AS uv
```

#### 底层机制：
+ 每次插入时写入状态（如 `uniqState` 的 bitmap）
+ 合并时执行状态合并
+ 查询时通过 `final` 强制 merge 执行完整聚合

#### 场景：
+ 大规模去重、HLL 近似统计
+ 用户自定义聚合函数存储

---

## 如何选择合适的 MergeTree 变体
+ **幂等数据写入** → 使用 `ReplacingMergeTree(version)`
+ **日志数据流入 + 撤销补偿** → `CollapsingMergeTree` 或 `VersionedCollapsingMergeTree`
+ **业务指标类数据，需周期汇总** → `SummingMergeTree`
+ **高精度聚合、近似统计** → `AggregatingMergeTree`
+ **不需要任何合并行为（如测试）** → `MergeTree`

---

