# AGENTS.md

## 项目定位

- 这个仓库是 `googlefonts/inconsolata` 的派生字体项目，当前派生名是 `Ligconsolata Next`。
- 修改版字体不要继续使用上游 `Inconsolata` family name。文档、源码配置、metadata 和构建产物里的公开名称都应保持 `Ligconsolata Next`。
- 这是字体源码项目，不是前端项目。除非任务明确涉及网页、浏览器 UI 或前端工程，不要套用全局前端规则。
- 默认用中文记录项目内协作说明；面向上游、Google Fonts 或英文用户的正式 README / metadata 可以继续用英文。

## Codex / Cursor Agent 分工

- 这个仓库里的非轻量任务仍优先考虑 Cursor Agent 分担，但 Codex 必须保持主控：整理任务包、判断边界、回收结果、复核 diff、跑必要验证，并给用户交付最终结论。
- 分派前先把 Cursor 子任务分成两类：
  - 探索型：问「你觉得应该怎样改」「还有什么风险」「给不同视角」。这类任务只读，优先用和 Codex 主线不同的模型，当前默认 `claude-opus-4-8-thinking-max`，让不同模型提供异质建议。实际模型 ID 必须以 `cursor-agent models` 为准；如果模型列表为空或目标模型不可用，要在最终回复里说明，不要假装已经调用成功。
  - 分派型：让 Cursor「把这个事情做了」，例如补样例、改脚本、做小范围文档或代码初稿。这类任务优先用和 Codex 同级的 `gpt-5.5-extra-high`，让实现口径、推理深度和 Codex 主线对齐。
- 探索型输出不能直接当结论。Codex 要回到字体源码、OpenType feature、`hb-shape`、SVG demo、HTML demo 或相关文档里复核；成立的再吸收，不成立的要标注为参考意见。
- 分派型改动后必须看 `git status --short`、关键 diff 和验证命令；必要时由 Codex 手工修正，不能把 Cursor 的 patch 原样交给用户。
- 本仓库适合交给 Cursor 的探索型任务包括：参考 Fira Code / JetBrains Mono / Iosevka 等字体的思路、梳理 feature 覆盖缺口、审视 demo 展示方式、提出 QA 样例。适合交给 Cursor 的分派型任务包括：补文档样例、整理 catalog、生成初稿、做局部脚本改动。权威 glyph / GSUB 改动仍要由 Codex 最终复核并验证。

## 源码与构建边界

- 字体源码的权威入口是 `sources/Inconsolata.glyphs`，构建配置入口是 `sources/config.yaml`。
- 先改 Glyphs 源码，再构建验证；不要把 `fonts/` 里的既有二进制字体当成可直接手改的权威来源。
- 开发 smoke build 默认输出到 `/tmp/ligconsolata-next-smoke/`，避免覆盖仓库里的字体文件。只有用户明确要求生成发布字体时，才改写仓库内的构建产物。
- `.venv/` 是本地构建环境，已加入忽略规则；`.idea/` 是用户本地 IDE 文件，除非用户明确要求，不要修改或清理。
- 当前依赖链路更适合 Python 3.10。初始化参考：

```sh
/opt/homebrew/bin/python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install "pip==23.3.2" "setuptools==58.5.3" "wheel==0.37.1"
python -m pip install --no-build-isolation -r requirements.txt
```

- `requirements.txt` 使用 `openstep-plist==0.3.0.post1`，因为原始 `0.3.0` 在当前 pip 元数据校验下安装会失败。

## 连字设计原则

