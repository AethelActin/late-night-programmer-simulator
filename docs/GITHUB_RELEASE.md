# GitHub 实验版发布记录

2026-10-19：作者明确授权公开发布，并同意别人下载、克隆或 fork；要求标注“实验性／不成熟”。目标仓库为 AethelActin/late-night-programmer-simulator，版本 v0.1.0-preview，使用预发布标记。

公开内容：干净的源码、事件配置、截图、文档、测试和许可文本；EXE 在 Releases 中提供。源码不携带原始游戏素材、个人配置、旧 Git 历史或构建垃圾。公开 EXE 按作者最新要求保留全部原背景音乐、排除 Zpix，改用已有 OFL 字体，附许可文本；本地旧完整包保留。

用户已接受公开副本不能完全收回的事实。代码开源许可证未选择，不自动添加 MIT。

下载说明和实际验证见 README.md 与 docs/PROJECT.md。远程发布状态以 GitHub 仓库与 Release 页面为准；下面保留本地准备过程作为历史记录。

---

# 历史：GitHub 上传准备

状态：本地准备已完成，供作者审查；未创建远程仓库、未 push、未发布 Release。

## 建议项目资料

- 中文名：深夜程序员模拟器
- 英文名：Late Night Programmer Simulator
- 仓库名：`late-night-programmer-simulator`
- 仓库描述：`A cozy pixel-art desktop game about late-night coding, coffee, rain, and a cat. Built with Python and pygame.`
- Topics 建议：`python`、`pygame`、`pixel-art`、`desktop-game`、`simulation`、`ai-assisted`
- 首次展示版本建议：`v0.1.0-preview`，尚未创建 tag。

新名称更直接地描述实际内容；保留 VCS 为旧工程代号，不需要改动内部 vibe 数值或旧历史文档。

## 此次准备公开的内容

使用 `tools/prepare_github.py` 从当前源码导出白名单，不复制现有 `.git`。包括 Python 源码、事件配置、依赖与打包配置、回归测试、素材配置说明、项目文档和实际截图。

不包括原始游戏素材、第三方 MP3、字体、EXE、原始 Git 历史、IDE／个人工具配置、缓存、构建目录或环境变量文件。现有历史已经跟踪过部分此类文件；仅新增 `.gitignore` 不会从旧历史中移除它们。因此后续应从这份干净副本开始新的 GitHub 仓库。

源码展示副本没有原始素材，不能直接启动游戏。README 和素材说明应保留这个限制，不能伪装成可立即下载试玩的完整发行版。完整本地 EXE 只用于作者检查，尚未准备公开上传。

## 本地准备结果

```powershell
python -B tools/prepare_github.py
```

默认输出：

```text
dist/github-prep/
├─ late-night-programmer-simulator/             # 干净文件目录，没有 .git
│  └─ PACKAGE_CONTENTS.json                    # 每个文件的 SHA-256 和公开范围
└─ late-night-programmer-simulator-source-0.1.0-preview.zip
```

实际上传前应审查 `PACKAGE_CONTENTS.json`，并在该干净目录运行测试：缺素材的 4 项图形检查应为 skipped，其他检查应通过。完整本地资源环境的通过结果不能挪用为此展示副本的全部检查结果。

已准备 `.github/workflows/tests.yml`，在 Windows + Python 3.13 上运行同一组 unittest；只读权限，不构建或上传 EXE。本轮尚未触发 GitHub Actions，不能写成远程 CI 已通过。Action 版本依据 [checkout 官方说明](https://github.com/actions/checkout)和 [setup-python 官方说明](https://github.com/actions/setup-python)选定。

## 待作者决定

1. 目标 GitHub 账号／仓库地址，本地当前没有配置远程地址。
2. 代码许可：暂时展示并保留权利，还是选择 MIT 等开源许可；本轮不代选。
3. 确认公开范围和截图内容。上传是后续独立动作，本轮没有发布。
4. 若要提供可玩 EXE 下载，先补齐素材许可或替换对应资源，再做公开试玩包；不必因此重做全部动画。

## 可用于首次仓库说明的版本文字

> 深夜程序员模拟器是一款 Python + pygame 像素风桌面陪伴游戏。玩家可以静静观看深夜编码场景，也可以通过事件选项影响氛围、理智和项目进度。当前展示版包含事件系统、动画状态机、按帧资源缓存、双语界面和回归测试；采用 AI 辅助开发，动画由作者生成、剪辑并集成。原始运行素材暂未随仓库提供，完整公开试玩版待素材许可整理后发布。项目尚无线上玩家或商业收入记录。

## 简历证据边界

可描述实际技术和交付：Python/pygame、事件与动画状态管理、96 帧 LRU、双语 UI、Windows 打包和回归测试。应能解释对应代码、问题根因和测试边界，并说明 AI 辅助范围。

GitHub 公开后可加仓库链接；真实 Release 发布后再写可下载版本。准备完成、公开仓库、正式商业上架是不同阶段，不写未发生的运营、用户量、收益或平台合作。

## 本轮实际检查

完整本地环境 28 项回归通过，更名 EXE 自检退出码为 0；导出目录运行 28 项检查，其中 24 项通过、4 项因素材未包含而 skipped。素材检查在该目录返回 1 并明确列出缺失资源，这是展示包的预期限制。ZIP 自带内容清单和 SHA-256；生成时检查 ZIP 完整性并拒绝个人配置、原始素材、音乐、字体、EXE 或旧历史。菜单的中英文字样、截图和水印遮罩已实际渲染查看。远程 CI 尚未触发。
