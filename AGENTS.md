# AGENTS.md

## 项目定位

- 这个仓库是 `googlefonts/inconsolata` 的派生字体项目，当前派生名是 `Ligconsolata Next`。
- 修改版字体不要继续使用上游 `Inconsolata` family name。文档、源码配置、metadata 和构建产物里的公开名称都应保持 `Ligconsolata Next`。
- 这是字体源码项目，不是前端项目。除非任务明确涉及网页、浏览器 UI 或前端工程，不要套用全局前端规则。
- 默认用中文记录项目内协作说明；面向上游、Google Fonts 或英文用户的正式 README / metadata 可以继续用英文。

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
  - 上游已有并继续优化：`!=`、`!==`、`==`、`===`、`->`、`=>`、`>=`、`<-`、`<=`。
  - 新增常用操作符：`<=>`、`<->`、`-->`、`<--`、`==>`、`<==`、`...`、`<>`、`::`、`:=`、`&&`、`||`、`++`、`--`、`**`、`//`、`/*`、`*/`、`??`、`?.`。
  - 参考 Fira Code 补充的一批固定操作符覆盖面由 `scripts/update-ligature-glyphs.py` 里的 `FIRA_CODE_COMPAT_SOURCES` 维护，例如 `<|>`、`<$>`、`<+>`、`</>`、`|>`、`<|`、`::=`、`..=`、`..<`、`?=`、`!!`、`!!.`、`+++`、`***`、`///`、`#{`、`#[`、`#_(` 等。
  - 第一批参考 Fira Code `calt` 行为但按固定连字落地的低风险组合由 `FIRA_CODE_CALT_FIXED_LIGATURES` 维护，例如 `##` 到 `########`、`__` 到 `______`、`=/=`、`=!=`、`=:=`、`=~`、`!~`、`/=`、`/==`、`.=`、`.-`、`:-`、`[]`、`->>`、`<<-`、`=>>`、`=<<`、`>--`、`--<`、`|--`、`--|`、`>==`、`==<`、`|==`、`==|`、`==/`、`>>-`、`>-`、`-<`、`|->`、`<-|`、`|=>`、`<=|`、`||-`、`-||`、`|-`、`-|`。
  - `calt` 可变长度箭头：`---->`、`<----`、`====>`、`<====`、`<--->`、`<===>` 这类长度不固定的 `-` / `=` 箭头。
  - `calt` 端点和 marker 小批次：单 `|` 端点长箭头，以及长 `=` 串里的单 `/` 端点、单 `/` middle、`:` / `!` middle，例如 `|--->`、`<===|`、`/===>`、`<===/`、`===/===`、`==:=`、`==!=`。
  - `calt` center alignment 小批次：`:<`、`:>`、`<:`、`>:`、`<:>`、`>:<` 这类 `:` / `<` / `>` 相邻场景会切换到 `.center` 视觉变体。这是标点对齐，不是新增 `.dlig` 连字。
  - 注释分割线辅助：`====`、`=====`、`----`、`-----`。
- 上游已有的一组连字原本存在于 Inconsolata 的 `dlig` 中；Ligconsolata Next 继续保留 `dlig`，并把当前支持的 substitution 同步暴露到 `liga`。
- glyph 名称可以继续沿用已有 `.dlig` 后缀。feature tag 和 glyph 命名不必强行一致，重点是 GSUB 里同时有 `dlig` 和 `liga` 规则。
- 连字的 advance width 必须等于原始字符序列的总 advance width。Regular 默认位置里，两字符连字应为 1000，三字符连字应为 1500，四字符分割线应为 2000，五字符分割线应为 2500。新增连字时也要按所有相关 master 或最终构建产物检查宽度。
- 新连字应从 Inconsolata 自己的笔画、比例和字面节奏里推出来。Fira Code 可以作为「程序员期待哪些连字」和「如何展示连字」的参考，但不能复制 Fira Code 的 outline。
- 新增连字优先走脚本化小步：把可重复的派生逻辑写进 `scripts/update-ligature-glyphs.py`，再生成 Glyphs 源码、验证构建、GSUB、宽度和视觉。
- `scripts/update-ligature-glyphs.py` 负责生成脚本派生 glyph，并同步改写 `calt` / `dlig` / `liga`。`liga` 规则必须保持长序列在短序列前面，例如 `=====` 在 `====` / `===` / `==` 前，`-->` 在 `--` / `->` 前。
- `==` 和 `!=` 必须保持两条横线。不要把它们从 `===` / `!==` 直接横向缩放出来，否则 overview 和真实编辑器里会看起来像三横线，和 Fira Code 及程序员预期不一致。
- 可变长度箭头参考 Fira Code 的处理思路，但只复用机制：用 `hyphen_start.seq` / `hyphen_middle.seq` / `greater_hyphen_end.seq`、`equal_start.seq` / `equal_middle.seq` / `greater_equal_end.seq` 等片段拼接，不复制 Fira Code outline。
- `calt` 长箭头当前采用 start lookup 加多轮 extend lookup。不要把所有逻辑塞进一个 lookup；否则 `<====` / `<----` 这类左向长箭头容易被后续固定 `===` / `--` 抢走。
- `calt` 规则要优先保证长箭头能随字符数自然延展；如果某条规则会破坏普通 `->` / `<-` / `=>` / `<=` / `==` / `===` / `!==` / `i--` 等既有 `liga` / `dlig`，宁可缩小 `calt` 覆盖范围，并用 `ignore sub` 明确避开这些固定连字。
- 新增与长箭头共享前缀的固定组合时，必须同步复核 `calt` 是否抢先替换。例如 `->>`、`=>>`、`<-|`、`<=|` 需要在 start lookup 中避让，`i--` 必须继续命中 `hyphen_hyphen.dlig`。
- 自动生成 glyph 名称时避免过长的生产名。像 `######`、`____` 这种重复字符运行应使用 `numbersign_run6.dlig`、`underscore_run4.dlig` 这类短名；过长名称可能让 `public.postscriptNames` 写出 `None`，导致 Glyphs plist 保存失败。
- `====` / `=====` 使用两条连续横线，`----` / `-----` 使用一条连续横线，用来改善注释分割线的视觉连续性。但字体不能修正源码里上下分割线字符数不一致的问题；生成注释分割线时仍应使用固定长度文本，避免手写差一个字符。
- `--` 不要做成一条连续横线；它应该保留两个减号的分隔感，避免和长 dash 或注释分割线混淆。
- `scripts/update-ligature-glyphs.py` 目前会全量重写大量 glyph block，新增覆盖面后耗时可能达到数分钟。后续优化优先把「只更新 feature」和「重建 glyph」拆开。

