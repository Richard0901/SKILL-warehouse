#!/usr/bin/env python3
"""
Bilibili 单视频字幕抓取脚本
用法: python fetch_single_video.py <BV号> [输出目录]

这个脚本直接通过 BV号 获取字幕，不受 up 主视频列表 API 限流影响
"""

import requests
import os
import re
import sys
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.bilibili.com",
    "Origin": "https://www.bilibili.com"
}

def get_video_info(bvid):
    """获取视频基本信息"""
    url = "https://api.bilibili.com/x/web-interface/view"
    params = {"bvid": bvid}
    resp = requests.get(url, params=params, headers=HEADERS)
    data = resp.json()

    if data.get("code") != 0:
        raise Exception(f"获取视频信息失败: {data.get('message')}")

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

def get_subtitle_content(suburl):
    """获取字幕内容"""
    base_url = "https://comment.bilibili.com"
    full_url = base_url + suburl

    try:
        resp = requests.get(full_url, timeout=10)
        if resp.status_code != 200:
            return None

        subtitle_data = resp.json()
        body = subtitle_data.get("body", [])

        if not body:
            return None

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
    filename = re.sub(r'[\\/:*?"<>|]', '_', filename)
    filename = filename.strip()
    if len(filename) > 100:
        filename = filename[:100]
    return filename

def fetch_single_video(bvid, output_dir=None):
    """获取单个视频的字幕"""

    # 1. 获取视频信息
    print(f"获取视频信息: {bvid}")
    video_info = get_video_info(bvid)

    title = video_info.get("title", "无标题")
    pubdate = video_info.get("pubdate")
    desc = video_info.get("desc", "")
    author = video_info.get("owner", {}).get("name", "未知")
    date_str = datetime.fromtimestamp(pubdate).strftime("%Y-%m-%d") if pubdate else "未知日期"

    print(f"标题: {title}")
    print(f"作者: {author}")
    print(f"日期: {date_str}")

    # 2. 获取视频分 P
    pages = get_video_pages(bvid)
    if not pages:
        print("错误: 无法获取视频分 P 信息")
        return None

    first_page = pages[0]
    cid = first_page.get("cid")

    # 3. 获取字幕列表
    subtitles = get_subtitle_list(cid, bvid)
    if not subtitles:
        print("错误: 该视频没有字幕")
        return None

    print(f"找到 {len(subtitles)} 个字幕")

    # 4. 获取字幕内容
    sub_info = subtitles[0]
    sub_url = sub_info.get("url")
    subtitle_content = get_subtitle_content(sub_url)

    if not subtitle_content:
        print("错误: 无法获取字幕内容")
        return None

    # 5. 生成文件名
    if output_dir is None:
        output_dir = os.path.expanduser(f"~/Documents/life/workspace/bilibili/{author}")

    os.makedirs(output_dir, exist_ok=True)

    safe_title = sanitize_filename(title)
    filename = f"{date_str}_{bvid}_{safe_title}.md"
    filepath = os.path.join(output_dir, filename)

    # 6. 写入文件
    content = f"""# {title}

- 发布时间：{date_str}
- 作者：{author}
- BV号：{bvid}
- 链接：https://www.bilibili.com/video/{bvid}
- 简介：{desc}

---

{subtitle_content}
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"已保存: {filepath}")
    return filepath


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python fetch_single_video.py <BV号> [输出目录]")
        print("示例: python fetch_single_video.py BV1mkZ5BAEtH")
        sys.exit(1)

    bvid = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    try:
        fetch_single_video(bvid, output_dir)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)
