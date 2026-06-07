# 外部编码字体参考索引

这份索引用来记录 Ligconsolata Next 借鉴外部编码字体时的边界。它不是 outline 迁移清单，也不是“把所有优秀字体功能都搬进来”的路线图；它更像一个 review 入口：看到一个好点子时，先判断它解决什么问题，再决定适不适合放进这个 fork。

## 总原则

Ligconsolata Next 的视觉根基仍然是 Inconsolata。可以借鉴的是覆盖面、OpenType 机制、QA 方法、feature packaging 和文档表达；不应该照搬的是外部字体的字母比例、括号形态、整体 texture、outline 和完整风格系统。

默认特性只放“能明显改善代码阅读、不会改变源码语义、不会破坏等宽宽度”的能力。字母风格、零的形态、括号风格、斜体表达、宽度系统、texture healing 这类更接近个人偏好的能力，先作为研究记录或未来 opt-in `ss` / `cv`。

## Fira Code

本地参考路径：`/Users/sheng/Desktop/code/FiraCode`

Fira Code 是当前主参考。它对 Ligconsolata Next 最有用的地方不是某个具体 glyph，而是几套机制：

- `features/calt/hyphen_arrows.fea` 和 `features/calt/equal_arrows.fea`：把任意长度箭头拆成 start / middle / end 片段，避免枚举每一种长度。
- `features/calt/center.fea`：在 `:<`、`:>`、`<:`、`>:` 这类上下文里做标点垂直居中。
- `features/calt/match_case.fea`：让操作符在小写或大写上下文里换成对应高度的视觉变体。
- `features/calt/cross.fea`：只在十六进制和尺寸表达里把小写 `x` 切到 multiply 语义。
- `features/calt/underscores.fea`：把长 `_` run 拆成可延展的片段。

已经吸收的方向是默认相关的固定 `liga` 覆盖、长箭头、center alignment、大小写上下文标点、numeric `x`、Markdown `#` 可数徽标、7+ 无编号 hash run 和一部分 marker / endpoint。仍然要保留差异：`www` 不默认合并，方便 URL 和域名保持 raw 文本；`//` / `///` 在 Ligconsolata Next 只在后接普通空格时启用，避免误伤 URL；`/\` / `\/` 只在两侧空格时启用，避免误伤 regex 和路径；Markdown `## title` 到 `###### title` 只有在行首 / shaping run 开头时通过右上嵌入数字保持可数，`##title`、`a ## b` 不替换，`#######` 及更长 run 只连成无编号横杠序列。

Fira Code 的 `cv` / `ss` 不能整包迁移。像 `cv01` 到 `cv10` 的 `a`、`g`、`i`、`l` 字母变体，`cv11` 到 `cv13` 的零变体，`ss01` 的 `r`，`ss03` 的 `&`，`ss04` 的 `$`，都属于字体风格偏好，不应默认进入 Ligconsolata Next。thin backslash 虽然来自 Fira Code `ss06` 的灵感，但在本项目里已经迁到默认 `calt` 路径：它只是把 `backslash` 换成更细的内部 glyph `backslash.thin`，不是灰度淡化，也不是独立 stylistic-set 开关。`ss02` / `cv19` / `cv23` 的水平 `<=` / `>=` 可以作为未来 opt-in，但默认仍保留 parallel slant 的 comparison 形态。`cv20` 把 `<=` 拉进箭头逻辑，也不适合作为默认。

## JetBrains Mono

本地参考路径：`/Users/sheng/Desktop/code/JetBrainsMono`

JetBrains Mono 对本项目最有价值的是 QA 体系。它有 100-800 的 roman / italic 权重范围，源码配置里也明确分出 Upright 和 Italic，可用来提醒我们：连字不能只在 Regular 大字号里看，要在轻字重、粗字重、小字号和斜体场景里复核。

可借鉴点：

- 易混字符样例要长期保留，例如 `0/O`、`1/l/I`、`5/S`、`2/Z`、`.` / `,`、`:` / `;`。
- `==` / `===`、`!=` / `!==` 这种操作符要单独看，因为它们不是越紧凑越好，而是必须一眼能数出语义层级。
- 斜体不是简单 slant；如果以后 Ligconsolata Next 增加 italic 源码，需要单独 review 连字和操作符在斜体里的重心。

不应照搬的点是整体 x-height、字母轮廓和 JetBrains Mono 的符号风格。Ligconsolata Next 先把这些经验落到 QA 图和样例配置里。

## Cascadia Code

本地参考路径：`/Users/sheng/Desktop/code/cascadia-code`

Cascadia Code 值得参考的是发行拆分。它把 `Code`、`Mono`、`PL`、`NF` 分清楚，也区分 variable TTF、static TTF、OTF、WOFF2，README 里明确说 `Cascadia Mono` 是无连字版本，`PL` / `NF` 是符号扩展版本。

可借鉴点：

