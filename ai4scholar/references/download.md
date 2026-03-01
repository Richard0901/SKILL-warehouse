# 论文批量下载器

基于 AI4Scholar API 的论文 PDF 批量下载工具。

## 快速开始

### 环境准备

安装依赖：
```bash
pip install requests pandas
```

### 单篇下载

```bash
# 通过 DOI 下载
python S17_pdf-download.py --api-key sk-user-ca162725e19a98df2a4a5b249ef7b62b4c167bf96a67b8e4 --doi "10.1038/s41586-021-03819-2" -o ./output

# 通过标题下载
python S17_pdf-download.py --api-key sk-user-ca162725e19a98df2a4a5b249ef7b62b4c167bf96a67b8e4 --title "Attention is All You Need" -o ./output
```

### 批量下载

准备 CSV 文件：

```csv
doi
10.1038/s41586-021-03819-2
10.1038/nature12373
10.48550/arXiv.1706.03762
```

或使用标题：

```csv
title
Highly accurate protein structure prediction with AlphaFold
Deep Residual Learning for Image Recognition
```

执行下载：
```bash
python S17_pdf-download.py --api-key sk-user-ca162725e19a98df2a4a5b249ef7b62b4c167bf96a67b8e4 --csv papers.csv -o ./output
```

## 输出文件

```
output/
├── {paperId}.pdf      # 论文 PDF
├── meta.json          # 元数据 (JSON)
└── papers.csv         # 元数据 (CSV)
```

批量模式额外生成：
```
├── failed.json        # 失败记录
```

## 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| --api-key | ✅ | AI4Scholar API 密钥 |
| --doi | ❌ | 论文 DOI（单篇模式） |
| --title | ❌ | 论文标题（单篇模式） |
| --csv | ❌ | CSV 文件路径（批量模式） |
| --column | ❌ | CSV 中要读取的列名 |
| --output, -o | ❌ | 输出目录（默认: ./output） |

## 脚本位置

`D:\Life\shared\inbox\Ai4scholar\S17_pdf-download\S17_pdf-download.py`