- 迁移 Fira Code 连字时，先读 `documentation/ligature-porting-notes.md`。那里记录了本轮适配遇到的真实问题、解决方式和可复用验证流程。
- 当前已启用的连字包括：
  - 当前上游 `dlig` baseline 已有并继续保留：`!==`、`===`、`->`、`=>`、`>=`、`<-`、`<=`。
  - Next 补充并修正的两字符相等 / 不等形态：`!=`、`==`。
  - 新增常用操作符：`<=>`、`<->`、`-->`、`<--`、`==>`、`<==`、`...`、`<>`、`::`、`:=`、`&&`、`||`、`++`、`--`、`**`、带上下文保护的行注释前缀和块注释边界、`??`、`?.`。
  - 参考 Fira Code 补充的一批默认固定操作符覆盖面由 `scripts/update-ligature-glyphs.py` 里的 `FIRA_CODE_COMPAT_SOURCES` 维护，例如 `<|>`、`<$>`、`<+>`、`</>`、`|>`、`<|`、`::=`、`..=`、`..<`、`?=`、`!!`、`!!.`、`+++`、`***`、`#{`、`#[`、`#_(` 等；`www` 不进入默认连字，保持 URL / 域名 raw 可读；`//` / `///` 虽然有 glyph，但只在注释前缀上下文启用。
  - 第一批参考 Fira Code `calt` 行为但按固定连字落地的低风险组合由 `FIRA_CODE_CALT_FIXED_LIGATURES` 维护，例如 `__` 到 `______`、`=/=`、`=!=`、`=:=`、`=~`、`!~`、`/=`、`/==`、`.=`、`.-`、`:-`、`[]`、`->>`、`<<-`、`=>>`、`=<<`、`>--`、`--<`、`|--`、`--|`、`>==`、`==<`、`|==`、`==|`、`==/`、`>>-`、`>-`、`-<`、`|->`、`<-|`、`|=>`、`<=|`、`||-`、`-||`、`|-`、`-|`。
  - `calt` 可变长度箭头：`---->`、`<----`、`====>`、`<====`、`<--->`、`<===>` 这类长度不固定的 `-` / `=` 箭头，以及单 `>` / `<` 端点的 `>---`、`---<`、`>===`、`===<`。
  - `calt` 端点和 marker 小批次：单 `|` 端点长箭头，以及长 `=` 串里的单 `/` 端点、单 `/` middle、`:` / `!` middle，例如 `|--->`、`<===|`、`/===>`、`<===/`、`===/===`、`==:=`、`==!=`。
  - `calt` center alignment 小批次：`:<`、`:>`、`<:`、`>:`、`<:>`、`>:<` 这类 `:` / `<` / `>` 相邻场景会切换到 `.center` 视觉变体。这是标点对齐，不是新增 `.dlig` 连字。
  - `calt` lowercase / uppercase operator matching 小批次：`var-name`、`a+b`、`*ptr` 会把 `-` / `+` / `*` 切到 `.lc` 视觉变体；`CONST:VALUE` 会把 `:` 切到 `.uc` 视觉变体。混合大小写上下文如 `A:b`、`a:B` 不替换，避免误导。
  - `calt` numeric `x` 小批次：`0xFF`、`0xff`、`0x10`、`800x600`、`1920x1080` 里的小写 `x` 会切换成 `x.multiply`。普通单词、字母两侧的 `x`、无效十六进制样式如 `0xG`、大写 `X` 不替换。
  - `calt` Markdown heading hash badge：行首 / shaping run 开头且后接普通空格的 `## title` 到 `###### title` 保持原始总 advance width，把井号横杠连成一组，并在最后一个 `#` 的右上区域嵌入数字 `2` 到 `6`；单个 `#`、`##title`、`a ## b` 保持 raw glyph；`#######` 及更长 run 使用 `numbersign_start.seq` / `numbersign_middle.seq` / `numbersign_end.seq` 连成无编号井号横杠序列。
  - `calt` 块注释边界：`/*` 只有后接普通空格时触发，`*/` 只有前接普通空格时触发；`**/*.{ts,tsx}`、`!**/composables/**/*.ts` 等 glob / path 场景保持 raw slash / asterisk，但 `**` 仍可作为 globstar 连写。
  - `calt` 逻辑 `/\` / `\/` 小批次：只有两侧都有普通空格的 `a /\ b`、`x \/ y` 触发；`/\d/`、`\/tmp` 等 regex / 路径场景保持 raw glyph。
  - 注释分割线辅助：`====`、`=====`、`----`、`-----`。
- 上游已有的一组连字原本存在于 Inconsolata 的 `dlig` 中；Ligconsolata Next 继续保留 `dlig`，并把当前支持的 substitution 同步暴露到 `liga`。当前可验证的上游 `dlig` baseline 不包含 `!=` / `==` 两字符形态；它们属于 Next 补充并修正过的 equality pair，不要在继承对比图里写成旧版已有。
- glyph 名称可以继续沿用已有 `.dlig` 后缀。feature tag 和 glyph 命名不必强行一致，重点是 GSUB 里同时有 `dlig` 和 `liga` 规则。
- 连字的 advance width 必须等于原始字符序列的总 advance width。Regular 默认位置里，两字符连字应为 1000，三字符连字应为 1500，四字符分割线应为 2000，五字符分割线应为 2500。新增连字时也要按所有相关 master 或最终构建产物检查宽度。
- 新连字应从 Inconsolata 自己的笔画、比例和字面节奏里推出来。Fira Code 可以作为「程序员期待哪些连字」和「如何展示连字」的参考，但不能复制 Fira Code 的 outline。
- 新增连字优先走脚本化小步：把可重复的派生逻辑写进 `scripts/update-ligature-glyphs.py`，再生成 Glyphs 源码、验证构建、GSUB、宽度和视觉。
- `scripts/update-ligature-glyphs.py` 负责生成脚本派生 glyph，并同步改写 `calt` / `dlig` / `liga`。`liga` 规则必须保持长序列在短序列前面，例如 `=====` 在 `====` / `===` / `==` 前，`-->` 在 `--` / `->` 前。
- `==` 和 `!=` 必须保持两条横线。不要把它们从 `===` / `!==` 直接横向缩放出来，否则 overview 和真实编辑器里会看起来像三横线，和 Fira Code 及程序员预期不一致。
- `===` 和 `!==` 必须保持三条清楚可辨的横线，不能被 `==` / `!=` 的两横线策略误伤。三横线整体视觉中心应对齐原始 `equal` / `==` 的中心；优先移动 `===`，不要为了对齐把 `==` 从原始 `equal` 位置下移。`====` / `=====` 以及更长连续等号才属于注释分割线 / run 语义，继续使用两条连续长线。
- `<=` / `>=` 是 comparison 语义，不是箭头语义。它们默认应画成 `<` / `>` 加一条同源、平行、等长的下斜线，参考 Fira Code 默认 `less_equal.liga` / `greater_equal.liga` 的思路；第二条斜线应与 `<` / `>` 的下斜边保持同一视觉跨度，并且两端使用竖切，不继承 `<` / `>` 内部连接处的斜切口。水平 bar 只适合作为未来 opt-in stylistic / character variant，不应作为默认。`<==`、`==>`、`<====`、`====>` 才属于 `=` 箭头族。
- Unicode `emdash` (U+2014) 和 `horizontalbar` (U+2015) 属于中文混排标点问题，不是编程连字：它们应保持两倍当前 Latin cell 宽度，并且横线轮廓应从 x=0 延伸到当前 advance 右边缘，让 `——`、`――` 和更长 dash run 自然连成一条。Regular 默认位置是 1000，Ultra Condensed 是 500，Ultra Expanded 是 2000；`endash` (U+2013) 和 `figuredash` (U+2012) 继续保持一格和原本留白，避免影响西文范围和数字排版。不要为 `emdash emdash` 单独加 GSUB 连字来解决这个问题，除非之后有明确证据说明边缘连续方案在目标编辑器里有副作用。
- 可变长度箭头参考 Fira Code 的处理思路，但只复用机制：用 `hyphen_start.seq` / `hyphen_middle.seq` / `greater_hyphen_end.seq`、`equal_start.seq` / `equal_middle.seq` / `greater_equal_end.seq` 等片段拼接，不复制 Fira Code outline。
- `calt` 长箭头当前采用 start lookup 加多轮 extend lookup。不要把所有逻辑塞进一个 lookup；否则 `<====` / `<----` 这类左向长箭头容易被后续固定 `===` / `--` 抢走。
- `calt` 规则要优先保证长箭头能随字符数自然延展；如果某条规则会破坏普通 `->` / `<-` / `=>` / `<=` / `==` / `===` / `!==` / `i--` 等既有 `liga` / `dlig`，宁可缩小 `calt` 覆盖范围，并用 `ignore sub` 明确避开这些固定连字。
- `//` / `///` 只在后面跟普通空格时启用注释前缀连字，例如 `// comment`、`/// reference`。不要把裸 `//` / `///` 写成无条件 `liga` / `dlig` 规则，否则 `https://example.com`、`file:///tmp/font`、路径和其他非注释文本会被误伤。Fira Code 的源码里有 `slash_slash.liga` / `slash_slash_slash.liga` 和 `.spacer` 上下文机制，但本项目为 URL 可读性保留这个有意差异。
- `/*` / `*/` 是块注释边界，不是 glob-star 或路径辅助符号。不要把它们写成无条件 `liga` / `dlig`；默认只在 `calt` 中用 spacer 两步保护：`/*` 需要后接普通空格，`*/` 需要前接普通空格。像 `**/*.{ts,tsx}`、`!**/composables/**/*.ts`、`src/*.ts` 这类 glob / path 样例必须保持 raw `/*` / `*/`。
- `www` 不默认合并。Fira Code 支持 `w_w_w.liga`，但本项目把 URL、域名和普通文本里的 `www` 保持 raw，以便扫读真实地址。后续不要把 `www` 加回 `FIRA_CODE_COMPAT_SOURCES`，除非先提供明确收益和 URL 可读性验证。
- `[]` 使用 `bracket_pair` 生成真实路径，不走普通 `compact_components`。原因是 `bracketright` 本身由 `bracketleft` 镜像组件构成，继续嵌套组件会让小字号下的方框左右观感不均衡；生成时要保持两字符 advance width，并按真实外轮廓居中。
- `x.multiply` 从 Inconsolata 自己的 `multiply` glyph 派生，不复制 Fira Code outline，并且必须显式清空 Unicode，避免继承 U+00D7。当前只迁移 Fira Code `features/calt/cross.fea` 里不依赖 `onum` 的小写 `x` 分支：`@HexZero x [@Digit @HexDigit]` 和 `@Digit x @Digit`。不要默认迁移 `x.multiply.tosf`、old-style figures、大写 `X` 或带空格的 `3 x 4`。
- 新增与长箭头共享前缀的固定组合时，必须同步复核 `calt` 是否抢先替换。例如 `->>`、`=>>`、`<-|`、`<=|` 需要在 start lookup 中避让，`i--` 必须继续命中 `hyphen_hyphen.dlig`。
- 自动生成 glyph 名称时避免过长的生产名。像 `____` 这种重复字符运行应使用 `underscore_run4.dlig` 这类短名；hash badge 使用 `numbersign_run2.dlig` 到 `numbersign_run6.dlig`，7 个及以上的 hash run 使用 `numbersign_start.seq` / `numbersign_middle.seq` / `numbersign_end.seq`。过长名称可能让 `public.postscriptNames` 写出 `None`，导致 Glyphs plist 保存失败。
- Markdown 标题里的连续 `#` 默认采用分层方案，不恢复旧的无编号固定覆盖。行首 / shaping run 开头且后接普通空格的 `## title` 到 `###### title` 只在 `calt` 中启用，使用 `numbersign_badge_spacer` 逐步折叠前置 `#`，最后输出 `numbersign_run2.dlig` 到 `numbersign_run6.dlig`；每个 glyph 保持原始总 advance width，把井号横杠连成一组，并在最后一个 `#` 的右上区域嵌入数字 `2` 到 `6`。单个 `#`、`##title`、`a ## b` 保持 raw glyph，避免行内文本误伤；`#######` 及更长 run 使用 `numbersign_start.seq` / `numbersign_middle.seq` / `numbersign_end.seq` 延展，但不加数字，避免把长分割线误装成 Markdown 标题层级。
- `====` / `=====` 使用两条连续横线，`----` / `-----` 使用一条连续横线，用来改善注释分割线的视觉连续性。但字体不能修正源码里上下分割线字符数不一致的问题；生成注释分割线时仍应使用固定长度文本，避免手写差一个字符。
- `--` 不要做成一条连续横线；它应该保留两个减号的分隔感，避免和长 dash 或注释分割线混淆。
- `scripts/update-ligature-glyphs.py` 默认会全量重写大量 glyph block，新增覆盖面后耗时可能达到数分钟；只需要刷新 class / feature 时可以使用 `--features-only` 跳过 glyph block。
- 兼容性 guard 要有可执行测试。新增或改动 `//` / `///`、`/*` / `*/`、`/\` / `\/`、numeric `x`、Markdown hash badge、长箭头与固定连字避让等特殊处理时，同步更新 `tests/test_ligature_context_guards.py`，用 `hb-shape` 验证真实 demo 字体输出，而不是只看 feature 源码。

## 目标编辑器与 OpenType feature 策略

- 默认目标是代码编辑器和网页代码展示，不是印刷排版软件。默认编辑器体验只依赖 `liga` 和 `calt`：短固定编程连字放在 `liga`，上下文判断、任意长度箭头、大小写/数字上下文和注释前缀保护放在 `calt`。
- `dlig` 只作为继承 Inconsolata / Ligconsolata 历史和少数编辑器 opt-in 的兼容层。新增短固定连字可以继续镜像到 `dlig`，但不要把任何核心体验设计成“只有打开 `dlig` 才能看到”。
- `ssXX` / `cvXX` / `salt` / `zero` / `frac` / `numr` / `dnom` / `subs` / `sups` / `ordn` 只适合风格、数字排版或高级排版入口，不承载默认编程连字。WebStorm / VS Code / Zed / Sublime 的普通“启用连写”路径都不应被假设会自动打开这些 feature。当前自定义编码体验不再依赖 `ss06`：细反斜杠由 `calt` 把 `backslash` 替换成内部 glyph `backslash.thin`，并且只改变 outline，不改变颜色或透明度。
- 当前 Ligconsolata Next 构建产物里还有 `aalt`、`case`、`ccmp`、`locl` 等 feature。`ccmp` / `locl` 更接近文字 shaping 基础能力，`case` 是大写标点/组合音标位置调整，和编程连字策略不是同一层。记录它们时要说明“字体包含”，不要写成“编辑器连写开关默认会启用”。
- WebStorm / IntelliJ 平台的「启用连写」开关不是手写 `liga` / `calt` 字符串，而是走 JetBrains Runtime 的 `TextAttribute.LIGATURES_ON`。本机 WebStorm.app 自带 JBR 已验证：勾选后 `a-b` 会命中 `hyphen.lc`，`A:B` 命中 `colon.uc`，`0xFF` 命中 `x.multiply`，`a---->b` / `a====>b` 命中 `.seq` 长箭头片段，说明当前 WebStorm 能吃到本项目 `calt`。
- WebStorm 2026.1 的 Font 设置把「Enable ligatures」和「Character variants」分开。前者用于连写，后者面向 OpenType stylistic sets；不要用 WebStorm 的连写开关证明 `ss01`、`zero` 或 `frac` 会生效。
- VS Code 官方在 1.40 release notes 里明确说明：`"editor.fontLigatures": true` 会开启 `liga` 和 `calt`；如果用户把 `editor.fontLigatures` 写成 feature 字符串，则以用户显式配置为准。验证 VS Code 时优先用 `true` 做默认路径，再用 `"'liga' 1, 'calt' 0"` / `"'liga' 0, 'calt' 1"` 做定位。
- WebView / Electron / 浏览器里的代码块和 Monaco 类编辑器通常走浏览器 CSS shaping。CSS `font-variant-ligatures: normal` 默认启用常见连字和上下文形式，`common-ligatures` 对应 `liga` / `clig`，`contextual` 对应 `calt`；`font-feature-settings` 可以显式写 `"liga" 1, "calt" 1`。不要假设所有网页代码块都会默认显示连字，因为站点 CSS 可能设置 `font-variant-ligatures: none`、`font-feature-settings: "liga" 0`，或没有加载 Ligconsolata Next。
- Sublime Text 官方文档明确说明：默认会使用 ASCII symbol 序列里的 `clig` / `liga` / `calt`；`dlig` 必须在 `font_options` 里添加 `"dlig"` 才会使用；也可以用 `"no_liga"` / `"no_calt"` 禁用对应 feature。验证 Sublime 时用 Plain Text 语法先排除 token 边界影响，再切回真实语言语法确认。
- Zed 官方 `buffer_font_features` 支持 OpenType feature 的 enable / disable 和数值设置；示例里用 `"calt": false` 关闭字体连字。验证 Zed 时设置 `buffer_font_family` 为 `Ligconsolata Next`，再分别切换 `"calt": false` 和 `"liga": false`：前者应影响 `a-b`、`0xFF`、长箭头等上下文效果，后者应影响 `!=`、`==`、`=>`、`<=` 等固定连字。
- 目标编辑器兼容性不要靠肉眼猜。推荐最小样本如下，能同时覆盖 `liga`、`calt`、URL 规避、注释前缀和 equality 区分：

```text
a-b
A:B
0xFF
a---->b
a====>b
https://x
// comment
!== === ==
```

- 本地命令级验证继续以 `hb-shape` 为主：用 `--features='liga=1,calt=0'` 和 `--features='liga=1,calt=1'` 对比上面的样本。若某个编辑器表现异常，先用它自己的 feature 开关复现差异，再判断是字体 GSUB 问题、编辑器 feature 开关问题、语法 token 边界问题，还是站点 CSS 问题。
- 默认编辑器路径的 smoke test 应显式把 `dlig` 关掉，避免误把兼容层当成功能来源：

```sh
hb-shape "documentation/demo/fonts/LigconsolataNext[wdth,wght].ttf" \
  "a != b a !== b a == b a === b x <==== y // comment https://x" \
  --features="liga=1,calt=1,dlig=0"
