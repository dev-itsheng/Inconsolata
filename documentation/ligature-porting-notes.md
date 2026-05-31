# Ligconsolata Next 连字迁移复盘

这份文档记录 Ligconsolata Next 在参考 Fira Code 补充编程连字时遇到的问题、最后采用的处理方式，以及可以迁移到其他字体项目里的经验。

Ligconsolata Next 的目标不是复制 Fira Code。我们喜欢 Fira Code 的连字覆盖面和 OpenType 行为，但这个项目是在 Inconsolata / Ligconsolata 这条线上继续补连字，所以字母、大括号、整体节奏和 glyph outline 都应继续扎根于 Inconsolata。

## 总体原则

1. 只参考 Fira Code 的覆盖面、交互行为和 OpenType 组织方式，不复制 Fira Code 的 outline。
2. 所有连字必须保持原始 ASCII 字符序列的 advance width，例如两字符连字保持两格，三字符连字保持三格。
3. 固定长度操作符优先用 `.dlig` glyph，同时同步暴露到 `dlig` 和 `liga`。
4. 可变长度箭头优先用 `calt` 和 start / middle / end 片段拼接，不枚举每一种长度。
5. 任何视觉样张都必须来自真实构建产物，不能用 Unicode 符号替身。
6. 每次改 glyph 或 feature 后，都要用 `hb-shape`、SVG specimen 和浏览器 demo 三条路径复核。

## 问题与解决

