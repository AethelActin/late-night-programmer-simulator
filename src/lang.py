# 语言包：中英文对照
from src.metadata import TITLE_EN, TITLE_ZH

# 开始界面
START_BTN = {"en": "[ start ]", "zh": "[ 开始 ]"}
QUIT_BTN = {"en": "[ quit ]", "zh": "[ 退出 ]"}
TITLE = {"en": TITLE_EN, "zh": TITLE_ZH}

# 状态面板
VIBE_LABEL = {"en": "vibe", "zh": "氛围"}
REALITY_LABEL = {"en": "sanity", "zh": "理智"}
COMPILING = {"en": "project progress", "zh": "项目进度"}

# 事件类别 header
CATEGORY = {
    "cozy": {"en": "[ system ]", "zh": "[ 系统 ]"},
    "distraction": {"en": "[ distraction ]", "zh": "[ 分心 ]"},
    "tech": {"en": "[ system ]", "zh": "[ 系统 ]"},
    "doom": {"en": "[ system ]", "zh": "[ 系统 ]"},
    "meta": {"en": "[ reality instability ]", "zh": "[ 现实扭曲 ]"},
    "rare": {"en": "[ system ]", "zh": "[ 系统 ]"},
}
CAT_CAT = {"en": "[ cat event ]", "zh": "[ 小橘来了 ]"}
HOW_TO_PLAY_BTN = {"en": "[ how to play ]", "zh": "[ 玩法 ]"}
HOW_TO_PLAY_LABEL = {"en": "How to Play", "zh": "玩法介绍"}
HOW_TO_PLAY_TEXT = {
    "en": [
        "A quiet companion while you wait for your AI.",
        "",
        "It runs silently, allowing you to wait for the AI to complete the task.",
        "",
        "No complicated operations or skills are required.",
        "",
        "Choose an event option, or leave it alone to close neutrally.",
        "",
        "The game ends when your sanity runs out.",
        "",
        "Project 100%: complete. Esc: pause / return to menu.",
    ],
    "zh": [
        "一款可以静静陪你等待 AI 的游戏。",
        "",
        "当你等待 AI 帮你干完活时，你可以在这里消磨时光。",
        "",
        "没有复杂机制，没有需要掌握的技巧。",
        "",
        "点击事件选项可影响数值；不操作则超时中性关闭。",
        "",
        "理智耗尽时，旅程结束。",
        "",
        "项目进度达到 100% 时编译完成。Esc 暂停 / 返回菜单。",
    ],
}
MUSIC_TOGGLE = {"en": "music: on", "zh": "音乐：开"}
MUSIC_TOGGLE_MUTED = {"en": "music: off", "zh": "音乐：关"}
LANG_TOGGLE = {"en": "English", "zh": "中文"}

# 底部随机展示语（有中英文对照）
TAGLINES = {
    "en": [
        "Keep the room alive while the code compiles.",
        "A small companion for late-night coding sessions.",
        "No pressure. Just you, the project, and the night.",
        "A quiet coding companion for long nights.",
        "Sit down. The project can wait.",
        "This game requires no skill.",
        "If your AI is still working, you can come here.",
    ],
    "zh": [
        "代码还在跑，房间也还醒着。",
        "属于深夜编码时光的小陪伴。",
        "不用着急。这里只有你、项目，还有夜晚。",
        "一个安静陪你熬夜编码的地方。",
        "坐一会吧。项目没有那么着急。",
        "不用操作太多，陪着它就好。",
        "等 AI 跑结果的时候，可以来这里待一会。",
    ],
}

# 时长选择
SESSION_LABEL = {"en": "Session Length", "zh": "游戏时长"}
SESSION_SHORT = {"en": "Short Session", "zh": "短时间"}
SESSION_NORMAL = {"en": "Normal Night", "zh": "正常"}
SESSION_LONG = {"en": "Long Companion", "zh": "长时间"}