```

## Fira Code 迁移队列

后续按这个队列一项一项推进。每完成一项，先验证，再把勾选状态和要点写回这里，避免上下文压缩或 Cursor worker 分工后丢失细节。

- [x] 派生字体命名、README / README.zh-CN、OFL 边界和 Fira Code 致谢说明。
- [x] 将 Inconsolata 原有 `dlig` 编程连字同步暴露到 `liga`。
- [x] 覆盖 Fira Code 静态 `liga` 清单里适合默认编辑器路径的大多数固定操作符，并保持 Inconsolata-family outline 来源。`www` 是有意差异，不默认合并。
- [x] 建立真实 specimen 链路：`overview-samples.txt` -> 临时构建字体 -> `hb-shape` -> SVG outline。
- [x] 建立浏览器真实对比 demo：`documentation/demo/index.html` + 本地生成字体。
- [x] 迁移第一批 Fira Code `calt`-inspired 固定组合，包括 underscore runs、`=/=` / `/=` 族、`->>` / `=>>` 族和 pipe endpoint 族。
- [x] 迁移第二批低风险固定端点组合，包括 `>--` / `--<`、`|--` / `--|`、`>==` / `==<`、`|==` / `==|`、`==/`，并补充 `_` run 到 6 字符。
- [x] 将 underscore runs 从有限固定清单推进到上下文型 `calt` 规则。已验证：`__` 到 `______` 继续命中固定 glyph，`_______` 及更长连续下划线使用 `underscore_start.seq` / `underscore_middle.seq` / `underscore_end.seq` 延展。
- [x] 评估旧版 hash run 压缩方案是否适合上下文型 `calt`。结论：不默认启用 `##` 到 `########` 的无编号固定覆盖，也不把短 Markdown 标题标记压成不可数形态。当前折中方案是 `## title` 到 `###### title` 加数字徽标，`#######` 及更长 run 用 seq glyph 连成无编号长 run。
- [x] 设计并迁移第一批任意长度 pipe/bar 端点箭头：`|---`、`---|`、`|--->`、`<---|`、`|===`、`===|`、`|===>`、`<===|` 这类单 `|` 端点，短组合 `|--` / `--|` / `|==` / `==|` 继续由固定 glyph 负责。
- [x] 设计并迁移第一批 slash / colon / exclamation 上下文组合：单 `/` 端点长 `=` 箭头 `/===`、`===/`、`/===>`、`<===/`，以及 `==:=`、`==!=` 这类长 `=` 串 marker；短组合 `/=`、`/==`、`==/`、`=:=`、`=!=` 继续由固定 glyph 负责。
- [x] 继续评估 Fira Code 更完整的 slash / colon / exclamation 机制。结论：先补单 `/` middle（如 `===/===`）；双 slash 端点和双字符端点依赖 Fira Code 的 `.spacer` 机制，容易和 `//` / `///` 注释、URL、路径冲突，暂缓迁移。
- [x] 梳理并迁移 Fira Code center alignment 行为：默认启用 `:<`、`:>`、`<:`、`>:`、`<:>`、`>:<` 这类 `:` / `<` / `>` 视觉居中；`<::>` / `<:::>` 等多冒号组合会被现有 `::` / `:::` 固定 glyph 接管，暂不宣称完整覆盖；`ss07`、`cv25`、`cv26`、`cv32` 等风格项维持现有固定覆盖，完整边界留到 `cv` / `ss` 特性整理。
- [x] 评估并迁移第一批 lowercase / uppercase operator matching：默认启用 `hyphen.lc`、`plus.lc`、`asterisk.lc`、`colon.uc`，只做垂直对齐调整且保持一格宽；已验证 `var-name`、`a+b`、`*ptr`、`CONST:VALUE` 命中新变体，`A:b`、`a:B` 不替换，`i--`、`->`、`=>`、`==`、`===`、`====`、`-->`、`==>` 等既有固定连字不被 `calt` 抢走。
- [x] 评估并迁移 hexadecimal / multiplication `x` 行为：默认启用 `0xFF` / `0xff` / `0x10` 和 `800x600` / `1920x1080` 这类小写 `x` 场景；`x.multiply` 从本字体 `multiply` 派生且不带 Unicode；`0xG`、`0XFF`、`800X600`、`xray`、`axb`、`x86`、`x64` 保持 raw。
- [x] 整理 Fira Code `cv` / `ss` 特性边界：默认只吸收与编程连字、操作符对齐、标点上下文直接相关且已验证不误伤源码语义的小批次，例如长箭头、center alignment、大小写操作符对齐、numeric `x`、hash badge、7+ 无编号 hash run、`/\` / `\/` 空白上下文、`=~` / `!~`、`.-`、`:-`、`.=`、`[]`；字母 / 数字 / 括号 / 符号风格、水平或箭头式 `<=` / `>=`、shift assignment 箭头恢复、long pipe、文本连字和双 slash 端点保留为未来 opt-in 或暂缓，不默认迁移，不复制外部 outline。详细边界见 `documentation/external-font-reference-index.md`。

### 下一批功能队列

这些项还没有实现。先写进这里，再按小批次推进；每做完一项都要把状态和验证结果改回本文件。

- [x] 重新设计 Markdown heading `#` 规则：已实现行首 / shaping run 开头且后接普通空格的 `## title` 到 `###### title` 可数徽标，使用 `numbersign_badge_spacer` + `numbersign_run2.dlig` 到 `numbersign_run6.dlig`，保持总 advance width，把井号横杠连成一组，并在最后一个 `#` 的右上区域嵌入数字；`#######` 及更长连续 `#` 使用 `numbersign_start.seq` / `numbersign_middle.seq` / `numbersign_end.seq` 连成无编号长 run；`#`、`##title`、`a ## b` 保持 raw glyph。已验证 `## title`、`###### title`、`####### title`、`######## title`、`#######`、`##title`、`a ## b`、`#include`、`#{`、`#[`、`#_(`。
- [x] 实现 hash badge 后同步文档和样例：已更新 `documentation/ligature-porting-notes.md`、`documentation/ligconsolata-next-optimizations.md`、`README.md`、`README.zh-CN.md`、overview、catalog、QA 和 demo。
- [x] 重新审计 `/\` / `\/` 逻辑符号：已从无条件固定 `liga` / `dlig` 中排除，改成 `slash_logic_spacer` / `backslash_logic_spacer` 两步 `calt`。已验证 `a /\ b`、`x \/ y` 命中，`/\d/`、`\/tmp` 保持 raw。
- [x] 评估并迁移下一批单字符端点长箭头：已扩展到 `>---`、`---<`、`>===`、`===<` 这类任意长度 `calt`，新增 `greater_hyphen_start.seq`、`less_hyphen_end.seq`、`greater_equal_start.seq`、`less_equal_end.seq`。短固定 `>--` / `--<`、`>==` / `==<` 仍由固定 glyph 负责。
- [x] 暂缓 Fira Code 双端点和 spacer 体系：`<<---`、`---<<`、`>>===`、`===>>`、`||---`、`//===`、双 slash 端点和双字符 middle 规则继续不默认迁移，原因是容易误伤 bitshift、注释、URL、路径和固定连字；记录在 `documentation/ligconsolata-next-optimizations.md` 与 `documentation/ligature-porting-notes.md`。
- [x] 评估 `bar_underscore_middle.seq` / `_|_` 类 underscore middle 机制：当前只作为 diagram / progress-bar 候选记录，不进入默认规则；没有明确高频代码收益前不实现。
- [x] 明确不迁移到默认 `liga` / `calt` 的 Fira `calt`：Greek 大写变音、`fi` / `fl` 文本连字、`twoemdash` / `threeemdash` GSUB、`asteriskmath`、old-style figure `.tosf` 分支不属于当前默认编程连字路径。
- [x] 每新增一批默认规则，同步更新 `documentation/overview-samples.txt`、`documentation/ligature-catalog-samples.txt`、QA 样例和 `documentation/demo/index.html` 相关样例，并用 smoke build、`hb-shape`、SVG XML 解析和视觉截图验证。
- [x] 拆分 `scripts/update-ligature-glyphs.py` 的「只更新 feature」和「重建 glyph」路径：新增 `--features-only`，默认无参数仍重建 glyph 和 feature。
- [x] 从默认迁移清单移除 `www`，并把历史生成的 `w_w_w.dlig` 加入 obsolete 清理；URL / 域名里的 `www` 后续保持 raw。
- [x] 将 Fira Code-inspired thin backslash 迁到默认 `calt` 路径：生成内部 glyph `backslash.thin`，并通过 `calt` 替换 raw `backslash`；不再生成项目自定义 `ss06` feature，避免核心编码体验依赖编辑器不一定暴露的 stylistic-set 开关。