| 问题 | 现象 | 原因 | 解决方式 |
| --- | --- | --- | --- |
| `liga` / `dlig` 默认行为不一致 | Inconsolata 已有连字在多数编辑器里看不到 | 上游把编程连字放在 `dlig`，编辑器通常只开 `liga` | 保留 `dlig`，同时把同一套 substitution 写入 `liga` |
| 不能直接搬 Fira Code outline | Fira Code 的连字好看，但字母和括号风格不是用户想要的 | 字形来源一旦混用，字体整体气质会散 | 只迁移覆盖面和 OpenType 行为，glyph 从 Inconsolata 现有笔画派生 |
| overview SVG 一开始不可信 | 早期图片用符号近似，例如 `⇒`、`≠`，看起来像连字但不是实际 glyph | Unicode 替身和真实 ASCII shaping 不是同一件事 | `scripts/generate-overview-svg.py` 改为读取构建字体 outline，并通过 `hb-shape` 得到真实 glyph 序列 |
| `==` 被 `calt` 抢走 | `a == b` 显示成两个 seq 片段，不是 `equal_equal.dlig` | `equal' [equal greater]` 这种规则会把普通 `==` 当作箭头起点 | 在 `calt` start lookup 里用 `ignore sub` 避开 `==`、`===` 等固定连字上下文 |
| `==` / `!=` 看起来像三条横线 | overview 里 `==` 和 `!=` 容易被读成 `===` / `!==` | 早期从三横线 glyph 横向缩放出两字符版本，视觉上仍保留三横线结构 | `==` 改为从原始 `equal` 的两条横线派生；`!=` 继续复用 `!==` 的斜杠结构，但替换为新的两横线 `equal_equal.dlig` |
| `!==` / `===` 被误伤 | 三字符固定连字被拆成普通 glyph 加 seq glyph | `calt` 和固定连字同时覆盖 `=` 串，lookup 顺序导致局部先替换 | 用 `hb-shape` 查真实输出，确保 `!==` 回到 `exclam_equal_equal.dlig`，`===` 回到 `equal_equal_equal.dlig` |
| `<====` / `<----` 左向长箭头不完整 | 后半段被 `===` 或 `--` 固定连字抢走 | 如果 start 和 extend 逻辑在同一轮里处理不完，后续 `liga` 会吃掉剩余字符 | 将长箭头 `calt` 拆成 start lookup 加多轮 extend lookup，让 seq 先完整延展 |
| `i--` 看起来像一条横线 | 两个减号直接连上，容易读成 dash 或分割线 | `--` 和 `----` 的语义不同，不能共用连续横线策略 | `--` 改成两个靠近但有明确间隔的减号；`----` / `-----` 继续作为注释分割线连续处理 |
| `:=` 视觉不舒服 | 冒号和等号不在同一视觉中心线上 | 直接拼组件会继承原字符位置，不一定适合作为操作符整体 | 参考 Fira Code 的思路，将冒号 dot 对齐到等号两条横线的中心高度 |
| Fira Code 静态 `liga` 清单与 `calt` 清单容易混在一起 | 看起来“都来自 Fira Code”，但实现风险完全不同 | 静态 `liga` 可以按固定 glyph 处理；复杂 `calt` 往往依赖上下文机器和大量 `ignore sub` | 先确认静态 `liga` 已完整覆盖，再把 `calt` 拆成低风险固定批次和需要专门设计的上下文批次 |
| 重复字符运行的 glyph 名太长 | `######` / `____` 这类自动命名会生成很长的 production name，构建时出现 `public.postscriptNames... = None` | Glyphs 源文件里的 postscript name 元数据不适合无限展开字符名 | 改用短名，例如 `numbersign_run6.dlig`、`underscore_run4.dlig`，并用脚本删除旧的过长生成块 |
| 新增固定组合被现有 `calt` 抢走 | `->>`、`=>>`、`<-|`、`<=|` 没有命中新增 `.dlig`，`i--` 又被长横线片段化 | 长箭头 start lookup 和新增固定连字共享前缀 | 在 `calt` start lookup 中添加更明确的 `ignore sub`，并把 `--` 与 `---` 分开：`i--` 仍命中 `hyphen_hyphen.dlig`，三字符以上再走长横线片段 |
| 下划线 run 只靠固定清单会到头 | `__` 到 `______` 可以固定生成，但再长就需要继续枚举 | 下划线本质是横线，适合 Fira Code 那种 start / middle / end 片段 | 保留短运行固定 glyph；超过 6 个 `_` 后，用 `underscore_start.seq` / `underscore_middle.seq` / `underscore_end.seq` 延展 |
| hash run 不适合立刻照搬同样机制 | `#` 不是简单横线，用 seq 草率拼接可能比固定 glyph 更难看 | `#` 的两个斜竖和横线需要单独设计 start / middle / end 视觉 | 当前保留 `##` 到 `########` 固定覆盖，后续先设计 glyph 再决定是否上下文化 |
| pipe/bar 端点长箭头需要避开短固定项 | `|--`、`--|`、`|==`、`==|` 已经有固定 glyph，如果直接从两个字符起步做 `calt` 会抢替换 | 固定短组合和任意长度端点箭头共享前缀 | 第一批只在至少 3 个 `-` / `=` 时启动 pipe/bar seq，例如 `|---`、`---|`、`|--->`、`<---|`、`|===>`、`<===|` |
| slash / marker 机制不能一口气全搬 | Fira Code 支持单 slash、双 slash、colon、exclamation 等多种 `=` 串上下文 | slash 很容易和 `/=`、`/==`、`//`、`///`、URL 和注释冲突；colon / exclamation 在 Fira Code 里更像 middle marker，不是完整端点 | 第一批只做单 `/` 长 `=` 端点、单 `/` middle 和 `:` / `!` middle marker，例如 `/===>`、`<===/`、`===/===`、`==:=`、`==!=`；短组合继续由固定 glyph 负责，并显式避让 `//===` / `///===` 这类注释前缀；双 slash 端点暂缓 |
| center alignment 不是连字清单 | Fira Code 的 `calt/center.fea` 只是在 `:` / `<` / `>` 相邻时切换到 `.center` 视觉变体 | 如果写成“新增连字”，会误导读者；如果直接套到多冒号场景，又会和现有 `::` / `:::` 固定 glyph 冲突 | 默认迁移 `:<`、`:>`、`<:`、`>:`、`<:>`、`>:<` 小批次；多冒号 center 和更多 `cv` / `ss` 风格项暂缓 |
| 固定清单很容易漏项 | 手动维护 README、脚本、SVG 清单容易不同步 | 连字覆盖面跨多个文件，新增时容易只改一处 | 以 `scripts/update-ligature-glyphs.py` 的 `LIGATURES` / `FIRA_CODE_COMPAT_SOURCES` 为核心来源，SVG 脚本动态读取这份清单 |
| 图片排版不利于复核 | 双栏 before / after 需要来回对照，右侧 raw 文本上下不容易对齐，窄网格下长样例容易贴近下一格 | specimen 是给人复核用的，不只是展示图 | 改成 Fira Code 式左右对比：左侧 shaped result，右侧 raw ASCII，同一行放多个相关样例；分组标题作为左侧表格列，水平左对齐、垂直居中，横线等距贯穿整行，并用更宽的固定网格槽位对齐 |
| 双语信息容易抢主视觉 | README 顶部图需要中文辅助，但主视觉仍应像专业 specimen | 中英文同权会让标题和图例显得吵 | 英文保留主层级；中文用小字号、弱颜色贴近对应英文。胶囊标签使用 `English / 中文`，斜线两边各留一个空格 |
| SVG 仍然不是交互式证据 | SVG 是生成时刻的静态 specimen | 用户需要确认浏览器和编辑器里真实字体开关如何表现 | 新增 `documentation/demo/index.html`，用 CSS `@font-face` 引入真实字体，并提供可编辑文本和 feature 开关 |
| 全量脚本变慢 | 新增大量 glyph 后，`update-ligature-glyphs.py` 可能跑数分钟 | 每次都 parse / rewrite 大型 Glyphs 源文件 | 短期接受，后续应拆分「只更新 feature」和「重建 glyph」两条路径 |

