---
title: "DRAGEN 分析"
date: 2026-07-30
summary: "DRAGEN Single Cell RNA 分析踩坑记录：BaseSpace 表单必填项排查、PIPseq 条码架构解读、UMI 长度异常核实全过程。"
type: tutorial
tags: ["Jian Wu", "jwtools", "PH project", "DRAGEN", "Illumina"]
cover: "https://jianwu-atlas.github.io/assets/img/logos/jianwu_social_preview.png"
#cover: "https://jianwu-atlas.github.io/assets/img/logos/jwtools_logo_social_preview.png"
#cover: "https://github.com/jianwu-atlas/jwtools/raw/main/man/figures/logo.png"
---

# DRAGEN 分析

基于当前两张截图的表单状态，我按"已确认正确 / 必须填写 / 需要展开核实 / 风险提醒"四类给你梳理：

## ✅ 已经填对，无需修改

| 字段 | 当前值 | 说明 |
| --- | --- | --- |
| Library Kit | Illumina Single Cell 3' RNA Library kit | 与Vishnu的手册匹配，选对了 |
| Input Type | Expression input only | 正确——Marek邮件已确认 **no hashing** |
| Save Results To | PH project | 已关联项目 |
| Map/Align Output | BAM | 保留BAM便于后续QC/追溯，合理 |
| Reference | Homo sapiens [1000 Genomes] hg38 v6 | 人源样本用内置参考基因组，OK |
| Use STAR Aligner | 未勾选 | **建议保持不勾选**，用DRAGEN原生比对器（更快、更成熟），STAR是备选路径不必启用 |

---

## ⚠️ 必须填写（当前为空，会阻塞Launch）

### 1. **Biosample(s)** 表格（第一张图）

`Select biosamples...` 目前是空的——这是**硬性必填项**。需要点击为 Expression Biosample 列选择你已上传的FASTQ对应的biosample条目。由于选的是"Expression input only"，Feature Biosample / HTO Biosample两列可以留空/灰显。

### 2. **Gene Annotation File**（第二张图）

`Select dataset file...` 也是空的——**这个必须填**，否则无法做基因定量（gene-level counting需要GTF）。

> ⚠️ **关键提醒**：这里的GTF **必须和你选的Reference（hg38 v6）版本严格匹配**（染色体命名格式如"chr1" vs "1"、基因ID版本等），否则会出现大量reads无法注释到基因上。建议直接用Illumina官方提供的与该reference配套的GTF，而不是自己从Ensembl/GENCODE下载的版本，除非你确认版本号完全一致。
> 

---

## 🔍 需要展开检查的折叠区域（第二张图底部5个）

这几个目前是收起状态，**必须逐一展开确认**，尤其前两个：

### **Library Kit Configuration**（最重要）

由于你选的是"Illumina Single Cell 3' RNA Library kit"预设，理论上barcode block结构（对应R1=45bp的cell barcode+UMI架构）应该已经自动配置好。**但仍需展开核实**：

- 显示的block长度总和是否等于45bp（R1长度）
- 是否有sub-version选项（比如是否对应你实际用的具体kit lot/chemistry版本）

如果这里显示的参数与Vishnu手册里的barcode架构图（block数量、linker序列、UMI位置）对不上，说明预设kit版本选错了，需要联系Illumina确认或手动改用Custom architecture。

### **Demultiplexing**

虽然bcl2fastq已经按sample sheet的12个index组合完成了lane级别的demux，但这里的Demultiplexing选项可能是指**cell-level的sample识别**（如果同一个biosample里混了多个样本条码）。根据你的sample sheet，12个样本（GFP/GFP_HCL/SOX9/SOX9TGFb × 3组细胞数14_2/25_13/16_15）已经在index层面拆开了，这里大概率不需要额外配置，但建议展开确认没有误勾选"pooled sample demux"之类选项。

### **Advanced Settings**（建议展开）