# 事件标题翻译
EVENT_TITLE = {
    "cat_on_keyboard": {"en": "Cat on Keyboard", "zh": "小橘踩键盘"},
    "drink": {"en": "Coffee O'Clock", "zh": "咖啡时间"},
    "phone_doomscroll": {"en": "Just One More Reel", "zh": "再刷一个"},
    "drowsy": {"en": "The Eyes Are Closing", "zh": "眼皮在打架"},
    "inspiration": {"en": "Eureka", "zh": "灵感爆发"},
    "ai_stuck": {"en": "AI Is Thinking", "zh": "AI 卡住了"},
    "windows_update": {"en": "Restart Required", "zh": "需要重启"},
    "refactor_impulse": {"en": "This Code Is Ugly", "zh": "这代码太丑了"},
    "rain_starts": {"en": "It's Raining", "zh": "下雨了"},
    "rain_cat_wakes": {"en": "The Cat Noticed the Rain", "zh": "小橘注意到雨了"},
    "rain_stops": {"en": "The Rain Softens", "zh": "雨渐渐停了"},
    "keyboard_asmr": {"en": "Mechanical Keyboard ASMR", "zh": "键盘 ASMR"},
    "youtube_recommendation": {"en": "YouTube Recommends", "zh": "YouTube 推荐"},
    "stackoverflow_savior": {"en": "Stack Overflow Saves the Day", "zh": "Stack Overflow 拯救世界"},
    "rain_heavier": {"en": "Rain Gets Heavier", "zh": "雨变大了"},
    "lofi_hits": {"en": "This Track Hits Different", "zh": "这首歌感觉不一样"},
    "monitor_glow": {"en": "Warm Monitor Glow", "zh": "显示器的暖光"},
    "twitter_spiral": {"en": "One Minute on Twitter", "zh": "刷了一会儿推特"},
    "steam_sale": {"en": "Steam Sale", "zh": "Steam 打折"},
    "npm_collapse": {"en": "npm Install", "zh": "npm 安装"},
    "rewrite_in_rust": {"en": "Maybe I Should Rewrite This in Rust", "zh": "也许该用 Rust 重写"},
    "todo_breeding": {"en": "TODO Breeding", "zh": "TODO 在繁殖"},
    "ai_hallucination": {"en": "AI Speaks", "zh": "AI 说话了"},
    "github_stars": {"en": "38k GitHub Stars", "zh": "38k GitHub Stars"},
    "package_success": {"en": "It Actually Installed", "zh": "居然装上了"},
    "code_speaks": {"en": "The Code Is Speaking", "zh": "代码在说话"},
    "compile_eta": {"en": "Estimated Time Remaining", "zh": "预计剩余时间"},
    "fake_discord": {"en": "New Message", "zh": "新消息"},
    "cat_stare": {"en": "The Cat Is Watching", "zh": "小橘在盯着你看"},
    "window_reflection": {"en": "Something in the Window", "zh": "窗户里有东西"},
    "cursor_stops": {"en": "The Cursor Stopped Blinking", "zh": "光标不动了"},
    "ai_sigh": {"en": "AI's Sigh", "zh": "AI 的叹息"},
    "ai_no_idea": {"en": "No Idea", "zh": "没招了"},
    "ai_self_aware": {"en": "AI Becomes Self-Aware", "zh": "AI 有了自我意识"},
    "night_philosophy": {"en": "Deep Thought", "zh": "深夜哲思"},
    "ai_actually_worked": {"en": "Wait. It Actually Works.", "zh": "等等，居然能跑"},
    "everything_works": {"en": "No Errors. No Warnings.", "zh": "零错误零警告"},
    "the_perfect_vibe": {"en": "The Perfect Vibe", "zh": "完美的氛围"},
    "sunrise": {"en": "Sunrise", "zh": "天亮了"},
    "done_question": {"en": "It's Done.", "zh": "做完了"},
    "done_still_watching": {"en": "Still Here?", "zh": "还在看？"},
    "done_ai_joke": {"en": "AI Thoughts", "zh": "AI 的感想"},
}