## Fira Code 给我们的关键启发

Fira Code 的价值不只是“有哪些连字”，更重要的是它处理上下文的方式。

- 固定连字覆盖面很广，例如函数式操作符、哈希族、点号族、冒号族、三连重复符号。
- 长箭头不是靠枚举 `-->`、`--->`、`---->`，而是用 start / middle / end 片段做任意长度拼接。
- 大量 `ignore sub` 用来避免误伤普通代码，例如 `==`、`===`、`!==`、`--`、注释分割线和语言特定上下文。
- specimen 很重视“同一 ASCII 源码变成什么效果”，这比单独展示最终 glyph 更能说明问题。

Ligconsolata Next 当前已经覆盖 Fira Code 静态 `liga` 清单里的固定操作符，并迁移了其中比较稳的一层：`-` / `=` 长箭头、真实 specimen、浏览器 demo，以及第一批 Fira Code `calt`-inspired 固定组合，例如 hash / underscore runs、`=/=` / `/=` 族、`=~` / `!~` / `.=` 这类 center-style 固定项、`->>` / `=>>` 族、`>--` / `==<` 族和 pipe endpoint 族。下划线 run 已经从固定清单继续推进到长运行 `calt` 延展；hash run 已评估并暂缓上下文化；pipe/bar 端点长箭头已经先迁移单 `|` 端点批次；slash / colon / exclamation 先迁移了单 `/` 长 `=` 端点、单 `/` middle 和 `:` / `!` middle marker 小批次；Fira Code center alignment 已先迁移 `:` / `<` / `>` 的小批次视觉居中。Fira Code 更复杂的双 slash 端点、多冒号 center、lowercase operator、hexadecimal `x` 等 `calt` 行为还没有完整迁入，后续应按小批量继续验证。

README 顶部 overview 是代表性样例，不是完整支持清单。完整规则以 `scripts/update-ligature-glyphs.py` 里的 `LIGATURES` 和 `FIRA_CODE_COMPAT_SOURCES` 为准。

## 迁移到其他字体时的通用流程

