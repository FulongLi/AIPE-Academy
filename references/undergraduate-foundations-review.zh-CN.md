# 从零基础到电力电子：MIT 与 Princeton 课程调研

核实日期：2026-09-06。用途：为 AIPE Academy 补齐本科基础与入门教学方法。本文是原创摘要和课程设计建议，配套[来源索引](undergraduate-sources.json)记录课程年份、类型与访问状态。

## 结论

建议形成三层：**零基础桥接 → 本科电气工程核心 → 电力电子专业学习**，然后进入研究准备与研究实践。用户不需要先学习提示词，由导师承担定位起点、选课、安排作业和反馈的组织工作。

一个定位修正：*Fundamentals of Power Electronics* 不仅用于研究生课，出版社也将高年级本科生列为读者。它是专业课教材，确实不应作为完全零基础学生的第一本书。[Springer](https://link.springer.com/book/10.1007/978-3-030-43881-4)

## MIT：基础课与教法

以下是具有完整公开材料的历史课程版本，并非宣称这些旧课号仍是 2026 年培养方案。

| 课程及版本 | 已核实内容与资源 | AIPE Academy 用法 |
|---|---|---|
| 6.002 电路与电子学，2007 春 | 本科课；有 syllabus、授课表、作业、实验和视频入口；指定 Agarwal/Lang 教材；要求 8.02、18.03 基础 | 基础电路和电子电路的主参考 |
| 6.01SC EECS 入门，2011 春 | 软件、信号系统、电路等整合；有开放课程讲义；无正式先修但建议电磁学同修，学习者仍需部分数学与电路基础 | 参考跨学科项目与辅导流程 |
| 8.02 电磁学，2007 春 | 电磁学概念与实验、问题练习相结合 | 选择与电压、电场、磁场、储能和感应相关的基础 |
| 18.01SC 微积分，2010 秋 | 单变量微积分的公开自学课程 | 支撑斜率、面积和变化率 |
| 18.03 微分方程，2010 春 | 常微分方程及物理系统建模；要求单变量微积分，多变量微积分同修 | 为 RC/RL/RLC 动态与控制提供数学 |
| 18.06SC 线性代数，2011 秋 | 公开自学课程 | 逐步引入节点方程组、矩阵与状态空间 |
| 6.0001 Python 入门，2016 秋 | 面向少量或没有编程经验者的编程课程 | 选择计算、函数、绘图数据准备与调试能力 |
| 6.003 信号与系统，2011 秋 | 连续/离散系统、频域、变换与系统响应 | 进入反馈和数字控制前的桥梁 |

官方入口：[6.002 syllabus](https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/pages/syllabus/)、[6.01SC syllabus](https://ocw.mit.edu/courses/6-01sc-introduction-to-electrical-engineering-and-computer-science-i-spring-2011/pages/syllabus/)、[8.02](https://ocw.mit.edu/courses/8-02-physics-ii-electricity-and-magnetism-spring-2007/pages/syllabus/)、[18.01SC](https://ocw.mit.edu/courses/18-01sc-single-variable-calculus-fall-2010/pages/syllabus/)、[18.03](https://www.ocw.mit.edu/courses/18-03-differential-equations-spring-2010/pages/syllabus/)、[18.06SC](https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/pages/syllabus/)、[6.0001](https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/pages/syllabus/)、[6.003](https://ocw.mit.edu/courses/6-003-signals-and-systems-fall-2011/)。

6.002 的课程安排可概括为：电路模型和分析 → 有源器件与小信号 → 储能和暂态 → 阻抗与滤波 → 运放反馈。它把讲课、习题讨论和实验交错安排。[公开授课表](https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/pages/calendar/)

值得借鉴的两种教法：

- **先实践、再理论、再实践：** 6.01 的教师访谈明确说明，先让学生遇到一个真实问题，再讲所需理论，然后重新解决问题。AIPE 可以先让学生观察分压输出变化，再引入等效电路。[教学访谈](https://ocw.mit.edu/courses/6-01sc-introduction-to-electrical-engineering-and-computer-science-i-spring-2011/pages/instructor-insights/shifting-to-a-practice-theory-practice-approach/)
- **在过程中检查理解：** 实验辅导通过对话追踪错误和早期误解。AIPE 可以要求学生解释“为什么会这样”，并根据回答回补先修知识。[形成性评估](https://ocw.mit.edu/courses/6-01sc-introduction-to-electrical-engineering-and-computer-science-i-spring-2011/pages/instructor-insights/formative-assessment-during-design-labs/)

6.01SC 的校内 Online Tutor 并未随 OCW 开放，不能把课程页面等同于完整自动评分系统。我们需要自己建立练习、反馈与记录机制。

## Princeton：从基础到项目与独立研究

学校公开培养路线先安排数学、物理和计算机基础，再进入电路与信息信号，之后是系统课程、专业方向和毕业论文。这种结构支持“基础 → 综合应用 → 独立工作”的递进。[本科课程结构](https://ece.princeton.edu/academics/undergraduate/curriculum)

| 课程 | 已核实内容 | AIPE Academy 用法 |
|---|---|---|
| ECE 203 电路设计、分析与实现 | 电阻、电容、电感、二极管、晶体管和运放；强调直觉、设计、SPICE 仿真与实验 | 电路理论与实验同时推进 |
| ECE 201 信息信号 | 采样、傅里叶变换、LTI 系统、频域与滤波 | 理解波形、采样与系统行为 |
| ECE 206 逻辑设计 | 从逻辑基础进入计算硬件 | 数字控制方向选学，非第一个 Buck 的门槛 |
| ECE 301 / 302 | 分别侧重系统设计及机器人系统实验；目录列 201/203 为先修 | 参考综合项目的组织方式 |
| ECE 297 / 298 | 二年级独立项目；通常包括文献检索 | 提前培养问题意识与资料检索 |

来源：[官方课程目录](https://ece.princeton.edu/academics/courses/catalog)。并非要求电力电子学习者完整复刻 Princeton 所有课程。

找到一套可用的历史课程站：Paul Cuff 的 **ELE 201，2016–17 学年春季**。它公开了[课程说明](https://www.princeton.edu/~cuff/ele201/)、[周安排](https://www.princeton.edu/~cuff/ele201/schedule.html)、[实验目录](https://www.princeton.edu/~cuff/ele201/labs.html)和 [Kulkarni 讲义入口](https://www.princeton.edu/~cuff/ele201/kulkarni.html)。周安排从频域分析推进到采样、系统稳定性与控制；课程用音频识别和压缩项目连接数学与实际任务。这可启发我们的“波形分析 → 滤波 → 电源纹波”项目链，但该项目链是 AIPE 原创建议。

这套旧课站不是 2026 年 syllabus。当前 ECE 203 的课程定位能由官方目录确认，但本轮未取得完整公开逐周授课表或指定教材清单；ABET 页面明确说明其课程文件夹有密码保护。[访问说明](https://ece.princeton.edu/abet)。因此不把 MIT 的指定教材推断为 Princeton 的指定教材。

## 教材如何选择

以下“建议用途”是我们基于公开目录的选用判断；没有要求学习者全部购买或通读。

| 书籍或讲义 | 建议用途 | 来源与说明 |
|---|---|---|
| **Fundamentals of Electric Circuits — Charles K. Alexander、Matthew N. O. Sadiku** | 可选基础电路主书：直流分析、储能、暂态、交流到变换 | [McGraw Hill 目录](https://www.mheducation.com/highered/product/Fundamentals-of-Electric-Circuits-Alexander.html)；商业教材，非已核实的 MIT/Princeton 指定书 |
| **Electric Circuits — James W. Nilsson、Susan A. Riedel** | 另一种基础电路主书，训练系统分析与解题 | [Pearson 第12版资料](https://www.pearson.com/content/dam/one-dot-com/one-dot-com/us/en/files/14939-ENG-Nilsson-ElectricCircuits-12E.pdf)；与上一种选一本即可 |
| **Foundations of Analog and Digital Electronic Circuits — Anant Agarwal、Jeffrey H. Lang** | 连接电路分析、器件模型、模拟数字电路与设计 | [MIT 6.002 指定教材记录](https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/pages/syllabus/)；数学与物理准备后使用 |
| **MIT 6.01 开放课程讲义** | 了解编程、系统与电路怎样连在一起 | [官方开放讲义入口](https://ocw.mit.edu/courses/6-01sc-introduction-to-electrical-engineering-and-computer-science-i-spring-2011/pages/syllabus/)；取相关单元，不把机器人整套作为必修 |
| **OpenStax Algebra and Trigonometry 2e** | 代数薄弱时回补方程、函数和三角基础 | [官方资源](https://openstax.org/books/algebra-and-trigonometry-2e/pages/preface)；作为数学桥接选项 |
| **OpenStax University Physics Volume 2** | 配合电学、磁学和储能基础，后续补热学 | [官方资源](https://openstax.org/books/university-physics-volume-2/pages/preface)；大学物理层次，仍需相应数学准备 |

默认可用路径：**仓库原创入门讲解＋公开课程 → 一种基础电路主书（可选）→ MIT 电路/系统相关单元 → Erickson/Maksimović 专业教材**。公开课程材料与商业教材全文的可访问性是两回事。

## 对仓库的具体落实

新增[先修路线](../curriculum/01-foundations/prerequisite-path.zh-CN.md)，把需要补齐的内容分成 F00–F09，并设置不同进入门槛：基础变换器、动态控制、工程设计与研究准备。数学和工具随任务引入，不把所有大学课程都放在第一项目前。

新增[学习入口](../START-HERE.md)与[导师流程](../prompts/tutor-guide.md)。用户只需普通语言表达学习意图；导师负责诊断、讲解、作业、反馈、复习及个人进度记录。另有[第一节原创示范](../curriculum/01-foundations/first-lesson.zh-CN.md)，用于验证流程。

已采集并归类的是课程元数据、先修要求、教学安排摘要、书目和公开资源入口。没有批量镜像讲义、作业解答或受保护文件。MIT OCW 页面列有自己的许可条件，外部材料不自动适用本仓库 CC BY 4.0。后续逐个选择可分发材料时应保留其许可与出处。