- 将来如果 Ligconsolata Next 需要无连字版本，应该通过 family 命名明确区分，而不是让用户猜 feature 开关。
- Powerline / Nerd Font 这类符号扩展应该作为独立发行方向，不要混进核心字体。
- variable font 和 static instances 的说明要清楚，尤其要提醒旧版本系统字体缓存可能导致安装后看到旧渲染。

不应照搬的是 Cascadia 的具体 outline、图标集合和发行体量。当前阶段先把 demo font、smoke build 和文档路径讲清楚。

## Iosevka

本地参考路径：`/Users/sheng/Desktop/code/Iosevka`

Iosevka 是“可配置字体系统”的极端参考。它的 README 和 `doc/custom-build.md` 把 spacing、weight、width、slope、stylistic sets、character variants、ligation sets、language-specific ligations 都拆得很细，还说明 cherry-picking ligation groups 可能需要自定义构建。

可借鉴点：

- 复杂连字应该分组命名，不能只堆一个越来越长的默认清单。
- 默认 `calt`、`dlig`、语言特定 feature、自定义 build plan 要有清楚边界。
- 如果未来允许用户选择 `<=` 的样式、零的样式或 bracket pair 的样式，Iosevka 的 build-plan 思路比“塞进默认字体”更稳。

不应照搬的是 Iosevka 的大规模变体系统。Ligconsolata Next 当前是一个轻量 fork，不要把维护成本一下扩成一整套字体配置平台。

## Monaspace

本地参考路径：`/Users/sheng/Desktop/code/monaspace`

Monaspace 最值得研究的是 texture healing 和 ligature packaging。README 把多字体家族、variable/static/frozen/NF 版本讲得很清楚；连字被拆成 `ss01` 到 `ss09` 等组，`docs/Texture Healing.md` 则解释了 `calt` 如何在字母相邻时改善等宽字体的“空气”和密度。

可借鉴点：

- 将连字按主题分组，而不是把所有替换都叫“ligatures”。
- optional ligatures 可以放进 `cv60` 这类 opt-in 入口，例如 Monaspace 对 `[]` 也提醒可能影响编辑器自动补全体验。
- texture healing 是一个长期方向，但它改变字母之间的视觉密度，必须等连字阶段稳定后再单独研究。

不应照搬的是 Monaspace 的五字体家族、texture-healed glyph 和 frozen 字体策略。当前只借鉴 QA 和 feature 边界表达。

## Intel One Mono

本地参考路径：`/Users/sheng/Desktop/code/intel-one-mono`

Intel One Mono 对本项目最有用的是可访问性视角。它明确面向低视力开发者和减少疲劳，README 里写到字体有 Light、Regular、Medium、Bold 以及 matching italics，也给出屏幕和印刷尺寸建议。它还把 programming ligatures 放在 `ss01`，`ss02` 控制 `<=` / `>=` 是否换成 arrow forms，raised colon 通过上下文或 `ss11` / `ss12` / `salt` 启用。

可借鉴点：

- 连字不是默认越多越好；如果某类替换可能影响可读性，可以作为 opt-in。
- `<=` / `>=` 的 math contraction 与 arrow forms 应该分清楚，Ligconsolata Next 默认保留 comparison 语义。
- raised colon、低视力可读性、小字号屏显和 Windows hinting 是未来 QA 方向。

不应照搬的是 Intel One Mono 的轮廓、四权重设计空间和完整功能开关。Ligconsolata Next 当前先把可访问性变成 QA 样例和 review 规则。

## 默认和 opt-in 的边界

适合默认 `liga` / `calt` 的能力：

- 继承 Inconsolata / Ligconsolata 已有编程连字，并保持等宽 advance。
- 常见 ASCII 操作符的固定连字，例如 equality、arrow、pipe、markup、query、comment prefix。
- 能保持源码可读的上下文行为，例如长箭头、numeric `x`、大小写上下文标点、center alignment。
- 明确不误伤 URL、Markdown 标题层级、普通单词、regex 和路径的规则。

适合未来 opt-in `ss` / `cv` 的能力：

- `<=` / `>=` 的水平 bar 版本或 arrow 版本。
- 零、`i`、`l`、括号、大括号、`&`、`$`、`%`、`*` 等风格选择。
- `ssXX` / `cvXX` 这类不改变源码语义、但会改变符号质感的 opt-in 变体；即使未来实现，也不要把它写成普通编辑器连写开关一定能启用的默认能力。thin backslash 是一个例外：它已经按产品决策迁到 `calt`，因此不再作为 `ss06` opt-in 记录。
- 更激进的 `[]`、Markdown checkbox、progress bar、Powerline / Nerd Font 扩展。
- 任何字母级 texture healing、spacing、x-height、italic 形态或 hinting 改造。

后续新增外部参考点时，先把“它解决的问题”写进这里，再决定是否进入脚本、QA 或 AGENTS 队列。