重点找 **Expected Cell Number / Force Cells** 类参数——按Marek邮件"~10000 cells per sample"应填入 `10000`（如果留空，DRAGEN会用knee-point自动估计，对于低质量或非常规化学的数据有时不够准确，建议显式指定）。

### **Cell Hashing and Feature Counting**

因为你选的是"Expression input only"，这个区域大概率是灰显/不生效的，可以跳过，无需展开修改。

### **Additional Arguments**

非必需，除非有特殊命令行参数需要传入（比如STARsolo兼容性参数），一般留空即可。

---

## 📋 建议的执行顺序

1. 先点开 **Library Kit Configuration**，截图给我核实block结构是否等于45bp（这是判断barcode识别会不会失败的关键）
2. 填 **Biosample(s)** → 选对应FASTQ
3. 填 **Gene Annotation File** → 选与hg38 v6匹配的GTF
4. 展开 **Advanced Settings** → 填 Expected Cells = 10000
5. 展开 **Demultiplexing** 确认无误
6. 确认 BaseSpace Labs 免责声明勾选（已勾）
7. Launch Application

---

**Analysis Name建议**：当前是自动生成的日期字符串（`DRAGEN Single Cell RNA 07/30/2026 10:01:41`），如果这是多个样本run里的一个，建议改成能追溯的名字，比如 `NM_0726_scRNA_DRAGEN_v4.5.4000`，方便以后在Analyses列表里快速定位，尤其如果同一个project下会跑多次分析。

---

## 1) Gene Annotation File 是否必填？—— **不是必填，之前我的回答需要修正**

看第一张截图里的悬浮提示文字：

> *"Specify a custom gene annotation file, **required if the selected reference doesn't contain a GTF**. ... `--annotation-file`"*
> 

关键逻辑是**条件式必填**：

| 情况 | 是否需要填 |
| --- | --- |
| 使用 **Custom Reference File**（自己上传的裸FASTA基因组，不含注释） | ✅ 必填，否则无法做gene-level counting |
| 使用内置的 **Homo sapiens [1000 Genomes] hg38 v6**（你现在选的） | ❌ 通常**不需要**——Illumina官方打包的DRAGEN reference package内部已经bundled了配套GTF |

另外注意字段标签本身：`Barcode Position *`、`UMI/BI Position *`这类**真正必填字段都带红色星号**，而 `Gene Annotation File`（无星号）和 `Custom Reference File`（无星号，且当前灰显不可点）在UI上都不是强制项。

**结论**：可以留空直接跳过，除非你后续发现hg38 v6内置注释版本与你的分析需求不匹配（比如需要特定的GENCODE版本），才需要手动指定。

---

## 2) 其他需要修改/核实的建议（按优先级排序）

### 🔴 高优先级——可能导致Launch失败或结果错误

**① Barcode Sequence List File —— 目前为空，这个才是Marek邮件里真正问的"proprietary whitelist"**

```
Barcode Sequence List File: Select dataset file...  （空）
```

这个字段大概率对应Vishnu手册里提到的"whitelist和software都是proprietary"那句话。虽然选了kit preset，UI仍然把这个字段单独暴露出来允许/要求手动指定，说明kit preset**不一定自带whitelist**，需要你先把Vishnu附件里的whitelist文件作为dataset上传到BaseSpace，再在这里选择。**这是当前最需要确认的一项。**

**② UMI/BI Position = `39_41`，长度只有3bp，明显异常偏短**

按你截图中的Barcode Position反推一下R1的45bp结构：

```
Barcode blocks: 0_7 (8bp) + 11_16 (6bp) + 20_25 (6bp) + 31_38 (8bp) = 28bp
中间linker gap: 8-10(3bp) + 17-19(3bp) + 26-30(5bp) = 11bp
Barcode+linker累计占用: 28+11 = 39bp
剩余可用于UMI: 45 - 39 = 6bp  (即位置39-44)
```

