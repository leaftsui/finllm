# 这是一个关于开源的不忘初心的故事

## 为什么要做开源LawGLM项目

### 初心

- 首先，LawGLM和我个人的经历是分不开的。20年我在Notre Dame法学院J.D.毕业以后，我就坚定了不做律师、All in AI的想法。我选择了继续留校攻读数据科学研究生，从而实现了从文科转码的跨越。考虑到家人原因，2021年夏天，我在抽中H1B的情况下，选择回国。回国首选就是奔赴自己热爱的，法律人工智能行业。当时挑来挑去，挑了一家看上去有大所背书的，法律科技初创公司。但是现实却狠狠地给我上了一课，因为我选的赛道是ToL的法律人工智能。
- ```国内当时ToG/ToC的法律人工智能一直做的很不错，因为在美国和诸多大所如Wilson Sonsini、Backer Mckenzie、Clifford Chance的IT负责人交流以后，他们给我定位的人才画像就是律所的首席AI官，所以我当时的想法就是做ToL。```

### 迷途
- 我加入了以后才发现，当年这行业哪有人工智能啊，我前前司连逻辑回归、支持向量机都没有，但不知道为什么，每次产品宣传上都会写上，使用了先进的人工智能技术（当时是机器学习和深度学习）。
- 除了秘塔在用深度学习模型做法律翻译SaaS外，好多机器学习模型都无用武之地。检索类产品也是关键词检索、模糊匹配，好点的话上```TF-IDF```和```BM25```。当时比较热门的ToL几款同类产品分别是案件检索平台（基于数据库的增删改查）、尽调报告自动生成（基于专家规则、由无数个if-then构成的完形填空）、数据治理（基于长篇正则表达式的数据处理），包括我前前司也在做。
- 这些在程序员眼里看都是上个世纪的远古巨神、在美国律所是基本面的东西，居然还在当年ToL端的法律AI界大行其道，第一次感受到了中美之间律所法律AI应用的落差。
- 结果就当我还在想怎么样打破中间的壁垒、弥补断层时，我收到消息说因为长期瞎指挥的G姓总经理助理作死，整个公司要倒闭了。

### 转折

- 然后事情又出现了反转，瞎指挥的人离职了，所有人马都被并入IT部门了，对内提供服务了。我也迎来了人生的转机，我遇到了，至今为止我都很感谢我的老板，主打一个专业的人干专业的事情。在22年，在IT部门，我有了自己的深度学习服务器（**没想到吧之前连台AI服务器都没有**）、开始基于飞桨框架（信创要求）部署企业级法律AI应用（GPT出现前，也感谢```PaddlePaddle```，给我认证了PPDE技术专家）、在八卡A10机器上完整微调了```Roberta```模型（用Roberta模型实现条款分类，并根据条款对应的类别推送风险点，训练数据为美国加州律协标注的开源M&A并购数据集，MUAD)、初代```GLM-130B```（GPT出现前，我至今都记得GLM初代目中英混杂的经典推理输出）。
- 在22年11月GPT出来后，先后尝试了```GPT-3```与```GPT-3.5```、初代```chatglm-6B```、企业级RAG框架```langchain-chatchat```（当时还叫作```langchain-chatglm-6b```）。从此，我完整了解到了企业级IT应用的项目流程以及完整的应用架构。
- 虽然没有怎么对外宣传，但第一次站在应用前沿的感觉，真爽。这里再次感谢我的前前老板。

### 逐梦

- 最后的最后，因为想要打破舒适圈、追寻更广阔的天地，23年4月我决定投身于数据要素行业，加入了开放群岛开源社区、然后就去了数据交易所，致力于建设以数据为中心的人工智能产业。
- 后面不知道为什么，我在23年4月份和大家科普数据资产、数据交易的概念时候，莫名其妙被国内的法律科技群群主给踢了，现在反思可能是因为我"**喷的**"实在是太多了，在我被踢之后，我就坚定了要做LawGLM的想法。
- LawGLM是要做一个以落地应用为导向的开源项目，旨在把两极（律师端和开发端）链接在一起，一方面让律师明白技术逻辑原理及实现路径（现诸多面向律师的AI应用指南，太浅、只能算作一个软件操作使用说明书），另一方面也让有志于做法律应用的开发者知道业主方真实的需求场景、从而更好地确认产品方向。

### 幸甚有你

- LawGLM项目来源于我和智谱AI**开源灵魂人物**的一次BrainStorming。彼时智谱AI刚刚结束FinGLM比赛，正在谋划下一场比赛。
- 在我不懈的努力、持续的骚扰（不是）下，该灵魂人物终于答应了，下一场比赛确定为LawGLM并且会将赛事的成果进行开源。
- 不过，这竟然已经是整整**1年前**的事情了。

## 为什么有开发者感觉这次比赛和Law关系不大

### FinGLM 2.0？不，我们持续进步