# 事件文本翻译
EVENT_TEXT = {
    "cat_on_keyboard": {"zh": "小橘醒了过来，打算打扰你敲键盘。\n\nasdjkhfkjashf\n\n呼噜声越来越大了。\n\n还是把它抱走吧。"},
    "drink": {"zh": "杯子空了。\n还有另一杯。\n循环往复。"},
    "phone_doomscroll": {"zh": "再看一个视频。\n\n...\n\n再看一个。"},
    "drowsy": {"zh": "凌晨 2:47。\n你不困。\n\n你绝对不困。"},
    "inspiration": {"zh": "等等。\n等等等等。\n\n你知道怎么修了。"},
    "ai_direct_answer": {"zh": "\"现在我给你最直接、最完整、最不绕弯子的答案...\"\n\n你等着。\n\nAI 看了一遍你的代码。\n\n它叹了口气。"},
    "ai_stuck": {"zh": "正在生成回复...\n\n正在生成回复...\n\n正在生成回复..."},
    "windows_update": {"zh": "Windows 要安装更新。\n\n现在。\n\n它总是要现在装。"},
    "low_sanity_how_long": {"zh": "你已经多久没睡了？"},
    "low_sanity_window": {"zh": "窗外刚才是不是不一样？"},
    "low_sanity_goal": {"zh": "你还记得项目一开始要做什么吗？"},
    "refactor_impulse": {"zh": "你盯着函数。\n函数盯着你。\n\n这代码太丑了。"},
    "rain_starts": {"zh": "雨开始敲打窗户。\n房间突然感觉更小了。\n\n也更温暖了。"},
    "rain_cat_wakes": {"zh": "小橘睁开一只眼。\n看看窗户。\n看看你。\n\n又看向窗户。"},
    "rain_stops": {"zh": "雨渐渐小了。\n窗户清晰起来。\n\n没有雨声的房间感觉不一样了。"},
    "keyboard_asmr": {"zh": "今晚键盘的声音格外悦耳。\n\n咔嗒。\n咔嗒。\n咔嗒。"},
    "youtube_recommendation": {"zh": "\"为什么日本程序员都改用 Vim\"\n\n820 万播放。"},
    "stackoverflow_savior": {"zh": "一个 7 年前的答案。\n3 个赞。被采纳。\n\n完美解决了你的问题。"},
    "rain_heavier": {"zh": "雨下得更大了。\n敲打窗户的声音更响了。\n房间感觉更小了。"},
    "lofi_hits": {"zh": "这首歌突然听起来像人生的意义。\n\n你没有哭。\n你没有哭。"},
    "monitor_glow": {"zh": "显示器的暖光莫名让人安心。\n\n也许这就是家。"},
    "twitter_spiral": {"zh": "你眨了一下眼。\n\n17 分钟不见了。"},
    "steam_sale": {"zh": "一个你永远不会玩的游戏打 90%。\n\n优惠还剩 02:14:33。"},
    "npm_collapse": {"zh": "正在安装依赖...\n\n23 秒安装了 842 个包\n\n⚠ 发现 142 个漏洞"},
    "rewrite_in_rust": {"zh": "Python 太慢。\nRust 很快。\n你从来没写过 Rust。\n\n...能有多难呢？"},
    "todo_breeding": {"zh": "# TODO: 修这个\n# TODO: 修那个\n# TODO: 这是啥\n# TODO: 我为什么要这么做\n# TODO: 留给未来的我"},
    "ai_hallucination": {"zh": "你让 AI 帮你修函数。\n\nAI 回复：\n\"你考虑过去当个山羊 farmer 吗？\""},
    "github_stars": {"zh": "这个项目有 38,000 颗星。\n别人一个周末做的。\n\n你盯着屏幕看了好一会儿。"},
    "package_success": {"zh": "成功安装 hope-0.1.2\n成功安装 clarity-3.0.1\n成功安装 tomorrow-1.0.0"},
    "code_speaks": {"zh": "print(\"你怎么还没睡\")\n\n你没有写过这行代码。"},
    "compile_eta": {"zh": "预计编译时间：\n\n482 年"},
    "fake_discord": {"zh": "bro 你还活着吗\n\n...\n\n你打开 Discord。\n没有新消息。"},
    "cat_stare": {"zh": "小橘直直地看着你。\n\n它没有眨眼。\n\n它知道。"},
    "window_reflection": {"zh": "有那么一瞬间，\n你觉得身后有人。\n\n你身后什么也没有。"},
    "ai_sigh": {"zh": "\"没关系，我来帮你解决。\"\n\n你等着。\n\nAI 看了一遍你的代码。\n\n它叹了口气。"},
    "ai_no_idea": {"zh": "\"现在我给你最直接、最完整、最不绕弯子的答案...\""},
    "cursor_stops": {"zh": "光标停止了闪烁。\n\n房间很安静。\n\n你等着。"},
    "ai_self_aware": {"zh": "正在生成回复...\n\n正在生成回复...\n\n我也不知道。"},
    "night_philosophy": {"zh": "也许 bug 从来就不在代码里。"},
    "ai_actually_worked": {"zh": "你运行了代码。\n\n没有错误。\n\n你又运行了一遍。\n\n还是没有错误。\n\n...你不信。"},
    "everything_works": {"zh": "没有错误。\n没有警告。\n没有 bug。\n\n这种事情从来没发生过。\n以后也不会再发生了。"},
    "the_perfect_vibe": {"zh": "音乐正好。\n小橘睡着了。\n雨还在下。\n\n现在没有什么需要修复的。"},
    "sunrise": {"zh": "窗户外的天亮了。\n\n雨停了。\n音乐慢了下来。\n\n你做到了。"},
    "done_question": {"zh": "我的项目编译完了。\n\n你的呢？"},
    "done_still_watching": {"zh": "我做完了。\n\n没有片尾字幕。\n窗口不会自动关闭。\n\n你还在看什么？"},
    "done_ai_joke": {"zh": "你的 AI 还没有帮你干完活吗？"},
}

