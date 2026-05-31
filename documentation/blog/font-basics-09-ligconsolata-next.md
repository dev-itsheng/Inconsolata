# Ligconsolata Next 的连字改造

前面几篇讲了字体怎样从字模、印刷、点阵、轮廓、可变字体、OpenType 替换规则走到源码。现在可以回到这个仓库本身。

Ligconsolata Next 不是从零设计一款字体。它是 Inconsolata 的派生项目，目标很克制：保留 Inconsolata 的字母、括号、节奏和阅读气质，把现代编辑器里常见的编程连字补起来。

## 为什么不是直接换 Fira Code

Fira Code 的连字做得很好。它覆盖了大量编程操作符，也处理了长箭头、上下文 marker、center alignment 等细节。很多程序员对“编程连字应该是什么样”这件事，都是从 Fira Code 建立直觉的。

但字体不是只有操作符。Inconsolata 的价值在于它自己的字母气质：窄、安静、带一点人文感，括号和标点也有自己的节奏。直接换成 Fira Code，会同时换掉字母、数字、括号和整行 texture。

Ligconsolata Next 的方向是：参考 Fira Code 的行为和覆盖面，不复制 Fira Code 的 outline。新增 glyph 应该从 Inconsolata 自己的 `equal`、`hyphen`、`less`、`greater`、`bar`、`slash` 等形态里派生。

这个取舍来自真实需求。用户喜欢 Inconsolata，不是只喜欢它有没有 `=>` 连字，而是喜欢整行代码的密度、字母比例、括号形态和安静的阅读 texture。直接换字体能立刻得到更多连字，但也会换掉长期习惯的阅读感觉。Ligconsolata Next 要解决的是“在这款字体里补现代连字”，不是“把这款字体变成另一款字体”。

## 为什么要改 `dlig` 和 `liga`

Inconsolata 源码原本就有一小组编程连字，但主要放在 `dlig`。很多编辑器打开“font ligatures”时启用的是标准 `liga`，不一定启用 discretionary ligatures。

Ligconsolata Next 的第一步，是把上游已有连字继续保留在 `dlig`，同时同步暴露到 `liga`。这样用户不需要理解 OpenType feature 细节，只要在编辑器里打开普通字体连字，就能看到 `!=`、`=>`、`<=` 等效果。

这也是早期 Ligconsolata 的核心思路。Ligconsolata Next 继续这条线，并跟进 Inconsolata v3 的可变字体源码。

`liga` 和 `dlig` 的选择也影响用户门槛。很多编辑器设置里只写“Font Ligatures”，用户不会逐个配置 OpenType feature。如果关键操作符只放在 `dlig`，字体源码里虽然有，普通用户却看不到。把已验证的编程连字同步到 `liga`，是为了让“打开编辑器连字”这件事足够简单。

## 为什么宽度比形状还重要

编程字体必须守住等宽。`=>` 原来占两个字符宽，连字后也必须占两个字符宽。`!==` 原来占三个字符宽，连字后也必须占三个字符宽。

宽度不对，编辑器里的光标、选择、多光标、竖向对齐和终端输出都会变得奇怪。一个连字看起来再漂亮，只要破坏列宽，就不适合默认启用。

Ligconsolata Next 的 review 会检查：

- raw glyph advance width 总和。
- ligature glyph advance width。
- `hb-shape` 实际命中的 glyph 名。
- SVG 和 HTML demo 里的真实视觉效果。

`==` 和 `!=` 的两横线问题就是这种 review 暴露出来的。它们不能因为借用了 `===` 或 `!==` 的结构，就在视觉上像三条横线。

这个问题很适合说明字体 review 的细度。脚本可以生成 glyph，`hb-shape` 可以证明替换命中，fontTools 可以证明宽度正确，但人眼仍然会发现“这不像 `==`”。代码字体的符号不是装饰图案，它们参与语义判断。一个看似小小的横线数量错误，会让读者误读比较运算符。

## 为什么 SVG 必须来自真实字体

README 顶部的 SVG 如果是手绘的，就只能说明设计意图，不能证明字体真的这么显示。

