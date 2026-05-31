# 不会字体设计，也能看懂字体改动

这篇默认读者已经看过 [《从活字到字体源码》](00-from-movable-type-to-font-source.md)，知道连字不是改源码字符，而是 OpenType shaping 阶段的 glyph 替换。这里重点讲普通开发者怎么 review 一次 AI 参与的字体改动。

很多开发者喜欢编程字体，但不熟悉字体设计。AI 让“试着改一款字体”变得容易了，也让 review 变得更重要：生成结果看起来像那么回事，不代表它真的适合放进编辑器。

这份清单写给不想一开始就学完字体设计、但希望能判断 AI 改动是否靠谱的开发者。

## 先看源码有没有被保留

编程连字的第一条底线是：源码不能变。

`a !== b` 在文件里仍然应该是三个 ASCII 字符。字体只能在渲染阶段把它显示成一个更容易扫读的形状。不要用 `≠`、`⇒`、`≤`、`≥` 这类 Unicode 符号冒充连字效果，它们不是同一套 glyph，也会误导宽度和光标判断。

Ligconsolata Next 的 SVG 都从 raw ASCII 样例生成。左边是 OpenType shaping 后的真实 glyph，右边是同一段 ASCII 的原始显示。这个对比能直接暴露“是不是偷换成 Unicode 符号”。

## 再看宽度有没有守住

等宽字体最怕连字破坏列宽。

两个字符宽的 `=>`，连字后仍然应该占两个字符宽。三个字符宽的 `!==`，连字后仍然应该占三个字符宽。否则编辑器里的对齐、光标移动、选择区域和多光标操作都会变得奇怪。

review 时不要只看图。需要用 fontTools 直接检查 raw glyph 宽度和 ligature glyph 宽度：

```sh
python - <<'PY'
from fontTools.ttLib import TTFont

font = TTFont("/tmp/ligconsolata-next-smoke/LigconsolataNext[wdth,wght].ttf")
hmtx = font["hmtx"].metrics
cmap = font.getBestCmap()

raw = [cmap[ord("=")], cmap[ord("=")]]
ligature = ["equal_equal.dlig"]

print(sum(hmtx[g][0] for g in raw))
print(sum(hmtx[g][0] for g in ligature))
PY
```

宽度一致只是入门条件，不代表视觉一定正确。

## 看它有没有像这款字体

连字不是越像数学符号越好。它必须像当前字体长出来的东西。

Ligconsolata Next 保留 Inconsolata 的字母、括号、节奏和 texture，所以新增操作符也应该优先复用 Inconsolata 自己的 `equal`、`hyphen`、`less`、`greater`、`slash`、`bar` 等笔画。Fira Code 可以告诉我们“哪些组合值得做”，但不能直接决定“这个 glyph 应该长什么样”。

review 时可以问三个问题：

- 这个 glyph 的笔画粗细和原字符一致吗。
- 斜线、箭头、横线的高度和原字符系统一致吗。
- 它放在一行真实代码里，会不会突然比旁边字母更亮、更黑或更挤。

如果答案含糊，先放进 demo 里看，不要急着写进 README。

## 看相似符号有没有区分

编程字体里很多错误来自“太像”。

`==` 和 `===` 必须能区分。`!=` 和 `!==` 也必须能区分。`--` 不应该被做成一条完整横线，因为它容易和 dash 或分割线混在一起。长分割线可以由 `----`、`-----` 负责。

这类问题很适合做成固定 QA 样例：

```text
a != b
a !== b
a == b
a === b
i --
// ----
```

只要其中一个看起来会误导读者，就说明生成逻辑需要改。

## 看 OpenType feature 边界

不是所有优化都应该默认启用。

`liga` 适合放大多数编辑器默认应看到的连字。`dlig` 适合保留兼容或可选连字。`calt` 适合处理上下文，比如任意长度箭头、长下划线、冒号居中。`ss01`、`cv01` 这类 stylistic set / character variant 更适合放风格选择。

Intel One Mono 把编程连字放在 `ss01`，JetBrains Mono 和 Iosevka 提供大量 `ss` / `cv` 选择，Cascadia Code 把 Code、Mono、PL、NF 版本拆开。这些做法都提醒我们：默认值要克制，风格项要有边界。

Ligconsolata Next 现在默认启用的是“更像现代编辑器预期”的编程连字。未来如果要做字母变体、不同斜体风格或更激进的操作符风格，应该优先放到可选特性里，不要直接改变默认气质。

## 看上下文规则有没有误伤

`calt` 很强，也很容易误伤。

长箭头需要把 `---->`、`<----` 这类序列拼成 start / middle / end 片段。但同一组字符又会和普通 `--`、`->`、`==`、`===` 共享前缀。如果 lookup 顺序不稳，就会出现普通操作符被长箭头规则提前吃掉的问题。

review 时要用 `hb-shape` 看真实输出，而不是只看代码里有没有规则：

```sh
hb-shape /tmp/ligconsolata-next-smoke/LigconsolataNext[wdth,wght].ttf \
  "a != b a !== b a == b a === b x <==== y i--" \
  --features=liga=1,dlig=1,calt=1
```

这个命令能直接告诉你最终命中了哪些 glyph。只看源码规则，很容易漏掉 lookup 顺序造成的覆盖。

## 看不同尺寸和不同字重

一张大图好看，不代表编辑器里好看。

真正的编程字体要在小字号、深色背景、浅色背景、Regular、Bold、Italic、不同渲染器里都尽量稳定。JetBrains Mono 的 100-800 字重和 Italic、Cascadia Code 的 variable TTF、Iosevka 的多 width / slope，都说明优秀编码字体不是只看一个 Regular 截图。

Ligconsolata Next 当前还没有完成完整多 master / 多字重 QA。后续要补的不是“把 catalog 做得更长”，而是让同一组关键样例在不同尺寸和字重下都能通过。

## 一份实用 review 清单

每次 AI 生成新连字后，可以按这个顺序看：

1. 源码仍然是 ASCII，没有偷换 Unicode。
2. advance width 等于原始字符序列总宽度。
3. `hb-shape` 命中预期 glyph，没有被别的 lookup 抢走。
4. 视觉上能区分相近操作符，比如 `==` / `===`、`!=` / `!==`。
5. 新 glyph 的笔画、重心、空白和 Inconsolata 气质一致。
6. 普通代码上下文没有被误伤，比如 `i--`、`//`、URL、路径。
7. SVG specimen 和 HTML demo 都能说明问题。
8. README 只写已经验证过的能力，候选项留在计划里。

AI 可以把改字体这件事变快，但不能替开发者做最后的判断。review 的价值就在这里：用少量字体设计原则，加上真实构建和真实渲染，把“看起来可以”的结果筛成“真的能用”的字体。
