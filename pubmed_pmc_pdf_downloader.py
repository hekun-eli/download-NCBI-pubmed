#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并脚本：1) 从 PubMed 文本中提取 PMC ID -> 生成 PDF 链接
          2) 使用 Selenium 打开每个 PDF 链接并下载 PDF（顺序进行，确保每个下载完成后再继续）
说明：
 - 请把下面的占位路径替换为你自己的路径（示例使用 xxx/xxxx/... 作为占位）
 - 需要：python + selenium + webdriver-manager
   pip install selenium webdriver-manager
"""

import re
import os
import time
import glob
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

###############################
# 用户需要修改的路径（占位符示例）
###############################
PUBMED_FILE = "xxx/xxxx/pubmed-pcnR-set.txt"   # <-- 将此处替换为你的 PubMed 格式文件路径
OUTPUT_LINK_FILE = "xxx/xxxx/pmc_links.txt"    # <-- 提取出的链接将写入此文件（中间文件）
DOWNLOAD_DIR = "xxx/xxxx/mcr-pcnR"             # <-- PDF 下载目录（必须是绝对路径）
###############################

# 正则用于匹配类似： "PMC - PMC11609744" 的行（忽略大小写）
PMC_PATTERN = re.compile(r"PMC\s*-\s*(PMC\d+)", re.IGNORECASE)

def extract_pmc_links(pubmed_path, out_link_path):
    """
    从 pubmed 文件中提取 PMC ID 并写成下载链接到 out_link_path
    返回：生成的链接列表
    """
    links = []
    if not os.path.exists(pubmed_path):
        raise FileNotFoundError(f"PubMed 文件未找到: {pubmed_path}")

    with open(pubmed_path, "r", encoding="utf-8") as fh:
        for line in fh:
            m = PMC_PATTERN.search(line)
            if m:
                pmc_id = m.group(1)
                # 形成 PDF 下载链接
                link = f"https://pmc.ncbi.nlm.nih.gov/articles/{pmc_id}/pdf/"
                links.append(link)

    # 写出链接（如果没有找到任何 PMC，也会写空文件）
    os.makedirs(os.path.dirname(out_link_path), exist_ok=True)
    with open(out_link_path, "w", encoding="utf-8") as outfh:
        for link in links:
            outfh.write(link + "\n")

    return links

def wait_for_downloads_to_finish(download_dir, timeout=180, poll_interval=1):
    """
    等待 download_dir 下的临时下载文件（例如 .crdownload 或 .part）消失，
    或者直到超时。返回 True 表示下载夹看起来已稳定（无临时文件），False 表示超时。
    """
    end_time = time.time() + timeout
    while time.time() < end_time:
        # 常见浏览器临时后缀： .crdownload (Chrome), .part (Firefox)
        tmp_files = glob.glob(os.path.join(download_dir, "*.crdownload")) + \
                    glob.glob(os.path.join(download_dir, "*.part"))
        if not tmp_files:
            return True
        time.sleep(poll_interval)
    return False

def ensure_dir_abs(path):
    """确保目录为绝对路径并存在；如果不是绝对路径，转换为绝对路径"""
    if not os.path.isabs(path):
        path = os.path.abspath(path)
    os.makedirs(path, exist_ok=True)
    return path

def download_with_selenium(links_file, save_dir, headless=True):
    """
    读取 links_file 中的每一行链接，使用 Selenium Chrome 打开并触发下载。
    每个链接等待下载完成（检测临时文件），然后继续下一个。
    """
    save_dir = ensure_dir_abs(save_dir)

    # Chrome 配置：直接下载 PDF（不在浏览器中打开）
    chrome_options = Options()
    prefs = {
        "plugins.always_open_pdf_externally": True,  # 直接下载 PDF，而不是在浏览器中打开
        "download.default_directory": save_dir,
        "download.prompt_for_download": False,
        # 如果需要禁用安全下载提示（视 Chrome 版本），可添加以下（但谨慎使用）
        # "safebrowsing.enabled": True,
        # "safebrowsing.disable_download_protection": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    if headless:
        # 新的 headless 模式标志（Chrome 109+），这里使用 headless=new
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # 启动 Chrome（自动安装驱动）
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # 读取链接
    with open(links_file, "r", encoding="utf-8") as fh:
        links = [line.strip() for line in fh if line.strip()]

    print(f"📄 共 {len(links)} 条链接待下载，下载目录：{save_dir}\n")

    for idx, url in enumerate(links, start=1):
        print(f"📥 正在处理 {idx}/{len(links)}: {url}")
        try:
            # 记录当前目录文件数，便于后面判断是否新增文件
            before_files = set(os.listdir(save_dir))

            driver.get(url)
            # 给浏览器一点时间来发起下载
            time.sleep(3)

            # 等待下载开始并完成：先等待一小段时间让 .crdownload 出现（或直接开始）
            # 然后调用 wait_for_downloads_to_finish 检查临时文件是否清空
            started_ok = wait_for_downloads_to_finish(save_dir, timeout=60)
            if not started_ok:
                # 如果在短时间内未稳定，尝试再等一会儿（扩展等待）
                print("⏳ 等待下载完成中（延长等待）...")
                started_ok = wait_for_downloads_to_finish(save_dir, timeout=120)
            # 为保险起见，再次检查是否有新增文件（有时候文件名会根据服务器返回确定）
            after_files = set(os.listdir(save_dir))
            new_files = after_files - before_files
            if new_files:
                print(f"✅ 发现新文件: {', '.join(sorted(new_files))}")
            else:
                # 没检测到新文件，仍然可能是下载失败或链接直接打开，但未产生文件
                print("⚠️ 未检测到新增文件（可能下载失败或网页未直接触发下载）。")

            # 小停顿，避免被服务器封禁
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ 下载时发生异常: {e}")
            # 继续下一个链接
        finally:
            # 每个链接之间再暂停一小会儿
            time.sleep(1)

    driver.quit()
    print("\n🎉 全部任务完成！请检查下载目录中的 PDF 文件。")

def main():
    # 1) 提取 PMC 链接
    print("步骤 1/2：从 PubMed 文件中提取 PMC 链接...")
    try:
        links = extract_pmc_links(PUBMED_FILE, OUTPUT_LINK_FILE)
        print(f"提取完成，共发现 {len(links)} 个 PMC 链接 -> 已写入: {OUTPUT_LINK_FILE}")
    except Exception as ex:
        print(f"❌ 提取 PMC 链接失败: {ex}")
        return

    if not links:
        print("未找到任何 PMC 条目，脚本结束。")
        return

    # 2) 下载 PDF（只有在提取出链接时才会执行）
    print("\n步骤 2/2：开始下载 PDF（使用 Selenium）...")
    try:
        download_with_selenium(OUTPUT_LINK_FILE, DOWNLOAD_DIR, headless=True)
    except Exception as ex:
        print(f"❌ 下载过程出现异常: {ex}")

if __name__ == "__main__":
    main()