## 外部编码字体参考路线

这些仓库只作为研究参考，不是 outline 来源。后续借鉴时继续遵守 Ligconsolata Next 的边界：保留 Inconsolata 字母、括号、整体节奏和 texture；只迁移适合本项目的 OpenType 行为、QA 方法、展示方式和可读性原则。

已放到本机 `~/Desktop/code/` 的参考仓库：

- `FiraCode`：主参考。继续研究固定 `liga` 覆盖面、`calt` 长箭头、center alignment、marker / endpoint 机制和 specimen 展示方式。只能借鉴行为和覆盖面，不复制 outline。
- `JetBrainsMono`：参考可读性体系。重点看 100-800 字重、Italic、较高 x-height、易混字符区分、符号清晰度、`ss` / `cv` 可选特性，以及“连字减少噪音、平衡空白”的产品解释方式。
- `cascadia-code`：参考发行拆分和编辑器适配。重点看 `Code` / `Mono` / `PL` / `NF` 的清晰命名、variable TTF、Powerline / Nerd Font 边界、italic stylistic set 和终端场景。
- `Iosevka`：参考可配置字体系统。重点看 width / weight / slope / spacing、stylistic sets、character variants、ligation feature tags、自定义 build plan 和“复杂 ligation 需要自定义构建”的边界说明。不要把 Iosevka 的大规模变体系统直接搬进本项目默认路径。
- `monaspace`：参考多字体家族和 texture healing 思路。这个方向涉及字母级 texture 调整，优先作为长期研究，不要在当前连字阶段贸然默认启用。
- `intel-one-mono`：参考可访问性和低视力开发者视角。重点看易读性目标、屏幕渲染尺寸建议、手工 hinting / rendering QA、raised colon，以及把编程连字放进 `ss01` 而非默认开启的谨慎边界。

