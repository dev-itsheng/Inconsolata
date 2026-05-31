# AI 改字体时到底在做什么

这篇接在 [《从活字到字体源码》](00-from-movable-type-to-font-source.md) 后面。基础系列已经把字模、glyph、轮廓字体、OpenType feature 和字体源码的基本关系铺好，这里只讨论 AI 进入这个流程后，具体能帮什么、不能替代什么。

Ligconsolata Next 的起点很简单：喜欢 Inconsolata 的字母和括号，但希望它像现代编程字体一样，把常见操作符连起来。

这件事看起来像“让 AI 画几个符号”。真正做起来，会发现字体不是一组孤立图片，而是一套约束很紧的系统。AI 可以帮忙搜索、归纳、写脚本、生成候选 outline，也可以参考 Fira Code 这类成熟字体的行为。但最后能不能用，仍然要回到字体设计和 OpenType 的基本规则。

## 字体源码不是最终字体文件

Inconsolata 这个仓库里真正值得改的是 `sources/Inconsolata.glyphs`，不是 `fonts/` 目录里的现成 TTF/OTF 文件。

TTF/OTF 更像编译产物。它们可以被检查、安装、截图和验证，但不适合当作主要编辑入口。Glyphs 源码里保留了 glyph 名称、master、feature、组件关系和构建所需的更多信息。Ligconsolata Next 的工作流也是先改 Glyphs 源码，再用 `fontmake` 构建临时字体，最后用 `hb-shape`、SVG specimen 和 HTML demo 验证。

这和普通代码项目很像：源码是权威入口，构建产物用来验证，不直接手改。

## 连字不是把字符替换成 Unicode 符号

编程字体里的 `=>` 不是把源码改成 `⇒`。源码仍然是两个 ASCII 字符，字体通过 OpenType GSUB 在渲染阶段把它们显示成一个 glyph。

这里有几个概念很关键：

- `liga` 是很多编辑器默认打开的标准连字特性。
- `dlig` 是 discretionary ligatures，通常需要用户显式打开。
- `calt` 是 contextual alternates，可以根据前后字符决定局部替换。
- glyph 的 advance width 必须和原始字符序列一致。两个字符的 `=>` 是两格宽，连字后仍然应该是两格宽。

Inconsolata 原本已经有一小组编程连字，但主要放在 `dlig`。Ligconsolata Next 先把这些已有替换同步暴露到 `liga`，再逐步扩展更多操作符。

## AI 能做什么

AI 在这个项目里最适合做三类事。

第一类是整理覆盖面。Fira Code、JetBrains Mono、Cascadia Code、Iosevka 这些字体已经把很多编程场景试过一遍。AI 可以帮忙读它们的 README、feature 文件和 specimen，把“哪些操作符值得支持”整理成候选清单。

第二类是写重复脚本。像 `==>`、`<==`、`|===>`、`<===|` 这类组合，如果每个都手工画，很容易不一致。脚本可以把已有 `equal`、`less`、`greater`、`bar` 等 glyph 拆出来、平移、缩放、组合，再把 feature 规则写回 Glyphs 文件。

第三类是做验证链路。现在的 overview SVG 和 catalog SVG 都不是手绘图，而是从临时构建字体读取 outline，再用 `hb-shape` 确认 `liga`、`dlig`、`calt` 的真实替换结果。HTML demo 也让输入文本保持 raw ASCII，只在对比区域开关 OpenType feature。

## AI 不能替代什么

AI 很容易把“规则成功”误判成“设计成功”。`hb-shape` 输出命中了某个 glyph，只能说明 OpenType 替换发生了，不能说明这个 glyph 好看、清楚、符合这款字体。

前面 `==` 和 `!=` 的问题就是典型例子：早期做法从三横线版本压缩出了两字符版本，宽度对了，GSUB 也对了，但视觉上仍然像三条横线。这个错误只有放进图里、用程序员的眼睛看，才会觉得不对。

所以字体项目里的 AI review 至少要看三层：

- 规则有没有命中：用 `hb-shape` 查 glyph 名。
- 宽度有没有保持：用 fontTools 查 raw glyph 和 ligature glyph 的 advance width。
- 视觉有没有误导：用 SVG、浏览器 demo、真实编辑器截图看形态。

这三层缺一层，都可能把“能运行”的东西误当成“能发布”的字体。

## 为什么不直接照搬 Fira Code

Fira Code 的连字做得很好，但它的字母、括号和整体纹理不是 Inconsolata。

Ligconsolata Next 的目标不是做一个 Fira Code 变体，而是继续 Ligconsolata 这条线：保留 Inconsolata 的感觉，把编程操作符体验补上。Fira Code 更适合作为行为参考和展示参考，告诉我们现代编辑器用户期待哪些连字、哪些上下文规则、哪些 specimen 方式。

具体到 outline，仍然要从 Inconsolata 自己的笔画里推导。这样改出来的字体才不会在字母和操作符之间突然换气质。

## 最小可行的字体改造流程

当前项目比较稳的流程是：

1. 先把候选操作符写进清单，不急着画 glyph。
2. 判断它适合固定连字，还是需要 `calt` 上下文规则。
3. 用脚本生成或更新 glyph，保持 advance width。
4. 同步写 `dlig`、`liga`，必要时写 `calt`。
5. 构建临时字体，不覆盖仓库里的发布字体。
6. 用 `hb-shape` 检查真实替换结果。
7. 生成 SVG specimen 和 HTML demo，看视觉是否误导。
8. 只把验证过的内容写进 README。

这个流程的重点不是“AI 一次性把字体设计完”，而是把 AI 放进一套可复核的工程管线里。字体设计仍然有审美和经验门槛，但开发者至少可以用这些检查项知道 AI 做了什么、改了哪里、有没有守住等宽字体的底线。
