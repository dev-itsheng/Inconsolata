# 连字让源码换一种读法

前面讲的是字形怎样被画出来。现在才轮到连字和替换规则。

连字最容易被误解成“把文本替换成另一个字符”。实际不是这样。文件里的字符没有变，变的是字体在显示阶段选择了哪个 glyph。这个差别非常关键：它决定了搜索、复制、编译、光标移动和版本 diff 都仍然面对原始文本，而读者看到的是更适合阅读的字形。

## 连字原本是为阅读和排版服务的

传统排版里的 ligature 并不是程序员发明的。拉丁字体里常见 `fi`、`fl` 连字，是为了处理字母碰撞和阅读节奏。阿拉伯文、印度文字等复杂书写系统里，字形还会根据位置、上下文和组合关系发生变化。字体不是只把字符一对一画出来，它还要参与排版。

现代 OpenType 把这类行为放进字体表和 shaping engine。应用把字符交给排版引擎，排版引擎根据字体规则选择 glyph、替换 glyph 或调整 glyph 位置。Microsoft 的 [GSUB 规范](https://learn.microsoft.com/en-us/typography/opentype/spec/gsub)说明，GSUB 表用于 glyph substitution，也就是 glyph 替换。

实际显示大致可以分成几步。文本先以 Unicode 字符存在，字体通过 `cmap` 找到初始 glyph，shaping engine 再根据脚本、语言、feature 和上下文应用替换或定位规则，最后渲染器把 glyph 轮廓栅格化到屏幕上。连字发生在 glyph 层，不发生在源码文本层。

以 `!==` 为例，源码里有三个字符：

```text
! = =
```

字体先把它们映射成 `exclam`、`equal`、`equal` 这类初始 glyph。启用对应 OpenType feature 后，GSUB 规则可以把这三个 glyph 替换成 `exclam_equal_equal.dlig` 这样的连字 glyph。编辑器显示的是一个更紧凑的不等号形态，但源码、复制结果、搜索结果和编译器输入仍然是三个字符。

## 编程连字解决的是扫读噪音

程序员写代码时，很多操作符本来就是多字符组合：

```text
if (a !== b) return x => x + 1
```

源码里必须保留 `!`、`=`、`>` 这些 ASCII 字符，因为语言语法、编辑器、编译器、搜索和版本控制都依赖它们。但阅读时，人眼更关心这些组合表达的关系：不等于、箭头、比较、逻辑与、管道、范围、注释边界。

编程连字解决的就是这个问题。它不改变源码，只是在显示阶段把常见组合显示得更像一个操作符，减少眼睛在符号碎片之间来回拼读的成本。

所以不能用 `≠` 冒充 `!=`，也不能用 `⇒` 冒充 `=>`。那是不同 Unicode 字符，不是同一段 ASCII 源码的字体表现。

这个边界对代码尤其重要。搜索 `!=` 应该能找到源码里的两个字符，复制出来也应该还是 `!=`，编译器读到的也必须是 `!` 和 `=`。如果 specimen 图为了好看直接写成 `≠`，读者会误以为字体改变了源文本，甚至误判宽度和光标行为。Ligconsolata Next 的 SVG 和 HTML demo 因此都要从 raw ASCII 生成。

## `liga`、`dlig` 和 `calt` 分工不同

编程字体常见的 feature 包括：

- `liga`：标准连字，很多编辑器开启“font ligatures”后会默认启用。
- `dlig`：discretionary ligatures，可选连字，通常需要用户显式开启。
- `calt`：contextual alternates，上下文替换，可以根据前后字符决定局部形态。

Inconsolata 原本已经有一小组编程连字，但主要放在 `dlig`，很多编辑器默认不会启用。Ligconsolata Next 做的第一步，是把这些已有连字同步暴露到 `liga`，让普通“开启字体连字”的编辑器也能看到。

新增连字时，可以这样分工：

- 固定短操作符适合 `liga` / `dlig`，例如 `!=`、`=>`、`<=`、`&&`。
- 任意长度箭头更适合 `calt`，例如 `---->`、`<====`。
- 标点居中、端点变化、上下文 marker 更适合 `calt`，因为它们依赖相邻字符。
- 风格选择更适合 `ss` / `cv`，不应该轻易改默认行为。

这几个 feature 的区别会影响默认体验。`liga` 放太多激进符号，用户一打开字体连字就会看到大量变化；`dlig` 放太多关键操作符，普通编辑器又可能默认看不到；`calt` 很适合处理长箭头和局部对齐，但规则写不好会误伤普通 `->`、`--`、`==` 或注释。字体工程里，feature 分工就是产品设计的一部分。

不同应用启用 feature 的方式也不完全一样。浏览器可以通过 CSS 控制 `font-variant-ligatures` 或 `font-feature-settings`，编辑器通常提供一个总开关，终端模拟器又可能有自己的默认策略。所以字体项目不能只看源码规则，要用 `hb-shape`、浏览器 demo 和真实编辑器一起确认。

## 等宽字体的底线是宽度不能变

代码字体通常是等宽字体。每个字符占固定宽度，缩进、对齐、多光标和终端输出才能稳定。

连字发生后，宽度也必须保持：

- `=>` 是两个字符宽，连字后仍然占两个字符宽。
- `!==` 是三个字符宽，连字后仍然占三个字符宽。
- `====` 是四个字符宽，连字后仍然占四个字符宽。

这个宽度叫 advance width。视觉上可以把两个字符连成一个箭头，但排版系统仍然要把它当作原来那段字符占用的宽度。

Ligconsolata Next 里曾经修过一个典型问题：`==` 和 `!=` 不能看起来像三条横线。即使 GSUB 命中了，宽度也对了，如果视觉形态误导读者，就不能算设计完成。

宽度检查还要分两层。第一层是数据层：用 fontTools 读 `hmtx`，确认 raw glyph 的宽度总和等于 ligature glyph 的 advance width。第二层是视觉层：放进真实字号和真实主题里，看它有没有贴边、重心偏移、误读或与相邻字符粘连。等宽字体的底线是数据，真正能不能发布还要看视觉。

## 好的编程连字应该克制

Fira Code 做得好的地方，是把很多程序员常见操作符归纳成一套行为体系。它的启发不只是“符号变漂亮”，而是几条设计边界：

- raw ASCII 不变。
- 操作符宽度保留。
- 常见组合更容易扫读。
- 长箭头能自然延展。
- 相似操作符仍然可区分。
- 默认连字不应该改变代码语义判断。

Ligconsolata Next 可以学习覆盖面和机制，但不能复制 Fira Code 的 outline。最终 glyph 仍然要从 Inconsolata 自己的笔画、比例和节奏里长出来。

Fira Code 的长箭头尤其值得学习。固定枚举 `->`、`-->`、`--->` 当然能覆盖几个长度，但程序员会写任意长的分隔箭头和注释箭头。更稳的机制是把起点、中间段、终点拆成上下文片段，让 `---->`、`<====` 这类长度自然延展。Ligconsolata Next 学的是这种机制，再用 Inconsolata 自己的横线、等号和箭头端点画出来。

好连字还要保留差异。`==` 不能像 `===`，`!=` 不能像 `!==`，`--` 不能和长横线完全糊成一条，`//` 注释不能被上下文规则误处理成别的东西。连字的目标不是把所有符号都变成漂亮图标，而是在不改变源码和不混淆语义的前提下减少阅读噪音。

## 继续阅读

- Microsoft Learn: [GSUB — Glyph Substitution Table](https://learn.microsoft.com/en-us/typography/opentype/spec/gsub)
- Microsoft Learn: [Registered features, a-e](https://learn.microsoft.com/en-us/typography/opentype/spec/features_ae)
- Microsoft Learn: [Registered features, k-o](https://learn.microsoft.com/en-us/typography/opentype/spec/features_ko)
- Fira Code: [tonsky/FiraCode](https://github.com/tonsky/FiraCode)
