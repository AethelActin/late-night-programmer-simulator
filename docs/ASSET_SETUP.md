# 素材配置

“深夜程序员模拟器”的代码展示包不附带游戏运行所需的原始图片、字体、音乐、图标或其历史版本。原始素材没有随源码提供；普通玩家可从 GitHub Releases 下载包含所需运行素材的 EXE。仅下载源码 ZIP 还不能直接启动图形游戏。

仓库中的截图用于说明已实现的画面；截图不构成原始美术、字体或音乐的授权。作者本机已验证完整资源，后续补齐许可或替换资源后可单独发布试玩版。

## 目录要求

在项目根目录提供以下资源：

```text
assets/
├─ fonts/
│  ├─ PressStart2P-Regular.ttf
│  └─ FusionPixel10.ttf
├─ images/sprites/
│  ├─ idle1/  idle2/  idle3/
│  ├─ cat_wake/  cat_type_remove/  cat_down/
│  ├─ rain/  rain_idle/  rain_cat_wake/  rain_cat_watch/
│  ├─ drink/  phone/  scratch/  drowsy/  excited/  done/
│  └─ 每个目录内为按文件名排序的 PNG 帧
└─ icon.ico                 # 使用 spec 打包时需要
```

实际目录名必须与事件、状态机一致；建议统一 1280×720，文件名使用 `frame_0001.png` 这样的补零序号。字体路径是当前项目约定；如自行更换字体，应修改 `src/font_manager.py` 路径并核对许可。

音乐可选，没有 `assets/audio/` 仍能运行。若有可分发资源，可按以下目录放入 MP3：`no_rain_loop/`、`rain_loop/`、`low_reality_loop/`、`done_loop/`。当前完整本地包中的音乐不包含在展示包里。

## 不依赖这些素材的检查

```powershell
python -B -m unittest discover -s tests -v
python -B tools/check_assets.py
```

源码展示包的非素材回归仍可运行；4 项真实画面测试会明确标为 skipped，不应写成全部通过。`check_assets.py` 在必需素材缺失时退出码为 1，并列出缺项。配置完成后再执行 `python main.py`。