1. 先确定派生字体要保留什么气质，例如字母、括号、行高、字重、终端阅读感。
2. 再选择参考字体，只借“用户期待的连字类别”和“OpenType 行为”，不要直接混用 outline。
3. 把连字分成固定长度和可变长度两类。
4. 固定长度先按最长序列排序，例如 `=====` 在 `====` / `===` / `==` 前。
5. 可变长度用 `calt` 片段，不要靠无限枚举。
6. 每新增一批连字，都检查 raw width 与 shaped width 是否一致。
7. 用 `hb-shape` 直接看 glyph 名称，不要只靠肉眼看图片。
8. 生成静态 specimen 时，一定要从真实字体 outline 渲染，不要用 Unicode 替身。
9. 再补一个真实运行环境 demo，例如 HTML + CSS `@font-face`，让用户能自己改样例。
10. 最后把踩坑记录写回项目规则，避免下一轮又从同一个坑开始。

## 本项目的验证锚点

常用生成命令：

```sh
python scripts/update-ligature-glyphs.py
python scripts/generate-overview-svg.py --build
python scripts/build-demo-assets.py
```

常用 shaping 检查：

```sh
/opt/homebrew/bin/hb-shape \
  "/tmp/ligconsolata-next-smoke/LigconsolataNext[wdth,wght].ttf" \
  "a != b a !== b a == b a === b x <==== y x <---- y i--" \
  --features="liga=1,dlig=1,calt=1"
```

期望看到的关键结果：

- `a != b` 使用 `exclam_equal.dlig`。
- `a !== b` 使用 `exclam_equal_equal.dlig`。
- `a == b` 使用 `equal_equal.dlig`。
- `a === b` 使用 `equal_equal_equal.dlig`。
- `x <==== y` 使用 `less_equal_start.seq`、多个 `equal_middle.seq` 和 `equal_end.seq`。
- `x <---- y` 使用 `less_hyphen_start.seq`、多个 `hyphen_middle.seq` 和 `hyphen_end.seq`。
- `i--` 使用 `hyphen_hyphen.dlig`，但视觉上两个减号仍有分隔。

新增 Fira Code `calt`-inspired 固定组合后，还应补充检查：

```sh
/opt/homebrew/bin/hb-shape \
  "/tmp/ligconsolata-next-smoke/LigconsolataNext[wdth,wght].ttf" \
  "a =/= b a /== b a =~ b a !~ b obj .= x a <:> b a :> b x ->> y x >-- y x ==< y f |---> g f <---| g f |===> g f <===| g f /===> g f <===/ g a ===/=== b a ==:= b a ==!= b md ####### title ______ _______" \
  --features="liga=1,dlig=1,calt=1"
```

期望看到 `equal_slash_equal.dlig`、`slash_equal_equal.dlig`、`equal_asciitilde.dlig`、`exclam_asciitilde.dlig`、`period_equal.dlig`、center alignment 里的 `less.center` / `greater.center` / `colon.center`、`hyphen_greater_greater.dlig`、`greater_hyphen_hyphen.dlig`、`equal_equal_less.dlig`、pipe/bar 长箭头里的 `bar_hyphen_start.seq` / `bar_hyphen_end.seq` / `bar_equal_start.seq` / `bar_equal_end.seq`、slash / marker 小批次里的 `slash_equal_start.seq` / `slash_equal_middle.seq` / `slash_equal_end.seq` / `colon_equal_middle.seq` / `exclam_equal_middle.seq`、`numbersign_run7.dlig`、`underscore_run6.dlig`，以及长下划线里的 `underscore_start.seq` / `underscore_middle.seq` / `underscore_end.seq`。

## 当前仍要小心的边界

- 新增 Fira Code 风格覆盖时，先从固定 glyph 开始，不要一口气迁移所有复杂 `calt`。
- pipe / slash / bar 端点的任意长度箭头会显著增加 lookup 复杂度，迁移前要先补足测试样例。
- 只看 GSUB 有替换并不等于视觉可用；overview 和 HTML demo 里看不出变化的连字，要么重新设计，要么先不要公开展示。
- `scripts/update-ligature-glyphs.py` 目前适合可靠生成，不适合高频快速迭代；后续优化应优先降低它的全量重写成本。
