# SPRITE_RULES.md

## 一、素材清单

| 文件夹 | 含义 | 循环 |
|--------|------|------|
| idle1/2/3 | 默认状态，猫睡着，三段随机切换 | 是 |
| cat_wake | 猫醒来 | 否 |
| cat_type_remove | 猫踩键盘，程序员把猫抱走 | 否 |
| cat_down | 把猫放回，继续敲键盘 | 否 |
| rain | 开始下雨 | 否 |
| rain_idle | 下雨中，猫睡着 | 是 |
| rain_cat_wake | 下雨中猫醒来 | 否 |
| rain_cat_watch | 下雨中猫盯着屏幕 | 是 |
| drink | 喝饮料 | 否 |
| phone | 看手机 | 否 |
| scratch | 烦躁挠头（AI卡住/Windows更新/重构冲动共用） | 否 |
| drowsy | 打瞌睡 | 否 |
| excited | 灵感爆发 | 否 |
| done | 胜利结局，开头是猫盯着屏幕 | 否 |

---

## 二、转场原则

**退出时用模糊转场的序列：**
drink / drowsy / excited / phone / rain / rain_cat_wake / rain_cat_watch / rain_idle / scratch

**进入 done 永远用模糊转场，无论从哪里来。**

**直接切换的例外（不受上方规则约束）：**
- cat_wake → cat_type_remove
- rain → rain_cat_wake
- rain_cat_wake → rain_cat_watch

其余所有切换：直接切换，无转场。

---

## 三、无雨域状态机
idle1 / idle2 / idle3（随机循环）
├─→ drink       → 模糊退出 → idle
├─→ phone       → 模糊退出 → idle
├─→ scratch     → 模糊退出 → idle
├─→ drowsy      → 模糊退出 → idle
├─→ excited     → 模糊退出 → idle
├─→ rain        → 模糊退出（进入下雨域）
└─→ cat_wake
    └─→ cat_type_remove（直接）
    └─→ cat_down（直接）
    └─→ idle（直接）

规则：
- cat_type_remove 只能接在 cat_wake 之后

---

## 四、下雨域状态机

一旦 rain 触发即进入下雨域，不会自动退出。
rain 播完后：
├─→ rain_cat_wake   （直接）
└─→ rain_idle       （模糊）

rain_idle 循环中（猫睡着）：
└─→ rain_cat_wake   （模糊，事件触发）

rain_cat_wake 播完后：
└─→ rain_cat_watch  （直接）

rain_cat_watch 循环中：
└─→ rain_idle       （模糊，猫回去睡觉）

规则：
- rain_idle 不可触发 drink / phone / scratch / drowsy / excited

## 五、胜利出口
任意状态 ──[Progress = 100%]──→ 模糊转场 → done

done 开头是猫盯着屏幕，模糊淡入自然衔接。