后续吸收这些字体经验时，按这个顺序推进：

1. 先写研究记录：参考字体做了什么、解决什么问题、是否属于连字、字母设计、spacing、hinting、feature packaging 或文档展示。
2. 再判断是否适合 Ligconsolata Next：能保持 Inconsolata 气质和等宽宽度的，才进入候选。
3. 默认优先做 QA 和文档能力，例如易混字符样例、不同字号/字重截图、编辑器真实 demo、feature 边界说明。
4. 涉及字母重画、整体 x-height、spacing、hinting、texture healing 的改动，先只写研究结论，不直接实现。
5. 每个外部参考点都要落到本项目的验证链路：Glyphs 源码、临时构建、`hb-shape`、宽度检查、SVG specimen、HTML demo。

当前已完成的参考与 QA 产物：

- [x] 写外部字体研究索引：`documentation/external-font-reference-index.md` 逐个记录 Fira Code、JetBrains Mono、Cascadia Code、Iosevka、Monaspace、Intel One Mono 对 Ligconsolata Next 有用的点，以及不应照搬的边界。
- [x] 增加易混字符 QA 样例：`documentation/qa/confusable-samples.txt` 覆盖 `0/O`、`1/l/I`、`5/S`、`2/Z`、`.` / `,`、`:` / `;`、`==` / `===`、`!=` / `!==`、URL/comment、hash 标题和下划线 run。
- [x] 增加字号和字重矩阵图：`documentation/img/ligconsolata-next-size-weight-matrix.svg` 覆盖当前 `wght` axis 的 100 / 400 / 700 / 900、11 / 13 / 16 / 20px、深色和浅色背景。当前源码只生成 upright variable font，Italic 被记录为未来有斜体源码后的 QA 补项，不要把它写成已覆盖。
- [x] 评估默认 `liga` / `calt` 与 opt-in `ss` / `cv` 边界：默认只放语义清楚、宽度不变、不会误伤源码的编程连字和上下文行为；字母风格、数字风格、括号风格、`<=` / `>=` 替代样式、Powerline / Nerd Font、texture healing、hinting、italic 形态等放进未来 opt-in 或长期研究。当前项目自定义编码行为都应落在 `liga` / `calt` 上；不要再把核心效果放进新 `ssXX` / `cvXX`。