## Fira Code 迁移队列

后续按这个队列一项一项推进。每完成一项，先验证，再把勾选状态和要点写回这里，避免上下文压缩或 Cursor worker 分工后丢失细节。

- [x] 派生字体命名、README / README.zh-CN、OFL 边界和 Fira Code 致谢说明。
- [x] 将 Inconsolata 原有 `dlig` 编程连字同步暴露到 `liga`。
- [x] 覆盖 Fira Code 静态 `liga` 清单里的固定操作符，并保持 Inconsolata-family outline 来源。
- [x] 建立真实 specimen 链路：`overview-samples.txt` -> 临时构建字体 -> `hb-shape` -> SVG outline。
- [x] 建立浏览器真实对比 demo：`documentation/demo/index.html` + 本地生成字体。
- [x] 迁移第一批 Fira Code `calt`-inspired 固定组合，包括 hash / underscore runs、`=/=` / `/=` 族、`->>` / `=>>` 族和 pipe endpoint 族。
- [x] 迁移第二批低风险固定端点组合，包括 `>--` / `--<`、`|--` / `--|`、`>==` / `==<`、`|==` / `==|`、`==/`，并补充 `#` / `_` run 到 8 / 6 字符。
- [x] 将 underscore runs 从有限固定清单推进到上下文型 `calt` 规则。已验证：`__` 到 `______` 继续命中固定 glyph，`_______` 及更长连续下划线使用 `underscore_start.seq` / `underscore_middle.seq` / `underscore_end.seq` 延展。
- [x] 评估 hash runs 是否适合上下文型 `calt`。结论：暂缓上下文化，当前保留 `##` 到 `########` 固定覆盖，因为 `#` 不是单纯横线；后续若要做，先单独设计 `numbersign_start.seq` / `numbersign_middle.seq` / `numbersign_end.seq`，不要用自动拉伸的矩形近似。
- [x] 设计并迁移第一批任意长度 pipe/bar 端点箭头：`|---`、`---|`、`|--->`、`<---|`、`|===`、`===|`、`|===>`、`<===|` 这类单 `|` 端点，短组合 `|--` / `--|` / `|==` / `==|` 继续由固定 glyph 负责。
- [x] 设计并迁移第一批 slash / colon / exclamation 上下文组合：单 `/` 端点长 `=` 箭头 `/===`、`===/`、`/===>`、`<===/`，以及 `==:=`、`==!=` 这类长 `=` 串 marker；短组合 `/=`、`/==`、`==/`、`=:=`、`=!=` 继续由固定 glyph 负责。
- [x] 继续评估 Fira Code 更完整的 slash / colon / exclamation 机制。结论：先补单 `/` middle（如 `===/===`）；双 slash 端点和双字符端点依赖 Fira Code 的 `.spacer` 机制，容易和 `//` / `///` 注释、URL、路径冲突，暂缓迁移。
- [x] 梳理并迁移 Fira Code center alignment 行为：默认启用 `:<`、`:>`、`<:`、`>:`、`<:>`、`>:<` 这类 `:` / `<` / `>` 视觉居中；`<::>` / `<:::>` 等多冒号组合会被现有 `::` / `:::` 固定 glyph 接管，暂不宣称完整覆盖；`ss07`、`cv25`、`cv26`、`cv32` 等风格项维持现有固定覆盖，完整边界留到 `cv` / `ss` 特性整理。
- [ ] 评估 lowercase / uppercase operator matching，例如 `hyphen.lc`、`plus.lc`、`asterisk.lc`、`colon.uc` 是否适合 Inconsolata 气质。
- [ ] 评估 hexadecimal / multiplication `x` 行为，例如 `0xFF`、`800x600`，先设计视觉再加规则。
- [ ] 整理 Fira Code `cv` / `ss` 特性边界：只吸收与编程连字体验直接相关的行为，不迁移 Fira Code 的风格化字母变体。

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