- 本次赛题设计时部分延续了智谱AI主办的FinGLM大赛的思路，技术场景为信息检索大类，应用场景为"数据要素×金融服务"中的尽职调查场景。我们在选取API以及构造API数据时，将法律数据和金融数据都进行了选取。本次大赛的核心考点，是考验大模型对于"可用不可见类"数据API的统筹调度能力，是为"Agentic AI"。Agentic AI与Agent Workflow不同的点在于，本次比赛没有人为设置行业知识壁垒，也不考察由人工拆解业务流形成SOP，而是由大模型根据用户需求、自主去规划任务可实现的路径并且完成执行。换句话说，就是考察大模型能不能根据用户的需求，在API类数据信息检索调度场景下，把业务专家、产品专家、工程专家的事情都干了。

### 出发！数据要素，乘风破浪！

- 总结一下， 本次LawGLM比赛，是探索与大模型在数据要素流通利用中关于数据智能调度编排、数据编制的可行性之探索。为了考验基座大模型的能力，我们特地选取了最需要具有行业先验知识的法律数据与金融数据，考察大模型拆解问题的能力以及按需索骥的能力。从这方面看，本次比赛源于法律场景、使用法律数据，但又不局限于法律场景、可在其他数据流与信息流充分的行业进行复制推广，朝着更高的目标迈进———就是现在这，风起云涌、波澜壮阔的数据要素市场。

- 当然，上文说的，法律AI企业级应用构建指南，是会一起放在本次开源项目里做的。

## LawGLM遇到的困难有哪些

### 奖金问题

  - 尽管国家数据局提出了"数据要素×"三年行动计划，号召"以赛促用"，但一到真的出钱，大家的钱袋子都捂得比谁都紧。我先后联系了
    - **某头部传统法律行业新媒体公司（打太极，原话我都记得清楚——"你们做的这个很有意义+大拇指"，然后就没有然后了）**
    - **某法律垂直大模型指导老师（已读不回）**
    - **多市律协（不知道开源是什么）**
    - **多家律所高级合伙人（摆烂）**
    - **多家数据商（愿意赞助、但要求换赛题，不想做法律）**
  - 最后在**中国信息通信研究院两化所**的支持下，本次**以赛促用、开源赋能产业**的开源项目终于找到了金主爸爸，就是**广州市人民政府**、**琶洲管委会**。
  - 终于，我们的开源项目有了一个温暖的家，那就是广州塔小蛮腰所在的**琶洲人工智能产业集聚区**。

### 数据问题

  - 出于合规性考虑，为了最大程度规避数据风险，在**中闻（上海）律所**的协助下，基于法律数据标注指南，**北京交通大学法学院**的同学们完成了数据标注，选取的数据为裁判文书，都是同学按标注指南阅读法律裁判文书，复制粘贴、改写转录、**纯手工**标注的。感谢**中闻（上海）律所**以及**北京交通大学法学院**对本次比赛数据部分的鼎力支持。

### 人工成本

  - 因为本次比赛纯属是各家单位主业务之外的事情，很多工程上的投入都需要智谱AI和安硕信息的专家在班后加班加点地完成，干到三点都是家常便饭，比如智谱AI的刘幼峰老师和安硕信息的静俐老师。LLM发展至今，算法工程师的时间都是很宝贵的，工资也是很高的（这才是真正的按小时计费）。但是为了共同的开源目标，大家都以200%在投入这场赛事。

```（🐂了，为爱发电！）```

  - 最后是赛事持续运营的问题。因为比赛周期比较长，为了保持赛事的热度，我们举办了选手的线上答疑活动，公布了榜A的Baseline。选手的分享费用，均由主办方人员个人赞助。

```（再次🐂了，为爱发电！）```

## LawGLM目前取得的成果

### 参赛队伍数量历年之最

  - 本次LawGLM吸引了**1387**只队伍参赛，覆盖超过**4000**余名开发者，创下了琶洲算法大赛的报名之最。本次比赛吸引了来自**清华**、**北大**、**北理工**、**北邮**、**华南理工**等学校，也吸引了**中国香港**、**中国澳门**的开发者报名参赛。企业参赛方面，**腾讯**、**电信**、**移动**、**联通**，甚至**虎牙直播**、**YY直播**也都参加了本次比赛。

### 参赛选手升职加薪

  - 另外，最让人自豪的是，本次的好几个参赛选手，因为打得好，方案被甲方采纳或者被下家采集，完成了**升职加薪**的目标！

## LawGLM开源路线图

### 咨询类
  - ToG的法律AI应用
  - ToL的法律AI应用
  - ToC的法律AI应用
### 数据类
  - 中国法律开源数据集汇总
  - 美国法律开源数据集汇总
  - 欧洲法律开源数据集汇总
### CookBook类
  - 信息抽取（含多模态）
  - 文本分类
  - 文本生成
    - 用大模型生成尽调报告
    - 合同审查
  - 舆情分析
### 基于langchain-chatchat的法律数据检索
### 基于Dify的面向律师工作场景的Workflow
### 大赛内容
  - 选手LawGLM解决方案

## 特别感谢

- 特别感谢**广州市人民政府**、**中国信息通信研究院**、**琶洲管委会**、**智谱AI**、**安硕信息**、**深圳数据交易所**的大力支持。
- 特别感谢**中关村科学城管委会**、**海新域城市更新集团**对本次**以赛促用**的宣传。
- 特别特别特别特别感谢所有参与开源项目的**志愿者**们。