## SVG Specimen 规则

- `documentation/img/ligconsolata-next-overview.svg` 必须从实际构建出来的字体 outline 生成，不能用 Unicode 符号近似代替。
- overview 图的代码样例配置在 `documentation/overview-samples.txt`，真实 ASCII 代码片段按行写，`##` 标题用于分组。overview 是代表性样例，不是完整清单；完整支持范围以 `scripts/update-ligature-glyphs.py` 为准。新增已支持连字或 `calt` 规则时，先改这个配置，再运行生成脚本。
- 详细对比图使用 `documentation/ligature-catalog-samples.txt` 作为配置，输出到 `documentation/img/ligconsolata-next-ligature-catalog.svg`。它用于展示“相比默认 Inconsolata raw ASCII，Ligconsolata Next 做了哪些已验证优化”，可以比 README hero 更长、更完整，但仍不等同于全部未来计划。
- 分组功能图库由 `scripts/generate-feature-gallery.py` 生成，输出到 `documentation/ligconsolata-next-feature-gallery.md` 和 `documentation/img/features/*.svg`。它用于按功能组展示当前实现的所有默认连字、上下文行为、guard、默认 `calt` 细反斜杠和 CJK dash 字宽修正；新增或移除默认规则时要同步刷新这个图库。
- 继承连字对比图使用 `documentation/inherited-ligature-comparison-samples.txt` 作为配置，输出到 `documentation/img/ligconsolata-next-inherited-comparison.svg`。它左侧 baseline 是 `fonts/variable/Inconsolata[wdth,wght].ttf` 开启 `dlig` 后的真实 outline，右侧是当前 Ligconsolata Next 开启 `liga` / `dlig` / `calt` 后的真实 outline。用户反馈 `=>`、`->`、`<=` 等旧版已有连字看起来漂移时，先生成并查看这张图，不要立刻改 glyph。
- 生成脚本是 `scripts/generate-overview-svg.py`。默认读取 `/tmp/ligconsolata-next-smoke/LigconsolataNext[wdth,wght].ttf`，需要从 Glyphs 源码重新构建时加 `--build`。
- overview 采用 Fira Code 式左右对比：同一组里左侧通过 `hb-shape` 展示 `calt` / `liga` / `dlig` shaping 后的真实 glyph，右侧展示同一 ASCII 源文本的 raw glyph 序列；同一行可以放多个相关样例。英文为主视觉，中文只作为弱化辅助信息；顶部字体名不加中文。
- overview 的同组样例应尽量落在固定网格槽位上，让 shaped result 和 raw ASCII 都有清晰的左边界，避免右侧 raw 文本上下看起来散乱。表格内部每个样例槽位要留足呼吸感，左右两列之间也要保留明显空隙，避免 shaped result 和 raw ASCII 黏在一起。左侧分组标题作为表格第一列处理，水平左对齐，并在该组内容块内垂直居中；分组横线应从左侧标题列贯穿到右侧，左右边距保持一致，形成清晰的横线表格感。用户指出某个连字不好看时，优先按配置文件里的样例文本定位。
- overview 里的胶囊标签如果需要双语，采用 `English / 中文` 格式，斜线两边各保留一个空格，中文放在右侧。
- 不要用 `⇒`、`≤`、`≥`、`≠`、`→`、`←` 这类符号当作 `=>`、`<=`、`>=`、`!==`、`->`、`<-` 的替身；它们不是同一套 glyph，也会误导宽度判断。
- SVG 只是生成时刻的 specimen，不是实时预览。只要修改了 glyph 或 OpenType feature，就要重新 smoke build，再重新生成 SVG。
- SVG 视觉上要保留足够左右留白；组标题与本组内容要比与上一组更近，遵守亲密性原则。不要让组间距和组内距看起来一样。
- 如果某个新增连字在 overview 里看不出变化，不能只因为 GSUB 替换成功就算完成；要么改成可辨认的派生形态，要么先从公开展示中移除并标为待设计。
- `documentation/demo/index.html` 是真实浏览器对比 demo。先运行 `python scripts/build-demo-assets.py`，生成 `documentation/demo/fonts/` 下的本地字体，再打开 HTML。脚本会读取上一份 `LigconsolataNext[wdth,wght].ttf` 的内部版本，并在新产物上自动 +1，方便 macOS / Font Book 把本地安装识别成新版本；不要为了这个安装递增去改 `sources/Inconsolata.glyphs` 的基础版本。这个 demo 的输入框应保持 raw ASCII，不要在输入框里开启 ligature；左右对比区域再通过 CSS feature 开关展示真实字体行为。
- QA 图使用 `documentation/qa/confusable-samples.txt` 和 `documentation/qa/matrix-samples.txt` 作为配置，生成脚本是 `scripts/generate-qa-svg.py`，输出到 `documentation/img/ligconsolata-next-confusables-qa.svg` 和 `documentation/img/ligconsolata-next-size-weight-matrix.svg`。它们用于 review 易混字符、操作符歧义、上下文误伤、字号、字重和深浅背景；不是 README hero，也不替代 overview / catalog。

