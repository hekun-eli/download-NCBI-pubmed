---

# PubMed PMC PDF 下载脚本

## 功能概述

该脚本结合了两个主要功能：

1. 从 PubMed 格式的文本文件中提取所有的 PMC 链接，并自动生成下载 PDF 的链接。
2. 使用 **Selenium** 和 **Chrome** 自动下载每个生成的 PDF 文件。

### 使用步骤

* 第一步：提取 PubMed 文本中的 PMC 链接，并生成对应的 PDF 下载链接。
* 第二步：通过 Selenium 打开每个 PDF 链接并开始下载文件。

## 需求

* Python 3.x
* 安装以下 Python 库：

  * `selenium`：用于自动化浏览器操作。
  * `webdriver-manager`：自动下载并管理适配的 ChromeDriver。
  * `glob`（标准库）：用于文件匹配。

  安装依赖：

  ```bash
  pip install selenium webdriver-manager
  ```

## 脚本说明

### `pubmed_pmc_download.py`

此脚本包含两个主要功能：

1. **提取 PMC 链接**

   * 从给定的 PubMed 格式文件（`.txt`）中提取所有 `PMC` 编号，并生成对应的 PDF 下载链接。
   * 提取的链接将保存到一个中间文件（如 `pmc_links.txt`），每行一个 PDF 链接。

2. **下载 PDF 文件**

   * 使用 **Selenium** 自动化控制 Chrome 浏览器，打开每个 PDF 下载链接。
   * 每个文件将在指定的下载目录（如 `~/Downloads/mcr-pcnR`）下载。
   * 支持 **Headless Chrome** 模式，下载过程无需浏览器界面显示。

## 配置

### 配置路径

修改脚本中的路径变量，以适配你的文件和下载需求。

```python
PUBMED_FILE = "xxx/xxxx/pubmed-pcnR-set.txt"   # PubMed 格式文件路径
OUTPUT_LINK_FILE = "xxx/xxxx/pmc_links.txt"    # 提取后的 PDF 下载链接文件路径
DOWNLOAD_DIR = "xxx/xxxx/mcr-pcnR"             # PDF 下载目录（绝对路径）
```

确保 `DOWNLOAD_DIR` 是你希望保存 PDF 文件的绝对路径。`OUTPUT_LINK_FILE` 是临时保存生成链接的文件。

### 可选配置：

* **Headless 模式**：通过设置 `headless=True`，脚本将以无头模式运行 Chrome 浏览器（即没有图形界面）。若想要看到浏览器界面，可以将 `headless=False`。

```python
download_with_selenium(OUTPUT_LINK_FILE, DOWNLOAD_DIR, headless=True)
```

### 运行脚本

1. **提取 PMC 链接并生成下载链接**

   * 运行脚本时，首先会从 `PUBMED_FILE` 中提取 `PMC` 编号，并生成 PDF 下载链接。这些链接将保存到 `OUTPUT_LINK_FILE` 文件中。

2. **开始下载 PDF 文件**

   * 在生成下载链接后，脚本将自动开始下载这些 PDF 文件。每个链接都将通过 **Selenium** 打开，下载文件将保存在 `DOWNLOAD_DIR` 中。

## 使用示例

### 运行脚本：

1. 修改配置中的路径变量：

   * `PUBMED_FILE`：你的 PubMed 数据文件路径（例如：`/path/to/pubmed-pcnR-set.txt`）。
   * `OUTPUT_LINK_FILE`：保存生成 PDF 链接的文件路径（例如：`/path/to/pmc_links.txt`）。
   * `DOWNLOAD_DIR`：保存 PDF 文件的目录路径（例如：`/path/to/download/folder`）。

2. 运行脚本：

   ```bash
   python pubmed_pmc_download.py
   ```

### 输出：

* **`pmc_links.txt`**：生成的每个 PDF 下载链接。
* **下载目录**（如：`/path/to/download/folder`）：下载的 PDF 文件。

## 错误与调试

### 常见错误：

1. **文件未找到**

   * 确保你已经正确设置了输入文件路径和下载目录路径。
   * 确保 `PUBMED_FILE` 存在并且格式正确。

2. **下载失败**

   * 有时如果页面没有及时加载或连接失败，Selenium 可能无法正常下载 PDF 文件。你可以通过增加 `time.sleep()` 或增加等待时间来改进。

3. **Chrome/ChromeDriver 版本不兼容**

   * 请确保 `chromedriver` 版本与你的 Chrome 浏览器版本兼容。可以通过 `webdriver-manager` 自动管理，也可以手动设置。

### 提示：

* 如果你遇到下载速度慢的问题，可以考虑将 `headless` 模式改为 `False`，这样可以看到实际的下载过程并进行调试。
* 若想手动调试，检查是否能够正常加载 PDF 页面，并手动尝试下载。

## 许可证

此脚本是开源的，免费用于学术和个人项目。任何商业用途请联系作者。

## 联系方式

* 作者：Kun He
* 电子邮件：[hekunhe98@126.com](mailto:hekunhe98@126.com)

---

### 你可以根据需要进一步修改或扩展此文档，适应更多的使用场景或错误处理。
