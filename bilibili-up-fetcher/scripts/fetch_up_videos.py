#!/usr/bin/env python3
"""
Bilibili Up 主视频字幕抓取脚本
用法: python fetch_up_videos.py <up主名字或ID> [输出目录]

注意: B站API有频率限制，可能需要添加延时或使用cookie
"""

import requests
import json
import os
import re
import time
import sys
from datetime import datetime

# 请求头，模拟浏览器
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com",
    "Origin": "https://www.bilibili.com"
}

def get_up_info(keyword):
    """获取 up 主信息"""
    url = "https://api.bilibili.com/x/web-interface/search/type"
    params = {
        "search_type": "bili_user",
        "keyword": keyword,
        "page": 1,
        "page_size": 10
    }
    resp = requests.get(url, params=params, headers=HEADERS)
    data = resp.json()

    if data.get("code") != 0:
        raise Exception(f"搜索失败: {data.get('message')}")

    # API 返回的数据在 data.result 中
    result = data.get("data", {}).get("result", [])
    if not result:
        raise Exception(f"未找到用户: {keyword}")

    # 优先找精确匹配的
    for user in result:
        if user.get("uname") == keyword:
            return user

    return result[0]  # 返回第一个结果


def get_up_videos_with_retry(mid, page=1, page_size=30, max_retries=3):
    """获取 up 主视频列表，带重试机制"""
    url = "https://api.bilibili.com/x/space/arc/search"
    params = {
        "mid": mid,
        "pn": page,
        "ps": page_size,
        "coop": 1,
        "interactive": 1
    }

    for attempt in range(max_retries):
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
            data = resp.json()

            if data.get("code") == 0:
                return data.get("data", {})

            # 检查是否是限流错误
            msg = data.get("message", "")
            if "频繁" in msg or "稍后再试" in msg:
                wait_time = (attempt + 1) * 3  # 递增等待时间
                print(f"  - 限流，等待 {wait_time} 秒...")
                time.sleep(wait_time)
                continue

            raise Exception(f"获取视频列表失败: {msg}")

        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            raise e

    raise Exception("获取视频列表失败: 达到最大重试次数")

def get_up_videos(mid, page=1, page_size=30):
    """获取 up 主视频列表"""
    url = "https://api.bilibili.com/x/space/arc/search"
    params = {
        "mid": mid,
        "pn": page,
        "ps": page_size,
        "coop": 1,
        "interactive": 1
    }
    resp = requests.get(url, params=params, headers=HEADERS)
    data = resp.json()

    if data.get("code") != 0:
        raise Exception(f"获取视频列表失败: {data.get('message')}")

    return data.get("data", {})

def get_video_pages(bvid):
    """获取视频分 P 信息"""
    url = "https://api.bilibili.com/x/player/pagelist"
    params = {"bvid": bvid}
    resp = requests.get(url, params=params, headers=HEADERS)
    data = resp.json()

    if data.get("code") != 0:
        return []

    return data.get("data", [])

def get_subtitle_list(cid, bvid):
    """获取视频字幕列表"""
    url = "https://api.bilibili.com/x/player/v2"
    params = {"cid": cid, "bvid": bvid}
    resp = requests.get(url, params=params, headers=HEADERS)
    data = resp.json()

    if data.get("code") != 0:
        return []

    subtitle_data = data.get("data", {}).get("subtitle", {})
    return subtitle_data.get("subtitles", [])

def get_subtitle_content(cid, suburl):
    """获取字幕内容"""
    # suburl 是相对路径，需要拼接完整 URL
    base_url = "https://comment.bilibili.com"
    full_url = base_url + suburl

    try:
        resp = requests.get(full_url, timeout=10)
        if resp.status_code != 200:
            return None

        # 解析 JSON 格式的字幕
        subtitle_data = resp.json()
        body = subtitle_data.get("body", [])

        if not body:
            return None

        # 拼接字幕文本
        texts = []
        for item in body:
            content = item.get("content", "").strip()
            if content:
                texts.append(content)

        return "\n".join(texts)
    except Exception as e:
        print(f"获取字幕失败: {e}")
        return None