## 验证清单

开发时优先用不会改写仓库字体文件的 smoke build：

```sh
fontmake -g sources/Inconsolata.glyphs -o variable \
  --master-dir "{tmp}" \
  --output-path "/tmp/ligconsolata-next-smoke/LigconsolataNext[wdth,wght].ttf"
```

构建后检查 name table 和 GSUB：

```sh
python - <<'PY'
from fontTools.ttLib import TTFont

font = TTFont("/tmp/ligconsolata-next-smoke/LigconsolataNext[wdth,wght].ttf")
names = sorted({n.toUnicode() for n in font["name"].names if n.nameID in {1, 4, 6}})
features = sorted({r.FeatureTag for r in font["GSUB"].table.FeatureList.FeatureRecord})
print(names)
print(features)
PY
```

检查关键连字宽度：

```sh
python - <<'PY'
from fontTools.ttLib import TTFont

font = TTFont("/tmp/ligconsolata-next-smoke/LigconsolataNext[wdth,wght].ttf")
hmtx = font["hmtx"].metrics
cmap = font.getBestCmap()
checks = {
    "=====": ([cmap[ord("=")]] * 5, ["equal_equal_equal_equal_equal.dlig"]),
    "-----": ([cmap[ord("-")]] * 5, ["hyphen_hyphen_hyphen_hyphen_hyphen.dlig"]),
    "!=": ([cmap[ord("!")], cmap[ord("=")]], ["exclam_equal.dlig"]),
    "!==": ([cmap[ord("!")], cmap[ord("=")], cmap[ord("=")]], ["exclam_equal_equal.dlig"]),
    "==": ([cmap[ord("=")], cmap[ord("=")]], ["equal_equal.dlig"]),
    "<=>": ([cmap[ord("<")], cmap[ord("=")], cmap[ord(">")]], ["less_equal_greater.dlig"]),
    "=>": ([cmap[ord("=")], cmap[ord(">")]], ["equal_greater.dlig"]),
    "<=": ([cmap[ord("<")], cmap[ord("=")]], ["less_equal.dlig"]),
}
for label, (raw, ligature) in checks.items():
    raw_width = sum(hmtx[g][0] for g in raw)
    ligature_width = sum(hmtx[g][0] for g in ligature)
    print(label, raw_width, ligature_width, raw_width == ligature_width)
PY
```

SVG 更新后至少做这些检查：

```sh
python scripts/generate-overview-svg.py --build

python - <<'PY'
import xml.etree.ElementTree as ET
ET.parse("documentation/img/ligconsolata-next-overview.svg")
print("svg xml ok")
PY

rg -n "≠|⇒|≤|≥|→|←|≡" documentation/img/ligconsolata-next-overview.svg
```