# 退出按钮
EXIT_BTN = {"en": "[ exit ]", "zh": "[ 退出 ]"}
EXIT_CONFIRM = {"en": "Return to menu?", "zh": "回到主菜单？"}
EXIT_CONFIRM_BTN = {"en": "[ confirm ]", "zh": "[ 确认 ]"}
EXIT_CANCEL_BTN = {"en": "[ cancel ]", "zh": "[ 取消 ]"}

# 选项按钮翻译（按事件 id + 选项索引）
CHOICE_TEXT = {
    "cat_on_keyboard": [
        {"en": "Let it happen", "zh": "随它去"},
        {"en": "Remove cat", "zh": "把小橘抱走"},
    ],
    "phone_doomscroll": [
        {"en": "Put it down", "zh": "放下手机"},
        {"en": "Keep scrolling", "zh": "继续刷"},
    ],
    "drowsy": [
        {"en": "Drink coffee", "zh": "喝咖啡"},
        {"en": "Embrace it", "zh": "接受它"},
    ],
    "ai_stuck": [
        {"en": "Wait patiently", "zh": "耐心等待"},
        {"en": "Refresh", "zh": "刷新"},
    ],
    "windows_update": [
        {"en": "Postpone (again)", "zh": "推迟（再次）"},
        {"en": "Restart now", "zh": "立即重启"},
    ],
    "refactor_impulse": [
        {"en": "Ignore it", "zh": "无视它"},
        {"en": "Rewrite everything", "zh": "全部重写"},
    ],
    "youtube_recommendation": [
        {"en": "Watch", "zh": "看看"},
        {"en": "Resist", "zh": "忍住"},
        {"en": "Open 4 tabs", "zh": "打开 4 个标签页"},
    ],
    "steam_sale": [
        {"en": "Buy it", "zh": "买了"},
        {"en": "Ignore", "zh": "忽略"},
    ],
    "rewrite_in_rust": [
        {"en": "Stay in Python", "zh": "留在 Python"},
        {"en": "Open a Rust tutorial", "zh": "打开 Rust 教程"},
    ],
    "github_stars": [
        {"en": "Get inspired", "zh": "受鼓舞"},
        {"en": "Close the tab", "zh": "关掉标签页"},
    ],
}
