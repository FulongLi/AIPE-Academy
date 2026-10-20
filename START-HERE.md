# 从这里开始 / Start learning

**English below.**

你不需要会写提示词，也不需要先买教材。选择一种方式：

- **Claude Code：** 在终端运行 `/plugin install aipe-academy --marketplace FulongLi/AIPE-Academy`，然后输入 `/aipe-academy:learn`，或直接说“请按 AIPE Academy 带我从零学习”。
- **Codex：** 克隆本仓库（`git clone https://github.com/FulongLi/AIPE-Academy`），在 Codex 中打开该文件夹，输入 `$aipe-academy` 或说“请按 AIPE Academy 带我从零学习”。
- **其他 AI 助手：** 把本仓库链接或本地文件夹交给它，再说：

> 请按 AIPE Academy 带我从零学习。我不知道该从哪里开始，请先了解我的基础，再带我完成第一小节。

如果已经学过一些内容，也可以说“检查我的基础，从适合我的位置开始”，或者直接点名一个主题（例如“讲讲 Buck 变换器”、“做一个三相功率计算”、“太阳能电池怎样发电”）。以后只需说“继续学习”“我没懂”“给我一点提示”或“检查我的作业”。

## 导师会怎样带你学

1. 了解你的目标、已有基础和可用时间。“完全不会”是有效答案。
2. 一次问一个小问题，用一个小任务确定起点，不要求你先选择教材或课程编号。
3. 先完成一个短任务，再学必要的概念，随后换条件再试一次。
4. 每节有解释、练习、可复现的 Python 实验和自测；每个阶段有小项目与掌握检查（G1/G2/G3）。
5. 有本地工作区时，把进度和作业保存在自己的 `learning/` 文件夹（不会被提交）；只有聊天时，给你可复制的进度摘要。

## 四个知识领域与入口课程

| 领域 | 入口课程（英文，含 Python 实验） | 中文内容 |
|---|---|---|
| 基础 Foundations | [DC circuit fundamentals](curriculum/foundations/circuits/dc-circuit-fundamentals.md) | [第一节：一个简单电路用了多少电？](curriculum/01-foundations/first-lesson.zh-CN.md)、[先修路线](curriculum/01-foundations/prerequisite-path.zh-CN.md) |
| 电力电子 Power Electronics | [Buck converter fundamentals](curriculum/power-electronics/dc-dc-conversion/buck-converter-fundamentals.md) → [开放 Buck 实验](curriculum/03-converters/buck-open-lab.md) → [Buck 设计教程](curriculum/03-converters/buck-converter.md) | 规划中 |
| 电力系统 Power Systems | [Three-phase system fundamentals](curriculum/power-systems/ac-power-networks/three-phase-fundamentals.md) | 规划中 |
| 可再生能源 Renewable Energy | [Solar PV fundamentals](curriculum/renewable-energy/solar-photovoltaics/solar-pv-fundamentals.md) | 规划中 |

数学按需要穿插学习：做电阻电路时先用代数，研究充放电时再补微积分，进入反馈控制时再补变换与系统理论。完整目录见[课程总览](curriculum/README.md)与[知识体系](curriculum/taxonomy.json)；学术范围参考见 [MIT OpenCourseWare 基准](references/mit-ocw-baseline.md)（外部资源，AIPE Academy 与 MIT 无隶属关系）。

其余多数主题仍是课程大纲或规划中的模块。导师可按大纲提供临时讲解和原创练习，但应说明哪些内容还没有经过仓库审核。Research 目前是发展路径，不是已完成的研究课程。

## 给 AI 导师的入口

在学习请求下，先读 [`skills/aipe-academy/SKILL.md`](skills/aipe-academy/SKILL.md) 与[导师流程](prompts/tutor-guide.md)，再根据学习者进度选读课程。不要要求学习者填写复杂提示词。无法读取仓库链接时，应说明访问限制并请学习者提供 README 或本地文件夹，不能假装已经读取。

---

## Start learning (English)

You do not need to write prompts or buy a textbook first. Pick one:

- **Claude Code:** run `/plugin install aipe-academy --marketplace FulongLi/AIPE-Academy`, then `/aipe-academy:learn`, or simply say "Teach me electrical engineering from the beginning."
- **Codex:** clone this repository (`git clone https://github.com/FulongLi/AIPE-Academy`), open the folder in Codex and type `$aipe-academy`, or say "Guide me through AIPE Academy from the beginning."
- **Any other AI assistant:** share this repository link or local folder and say:

> Guide me through AIPE Academy from the beginning. I do not know where to start; find my starting point with short questions, then teach the first lesson.

You can also name a topic directly ("Explain the operation of a Buck converter", "Run a simple three-phase power calculation", "Help me understand how solar panels generate electricity") or say "Continue my previous learning session".

The tutor asks one short question at a time, places you with a small task, teaches intuition before equations, runs reproducible Python labs with you, checks understanding progressively and keeps your progress in a local `learning/` folder that is never committed. The four domains and their entry lessons are listed in the table above; most other modules are outlines or planned, and the tutor says so. Installation details: [docs/plugin-installation.md](docs/plugin-installation.md).
