# Citation Finder 使用示例

## 快速开始

### 1. 基本用法 - 分析文件中的文本

```bash
cd /Users/richard/Documents/life/SKILLS/citation-finder

python3 citation_finder.py \
  --input /path/to/your/introduction.txt \
  --output my_citations.md
```

### 2. 直接输入文本

```bash
python3 citation_finder.py \
  --text "Your academic text here..." \
  --output report.md
```

### 3. 输出 JSON 格式（便于后续处理）

```bash
python3 citation_finder.py \
  --input article.txt \
  --format json \
  --output citations.json
```

---

## 实际案例演示

### 案例：Glomus Tumor Introduction

**输入文本：**
```
Glomus tumors are rare perivascular neoplasms that originate from modified
smooth-muscle cells of the glomus body. They arise most often in the distal
extremities and are typically benign. Tracheobronchial glomus tumors are far
less common; since the first description in 1950, involvement of the main
bronchus or distal airways has been documented almost exclusively in isolated
case reports.

The current World Health Organization classification defines malignancy on
morphologic grounds—nuclear atypia, mitotic activity, tumor size, and
infiltrative growth—but these criteria do not fully account for observed
clinical heterogeneity.

Recurrent NOTCH pathway rearrangements, particularly NOTCH2 fusions, have been
identified in malignant glomus tumors.

The tumor microenvironment (TME) is increasingly recognized as a modulator of
tumor progression and treatment response in solid malignancies. Single-cell
RNA sequencing (scRNA-seq) now permits high-resolution dissection of
intratumoral heterogeneity.
```

**运行命令：**
```bash
python3 citation_finder.py \
  --text "Glomus tumors are rare perivascular neoplasms..." \
  --output glomus_report.md
```

**识别结果：**
- ✅ 7 处引用需求被识别
- ✅ 21 篇相关文献被检索
- ✅ 涵盖定义、历史、分类、分子发现、TME、方法学等类型

---

## 支持的引用类型

工具会自动识别以下类型的陈述：

| 类型 | 关键词触发 | 示例 |
|:---|:---|:---|
| **定义/分类** | is defined as, characterized by | "X is defined as Y" |
| **历史事实** | first described, since 1950 | "since the first description in 1950" |
| **流行病学** | rare, common, prevalence | "rare perivascular neoplasms" |
| **分子发现** | gene, mutation, fusion | "NOTCH2 fusions have been identified" |
| **分类标准** | WHO classification, criteria | "WHO classification defines..." |
| **技术方法** | scRNA-seq, sequencing | "Single-cell RNA sequencing..." |
| **临床行为** | indolent, malignant | "typically benign" |
| **肿瘤微环境** | TME, microenvironment | "tumor microenvironment is..." |

---

## 输出报告结构

生成的 Markdown 报告包含：

```markdown
# 文献引用检索报告

## 1. [引用类型]
**原文**: [需要引用的句子]

**推荐引用 (X篇)**:

### 1. [论文标题]
- **作者**: [作者列表]
- **期刊**: [期刊名]
- **年份**: [发表年份]
- **被引**: [被引次数]次
- **DOI**: [DOI号]
- **PMID**: [PubMed ID]
```

---

## 高级用法

### 调整检索结果数量

```bash
python3 citation_finder.py \
  --input article.txt \
  --max-results 10 \
  --output detailed_report.md
```

### 批量处理多个段落

创建脚本 `batch_process.sh`：

```bash
#!/bin/bash

for file in sections/*.txt; do
    filename=$(basename "$file" .txt)
    python3 citation_finder.py \
        --input "$file" \
        --output "citations/${filename}_citations.md"
    echo "Processed: $file"
done
```

---

## 注意事项

1. **人工审核**：工具推荐的文献基于算法匹配，请务必人工确认相关性
2. **高影响力优先**：优先选择被引次数高、发表在权威期刊的文献
3. **补充检索**：对于快速发展的领域，建议补充检索最近1-2年的文献
4. **历史文献**：某些历史性陈述可能需要查阅经典文献或教科书

---

## 故障排除

### API 错误
如果遇到 API 错误，检查：
- 网络连接是否正常
- API 密钥是否有效（内置密钥通常可用）

### 无相关文献
如果某句话找不到相关文献：
- 尝试手动拆分长句
- 提取核心关键词在 PubMed/Google Scholar 中搜索
- 考虑是否需要引用综述文章而非原始研究

---

## 相关资源

- **ai4scholar**: 底层文献检索 API
- **paper-download**: 下载检索到的 PDF 全文