Ligconsolata Next 的 overview SVG 和 catalog SVG 应该来自实际构建出来的字体 outline。配置文件写 raw ASCII 样例，脚本构建临时字体，再用 shaping 结果生成对比。这样图里的 `=>`、`!=`、`<===|` 都是当前字体真实能显示出来的效果。

这条规则很重要。字体项目里的截图和 specimen 不是装饰，而是 QA 证据。

这也是为什么 overview 只放代表性样例，catalog 才放更完整目录。README 顶部图片要让人快速理解项目做了什么，不适合塞满所有符号；详细目录则负责让维护者和感兴趣的读者检查“到底支持了哪些”。两张图的任务不同，但都必须来自真实字体。

## 为什么还需要 HTML demo

SVG 能展示静态结果，但开发者真正使用字体是在编辑器和浏览器里。HTML demo 让同一段 raw ASCII 在“启用 feature”和“关闭 feature”之间切换，读者可以直接输入自己的样例。

这个 demo 有两个作用：

1. 证明源码字符没有变，变的是字体 shaping。
2. 让 review 不只依赖一张官方图，而是能看真实浏览器渲染。

后续如果新增大批连字，HTML demo 会比 README hero 更重要。README 只应该放代表性样例，详细目录和可编辑 demo 承担完整验证。

HTML demo 还有一个实际价值：读者可以输入自己的代码片段。README 里的样例再多，也覆盖不了所有语言和个人习惯。有人关心 Rust 的 `::<`，有人关心 Haskell 的箭头，有人关心 Markdown 分隔线，有人只想确认 `==` 和 `!=` 不会误导。可编辑 demo 能把“作者展示”变成“读者验证”。

## AI 在这个项目里的位置

AI 可以帮忙做很多事：读 Fira Code、JetBrains Mono、Cascadia Code、Iosevka 的覆盖面，整理候选连字，写生成脚本，生成初稿文档，做只读 review。

AI 不能替代最后判断。字体设计有很多“看起来能运行但不应该发布”的情况：

- GSUB 命中了，但视觉误导。
- 宽度对了，但重心不稳。
- 单个字号好看，小字号糊掉。
- 当前 Regular 正常，Bold 或 Italic 出问题。
- README 写得很漂亮，真实 demo 里没效果。

所以 Ligconsolata Next 的流程不是“让 AI 画完字体”，而是把 AI 放进可复核链路里：源码、脚本、临时构建、hb-shape、宽度检查、SVG、HTML demo 和人工 review。

这个流程也适合其他字体迁移。AI 可以很快从 Fira Code、JetBrains Mono、Cascadia Code 里整理候选行为，但每个候选行为都要回到当前字体的气质、源码结构和验证链路里。能学的是问题定义、feature 组织和 QA 方法；不能偷懒搬的是 outline、默认行为和最终审美判断。

## 后续还能继续学什么

Fira Code 是主参考，但不是唯一参考。

JetBrains Mono 值得看字重、Italic、易混字符区分和说明文档；Cascadia Code 值得看发行拆分和终端场景；Iosevka 值得看可配置字体系统；Monaspace 值得看 texture healing；Intel One Mono 值得看可访问性和低视力开发者视角。

这些参考不应该直接变成 outline 迁移。更稳的方式是先写研究记录，再判断哪些适合 Ligconsolata Next：

- 行为可以学。
- QA 方法可以学。
- 展示方式可以学。
- 字母气质和 outline 不能直接搬。

这条边界守住了，Ligconsolata Next 才会像 Inconsolata 自己继续长出来，而不是变成另一款字体的拼贴。

后续真正值得做的，不一定是把所有字体的所有功能都搬进来。更稳的路线是先补容易误读和高频使用的操作符，再补真实编辑器里能证明价值的上下文规则；同时增加字号、字重、主题、编辑器和终端里的 QA 截图。代码字体最终服务日常阅读，覆盖面、克制感和验证强度要一起增长。

## 继续阅读

- [Ligconsolata Next 连字迁移复盘](../ligature-porting-notes.md)
- [Ligconsolata Next 优化目录](../ligconsolata-next-optimizations.md)
- [AI 改字体时到底在做什么](01-vibe-coding-a-programming-font.md)
- [不会字体设计，也能看懂字体改动](02-reviewing-ai-font-changes.md)