但当前UMI/BI Position填的是 `39_41`，只用了**3bp**（39、40、41），而不是理论上应该占满的6bp（39_44）。3bp UMI的多样性只有4³=64种组合，**UMI碰撞率会非常高**，会导致：

- PCR duplicate去重不准确
- 表观上的unique molecule count被系统性低估
- 下游定量出现虚假的低表达

**建议**：这个字段是kit preset自动填充的，理论上不应该错，但3bp确实反常。请对照Vishnu附件里的barcode架构图，确认这个数字是否真的是"39_41"还是UI截断显示不全（比如实际可能是`39_44`但输入框宽度限制显示成`39_41`），务必展开/点击进这个输入框核实完整数值。

**③ Number of Samples 出现红色报错，即使 Demultiplexing Method = None**

```
Demultiplexing Method: None  ✅ 正确（Marek确认 no multiplexing, no hashing）
Number of Samples: [空]  ⚠️ Please enter a positive integer.
```

理论上选了"None"之后这些字段应该automatically变成非必填/灰显，但看截图这个报错仍然显示为红色。这**很可能是表单UI的一个bug**——建议：

- 先尝试直接点击 **Launch Application** 看是否真的被这个报错阻塞
- 如果确实阻塞，就手动填 `1` 作为workaround（不影响实际分析逻辑，因为Demultiplexing Method是None时这个数字不会被使用）

---

### 🟡 中优先级——影响数据质量，建议调整

**④ Expected Number of Cells —— 目前为空，建议填 `10000`**

按Marek邮件"I guess ~10000 cells were loaded"，应显式填入，避免完全依赖DRAGEN的knee-point自动估计（对于非标准化学/低质量文库，自动估计有时会偏差较大）。

**⑤ Poly-A Trimming —— 目前是 None，建议考虑启用**

你的R2是72bp（cDNA read）。对于3'-tag类型的scRNA-seq，如果转录本的3'UTR较短，72bp的R2很容易读穿到poly-A尾巴里，导致：

- 大量A-homopolymer污染比对（多重比对到基因组poly-A富集区域）
- 部分reads比对质量下降或被丢弃

**建议**：展开Poly-A Trimming下拉框，改成启用（通常选项名类似"Enable"或指定最小poly-A长度阈值），这对短UTR基因的定量准确性有实际帮助。

**⑥ RNA Library Type = Forward —— 建议交叉核对**

这个决定了链特异性方向的判定（sense vs antisense比对）。多数3' kit默认是Forward没错，但既然Vishnu附件里有完整protocol，建议花30秒交叉确认一下，避免链方向判断错误导致reads被系统性丢弃到"antisense"类别。

---

### 🟢 低优先级——不影响结果但建议规范化

**⑦ Analysis Name 建议重命名**（之前已提过）：从默认的时间戳字符串改成能追溯的名字，比如：

```
NM_0726_scRNA_hg38v6_DRAGEN_v4.5.4000
```

---

## 总结行动清单

| 步骤 | 字段 | 操作 |
| --- | --- | --- |
| 1 | Biosample(s) | 选对应FASTQ（前一轮提到，仍需确认已填） |
| 2 | Barcode Sequence List File | 上传Vishnu提供的proprietary whitelist后选择 |
| 3 | UMI/BI Position | 点开确认完整数值，核对是否应为`39_44`而非`39_41` |
| 4 | Number of Samples | 尝试Launch，若报错阻塞则填`1`作为workaround |
| 5 | Expected Number of Cells | 填 `10000` |
| 6 | Poly-A Trimming | 建议启用 |
| 7 | RNA Library Type | 交叉核对Vishnu手册确认Forward是否正确 |
| 8 | Analysis Name | 改成可追溯命名 |

其余字段（Reference hg38 v6、Input Type、Demultiplexing Method=None、Use STAR Aligner未勾选、Thresholding Method=Ratio、Samples Per Node=1）均**保持现状，无需修改**。

---

## 是的，成功了——而且现在是真正意义上的"分析已经在跑"