需要视觉确认时，用 Chrome headless 渲染 SVG，再查看截图：

```sh
mkdir -p /tmp/ligconsolata-next-svg-preview
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new \
  --disable-gpu \
  --screenshot=/tmp/ligconsolata-next-svg-preview/chrome.png \
  --window-size=960,540 \
  "file:///Users/sheng/Desktop/code/Inconsolata/documentation/img/ligconsolata-next-overview.svg"
```

QA 图更新后至少做这些检查：

```sh
python scripts/generate-qa-svg.py \
  --font "/tmp/ligconsolata-next-smoke/LigconsolataNext[wdth,wght].ttf"

python - <<'PY'
import xml.etree.ElementTree as ET
for path in [
    "documentation/img/ligconsolata-next-confusables-qa.svg",
    "documentation/img/ligconsolata-next-size-weight-matrix.svg",
]:
    ET.parse(path)
    print(path, "xml ok")
PY
```

## 文档规则

- 英文入口是 `README.md`，中文说明是 `README.zh-CN.md`。两个 README 要互相链接。
- README 里只写已经验证过的默认启用连字。候选连字可以写在计划里，但不要把未完成 glyph 写成已支持。
- overview SVG 更新后，要确认 README 中引用路径仍然有效。
- 授权说明继续指向 `OFL.txt`，并明确这是派生字体项目，不是上游官方发布。
- blog 写作顺序要先科普基础，再进入项目复盘。`documentation/blog/00-from-movable-type-to-font-source.md` 是系列导读；`font-basics-01-movable-type.md` 到 `font-basics-09-ligconsolata-next.md` 分别展开字形复用和书法传统、中国近代印刷、西文字体迁移、常见字体案例、点阵到轮廓、可变字体、OpenType shaping 和连字、字体源码、本项目改造；`01-vibe-coding-a-programming-font.md` 再讲 AI 在字体工程里的角色；`02-reviewing-ai-font-changes.md` 再讲开发者如何 review AI 生成的字体改动。
- 写字体科普时优先用“从媒介到系统”的叙述：书写传统 -> 字模复用 -> 印刷工业里的笔画规范 -> 点阵 -> 轮廓 -> 可变字体 -> OpenType shaping -> 本仓库源码。不要一上来就写项目总结，也不要把 TTF/OTF 写成源码。
- 标题尽量自然，避免大量使用“A：B”式标题。需要解释概念时，可以在正文里展开，不要让目录看起来像 AI 提纲。
- 历史和字体技术事实要有来源。中国古代部分要讲清书法传统和字体工程的区别，可以提到篆、隶、楷、行、草，以及颜体、柳体、欧体、赵体、瘦金体等风格，但不要把书法作品直接等同为现代字体文件。中国近代印刷要补 1840 以后报纸、画报、连环画、宣传册、电报和出版工业的媒介变化；现代中文排版要提到王选院士和汉字激光照排系统；国外发展要补 Gutenberg、金属活字、机械排版、照排和数字字体；上海印刷技术研究所可以写成“现代汉字印刷字体的重要发源地”，并提到宋一体、黑一体、宋二体、新魏、牟体、宋七等代表线索；如果没有可靠来源，不要把“第一个字体设计单位”“首次使用”写成绝对断言。
- 常见字体案例要区分“字体类别”和“具体字体文件”。宋体、楷体、仿宋既是风格类别，也可能指系统字体；Arial、Helvetica、Times New Roman、Comic Sans MS、微软雅黑、等线、苹方、思源黑体、思源宋体等案例要写来源、典型使用场景、系统搭载或分发方式、授权边界和启发，不要只写审美评价。
- 第五篇 `font-basics-05-bitmap-to-outline.md` 只讲点阵、轮廓、贝塞尔、hinting、TTF/OTF 作为字体文件这一层；连字、GSUB、`liga` / `dlig` / `calt` 和源码不变的替换逻辑放到 `font-basics-07-opentype-shaping-and-ligatures.md` 单独讲。
- 解释 `.glyphs`、`.nam`、`config.yaml` 时要贴合本仓库：`.glyphs` 是主要字体源码，`.nam` 是字符集 / glyph 清单，`config.yaml` 是构建配置。不要把 `.nam` 说成通用字体源格式。
- 字体科普插图优先用本项目自绘 SVG / Mermaid / 表格示意；也可以插入来自 Wikimedia Commons、官方博物馆、官方资料页等可追溯来源的互联网图片。外部图片要在正文附近标明图源和文件页，不要直接搬运授权不清的字体截图、字体 outline、宣传图或商业 specimen。当前基础系列自绘图片放在 `documentation/img/font-basics/`。
- 科普文章里的长表格优先做成 SVG 图片，再在正文里用自然段解释“这张图怎么读”。表格 SVG 的分割线用 `line` 和 `shape-rendering="crispEdges"`，避免用斜率为 0 或垂直的 `path` 造成抗锯齿观感不直。

## Cursor Worker 协作

- 如果用户因为额度希望把任务交给 Cursor worker，Codex 继续作为主控，负责拆任务、写清 workspace、关键文件、约束、停手条件和预期输出。
- 适合交给 worker 的任务包括只读复核、候选连字清单、构建错误初筛、文档初稿，以及用户明确要求时的受控执行，例如局部代码、脚本或文档修改。
- Codex 必须回收 worker 的 diff，回读关键文件，并按任务风险运行构建、GSUB、宽度、SVG 或文档验证；涉及最终源码修改、构建产物写入和对用户交付的结论，仍由 Codex 复核后再确认。
- 对 `sources/Inconsolata.glyphs` 这种巨大源码，不要让 Cursor 长时间直接跑全量生成。更稳的拆法是：Cursor 写脚本 patch 或小范围文档/HTML 改动，Codex 回收后运行 `scripts/update-ligature-glyphs.py`、`fontmake` 和 `hb-shape`。
- worker 不应提交、不应 push、不应擅自覆盖字体二进制、不应清理用户本地文件、不应做无边界重构，也不应把 Fira Code outline 引入本项目。
