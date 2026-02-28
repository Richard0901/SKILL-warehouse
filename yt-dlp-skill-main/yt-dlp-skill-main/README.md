# yt-dlp 技能（Claude Code）
一个用于从 YouTube 和 1000+ 网站下载视频和音频的 Claude Code 技能，使用 [yt-dlp](https://github.com/yt-dlp/yt-dlp)。

## 安装
将 `SKILL.md` 文件复制到你的 Claude Code 技能目录：
```bash
mkdir -p ~/.claude/skills/yt-dlp
cp SKILL.md ~/.claude/skills/yt-dlp/
```

## 使用方法
安装后，当你执行以下操作时，Claude Code 会自动使用此技能（或者第一次使用时，告诉Claude使用yt-dlp这个skill）：
- 第一次使用可能会自动下载脚本，不用慌
- 提供视频 URL 并要求下载
- 要求从视频中提取音频
- 请求从支持的网站下载（YouTube、Bilibili、TikTok、Twitter/X、Vimeo 等）


### 示例提示
- "下载这个视频：https://youtube.com/watch?v=..."
- "将这个视频的音频提取为 mp3"
- "下载这个播放列表，720p 画质"

## 功能特性
- 下载各种质量级别的视频
- 提取 mp3/m4a 格式的音频
- 下载完整播放列表
- 下载并嵌入字幕
- 自定义输出路径和文件名