这份日志比上一张截图的"Initializing"状态更进一步，出现了几个关键的确认信号：

```
ICA pipeline analysis has started
ICA Analysis Id: '7d89f2d0-2fb7-45e6-b518-5003dcbbd120'
```

这说明 BaseSpace 已经把job成功转交给底层的 **ICA (Illumina Connected Analytics)** 计算集群，拿到了真实的Analysis ID，说明12个biosample的FASTQ路径全部被正确解析并挂载（能看到12个`biosamples/xxxxx/ds.xxxxx`路径，与你选的12个样本一一对应，数量吻合，没有漏掉或重复）。

---

## 🔑 重要发现——这份日志间接回答了之前的疑虑

### ① 确认了 kit 类型：`$library_kit (Value: pipseq-kit)`

这印证了Marek邮件里那句**"This is a PIP-seq protocol, overall very similar to 10x, but without microfluidics"**——DRAGEN内部真的把这套化学识别为 Fluent Biosciences PIPseq 的预设架构，而不是标准10x Chromium。这也解释了为什么barcode结构长得比较特殊（4个block + 特定linker间隔），因为PIP-seq是靠**split-pool组合标记**而非微流控液滴来给细胞打条码的，架构天然和10x不同。

### ② `$rna_library_type (Value: SF)`

之前UI显示的"Forward"在底层实际编码为 **SF**（Stranded Forward），这是正常的内部值映射，无需担心。

### ③ ⚠️ 需要重点关注：`$scrna_umi_position (Value: 39_41)` —— 现在被**实锤确认**，不是UI显示截断

上一轮我猜测这可能是"输入框显示不全"，但这份日志是**直接从提交给ICA后端的实际JSON参数**摘出来的，证明 `39_41` 就是**真实被使用的UMI长度参数（仅3bp）**，而不是显示问题。

结合前面反推的barcode结构：

```
Barcode blocks: 0_7 (8bp) + 11_16 (6bp) + 20_25 (6bp) + 31_38 (8bp)
→ 占用到 position 38 为止
→ R1总长45bp (position 0-44)
→ 理论剩余可用UMI空间: position 39-44 (共6bp)
→ 但实际配置只用了 39-41 (3bp)，position 42-44 (3bp) 完全没被分配用途
```

**这是这套"pipseq-kit"官方预设本身自带的参数**（不是你手动填错），所以大概率是Illumina针对某个特定版本PIP-seq化学试剂预置的标准值——**Fluent PIPseq不同版本的UMI长度确实存在差异**（有的版本UMI比10x的12bp短很多），所以3bp也并非绝无可能，但这个长度确实明显偏短，会直接影响molecule去重的准确性。

**建议动作**：这个job已经启动，现在中途改参数已经来不及了（除非cancel重跑）。但请趁分析还在跑的这段时间，**对照Vishnu提供的官方PDF manual里的barcode结构示意图**，确认一下UMI区段的官方标注长度是否确实是3bp。如果manual里写的是6bp而这里用了3bp，说明kit preset本身可能有bug或版本不匹配，之后需要联系Illumina支持或改用Custom barcode architecture重新提交一次。

---

## 下一步：如何监控进度

1. 页面上的 **Status** 字段会从 `Initializing` → `Running` → `Complete`，可以刷新页面查看
2. 由于是12个样本一起跑（`samples_per_node = 1`表示每个node只处理1个样本，即会并行跑12个独立compute node），根据每个样本的read深度，预计整体耗时可能在**1-3小时**左右
3. 完成后重点看 **REPORTS** 页签里每个样本的：
    - **Valid barcode rate**（如果UMI只有3bp确实有问题，这里的estimated cell number或saturation曲线可能会出现异常）
    - **Sequencing saturation** 是否偏高（UMI多样性不足会导致这个指标虚高，掩盖了真实的library complexity）

完成后把REPORTS页面截图发我，我帮你核实这个3bp UMI长度在实际数据里有没有造成可见的duplication异常。