后续待办：

- [ ] 写一份外部字体研究索引，逐个记录 Fira Code、JetBrains Mono、Cascadia Code、Iosevka、Monaspace、Intel One Mono 对 Ligconsolata Next 有用的点。
- [ ] 增加易混字符 QA 样例，例如 `0/O`、`1/l/I`、`5/S`、`2/Z`、`.` / `,`、`:` / `;`、`==` / `===`、`!=` / `!==`。
- [ ] 增加字号和字重矩阵截图，确认连字在小字号、Regular、Bold、Italic 和深浅背景里都不误导。
- [ ] 评估哪些未来能力应该放进默认 `liga` / `calt`，哪些应该作为 opt-in `ss` / `cv`。

## SVG Specimen 规则

- `documentation/img/ligconsolata-next-overview.svg` 必须从实际构建出来的字体 outline 生成，不能用 Unicode 符号近似代替。
- overview 图的代码样例配置在 `documentation/overview-samples.txt`，真实 ASCII 代码片段按行写，`##` 标题用于分组。overview 是代表性样例，不是完整清单；完整支持范围以 `scripts/update-ligature-glyphs.py` 为准。新增已支持连字或 `calt` 规则时，先改这个配置，再运行生成脚本。
- 详细对比图使用 `documentation/ligature-catalog-samples.txt` 作为配置，输出到 `documentation/img/ligconsolata-next-ligature-catalog.svg`。它用于展示“相比默认 Inconsolata raw ASCII，Ligconsolata Next 做了哪些已验证优化”，可以比 README hero 更长、更完整，但仍不等同于全部未来计划。
- 生成脚本是 `scripts/generate-overview-svg.py`。默认读取 `/tmp/ligconsolata-next-smoke/LigconsolataNext[wdth,wght].ttf`，需要从 Glyphs 源码重新构建时加 `--build`。
- overview 采用 Fira Code 式左右对比：同一组里左侧通过 `hb-shape` 展示 `calt` / `liga` / `dlig` shaping 后的真实 glyph，右侧展示同一 ASCII 源文本的 raw glyph 序列；同一行可以放多个相关样例。英文为主视觉，中文只作为弱化辅助信息；顶部字体名不加中文。
- overview 的同组样例应尽量落在固定网格槽位上，让 shaped result 和 raw ASCII 都有清晰的左边界，避免右侧 raw 文本上下看起来散乱。表格内部每个样例槽位要留足呼吸感，左右两列之间也要保留明显空隙，避免 shaped result 和 raw ASCII 黏在一起。左侧分组标题作为表格第一列处理，水平左对齐，并在该组内容块内垂直居中；分组横线应从左侧标题列贯穿到右侧，左右边距保持一致，形成清晰的横线表格感。用户指出某个连字不好看时，优先按配置文件里的样例文本定位。
- overview 里的胶囊标签如果需要双语，采用 `English / 中文` 格式，斜线两边各保留一个空格，中文放在右侧。
- 不要用 `⇒`、`≤`、`≥`、`≠`、`→`、`←` 这类符号当作 `=>`、`<=`、`>=`、`!==`、`->`、`<-` 的替身；它们不是同一套 glyph，也会误导宽度判断。
- SVG 只是生成时刻的 specimen，不是实时预览。只要修改了 glyph 或 OpenType feature，就要重新 smoke build，再重新生成 SVG。
- SVG 视觉上要保留足够左右留白；组标题与本组内容要比与上一组更近，遵守亲密性原则。不要让组间距和组内距看起来一样。
- 如果某个新增连字在 overview 里看不出变化，不能只因为 GSUB 替换成功就算完成；要么改成可辨认的派生形态，要么先从公开展示中移除并标为待设计。
- `documentation/demo/index.html` 是真实浏览器对比 demo。先运行 `python scripts/build-demo-assets.py`，生成 `documentation/demo/fonts/` 下的本地字体，再打开 HTML。这个 demo 的输入框应保持 raw ASCII，不要在输入框里开启 ligature；左右对比区域再通过 CSS feature 开关展示真实字体行为。

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
- 适合交给 worker 的任务包括只读复核、候选连字清单、构建错误初筛和文档初稿。涉及最终源码修改、构建产物写入和对用户交付的结论，仍由 Codex 回收并复核。
- worker 不应擅自覆盖字体二进制、不应清理用户本地文件，也不应把 Fira Code outline 引入本项目。
