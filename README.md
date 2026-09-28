# Kasumi Scientific Plotting Skill

一个统一、可安装的 Codex 科研绘图 Skill，整合：

- Kasumi 的光电探测器个人 Python 模板（I–V、I–t、光谱、Rise/Fall、偏振）；
- 通用论文图、多面板证据结构与 PDF/版式质量检查；
- 使用 Codex 内置图像生成的机制图与 graphical abstract 工作流；
- 仅在明确请求时启用的 Origin/OPJU 与 EditaPlot 兼容路线。

仓库不包含实验结果、私人路径、API 密钥、Origin 软件或许可证，也没有收录许可不明确的 `figures4papers` 第三方素材。附带的数据均为明确标注的模拟或历史调整示例。

## 安装

将 Skill 目录克隆或复制到 Codex skills 目录：

```bash
git clone https://github.com/Kasnm1/kasumi-scientific-plotting-skill.git
mkdir -p ~/.codex/skills
cp -R kasumi-scientific-plotting-skill/kasumi-scientific-plotting ~/.codex/skills/
```

重新打开 Codex 任务后，可使用：

```text
Use $kasumi-scientific-plotting to plot my verified data with the personal photodetector template.
```

普通 Python 绘图与 QA 依赖：

```bash
python3 -m pip install -r kasumi-scientific-plotting/requirements.txt
```

Origin 路线需要用户自行提供合法安装并激活的 Windows Origin/OriginPro。公开仓库中的 EditaPlot 仅包含兼容包装与安全规范，完整渲染还需要独立的 EditaPlot engine。

固定 Origin I–t 渲染器的可选 Python 依赖位于：

```bash
python -m pip install -r kasumi-scientific-plotting/requirements-origin.txt
```

## 安全边界

- 原始数据默认只读；不会静默平滑、删点、归一化、拟合或补造统计结果。
- AI 示意图不会被当作定量数据或实验结果。
- 模拟示例必须保留 `SIMULATED_REHEARSAL` 或同等清楚的来源标记。
- 最终图应保留可复现代码、可编辑 PDF/SVG（适用时）、PNG 预览和必要的来源记录。

## License and notices

The repository uses the Apache License 2.0. Some adapted material retains separate attribution and compatible terms; see [NOTICE](NOTICE) and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