def sanitize_filename(filename):
    """清理文件名中的非法字符"""
    # 替换或移除特殊字符
    filename = re.sub(r'[\\/:*?"<>|]', '_', filename)
    filename = filename.strip()
    # 限制长度
    if len(filename) > 100:
        filename = filename[:100]
    return filename

def fetch_up_videos(keyword, output_dir=None):
    """主函数：获取 up 主所有视频字幕"""

    # 1. 获取 up 主信息
    print(f"搜索用户: {keyword}")
    up_info = get_up_info(keyword)
    mid = up_info.get("mid")
    uname = up_info.get("uname")
    print(f"找到用户: {uname} (MID: {mid})")

    # 等待一下，避免被限流
    time.sleep(2)

    # 设置输出目录
    if output_dir is None:
        output_dir = os.path.expanduser(f"~/Documents/life/workspace/bilibili/{uname}")

    os.makedirs(output_dir, exist_ok=True)
    print(f"输出目录: {output_dir}")

    # 2. 获取所有视频
    print("\n获取视频列表...")
    first_page = get_up_videos_with_retry(mid, page=1, page_size=30)
    page_count = first_page.get("page", {}).get("pages", 1)
    num_results = first_page.get("page", {}).get("numResults", 0)

    print(f"共 {num_results} 个视频，分 {page_count} 页")

    all_videos = []

    for pn in range(1, page_count + 1):
        print(f"获取第 {pn}/{page_count} 页...")
        page_data = get_up_videos(mid, page=pn, page_size=30)
        videos = page_data.get("list", {}).get("vlist", [])
        all_videos.extend(videos)
        time.sleep(1)  # 避免请求过快

    print(f"\n共获取 {len(all_videos)} 个视频")

    # 3. 遍历每个视频获取字幕
    success_count = 0
    skip_count = 0

    for i, video in enumerate(all_videos):
        bvid = video.get("bvid")
        title = video.get("title", "无标题")
        pubdate = video.get("pubdate")
        desc = video.get("description", "")

        # 格式化日期
        date_str = datetime.fromtimestamp(pubdate).strftime("%Y-%m-%d") if pubdate else "未知日期"

        print(f"\n[{i+1}/{len(all_videos)}] 处理: {title[:30]}...")

        # 获取视频分 P 信息
        pages = get_video_pages(bvid)
        if not pages:
            print("  - 无分 P 信息，跳过")
            skip_count += 1
            continue

        # 获取第一个 P 的 cid
        first_page = pages[0]
        cid = first_page.get("cid")

        # 获取字幕列表
        subtitles = get_subtitle_list(cid, bvid)

        if not subtitles:
            print("  - 无字幕，跳过")
            skip_count += 1
            continue

        # 获取第一个字幕的内容
        sub_info = subtitles[0]
        sub_url = sub_info.get("url")
        subtitle_content = get_subtitle_content(cid, sub_url)

        if not subtitle_content:
            print("  - 字幕内容为空，跳过")
            skip_count += 1
            continue

        # 生成文件名
        safe_title = sanitize_filename(title)
        filename = f"{date_str}_{bvid}_{safe_title}.md"
        filepath = os.path.join(output_dir, filename)

        # 写入文件
        content = f"""# {title}

- 发布时间：{date_str}
- BV号：{bvid}
- 链接：https://www.bilibili.com/video/{bvid}
- 简介：{desc}

---

{subtitle_content}
"""

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"  - 已保存: {filename}")
        success_count += 1

        time.sleep(0.5)  # 避免请求过快

    print(f"\n完成! 成功: {success_count}, 跳过: {skip_count}")
    print(f"文件保存在: {output_dir}")

    return output_dir

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python fetch_up_videos.py <up主名字或ID> [输出目录]")
        sys.exit(1)

    keyword = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        fetch_up_videos(keyword, output_dir)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)
