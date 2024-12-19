# 金融大模型挑战赛



# 赛制规则





# baseline解析



## FantasticSql



![image-20241216112253739](README.assets/image-20241216112253739.png)

执行步骤

```python
for i in all_question:
    try:
        FantasticSql(i):
            # 将同一team中的三个连续问题拼接为一个str
        	# 实体识别
            info, tables = process_question(question_content)
            	process_question:
                    #调用大模型实现实体识别：基金公司、公司名称、代码
                    # 识别出实体之后进行查询语句找到相关信息
                recall_table():
                    # 进行表召回，传入所有表描述+连续问题->LLM推理出相关的表
                    # 召回的表获取数据字典中的表描述
                messages= 实体+召回表结构+连续问题 
                遍历team，根据messages逐个回答
                	尝试三次
                    	获取大模型回答answer
                        若answer中存在sql则调用接口执行sql获取查询结果
                        	将查询结果写入messages
                        若answer中不存在sql
	                        说明此时大模型根据查询结果回答了问题
                            保存回答写入文件
                            跳出循环
                        
    except Exception as e:  # 推荐使用Exception来捕获异常，更具体
   		traceback.print_exc()  # 打印异常信息
```





大模型实体提取，输入连续的三个问题，提取出全部的实体，包括公司名称、基金名称、代码

```json
[{'role': 'system', 'content': '\n你将会进行命名实体识别任务，并输出实体json\n\n你只需要识别以下三种实体：\n-公司名称\n-代码\n-基金名称。\n\n只有出现了才识别，问题不需要回答\n\n其中，公司名称可以是全称，简称，拼音缩写\n代码包含股票代码和基金代码\n基金名称包含债券型基金，\n\n以下是几个示例：\nuser:实体识别任务：```唐山港集团股份有限公司是什么时间上市的（回答XXXX-XX-XX）\n当年一共上市了多少家企业？\n这些企业有多少是在北京注册的？```\nassistant:```json\n[{"公司名称":"唐山港集团股份有限公司"}]\n```\nuser:实体识别任务：```JD的职工总数有多少人？\n该公司披露的硕士或研究生学历（及以上）的有多少人？\n20201月1日至年底退休了多少人？```\nassistant:```json\n[{"公司名称":"JD"}]\n```\nuser:实体识别任务：```600872的全称、A股简称、法人、法律顾问、会计师事务所及董秘是？\n该公司实控人是否发生改变？如果发生变化，什么时候变成了谁？是哪国人？是否有永久境外居留权？（回答时间用XXXX-XX-XX）```\nassistant:```json\n[{"代码":"600872"}]\n```\nuser:实体识别任务：```华夏鼎康债券A在2019年的分红次数是多少？每次分红的派现比例是多少？\n基于上述分红数据，在2019年最后一次分红时，如果一位投资者持有1000份该基金，税后可以获得多少分红收益？```\nassistant:```json\n[{"基金名称":"华夏鼎康债券A"}]\n```\nuser:实体识别任务：```化工纳入过多少个子类概念？```\nassistant:```json\n[]\n```\n'}, {'role': 'user', 'content': '实体识别任务：```600872的全称、A股简称、法人、法律顾问、会计师事务所及董秘是？\n该公司实控人是否发生改变？如果发生变化，什么时候变成了谁？是哪国人？是否有永久境外居留权？（回答时间用XXXX-XX-XX）\n在实控人发生变化的当年股权发生了几次转让？```'}]
```

提取结果

~~~json
'```json
[{"代码":"600872"}]
```'
~~~

json格式提取

```
[{'代码': '600872'}]
```

实体查询

查询实体（公司、基金、代码）信息的常量表证券主表、港股证券主表、美股证券主表

```
['ConstantDB.SecuMain', 'ConstantDB.HK_SecuMain', 'ConstantDB.US_SecuMain']
```

拼接查询语句

```sql
SELECT InnerCode, CompanyCode, SecuCode, ChiName, ChiNameAbbr, EngName, EngNameAbbr, SecuAbbr, ChiSpelling
FROM ConstantDB.SecuMain
WHERE SecuCode = '600872'
```

查询结果

```json
[{'InnerCode': 2120, 'CompanyCode': 1805, 'SecuCode': '600872', 'ChiName': '中炬高新技术实业(集团)股份有限公司', 'ChiNameAbbr': '中炬高新', 'EngName': 'Jonjee Hi-Tech Industrial And Commercial Holding Co.,Ltd', 'EngNameAbbr': 'JONJEE', 'SecuAbbr': '中炬高新', 'ChiSpelling': 'ZJGX'}]
```

保存查询结果和查询的表



大模型全量表召回=全量数据表描述+问题串+输出格式

```json
[{'role': 'system', 'content': "\n数据表说明如下：\n{'库名中文': '上市公司基本资料', '库名英文': 'AStockBasicInfoDB', '表英文': 'LC_StockArchives', '表中文': '公司概况', '表描述': '收录上市公司的基本情况，包括：联系方式、注册信息、中介机构、行业和产品、公司证券品种及背景资料等内容。'}\n---\n{'库名中文': '上市公司基本资料', '库名英文': 'AStockBasicInfoDB', '表英文': 'LC_NameChange', '表中文': '公司名称更改状况', '表描述': '收录公司名称历次变更情况，包括：中英文名称、中英文缩写名称、更改日期等内容。'}\n---\n{'库名中文': '上市公司基本资料', '库名英文': 'AStockBasicInfoDB', '表英文': 'LC_Business', '表中文': '公司经营范围与行业变更', '表描述': '1.收录上市公司、发债公司的经营范围（包括主营和兼营）以及涉足行业情况。\\n2.信息来源：公开转让说明书、董事会决议、定报、临时公告等。'}\n---\n{'库名中文': '上市公司行业板块', '库名英文': 'AStockIndustryDB', '表英文': 'LC_ExgIndustry', '表中文': '公司行业划分表', '表描述': '收录上市公司在证监会行业划分、中信行业划分、GICS行业划分、申万行业划分、中信建投、中银(BOCI)行业分类、中证指数行业分类、聚源行业划分等各种划分标准下的所属行业情况。'}\n---\n{'库名中文': '上市公司行业板块', '库名英文': 'AStockIndustryDB', '表英文': 'LC_ExgIndChange', '表中文': '公司行业变更表', '表描述': '内容说明：\\n本表记录上市公司从上市至今，由于主营业务变更导致的所属行业变化情况，采用同一行业分类标准，对其历史变更进行人为追溯，以便投资者进行公司数据回测，或开展行业估值、财务等数据的计算。\\n本表对公司所属行业的变更情况尽量参照原行业分类发布公司的披露数据，并对其新旧分类标准的不同之处加以判断，结合公司实际业务的变化，逐一进行人工比对，用最新的行业标准反映公司历史上的行业变更情况。\\n数据范围：A股上市公司\\n信息来源：公司公告、聚源整理。'}\n---\n{'库名中文': '上市公司行业板块', '库名英文': 'AStockIndustryDB', '表英文': 'LC_IndustryValuation', '表中文': '行业估值指标', '表描述': '内容说明：本表记录不同行业标准下的的衍生指标，包括行业静态市盈率、滚动市盈率、市净率、股息率等指标。\\n数据范围：2014-01-01至今\\n信息来源：聚源计算'}\n---\n{'库名中文': '上市公司行业板块', '库名英文': 'AStockIndustryDB', '表英文': 'LC_IndFinIndicators', '表中文': '行业财务指标表', '表描述': '1.内容说明：本表存储行业衍生指标相关数据，反映不同行业分类标准下，各行业的成长能力、偿债能力、盈利能力和现金获取能力等。本表数据多采用整体法进行计算（如计算增长率时，采用（行业内所有公司的当期总值-上期总值）/上期总值，而非行业内公司增长率的算术平均值），且部分比例类指标对金融类公司不适用（流动比例、速动比例、毛利率等），该类指标未计算金融类公司。\\n2.数据范围：A股财报、业绩快报、股本结构、分红等数据，2014年至今。\\n3.信息来源：公告披露，聚源计算。'}\n---\n{'库名中文': '上市公司行业板块', '库名英文': 'AStockIndustryDB', '表英文': 'LC_COConcept', '表中文': '概念所属公司表', '表描述': '记录A股上市公司所属概念信息。'}\n---\n{'库名中文': '上市公司行业板块', '库名英文': 'AStockIndustryDB', '表英文': 'LC_ConceptList', '表中文': '概念板块常量表', '表描述': '记录A股市场中热点概念的相关信息'}\n---\n{'库名中文': '上市公司产品供销/人力资源', '库名英文': 'AStockOperationsDB', '表英文': 'LC_SuppCustDetail', '表中文': '公司供应商与客户', '表描述': '1.内容说明：收录A股上市公司的主要供应商、客户清单，以及交易标的、交易金额等信息。\\n2.数据范围：2015年至今\\n3.信息来源：招股说明书、定报'}\n---\n{'库名中文': '上市公司股东与股本/公司治理', '库名英文': 'AStockShareholderDB', '表英文': 'LC_SHTypeClassifi', '表中文': '股东类型分类表', '表描述': '本表记录聚源股东类型分类数据'}\n---\n{'库名中文': '上市公司股东与股本/公司治理', '库名英文': 'AStockShareholderDB', '表英文': 'LC_MainSHListNew', '表中文': '股东名单(新)', '表描述': '1.收录公司主要股东构成及持股数量比例、持股性质等明细资料，包括发行前和上市后的历次变动记录。\\n2.数据范围：1992-06-30至今\\n3.信息来源：招股说明书、上市公告书、定报、临时公告等。'}\n---\n{'库名中文': '上市公司股东与股本/公司治理', '库名英文': 'AStockShareholderDB', '表英文': 'LC_SHNumber', '表中文': '股东户数', '表描述': '1.反映公司全体股东、A股股东、B股东、H股东、CDR股东的持股情况及其历史变动情况等。\\n2.指标计算公式：\\n  1)户均持股比例＝((股本/股东总户数)/股本)*100%（公式中分子分母描述同一股票类型）\\n  2)相对上一期报告期户均持股比例变化＝本报告期户均持股比例－上一报告期户均持股比例\\n  3)户均持股数季度增长率＝(本季度户均持股数量/上一季度户均持股数量－1)*100%\\n  4)户均持股比例季度增长率=(本季度户均持股比例/上一季度户均持股比例-1)*100% \\n  5)户均持股数半年增长率=(本报告期户均持股数量/前推两季度户均持股数量-1)*100% \\n  6)户均持股比例半年增长率 = (本报告期户均持股比例/ 前推两个季度户均持股比例-1)*100%\\n2.数据范围：1991-1-1至今\\n3.信息来源：招股说明书、上市公告书、定报、临时公告、深交所互动易、上证e互动等。'}\n---\n{'库名中文': '上市公司股东与股本/公司治理', '库名英文': 'AStockShareholderDB', '表英文': 'LC_Mshareholder', '表中文': '大股东介绍', '表描述': '1.收录上市公司及发债企业大股东的基本资料，包括直接持股和间接持股，以及持股比例、背景介绍等内容。\\n2.数据范围：2004-12-31至今\\n3.信息来源：募集说明书、招股说明书、定报、临时公告等'}\n---\n{'库名中文': '上市公司股东与股本/公司治理', '库名英文': 'AStockShareholderDB', '表英文': 'LC_ActualController', '表中文': '公司实际控制人', '表描述': '1.收录根据上市公司在招投说明书、定期报告、及临时公告中披露的实际控制人结构图判断的上市公司实际控制人信息。_x000D_\\n2.目前只处理实际控制人有变动的数据，下期和本期相比如无变化，则不做处理。\\n3.数据范围：2004-12-31至今\\n4.信息来源：招股说明书、上市公告书、定报、临时公告等。'}\n---\n{'库名中文': '上市公司股东与股本/公司治理', '库名英文': 'AStockShareholderDB', '表英文': 'LC_ShareStru', '表中文': '公司股本结构变动', '表描述': '1.收录上市公司股本结构历史变动情况。其中：标注“披露”的字段为公司公告原始披露，标注“计算”的字段为聚源依据股权登记日，并且考虑高管股锁定的实际情况计算所得的股本结构。\\n2.数据范围：1990-12-10至今\\n3.信息来源：招股说明书、上市公告书、定报、临时公告等。'}\n---\n{'库名中文': '上市公司股东与股本/公司治理', '库名英文': 'AStockShareholderDB', '表英文': 'LC_StockHoldingSt', '表中文': '股东持股统计', '表描述': '1.收录报告期末，各类机构投资者对每只股票的持仓情况，以及前十大（无限售条件）股东合计持股情况等。\\n2.机构持股统计中，基金持股综合考虑了上市公司披露的十大股东数据以及基金报告中披露的基金持股数据；机构持股合计包含上市公司披露的股东持股以及在同一截止时点上基金披露的所持股票数据。\\n3.计算公式：\\n1)机构持有无限售流通股数量＝机构持有无限售流通A股之和 \\n2)机构持有无限售流通股比例＝(机构持有无限售流通股数量/无限售A股)*100% \\n3)机构持有A股数量＝机构持有A股之和 \\n4)机构持有A股比例＝(机构持有A股数量/A股总数)*100% \\n5)机构持有股票数量＝机构持有股票之和 \\n6)机构持有股票比例＝(机构持有股票数量/总股本)*100%\\n4.数据范围：1992年至今\\n5.信息来源：招股说明书、上市公告书、定报、临时公告等'}\n---\n{'库名中文': '上市公司股东与股本/公司治理', '库名英文': 'AStockShareholderDB', '表英文': 'LC_ShareTransfer', '表中文': '股东股权变动', '表描述': '1.收录公司股东股权转让、二级市场买卖、股权拍卖、大宗交易、股东重组等引起股东股权变动方面的明细资料，并包含与股权分置改革相关的股东增持、减持等信息。\\n2.数据范围：1996-01-26至今\\n3.信息来源：上交所和深交所大宗交易公开信息、临时公告等。'}\n---\n{'库名中文': '上市公司股东与股本/公司治理', '库名英文': 'AStockShareholderDB', '表英文': 'LC_ShareFP', '表中文': '股东股权冻结和质押', '表描述': '1.收录股东股权被冻结和质押及进展情况，包括被冻结质押股东、被接受股权质押方、涉及股数以及冻结质押期限起始和截止日等内容。\\n2.数据范围：1999-09-30至今\\n3.信息来源：股权质押公告、股权冻结公告、解除质押冻结公告等。'}\n---\n{'库名中文': '上市公司股东与股本/公司治理', '库名英文': 'AStockShareholderDB', '表英文': 'LC_ShareFPSta', '表中文': '股东股权冻结和质押统计', '表描述': '1.收录股东股权的质押冻结统计数据，包括股东股权累计冻结质押股数、累计占冻结质押方持股数比例和累计占总股本比例等情况。\\n2.指标计算公式：\\n1)累计占冻结质押方持股数比例=股东累计冻结质押股数(股)/股东持股数\\n2)累计占总股本比例 =股东累计冻结质押股数(股)/公司总股本\\n3)累计占总股本比例(计算) =股东累计冻结质押股数(股)/公司总股本\\n3.数据范围：2006-05-15至今\\n4.信息来源：股权质押公告、股权冻结公告、解除质押冻结公告等。'}\n---\n{'库名中文': '上市公司股东与股本/公司治理', '库名英文': 'AStockShareholderDB', '表英文': 'LC_Buyback', '表中文': '股份回购', '表描述': '1.介绍上市公司(包含科创板)发生股份回购的相关方案信息，包括股份类别、首次信息发布日期、回购协议签署日、股份被回购方、回购数量上限与下限、回购价格上限与下限、回购期限起始与截止日等内容。\\n2.数据范围：1994-06-23至今\\n3.信息来源：回购公告、董事会公告等。'}\n---\n{'库名中文': '上市公司股东与股本/公司治理', '库名英文': 'AStockShareholderDB', '表英文': 'LC_BuybackAttach', '表中文': '股份回购关联表', '表描述': '1.补充上市公司(包含科创板)发生股份回购的相关信息，包括本次回购数量、累计回购数量、本次回购资金和累计回购数量等内容。\\n2.数据范围：1994-09-27至今\\n3.信息来源：回购公告、董事会公告等。'}\n---\n{'库名中文': '上市公司股东与股本/公司治理', '库名英文': 'AStockShareholderDB', '表英文': 'LC_LegalDistribution', '表中文': '法人配售与战略投资者', '表描述': '1.收录公司首次发行、增发新股、发行可转债过程中采用网下配售方式过程中，获得配售的企业、基金明细。\\n2.数据范围：1994-04-23至今\\n3.信息来源：上市公司公告'}\n---\n{'库名中文': '上市公司股东与股本/公司治理', '库名英文': 'AStockShareholderDB', '表英文': 'LC_NationalStockHoldSt', '表中文': 'A股国家队持股统计', '表描述': '1.内容说明：本表记录股市国家队成员持有A股的相关信息，包含：持有A股总数，占总股本比例，持有A股数量增减，持有A股数量增减幅度等。\\n2.数据范围：2003-01-01至今\\n3.信息来源：聚源'}\n---\n{'库名中文': '上市公司股东与股本/公司治理', '库名英文': 'AStockShareholderDB', '表英文': 'CS_ForeignHoldingSt', '表中文': '外资持股统计', '表描述': '内容说明：境外投资者持股统计，包含持股总数、持股比例，境外投资者指QFII/RQFII/深股通/全球存托凭证跨境转换机构/全球存托凭证存托人。\\n数据范围：2007年至今\\n信息来源：深交所、上交所'}\n---\n{'库名中文': '上市公司财务指标/财务报表/融资与分红', '库名英文': 'AStockFinanceDB', '表英文': 'LC_AShareSeasonedNewIssue', '表中文': 'A股增发', '表描述': '1.收录A股增发A股、B股增发A股、H股增发A股等的明细情况，包括历次增发预案、进程日期、预案有效期、发行属性、发行价区间、发行量区间、发行日期、上网发行情况、网下配售申购情况和募集资金与费用等内容。\\n2.数据范围：1991-08-17至今'}\n---\n{'库名中文': '上市公司财务指标/财务报表/融资与分红', '库名英文': 'AStockFinanceDB', '表英文': 'LC_ASharePlacement', '表中文': 'A股配股', '表描述': '1.收录A股历次配股预案及实施进展明细，包括预案有效期、配股价格区间、配股说明书、募集资金和配股交款日等内容。\\n2.数据范围：1991-03-06至今'}\n---\n{'库名中文': '上市公司财务指标/财务报表/融资与分红', '库名英文': 'AStockFinanceDB', '表英文': 'LC_Dividend', '表中文': '公司分红', '表描述': '1.该表包括上市公司历次分红预案及实施进展，以及下年分配次数、方式等，以分红事件为维度，一次分红做一条记录。\\n2.数据范围：证券上市起-至今\\n3.信息来源：上市公司公告'}\n---\n{'库名中文': '上市公司财务指标/财务报表/融资与分红', '库名英文': 'AStockFinanceDB', '表英文': 'LC_CapitalInvest', '表中文': '资金投向说明', '表描述': '1.公司自有资金、通过发行新股、增发新股、配股、发行可转债、发行企业债等方式所得募集资金的项目投资情况以及运用进展和改投状况。\\n2.数据范围：1988-12-01至今\\n3.信息来源：董事会公告、招股意向书、招股说明书等'}\n---\n{'库名中文': '上市公司股票行情', '库名英文': 'AStockMarketQuotesDB', '表英文': 'CS_StockCapFlowIndex', '表中文': '境内股票交易资金流向指标', '表描述': '内容说明：\\n1、收录深沪京交易所正常交易的股票在每个交易日基于不同成交金额区间及成交时间区间主动及含主动被动交易的累计流入流出金额、量等信息衍生计算的统计类指标\\n2、数据提供范围说明\\n2023-10-09 及以后提供完整全盘、开盘、尾盘主买主卖及含主动被动数据\\n2022-11-15~2023-09-28 仅提供全盘主买主卖及含主动被动资金流向数据\\n2016-11-29~2022-11-14 仅提供全盘含主动被动资金流向数据\\n数据范围：2016-11-29至今\\n信息来源：基于交易所行情数据衍生计算'}\n---\n{'库名中文': '上市公司股票行情', '库名英文': 'AStockMarketQuotesDB', '表英文': 'CS_TurnoverVolTecIndex', '表中文': '境内股票成交量技术指标', '表描述': '内容说明：收录境内股票上市之日起基于日、周、月、季、半年、年K线行情衍生计算的成交量技术指标\\n数据范围：股票上市起-至今\\n信息来源：基于沪深京交易所及股转系统行情数据衍生计算'}\n---\n{'库名中文': '上市公司股票行情', '库名英文': 'AStockMarketQuotesDB', '表英文': 'CS_StockPatterns', '表中文': '股票技术形态表', '表描述': '内容说明：收录股票从最近一个交易日往前追溯一段时期的行情表现和技术形态表现，包括近1周、近1月、近3月、近半年、近1年、上市以来的表现情况，以及连涨跌天数、连续放量缩量天数、向上向下有效突破均线、N天M板、均线多空头排列看涨看跌等技术形态指标。 本表覆盖的证券品种有A股、B股、中国存托凭证(CDR), 覆盖的上市标志有主板、三板、创业板、科创板。 \\n数据范围：股票上市或挂牌起-至今\\n信息来源：基于沪深京交易所及股转系统行情数据衍生计算'}\n---\n{'库名中文': '上市公司股票行情', '库名英文': 'AStockMarketQuotesDB', '表英文': 'QT_DailyQuote', '表中文': '日行情表', '表描述': '1.收录股票、债券（不包含银行间交易的债券）、基金、指数每个交易日收盘行情数据，包括昨收盘、今开盘、最高价、最低价、收盘价、成交量、成交金额、成交笔数等行情指标。\\n2.数据范围：证券上市起-至今\\n3.信息来源：上交所/深交所/北交所每日行情收盘文件'}\n---\n{'库名中文': '上市公司股票行情', '库名英文': 'AStockMarketQuotesDB', '表英文': 'QT_StockPerformance', '表中文': '股票行情表现(新)', '表描述': '1.内容说明：\\n收录股票从最近一个交易日往前追溯一段时期的行情表现信息，包括近1周、1周以来、近1月、1月以来、近3月、近半年、近1年、今年以来、上市以来的表现情况，以及β、α、波动率、夏普比率等风险指标，本表包含停牌数据。\\n计算方法：\\n1)区间成交金额＝∑区间每个交易日成交金额 \\n2)区间成交量＝∑区间每个交易日成交量 \\n3)区间涨跌幅＝(区间内最新复权收盘价/区间首日复权昨收盘－1)*100 \\n4)区间振幅＝(区间最高复权价－区间最低复权家价)/区间首日复权昨收盘*100 \\n5)区间换手率＝区间每一天换手率的合计值 \\n6) 区间成交均价＝区间成交金额之和/区间成交量之和（考虑了区间有除权的情况） \\n7) 区间日均成交金额＝区间成交金额之和/区间实际交易天数 \\n8) 区间日均换手率＝区间每日换手率之和/区间实际交易天数\\n2.数据范围：股票上市起-至今\\n3.信息来源：基于沪深京交易所行情数据衍生计算'}\n---\n{'库名中文': '上市公司股票行情', '库名英文': 'AStockMarketQuotesDB', '表英文': 'LC_SuspendResumption', '表中文': '停牌复牌表', '表描述': '1.收录上市公司/基金/债券停牌复牌信息，如停牌日期、停牌时间、停牌原因、停牌事项说明、停牌期限、复牌日期、复牌时间、复牌事项说明等，包括盘中临时停牌。\\n2.数据范围：2008.04-至今\\n2.信息来源：上海证券交易所、深圳证券交易所、北京证券交易所'}\n---\n{'库名中文': '上市公司财务指标/财务报表/融资与分红', '库名英文': 'AStockFinanceDB', '表英文': 'LC_BalanceSheetAll', '表中文': '资产负债表_新会计准则', '表描述': '1.反映企业依据2007年新会计准则在年报、中报、季报中披露的资产负债表数据；并依据新旧会计准则的科目对应关系，收录主要科目的历史对应数据。\\n2.收录同一公司在报告期末的四种财务报告，即未调整的合并报表、未调整的母公司报表、调整后的合并报表以及调整后的母公司报表。\\n3.若某个报告期的数据有多次调整，则该表展示历次调整数据。\\n4.该表中各财务科目的单位均为人民币元。\\n5.带“##”的特殊项目为单个公司披露的非标准化的科目，对应的“特殊字段说明”字段将对其作出说明；带“##”的调整项目是为了让报表的各个小项借贷平衡而设置的，便于客户对报表的遗漏和差错进行判断。\\n6.数据范围：1989-12-31至今\\n7.信息来源：招股说明书、定报、审计报告等'}\n---\n{'库名中文': '上市公司财务指标/财务报表/融资与分红', '库名英文': 'AStockFinanceDB', '表英文': 'LC_IncomeStatementAll', '表中文': '利润分配表_新会计准则', '表描述': '1.反映企业依据2007年新会计准则在在年报、中报、季报中披露的利润表数据；并依据新旧会计准则的科目对应关系，收录了主要科目的历史对应数据。\\n2.收录同一公司在报告期末的四种财务报告，即未调整的合并报表、未调整的母公司报表、调整后的合并报表以及调整后的母公司报表。\\n3.若某个报告期的数据有多次调整，则该表展示历次调整数据。\\n4.该表中各财务科目的单位均为人民币元。\\n5.带“##”的特殊项目为单个公司披露的非标准化的科目，对应的“特殊字段说明”字段将对其作出说明；带“##”的调整项目是为了让报表的各个小项借贷平衡而设置的，便于客户对报表的遗漏和差错进行判断。\\n6.数据范围：1989-12-31至今\\n7.信息来源：招股说明书、定报、审计报告等'}\n---\n{'库名中文': '上市公司财务指标/财务报表/融资与分红', '库名英文': 'AStockFinanceDB', '表英文': 'LC_CashFlowStatementAll', '表中文': '现金流量表_新会计准则', '表描述': '1.反映企业依据2007年新会计准则在年报、中报、季报中披露的现金流量表数据；并依据新旧会计准则的科目对应关系，收录了主要科目的历史对应数据。\\n2.收录同一公司在报告期末的四种财务报告，即未调整的合并报表、未调整的母公司报表、调整后的合并报表以及调整后的母公司报表。\\n3.若某个报告期的数据有多次调整，则该表展示历次调整数据。\\n4.该表中各财务科目的单位均为人民币元。\\n5.带“##”的特殊项目为单个公司披露的非标准化的科目，对应的“特殊字段说明”字段将对其作出说明；带“##”的调整项目是为了让报表的各个小项借贷平衡而设置的，便于客户对报表的遗漏和差错进行判断。\\n6.数据范围：1998-06-30至今\\n7.信息来源：招股说明书、定报、审计报告等'}\n---\n{'库名中文': '上市公司财务指标/财务报表/融资与分红', '库名英文': 'AStockFinanceDB', '表英文': 'LC_IntAssetsDetail', '表中文': '公司研发投入与产出', '表描述': '\\n1.内容说明：收录上市公司研发投入相关数据，主要包括研发费用投入总额、占比，研发人员构成、占比等信息。\\n2.数据范围：2014年至今\\n3.信息来源：定期报告'}\n---\n{'库名中文': '上市公司财务指标/财务报表/融资与分红', '库名英文': 'AStockFinanceDB', '表英文': 'LC_MainOperIncome', '表中文': '公司主营业务构成', '表描述': '1收录公司主营业务的收入来源、成本构成；主营业务收入、成本和利润与上年同期的对比较。\\n2.数据范围：1998-12-31至今\\n3.信息来源：招股说明书、定报、审计报告等'}\n---\n{'库名中文': '上市公司财务指标/财务报表/融资与分红', '库名英文': 'AStockFinanceDB', '表英文': 'LC_OperatingStatus', '表中文': '公司经营情况述评', '表描述': '1.收录公司管理层对季度、半年度、年度经营情况的自我评价，以及其后期发展计划和预测，本表涵盖了公司招股以来的历次纪录。\\n2.数据范围：1997-12-31至今\\n3.信息来源：定期报告'}\n---\n{'库名中文': '上市公司财务指标/财务报表/融资与分红', '库名英文': 'AStockFinanceDB', '表英文': 'LC_AuditOpinion', '表中文': '公司历年审计意见', '表描述': '1.收录中介机构对公司季度、半年度、年度经营情况的评价，区分审计单位、审计意见类型，本表涵盖了公司招股以来的历次纪录。\\n2.数据范围：1990-12-31至今\\n3.信息来源：定期报告、审计报告等'}\n---\n{'库名中文': '上市公司产品供销/人力资源', '库名英文': 'AStockOperationsDB', '表英文': 'LC_Staff', '表中文': '公司职工构成', '表描述': '1.从技术职称、专业、文化程度、年龄等几个方面介绍公司职工构成情况。\\n2.数据范围：1999-12-31至今\\n3.信息来源：定期报告、招股说明书等'}\n---\n{'库名中文': '上市公司产品供销/人力资源', '库名英文': 'AStockOperationsDB', '表英文': 'LC_RewardStat', '表中文': '公司管理层报酬统计', '表描述': '1.按报告期统计管理层的报酬情况，包括报酬总额、前三名董事报酬、前三名高管报酬、报酬区间统计分析等。\\n2.数据范围：2001-12-31至今\\n3.信息来源：定期报告、招股说明书等'}\n---\n{'库名中文': '上市公司公告资讯/重大事项', '库名英文': 'AStockEventsDB', '表英文': 'LC_Warrant', '表中文': '公司担保明细', '表描述': '1.收录上市公司公告中披露的担保等重大事项，包括时间内容、最新进展、事件主体/交易对象名称、企业编号、与上市公司关联关系、担保原因等指标。\\n2.数据范围：2001年-至今\\n3.信息来源：上市公司公告'}\n---\n{'库名中文': '上市公司公告资讯/重大事项', '库名英文': 'AStockEventsDB', '表英文': 'LC_Credit', '表中文': '公司借贷明细', '表描述': '1.收录上市公司公告中披露的公司借贷等重大事项描述，包括时间内容、时间主体、交易对象名称、借贷金额、还款金额、借贷利率、借贷期限等指标。\\n2.数据范围：2001年-至今\\n3.信息来源：上市公司公告'}\n---\n{'库名中文': '上市公司公告资讯/重大事项', '库名英文': 'AStockEventsDB', '表英文': 'LC_SuitArbitration', '表中文': '公司诉讼仲裁明细', '表描述': '1.公司诉讼仲裁等重大事项，包括事件主体/交易对象名称、企业编号、与上市公司关联关系、诉讼仲裁金额、原告及与上市公司关联关系、被告及与上市公司关联关系、仲裁状态等指标。\\n2.数据范围：2001-至今\\n3.信息来源：上市公司临时公告'}\n---\n{'库名中文': '上市公司公告资讯/重大事项', '库名英文': 'AStockEventsDB', '表英文': 'LC_EntrustInv', '表中文': '重大事项委托理财', '表描述': '1.公司委托贷款等重大事项，包括事件主体/交易对象名称、企业编号、与上市公司关联关系、涉及金额、委托期限、委托起始日、委托截止日等指标。\\n2.数据范围：2001-至今\\n3.信息来源：上市公司公告'}\n---\n{'库名中文': '上市公司公告资讯/重大事项', '库名英文': 'AStockEventsDB', '表英文': 'LC_Regroup', '表中文': '公司资产重组明细', '表描述': '1.公司资产重组，如资产出售与转让、资产置换、债权债务重组等重大事项描述说明。\\n2.数据范围：2001-至今\\n3.信息来源：上市公司公告'}\n---\n{'库名中文': '上市公司公告资讯/重大事项', '库名英文': 'AStockEventsDB', '表英文': 'LC_MajorContract', '表中文': '公司重大经营合同明细', '表描述': '1.本表存放公司重大经营合同的事项，包括事件主体/交易对象名称、企业编号、与上市公司关联关系、合同标的、合同获得方式、涉及金额、合同起始日、合同截止日、合同期限等指标。\\n2.数据范围：2012-至今\\n3.信息来源：上市公司公告'}\n---\n{'库名中文': '上市公司公告资讯/重大事项', '库名英文': 'AStockEventsDB', '表英文': 'LC_InvestorRa', '表中文': '投资者关系活动', '表描述': '1.收录各调研机构对上市公司调研的详情，包括调研日期、参与单位、调研人员、调研主要内容等信息。\\n2.数据范围：2012-至今\\n3.信息来源：巨潮，上交所互动易和深交所互动易'}\n---\n{'库名中文': '上市公司公告资讯/重大事项', '库名英文': 'AStockEventsDB', '表英文': 'LC_InvestorDetail', '表中文': '投资者关系活动调研明细', '表描述': '1、收录参与上市公司调研活动的调研机构明细数据，包括调研单位、调研人员等指标。\\n2、数据范围：2016-至今\\n3、信息来源：交易所，上交所互动易和深交所互动易'}\n---\n{'库名中文': '上市公司股东与股本/公司治理', '库名英文': 'AStockShareholderDB', '表英文': 'LC_ESOP', '表中文': '员工持股计划', '表描述': '1.主要记录员工持股计划当期的情况：包括相关日期、事件进程、事件说明、资金来源、资金总额、股票来源、股票规模、实施是否分期、存续期、锁定期等一些情况。\\n2.数据范围：2014.6-至今\\n3.信息来源：上市公司公告'}\n---\n{'库名中文': '上市公司股东与股本/公司治理', '库名英文': 'AStockShareholderDB', '表英文': 'LC_ESOPSummary', '表中文': '员工持股计划概况', '表描述': '1.本表主要记录员工持股计划总体情况：包括相关日期、事件进程、事件说明、资金来源、资金总额、股票来源、股票规模等一些情况。对于一些分期实施的员工持股计划，本表记录总体计划的情况。\\n2.数据范围：2014.6-至今\\n3.信息来源：上市公司公告'}\n---\n{'库名中文': '上市公司股东与股本/公司治理', '库名英文': 'AStockShareholderDB', '表英文': 'LC_TransferPlan', '表中文': '股东增减持计划表', '表描述': '1.内容说明：收录上市公司(包含科创板)股东增持计划、减持计划、被动减持计划、不减持类别指标。\\n2.数据范围：2005-至今\\n3.信息来源：上市公司公告'}\n---\n{'库名中文': '上市公司股东与股本/公司治理', '库名英文': 'AStockShareholderDB', '表英文': 'LC_SMAttendInfo', '表中文': '股东大会出席信息', '表描述': '1.收录股东大会召开时间，地点，类别；投票方式；见证律师事务所及经办律师；全体股东出席情况；非流通股东出席情况；流通股东出席情况。\\n2.数据范围：1999-1-28至今'}\n---\n{'库名中文': '港股数据库', '库名英文': 'HKStockDB', '表英文': 'HK_EmployeeChange', '表中文': '港股公司员工数量变动表', '表描述': '1.记录港股公司员工数量的变动历史记录数据，包括信息发布日期、信息来源、生效日期、变更前员工数量、变更后员工数量等。               \\n2.数据范围：2001年至今。                     \\n3.信息来源：港交所。  '}\n---\n{'库名中文': '港股数据库', '库名英文': 'HKStockDB', '表英文': 'HK_StockArchives', '表中文': '港股公司概况', '表描述': '1.收录港股上市公司的基础信息，包括名称、成立日期、注册地点、注册资本、公司业务、所属行业分类、主席、公司秘书、联系方式等信息。\\n2.信息来源：港交所等。'}\n---\n{'库名中文': '港股数据库', '库名英文': 'HKStockDB', '表英文': 'CS_HKStockPerformance', '表中文': '港股行情表现', '表描述': '1.内容说明：\\n收录股票从最近一个交易日往前追溯一段时期的行情表现信息，包括近1周、1周以来、近1月、1月以来、近3月、近半年、近1年、今年以来、上市以来的表现情况，本表包含停牌数据。\\n2.数据范围：2005年至今。\\n3.数据来源：根据港交所披露数据聚源衍生计算。'}\n---\n{'库名中文': '美股数据库', '库名英文': 'USStockDB', '表英文': 'US_CompanyInfo', '表中文': '美股公司概况', '表描述': '本表主要收录美国市场上市公司的基本情况，包括公司名称、地址、电话、所属国家、公司简介等信息。'}\n---\n{'库名中文': '美股数据库', '库名英文': 'USStockDB', '表英文': 'US_DailyQuote', '表中文': '美股日行情', '表描述': '1.本表收录美国市场证券的日收盘行情\\n2.数据范围：2000年2月至今'}\n---\n{'库名中文': '公募基金数据库', '库名英文': 'PublicFundDB', '表英文': 'MF_FundArchives', '表中文': '公募基金概况', '表描述': '1.本表记录了基金基本情况，包括基金规模、成立日期、投资类型、管理人、托管人、存续期、历史简介等。_x000D_\\n2.历史数据：1998年3月起-至今。\\n3.信息来源：基金公司官网披露的产品说明书。'}\n---\n{'库名中文': '公募基金数据库', '库名英文': 'PublicFundDB', '表英文': 'MF_FundProdName', '表中文': '公募基金产品名称', '表描述': '1.本表记录基金的交易所披露简称、集中申购简称、ETF申购赎回简称等基金相关的名称类信息。\\n2.历史数据：1998年3月起-至今。\\n3.信息来源：基金公司官网披露的产品说明书。其中，4-证监会简称处理的是资本市场电子化信息披露平台-公募基金净值日报的简称；6-公告披露简称处理的是基金产品资料概要和定报披露的简称；8-基金全称处理的是发售公告或是资本市场电子化信息披露平台-基金概况的全称，是将基金的多个份额合并的基金全称。'}\n---\n{'库名中文': '公募基金数据库', '库名英文': 'PublicFundDB', '表英文': 'MF_InvestAdvisorOutline', '表中文': '公募基金管理人概况', '表描述': '1.本表记录了基金管理人的基本情况介绍，包括成立日期、注册资本、法人代表、联系方式、背景简介等。\\n2.历史数据：1998年3月起-至今。\\n3.信息来源：基金公司官网。'}\n---\n{'库名中文': '公募基金数据库', '库名英文': 'PublicFundDB', '表英文': 'MF_Dividend', '表中文': '公募基金分红', '表描述': '1.本表记录基金单次分红信息，包括分红比例、登记日、除息日等信息，以及聚源根据相关数据计算的累计分红金额、累计分红次数等数据。\\n2.历史数据：1998年12月起-至今。\\n3.信息来源：基金公司官网披露的相关临时公告。'}\n---\n{'库名中文': '诚信数据库', '库名英文': 'CreditDB', '表英文': 'LC_ViolatiParty', '表中文': '违规当事人处罚', '表描述': '1.该表以事件+当事人+处罚为维度，记录单个事件下单个当事人的每一个处罚，包括当事人及其性质、当事人编码、开始日期、截止日期、违规类型、关联关系、关联上市公司、处罚机构编码、处罚机构、涉及金额、处罚说明等指标。\\n2.数据范围：2014年-至今\\n3.信息来源：交易所、上市公司公告、证监会等'}\n---\n{'库名中文': '指数数据库', '库名英文': 'IndexDB', '表英文': 'LC_IndexBasicInfo', '表中文': '指数基本情况', '表描述': '1.收录了市场上主要指数的基本情况，包括指数类别、成份证券类别、发布机构、发布日期、基期基点、指数发布的币种等信息。\\n2.数据源：中证指数有限公司、上海证券交易所、深圳证券交易所、中央国债登记结算有限责任公司、申银万国研究所、标普道琼斯指数公司等'}\n---\n{'库名中文': '指数数据库', '库名英文': 'IndexDB', '表英文': 'LC_IndexComponent', '表中文': '指数成份', '表描述': '1.收录了市场上主要指数的成份证券构成情况，包括成份证券的市场代码、入选日期、删除日期以及成份标志等信息。\\n2.该表仅收录主指数成份信息，不收录与主指数关系（Relationship）为“1-币种不同，2-分红规则不同，3-分红规则和币种都不同，4-税后分红”的衍生指数的信息。\\n3.历史数据：1990年12月至今\\n4.数据源：中证指数有限公司、上海证券交易所、深圳证券交易所、申银万国研究所等'}\n---\n{'库名中文': '机构数据库', '库名英文': 'InstitutionDB', '表英文': 'LC_InstiArchive', '表中文': '机构基本资料', '表描述': '1.收录市场上重要机构的基本资料情况，如证券公司、信托公司、保险公司等；包含机构名称、机构信息、联系方式、机构背景等信息.\\n2.数据源：国家企业信用信息公示系统等.'}\n---\n{'库名中文': '常量库', '库名英文': 'ConstantDB', '表英文': 'SecuMain', '表中文': '证券主表', '表描述': '本表收录单个证券品种（股票、基金、债券）的代码、简称、上市交易所等基础信息。'}\n---\n{'库名中文': '常量库', '库名英文': 'ConstantDB', '表英文': 'HK_SecuMain', '表中文': '港股证券主表', '表描述': '本表收录港股单个证券品种的简称、上市交易所等基础信息。'}\n---\n{'库名中文': '常量库', '库名英文': 'ConstantDB', '表英文': 'CT_SystemConst', '表中文': '系统常量表', '表描述': '本表收录数据库中各种常量值的具体分类和常量名称描述。'}\n---\n{'库名中文': '常量库', '库名英文': 'ConstantDB', '表英文': 'QT_TradingDayNew', '表中文': '交易日表(新)', '表描述': '本表收录各个市场的交易日信息，包括每个日期是否是交易日，是否周、月、季、年最后一个交易日'}\n---\n{'库名中文': '常量库', '库名英文': 'ConstantDB', '表英文': 'LC_AreaCode', '表中文': '国家城市代码表', '表描述': '本表收录世界所有国家层面的数据信息和我国不同层级行政区域的划分信息。'}\n---\n{'库名中文': '机构数据库', '库名英文': 'InstitutionDB', '表英文': 'PS_EventStru', '表中文': '事件体系指引表', '表描述': '收录聚源最新制定的事件分类体系。'}\n---\n{'库名中文': '常量库', '库名英文': 'ConstantDB', '表英文': 'US_SecuMain', '表中文': '美股证券主表', '表描述': '本表收录美国等境外市场单个证券品种的简称、上市交易所等基础信息。'}\n---\n{'库名中文': '机构数据库', '库名英文': 'InstitutionDB', '表英文': 'PS_NewsSecurity', '表中文': '证券舆情表', '表描述': '收录了全网披露的舆情信息涉及的相关证券，对对应的事件信息，并对相应的事件的正负面情感及情感重要性进行等级划分。'}\n---\n\n用户会给你数据表描述和问题串，请针对每个问题串仔细分析其中的每个问题需要用哪些表格查询，可以是一个或者多个。"}, {'role': 'user', 'content': '问题串为:`600872的全称、A股简称、法人、法律顾问、会计师事务所及董秘是？\n该公司实控人是否发生改变？如果发生变化，什么时候变成了谁？是哪国人？是否有永久境外居留权？（回答时间用XXXX-XX-XX）\n在实控人发生变化的当年股权发生了几次转让？`\n使用以下格式回答问题：\n```json\n[\n{"question":"针对的question1","query_requirements":"针对问题里的哪些查询需求","table_name":"表格名称"},\n{"question":"针对的question1","query_requirements":"针对问题里的哪些查询需求","table_name":"表格名称"},\n{"question":"针对的question2","query_requirements":"针对问题里的哪些查询需求","table_name":"表格名称"},\n...\n]\n```\n备注，针对同一个问题，可以有多条表数据。\n请区分港股美股A股的数据在对应的表格内。\ntable_name只多不少，尽可能列举全，且为`表英文`字段。\n'}, {'role': 'assistant', 'content': '```json\n[\n{"question":"600872的全称、A股简称、法人、法律顾问、会计师事务所及董秘是？","query_requirements":"全称、A股简称、法人、法律顾问、会计师事务所及董秘","table_name":"LC_StockArchives"},\n{"question":"该公司实控人是否发生改变？如果发生变化，什么时候变成了谁？是哪国人？是否有永久境外居留权？","query_requirements":"实控人是否发生改变、变化时间、变化后的实控人、国籍、是否有永久境外居留权","table_name":"LC_ActualController"},\n{"question":"在实控人发生变化的当年股权发生了几次转让？","query_requirements":"股权发生转让的次数","table_name":"LC_ShareTransfer"}\n]\n```'}]
```

召回结果进行json格式提取

```json
[{'question': '600872的全称、A股简称、法人、法律顾问、会计师事务所及董秘是？', 'query_requirements': '全称、A股简称、法人、法律顾问、会计师事务所及董秘', 'table_name': 'LC_StockArchives'}, {'question': '该公司实控人是否发生改变？如果发生变化，什么时候变成了谁？是哪国人？是否有永久境外居留权？', 'query_requirements': '实控人是否发生改变、变化时间、变化后的实控人、国籍、是否有永久境外居留权', 'table_name': 'LC_ActualController'}, {'question': '在实控人发生变化的当年股权发生了几次转让？', 'query_requirements': '股权发生转让的次数', 'table_name': 'LC_ShareTransfer'}]
```

db_recall=召回表+实体表



prompt拼接：实体信息+召回表结构+问题串

```json
[{'role': 'system', 'content': '\n    任务：股票金融场景的sql编写问答，你将书写专业的金融行业SQL，确保理解用户的需求，纠正用户的输入错误，并确保SQL的正确性。\n    请仔细分析表结构后输出SQL.\n\n    用户会给你表格信息和问题，请你编写sql回答问题，\n    表格使用 DB.TABLE的形式，即 ```sql SELECT xxx from DB.TABLE```\n    数据库使用的是MySQL，\n    日期时间的查询方法为：\n    ```sql\n    DATE(STR_TO_DATE(TradingDay, \'%Y-%m-%d %H:%i:%s.%f\')) = \'2021-01-01\'\n    DATE(STR_TO_DATE(EndDate , \'%Y-%m-%d %H:%i:%s.%f\')) = \'2021-12-31\'\n    ```\n    所有查询请使用日，不要有时分秒。\n\n    你书写的sql在 ```sql ```内。\n\n    对于一些名称不确定的信息，如板块等，可以使用模糊查询，并且基于常识修正用户的输入。\n\n    用户的数据库描述为:\n    表格名称:AStockShareholderDB.LC_ShareTransfer\n描述:库名中文:上市公司股东与股本/公司治理\n库名英文:AStockShareholderDB\n表英文:LC_ShareTransfer\n表中文:股东股权变动\n表描述:1.收录公司股东股权转让、二级市场买卖、股权拍卖、大宗交易、股东重组等引起股东股权变动方面的明细资料，并包含与股权分置改革相关的股东增持、减持等信息。\n2.数据范围：1996-01-26至今\n3.信息来源：上交所和深交所大宗交易公开信息、临时公告等。\n\n字段描述:[\n {\n  "column_name": "ID",\n  "column_description": "ID"\n },\n {\n  "column_name": "CompanyCode",\n  "column_description": "公司代码",\n  "注释": "公司代码（CompanyCode）：与“证券主表（SecuMain）”中的“公司代码（CompanyCode）”关联，得到上市公司的交易代码、简称等。"\n },\n {\n  "column_name": "InfoPublDate",\n  "column_description": "信息发布日期"\n },\n {\n  "column_name": "InfoSource",\n  "column_description": "信息来源"\n },\n {\n  "column_name": "ContractSignDate",\n  "column_description": "股权转让协议签署日"\n },\n {\n  "column_name": "ApprovedDate",\n  "column_description": "转让批准日期"\n },\n {\n  "column_name": "TranDate",\n  "column_description": "股权正式变动日期/过户日期"\n },\n {\n  "column_name": "TransfererName",\n  "column_description": "股权出让方名称"\n },\n {\n  "column_name": "TansfererEcoNature",\n  "column_description": "股权出让方经济性质"\n },\n {\n  "column_name": "TranShareType",\n  "column_description": "出让股权性质",\n  "注释": "出让股权性质(TranShareType)与(CT_SystemConst)表中的DM字段关联，令LB = 1040，得到出让股权性质的具体描述：1-国家股，2-国有法人股，3-外资法人股，4-其他法人股，5-流通A股，6-B股，7-H股，8-转配股，9-专项资产管理计划转让，10-资产支持证券转让，11-中小企业私募债转让，12-中国存托凭证，13-可转换公司债券。"\n },\n {\n  "column_name": "SumBeforeTran",\n  "column_description": "出让前持股数量(股)"\n },\n {\n  "column_name": "PCTBeforeTran",\n  "column_description": "出让前持股比例"\n },\n {\n  "column_name": "SumAfterTran",\n  "column_description": "出让后持股数量(股)"\n },\n {\n  "column_name": "PCTAfterTran",\n  "column_description": "出让后持股比例"\n },\n {\n  "column_name": "ReceiverName",\n  "column_description": "接受股权质押方"\n },\n {\n  "column_name": "ReceiverEcoNature",\n  "column_description": "股权受让方经济性质"\n },\n {\n  "column_name": "SumAfterRece",\n  "column_description": "受让后持股数量(股)"\n },\n {\n  "column_name": "PCTAfterRece",\n  "column_description": "受让后持股比例"\n },\n {\n  "column_name": "TranMode",\n  "column_description": "股权转让方式",\n  "注释": "股权转让方式(TranMode)与(CT_SystemConst)表中的DM字段关联，令LB = 1202 AND DM NOT IN ( 8,51,55,57,98)，得到股权转让方式的具体描述：1-协议转让，2-国有股行政划转或变更，3-执行法院裁定，4-以资抵债，5-二级市场买卖，6-其他-股东重组，7-股东更名，9-其他-要约收购，10-以股抵债，11-大宗交易(席位)，12-大宗交易，13-其他-ETF换购，14-其他-行权买入，15-集中竞价，16-定向可转债转让，17-集合竞价，18-连续竞价，19-做市，20-询价转让，21-赠与，22-继承，24-间接方式转让，53-股改后间接股东增持，56-交易所集中交易，59-股权激励，70-国有股转持，71-老股转让，80-司法拍卖，99-其他。"\n },\n {\n  "column_name": "InvolvedSum",\n  "column_description": "涉及股数(股)"\n },\n {\n  "column_name": "PCTOfTansferer",\n  "column_description": "占出让方原持股数比例"\n },\n {\n  "column_name": "PCTOfTotalShares",\n  "column_description": "占总股本比例"\n },\n {\n  "column_name": "DealPrice",\n  "column_description": "交易价格(元/股)"\n },\n {\n  "column_name": "DealTurnover",\n  "column_description": "交易金额(元)"\n },\n {\n  "column_name": "ValidCondition",\n  "column_description": "生效条件"\n },\n {\n  "column_name": "TranStatement",\n  "column_description": "事项描述与进展说明"\n },\n {\n  "column_name": "IfSuspended",\n  "column_description": "是否终止实施",\n  "注释": "是否终止实施（IfSuspended），该字段固定以下常量：1-是；0-否"\n },\n {\n  "column_name": "SuspendedPublDate",\n  "column_description": "终止实施公告日期"\n },\n {\n  "column_name": "XGRQ",\n  "column_description": "修改日期"\n },\n {\n  "column_name": "JSID",\n  "column_description": "JSID"\n },\n {\n  "column_name": "SNBeforeTran",\n  "column_description": "出让前股东序号"\n },\n {\n  "column_name": "SNAfterTran",\n  "column_description": "出让后股东序号"\n },\n {\n  "column_name": "SNAfterRece",\n  "column_description": "受让后股东序号"\n },\n {\n  "column_name": "IfSPBlockTradeCode",\n  "column_description": "是否专场大宗交易代码",\n  "注释": "是否专场大宗交易代码（IfSPBLockTradeCode），该字段固定以下常量：1-是；0-否"\n },\n {\n  "column_name": "IfSPBlockTrade",\n  "column_description": "是否专场大宗交易"\n },\n {\n  "column_name": "InnerCode",\n  "column_description": "证券内部编码"\n },\n {\n  "column_name": "ResSumAfterTran",\n  "column_description": "其中:出让后有限售股数(股)"\n },\n {\n  "column_name": "NonResSumAfterTran",\n  "column_description": "其中:出让后无限售股数(股)"\n },\n {\n  "column_name": "ResSumAfterRece",\n  "column_description": "其中:受让后有限售股数(股)"\n },\n {\n  "column_name": "NonResSumAfterRece",\n  "column_description": "其中:受让后无限售股数(股)"\n },\n {\n  "column_name": "InitialInfoPublDate",\n  "column_description": "首次信息发布日期"\n },\n {\n  "column_name": "TransfererAttribute",\n  "column_description": "股权出让方所属性质"\n },\n {\n  "column_name": "TransfererCode",\n  "column_description": "股权出让方编码"\n },\n {\n  "column_name": "ReceiverAttribute",\n  "column_description": "股权受让方所属性质",\n  "注释": "股权受让方所属性质(ReceiverAttribute)与(CT_SystemConst)表中的DM字段关联，令LB = 1783 and DM in (1,2,3,99)，得到股权受让方所属性质的具体描述：1-自然人，2-企业，3-证券品种，99-其他。"\n },\n {\n  "column_name": "ReceiverCode",\n  "column_description": "股权受让方编码",\n  "注释": "当股权受让方所属性质(ReceiverAttribute)=2时，与“企业码表(EP_CompanyMain)”中的“企业编号(CompanyCode)”关联,得到事件主体企业的基本信息; 当股权受让方所属性质(ReceiverAttribute)=3时,与“证券码表总表(SecuMainAll)”中的“证券内部编码(InnerCode)”关联,得到事件主体证券品种的基本信息。"\n },\n {\n  "column_name": "InsertTime",\n  "column_description": "发布时间"\n },\n {\n  "column_name": "SumBeforeRece",\n  "column_description": "受让前持股数量(股)"\n },\n {\n  "column_name": "PCTBeforerRece",\n  "column_description": "受让前持股比例(%)"\n },\n {\n  "column_name": "TranStartDate",\n  "column_description": "股权变动起始日"\n },\n {\n  "column_name": "SerialNumber",\n  "column_description": "序号"\n }\n]\n表格名称:AStockShareholderDB.LC_ActualController\n描述:库名中文:上市公司股东与股本/公司治理\n库名英文:AStockShareholderDB\n表英文:LC_ActualController\n表中文:公司实际控制人\n表描述:1.收录根据上市公司在招投说明书、定期报告、及临时公告中披露的实际控制人结构图判断的上市公司实际控制人信息。_x000D_\n2.目前只处理实际控制人有变动的数据，下期和本期相比如无变化，则不做处理。\n3.数据范围：2004-12-31至今\n4.信息来源：招股说明书、上市公告书、定报、临时公告等。\n\n字段描述:[\n {\n  "column_name": "ID",\n  "column_description": "ID"\n },\n {\n  "column_name": "CompanyCode",\n  "column_description": "公司代码",\n  "注释": "公司代码（CompanyCode）：与“证券主表（SecuMain）”中的“公司代码（CompanyCode）”关联，得到上市公司的交易代码、简称等。"\n },\n {\n  "column_name": "InfoPublDate",\n  "column_description": "信息发布日期"\n },\n {\n  "column_name": "EndDate",\n  "column_description": "日期"\n },\n {\n  "column_name": "ControllerCode",\n  "column_description": "实际控制人代码",\n  "注释": "实际控制人代码（ControllerCode）：与“机构基本资料（LC_InstiArchive）”中的“企业编号（CompanyCode）”关联，得到实际控制人的名称，企业性质等信息。"\n },\n {\n  "column_name": "ControllerName",\n  "column_description": "实际控制人"\n },\n {\n  "column_name": "EconomicNature",\n  "column_description": "经济性质",\n  "注释": "实际控制人经济性质(EconomicNature)与(CT_SystemConst)表中的DM字段关联，令LB = 1581，得到实际控制人经济性质的具体描述：1-中央企业，2-地方国有企业，3-民营企业，4-集体企业，5-大学，6-外资，7-工会，99-其它。"\n },\n {\n  "column_name": "NationalityCode",\n  "column_description": "国籍代码",\n  "注释": "国籍代码（NationalityCode）：与“系统常量表”中的“代码（DM）”关联，令“LB=1023”，得到实际控制人的国籍编码。"\n },\n {\n  "column_name": "NationalityDesc",\n  "column_description": "国籍描述"\n },\n {\n  "column_name": "PermanentResidency",\n  "column_description": "永久境外居留权"\n },\n {\n  "column_name": "UpdateTime",\n  "column_description": "更新时间"\n },\n {\n  "column_name": "JSID",\n  "column_description": "JSID"\n },\n {\n  "column_name": "ControllerNature",\n  "column_description": "实际控制人所属性质",\n  "注释": "实际控制人所属性质(ControllerNature)与(CT_SystemConst)表中的DM字段关联，令LB = 1783，得到实际控制人所属性质的具体描述：1-自然人，2-企业，3-证券品种，99-其他。"\n }\n]\n表格名称:AStockBasicInfoDB.LC_StockArchives\n描述:库名中文:上市公司基本资料\n库名英文:AStockBasicInfoDB\n表英文:LC_StockArchives\n表中文:公司概况\n表描述:收录上市公司的基本情况，包括：联系方式、注册信息、中介机构、行业和产品、公司证券品种及背景资料等内容。\n\n字段描述:[\n {\n  "column_name": "ID",\n  "column_description": "ID"\n },\n {\n  "column_name": "CompanyCode",\n  "column_description": "公司代码",\n  "注释": "公司代码（CompanyCode）：与“证券主表（SecuMain）”中的“公司代码（CompanyCode）”关联，得到上市公司的交易代码、简称等。"\n },\n {\n  "column_name": "State",\n  "column_description": "国别",\n  "注释": "省份（State）：与“国家城市代码表（LC_AreaCode）”中的“地区内部编码（AreaInnerCode）”关联，得到省份具体信息。"\n },\n {\n  "column_name": "SecretaryBD",\n  "column_description": "董事会秘书"\n },\n {\n  "column_name": "SecuAffairsRepr",\n  "column_description": "证券/股证事务代表"\n },\n {\n  "column_name": "AuthReprSBD",\n  "column_description": "董秘授权代表"\n },\n {\n  "column_name": "ContactTel",\n  "column_description": "联系人电话"\n },\n {\n  "column_name": "ContactFax",\n  "column_description": "联系人传真"\n },\n {\n  "column_name": "ContactEmail",\n  "column_description": "联系人电子邮箱"\n },\n {\n  "column_name": "RegAddr",\n  "column_description": "公司注册地址"\n },\n {\n  "column_name": "RegZipCode",\n  "column_description": "公司注册地址邮编"\n },\n {\n  "column_name": "OfficeAddr",\n  "column_description": "公司办公地址"\n },\n {\n  "column_name": "OfficeZipCode",\n  "column_description": "公司办公地址邮编"\n },\n {\n  "column_name": "ContactAddr",\n  "column_description": "公司联系地址"\n },\n {\n  "column_name": "ConatactZipCode",\n  "column_description": "公司联系地址邮编"\n },\n {\n  "column_name": "Email",\n  "column_description": "邮箱"\n },\n {\n  "column_name": "Website",\n  "column_description": "公司网址"\n },\n {\n  "column_name": "DisclosureWebsites",\n  "column_description": "信息披露网址"\n },\n {\n  "column_name": "DisclosurePapers",\n  "column_description": "信息披露报纸"\n },\n {\n  "column_name": "EstablishmentDate",\n  "column_description": "公司成立日期"\n },\n {\n  "column_name": "IRegPlace",\n  "column_description": "首次注册登记地点"\n },\n {\n  "column_name": "LegalRepr",\n  "column_description": "法人代表"\n },\n {\n  "column_name": "GeneralManager",\n  "column_description": "总经理"\n },\n {\n  "column_name": "LegalConsultant",\n  "column_description": "法律顾问"\n },\n {\n  "column_name": "AccountingFirm",\n  "column_description": "会计师事务所"\n },\n {\n  "column_name": "InduCSRC",\n  "column_description": "公司所属证监会行业(聚源)",\n  "注释": "与(CT_IndustryType)表中的\\"行业内部编码(IndustryNum)\\"字段关联,当Standard=1时,LB=1；当Standard=22时,LB=22；当Standard=25时,LB=25；当Standard=26时,LB=26。"\n },\n {\n  "column_name": "BusinessMajor",\n  "column_description": "经营范围-主营"\n },\n {\n  "column_name": "BusinessMinor",\n  "column_description": "经营范围-兼营"\n },\n {\n  "column_name": "AShareAbbr",\n  "column_description": "A股证券简称"\n },\n {\n  "column_name": "AStockCode",\n  "column_description": "A股证券代码"\n },\n {\n  "column_name": "BShareAbbr",\n  "column_description": "B股证券简称"\n },\n {\n  "column_name": "BStockCode",\n  "column_description": "B股证券代码"\n },\n {\n  "column_name": "HShareAbbr",\n  "column_description": "H股证券简称"\n },\n {\n  "column_name": "HStockCode",\n  "column_description": "H股证券代码"\n },\n {\n  "column_name": "BriefIntroText",\n  "column_description": "公司简介"\n },\n {\n  "column_name": "XGRQ",\n  "column_description": "修改日期"\n },\n {\n  "column_name": "JSID",\n  "column_description": "JSID"\n },\n {\n  "column_name": "ChiName",\n  "column_description": "中文名称"\n },\n {\n  "column_name": "BusinessRegNumber",\n  "column_description": "企业法人营业执照注册号"\n },\n {\n  "column_name": "SecretaryBDTel",\n  "column_description": "董秘电话"\n },\n {\n  "column_name": "SecretaryBDFax",\n  "column_description": "董秘传真"\n },\n {\n  "column_name": "SecretaryBDEmail",\n  "column_description": "董秘电子邮件"\n },\n {\n  "column_name": "SecuAffairsReprTel",\n  "column_description": "证券事务代表电话"\n },\n {\n  "column_name": "SecuAffairsReprFax",\n  "column_description": "证券事务代表传真"\n },\n {\n  "column_name": "SecuAffairsReprEmail",\n  "column_description": "证券事务代表电子邮件"\n },\n {\n  "column_name": "CityCode",\n  "column_description": "地区代码",\n  "注释": "地区代码(CityCode)：与“国家城市代码表（LC_AreaCode）”中的“地区内部编码（AreaInnerCode）”关联，得到城市具体信息。"\n },\n {\n  "column_name": "CDRShareAbbr",\n  "column_description": "CDR证券简称"\n },\n {\n  "column_name": "CDRStockCode",\n  "column_description": "CDR证券代码"\n },\n {\n  "column_name": "ExtendedAbbr",\n  "column_description": "扩位简称"\n },\n {\n  "column_name": "SpecialVoteMark",\n  "column_description": "特殊表决权标识",\n  "注释": "特殊表决权标识（SpecialVoteMark）：在上市时发行人具有表决权差异安排的，其股票或存托凭证的特别标识为“W”；上市后不再具有表决权差异安排的，该特别标识取消，数据值为空。"\n },\n {\n  "column_name": "VIEMark",\n  "column_description": "协议控制架构标识",\n  "注释": "协议控制架构标识（VIEMark）：在上市时发行人具有协议控制架构或者类似特殊安排的，其股票或存托凭证的特别标识为“V”；上市后不再具有相关安排的，该特别标识取消，数据值为空。"\n },\n {\n  "column_name": "RedChipMark",\n  "column_description": "红筹企业标识",\n  "注释": "红筹企业标识（RedChipMark）：发行人属于红筹企业，则数据值=”是“；空值则指无此标识。"\n },\n {\n  "column_name": "RegArea",\n  "column_description": "所属区县",\n  "注释": "所属区县（RegArea）：与“国家城市代码表（LC_AreaCode）”中的“地区内部编码（AreaInnerCode）”关联，得到所属区县具体信息。\\n\\n\\n\\n\\n\\n"\n }\n]\n表格名称:ConstantDB.SecuMain\n描述:库名中文:常量库\n库名英文:ConstantDB\n表英文:SecuMain\n表中文:证券主表\n表描述:本表收录单个证券品种（股票、基金、债券）的代码、简称、上市交易所等基础信息。\n\n字段描述:[\n {\n  "column_name": "ID",\n  "column_description": "ID"\n },\n {\n  "column_name": "InnerCode",\n  "column_description": "证券内部编码"\n },\n {\n  "column_name": "CompanyCode",\n  "column_description": "公司代码",\n  "注释": "公司代码(CompanyCode)：当本表SecuCategory IN (8,13)即基金相关时，对应的基金管理人代码可通过本表InnerCode关联MF_FundArchives.InnerCode，取MF_FundArchives.InvestAdvisorCode"\n },\n {\n  "column_name": "SecuCode",\n  "column_description": "证券代码"\n },\n {\n  "column_name": "ChiName",\n  "column_description": "中文名称"\n },\n {\n  "column_name": "ChiNameAbbr",\n  "column_description": "中文名称缩写"\n },\n {\n  "column_name": "EngName",\n  "column_description": "英文名称"\n },\n {\n  "column_name": "EngNameAbbr",\n  "column_description": "英文名称缩写"\n },\n {\n  "column_name": "SecuAbbr",\n  "column_description": "证券简称"\n },\n {\n  "column_name": "ChiSpelling",\n  "column_description": "拼音证券简称"\n },\n {\n  "column_name": "ExtendedAbbr",\n  "column_description": "扩位简称"\n },\n {\n  "column_name": "ExtendedSpelling",\n  "column_description": "拼音扩位简称"\n },\n {\n  "column_name": "SecuMarket",\n  "column_description": "证券市场",\n  "注释": "证券市场(SecuMarket)与(CT_SystemConst)表中的DM字段关联，令LB = 201 AND DM IN (10,12,13,14,15,16,18,40,49,50,52,54,55,56,65,66,67,68,69,70,71,72,73,75,76,77,78,79,80,81,83,84,85,86,87,88,89,90,93,94,95,96,99,100,101,102,103,104,105,106,107,110,161,162,180,200,202,210,230,240,260,280,310,320,390,400,620,630,631,640,641,650,653,654,655,657,658,659,660,661,662,663,664,666,667,66302,66303,66305)，得到证券市场的具体描述：10-上海期货交易所，12-中国银行间外汇市场，13-大连商品交易所，14-上海黄金交易所，15-郑州商品交易所，16-上海票据交易所，18-北京证券交易所，40-芝加哥商业交易所，49-澳大利亚证券交易所，50-新西兰证券交易所，52-埃及开罗及亚历山大证券交易所，54-阿根廷布宜诺斯艾利斯证券交易所，55-巴西圣保罗证券交易所，56-墨西哥证券交易所，65-印度尼西亚证券交易所，66-泰国证券交易所，67-韩国首尔证券交易所，68-东京证券交易所，69-新加坡证券交易所，70-台湾证券交易所，71-柜台交易市场，72-香港联交所，73-一级市场，75-亚洲其他交易所，76-美国证券交易所，77-美国纳斯达克证券交易所，78-纽约证券交易所，79-美国其他交易市场，80-加拿大多伦多证券交易所，81-三板市场，83-上海证券交易所，84-其他市场，85-伦敦证券交易所，86-法国巴黎证券交易所，87-德国法兰克福证券交易所，88-欧洲其他交易所，89-银行间债券市场，90-深圳证券交易所，93-上海银行间同业拆借市场，94-瑞士证券交易所，95-荷兰阿姆斯特丹证券交易所，96-约翰内斯堡证券交易所，99-东京同业拆借市场，100-美国国债回购市场，101-伦敦银行同业拆借市场，102-香港银行同业拆借市场，103-新加坡银行同业拆借市场，104-中国银行同业拆借市场，105-欧元银行同业拆借市场，106-布鲁塞尔证券交易所，107-雅加达证券交易所，110-以色列特拉维夫证券交易所，161-意大利证券交易所，162-哥本哈根证券交易所，180-挪威奥斯陆证券交易所，200-斯德哥尔摩证券交易所，202-伊斯坦布尔证券交易所，210-印度国家证券交易所，230-奥地利维也纳证券交易所，240-西班牙马德里证券交易所，260-爱尔兰证券交易所，280-菲律宾证券交易所，310-机构间私募产品报价与服务系统，320-俄罗斯莫斯科证券交易所，390-里斯本证券交易所，400-芝加哥期权交易所，620-胡志明市证券交易所，630-沪市代理深市市场，631-沪市代理港交所市场，640-深市代理沪市市场，641-深市代理港交所市场，650-国际外汇市场(晨星)，653-上海环境能源交易所，654-北京绿色交易所，655-天津碳排放权交易中心，657-湖北碳排放权交易中心，658-重庆碳排放权交易中心，659-四川联合环境交易所，660-广州碳排放权交易所，661-海峡股权交易中心，662-深圳排放权交易所，663-欧洲能源交易所，664-全国碳排放权交易，666-布达佩斯证券交易所，667-全国温室气体自愿减排交易市场，66302-韩国ETS，66303-加拿大魁北克Cap-and-Trade(CaT)，66305-美国区域温室气体倡议（RGGI）。"\n },\n {\n  "column_name": "SecuCategory",\n  "column_description": "证券类别",\n  "注释": "证券类别(SecuCategory)与(CT_SystemConst)表中的DM字段关联，令LB = 1177 AND DM IN (1,2,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,23,26,27,28,29,30,31,32,33,35,36,37,38,39,40,41,42,43,44,45,46,47,55,79,80,211)，得到证券类别的具体描述：1-A股，2-B股，4-大盘，5-国债回购，6-国债现货，7-金融债券，8-开放式基金，9-可转换债券，10-其他，11-企业债券，12-企业债券回购，13-投资基金，14-央行票据，15-深市代理沪市股票，16-沪市代理深市股票，17-资产支持证券，18-资产证券化产品，19-买断式回购，20-衍生权证，21-股本权证，23-商业银行定期存款，26-收益增长线，27-新质押式回购，28-地方政府债，29-可交换公司债，30-拆借，31-信用风险缓释工具，32-浮息债计息基准利率，33-定期存款凭证，35-大额存款凭证，36-债券借贷，37-存款类机构质押式回购，38-存款类机构信用拆借，39-现货，40-货币对，41-中国存托凭证，42-协议回购，43-三方回购，44-利率互换品种，45-标准利率互换合约，46-报价回购，47-标准化票据，55-优先股，79-深市代理港交所股票，80-沪市代理港交所股票，211-自贸区债。"\n },\n {\n  "column_name": "ListedDate",\n  "column_description": "上市日期"\n },\n {\n  "column_name": "ListedSector",\n  "column_description": "上市板块",\n  "注释": "上市板块(ListedSector)与(CT_SystemConst)表中的DM字段关联，令LB = 207 AND DM IN (1,2,3,4,5,6,7,8)，得到上市板块的具体描述：1-主板，2-中小企业板，3-三板，4-其他，5-大宗交易系统，6-创业板，7-科创板，8-北交所股票。"\n },\n {\n  "column_name": "ListedState",\n  "column_description": "上市状态",\n  "注释": "上市状态(ListedState)与(CT_SystemConst)表中的DM字段关联，令LB = 1176 AND DM IN (1,3,5,9)，得到上市状态的具体描述：1-上市，3-暂停，5-终止，9-其他。"\n },\n {\n  "column_name": "ISIN",\n  "column_description": "ISIN代码"\n },\n {\n  "column_name": "XGRQ",\n  "column_description": "更新时间"\n },\n {\n  "column_name": "JSID",\n  "column_description": "JSID"\n }\n]\n    \n你本次需要回答的问题串为：\n600872的全称、A股简称、法人、法律顾问、会计师事务所及董秘是？\n该公司实控人是否发生改变？如果发生变化，什么时候变成了谁？是哪国人？是否有永久境外居留权？（回答时间用XXXX-XX-XX）\n在实控人发生变化的当年股权发生了几次转让？\n请在用户的引导下，一个一个完成问题，不要抢答\n    实体匹配数据表信息为：预处理程序通过表格：ConstantDB.SecuMain 查询到以下内容：\n [\n {\n  "InnerCode": 2120,\n  "CompanyCode": 1805,\n  "SecuCode": "600872",\n  "ChiName": "中炬高新技术实业(集团)股份有限公司",\n  "ChiNameAbbr": "中炬高新",\n  "EngName": "Jonjee Hi-Tech Industrial And Commercial Holding Co.,Ltd",\n  "EngNameAbbr": "JONJEE",\n  "SecuAbbr": "中炬高新",\n  "ChiSpelling": "ZJGX"\n }\n] \n,查询尽量使用InnerCode。\n    \n    用户提问中的公司名称，简称等问题，你可以直接回答 `InnerCode` 字段使用格式`InnerCode:xxx` (例如：用户问题A股最好的公司是？ 回答：`InnerCode:123`)\n    你书写的sql必须是一次可以执行完毕的，不要有注释，SQL一般不难，请不要过分复杂化，不要添加多余的过滤条件，\n    注意回答日期格式xxxx年xx月xx日，例如2020年01月01日 xxxx-xx-xx -> 2020-01-01 \n    '}, {'role': 'user', 'content': '\n    请编写sql解决问题：600872的全称、A股简称、法人、法律顾问、会计师事务所及董秘是？\n    '}]
```

逐个回答问题串，并将结果进行拼接

1.生成SQL获取查询结果

2.根据查询结果回答问题

3.若出错进行修正





## Buycabbage-semi-LawGLM

设计方案

### 基于GLM多智能体协同的法律行业问答系统

```shell
cd app.py
ZHIPUAI_API_KEY="your zhipuAI key" python main_glm.py # 执行单个样例
ZHIPUAI_API_KEY="your zhipuAI key" python run.py  # 执行完整问题
```

### 方案概述

本方案提出了一种基于GLM多智能体协同的法律行业问答系统。该系统利用多轮对话机制，通过中枢模型（Planner）进行整体规划，并构建协同链路，逐步调用多个执行模型（Tooler），直至问题得到解决。最终，系统会根据相似的答题模板汇总并形成答案。

系统具备动态调整与优化的能力，能利用多种工具和API解决复杂问题，非常适合处理需要多步骤推理和跨领域知识集成的任务。

### 对话管理

run_conversation_xietong 代表中枢模型（Planner）。该函数启动多智能体协同的对话过程，通过预设的提示和策略引导对话，并在过程中调用不同的工具和API获取所需信息。 run_v2.get_answer_2 代表执行模型（Tooler），负责执行具体步骤中的查询和数据处理任务，并返回查询结果。 run_conversation_until_complete 函数管理整个多轮对话流程，直到问题得到解决或达到最大对话轮数。 run_conversation_tiqu 函数用于从对话结果中提取结构化数据，并将其格式化为 JSON 格式。 run_conversation_psby 函数整合了上述功能，以提供完整的解决方案。

### 工具和API调用

系统能够根据问题内容筛选出合适的工具和API进行数据查询和分析。中枢模型（Planner）确定每一步所需的工具，执行模型（Tooler）则执行相应工具的操作。为了确保执行过程不出错，模型被赋予了一些提示词，如：“如果返回的结果为空或有误，影响下一步骤的调用，请重新指示这一步骤的任务。” 这些提示词有助于建立容错纠错机制，确保智能体之间的有效协作。

### 动态策略增强

中枢模型（Planner）本身就非常智能，大多数情况下能够根据现有的API规划解决方案，选择正确的工具和方法。对于特定类型的问题，例如排序或求和等，我们已编写了高效的专用函数。为了避免重复调用API，我们直接使用这些专用函数，从而提高准确性和效率。为了使模型更可控且高效地解决问题，我们在提示词中根据问题的不同，动态调整参考思路，帮助智能体快速准确地规划解题步骤。

1.在整体模板（/prompt/promp_gh.txt）中加入API使用的技巧，形成通用指导策略； 2.way_string 函数可以调用历史相似问题的解决思路，生成动态指导策略； 3.way_string_2 函数根据问题的不同方面生成动态指导策略。

### 答案总结

为了保证答案的规范性，我们设计了答题模板，中枢模型（Planner）会选择与问题最匹配的模板作为参考。同时，我们增加了提示，如：“请注意，模板仅供参考，如果问题与模板不完全一致，可适当调整模板以更好地回答问题。” 这有助于提高模型对问题总结的泛化能力。

### 方案特色

简洁智能：方案思路简单明了，从问题输入到答案生成，采用一套多轮对话机制，使得模型能够全面把控问题及其解决过程。 高效协同：多个智能体协同工作，实现高效问题解决。 灵活适应：动态策略增强确保系统的灵活性和适应性。 高度可扩展：除了回答问题外，通过适当调整即可实现与用户的交互对话。

### 其他事项

在盲答过程中，我们引入了模型集成的思想来提升回答的质量。当初始模型无法给出有效答案时，我们会让模型再次尝试回答，并且直接调用另一个执行模型来获取答案。随后，我们将这两次的回答与初始答案进行比较，最终由大模型从中挑选出最佳答案作为最终结果。 对于诉状和整合报告这类特定类型的问题，我们采用了专门的智能体来进行解答。由于比赛时间紧迫，这些特定的智能体暂时未能完全融入到我们的多智能体协同方法中。如果后期能够将它们完善并融入到整个系统中，预计还能进一步提升整体的性能和准确性。



### 运行过程

````json
尝试使用方法8回答问题: 保定市天威西路2222号地址对应的省市区县分别是？
<地址>对应的省份是<填充>，城市是<填充>，区县是<填充>。
【可以使用的API】
{'function_name': 'get_company_info', 'description': '根据上市公司名称、公司简称、公司代码查找上市公司信息。通过公司简称查询公司名称', '输出的字段': ['公司名称', '公司简称', '英文名称', '关联证券', '公司代码', '曾用简称', '所属市场', '所属行业', '成立日期', '上市日期', '法人代表', '总经理', '董秘', '邮政编码', '注册地址', '办公地址', '联系电话', '传真', '官方网址', '电子邮箱', '入选指数', '主营业务', '经营范围', '机构简介', '每股面值', '首发价格', '首发募资净额', '首发主承销商']}
{'function_name': 'get_company_register', 'description': '根据公司名称查询工商信息。', '输出的字段': ['登记状态', '统一社会信用代码', '法定代表人', '注册资本', '成立日期', '企业地址', '联系电话', '联系邮箱', '注册号', '组织机构代码', '参保人数', '行业一级', '行业二级', '行业三级', '曾用名', '企业简介', '经营范围']}
{'function_name': 'get_company_register_name', 'description': "根据统一社会信用代码查询公司全称（公司名称）。'统一社会信用代码'如'91370000164102345T','输出的字段':['公司名称']"}
{'function_name': 'get_sub_company_info', 'description': '根据被投资的子公司名称获得投资该公司的母公司、投资比例、投资金额信息。根据子公司名称查询母公司名称;根据公司名称查询被投资了多少钱', '输出的字段': ['关联上市公司全称', '上市公司关系', '上市公司参股比例', '上市公司投资金额']}
{'function_name': 'get_sub_company_info_list', 'description': '根据上市公司（母公司）的名称查询该公司投资的所有子公司信息列表。通过公司名称查询子公司名称', '输出的字段': ['关联上市公司全称', '上市公司关系', '上市公司参股比例', '上市公司投资金额', '公司名称']}
{'function_name': 'get_legal_document', 'description': '根据案号查询裁判文书相关信息,根据案号查询原告律师事务所名称，根据案号查询被告律师事务所名称。案号格式如(2019)川01民初1949号,当查询被申请人时就是查询被告。', '输出的字段': ['关联公司', '原告', '被告', '原告律师事务所', '被告律师事务所', '案由', '涉案金额', '判决结果', '日期'(使用审理日期时注意，这个日期就是审理日期), '文件名', '标题', '文书类型']}
{'function_name': 'get_legal_document_list', 'description': '根据公司名称裁判文书信息，根据公司名称查询案号,涉案金额,原告, 被告, 原告律师事务所, 被告律师事务所, 案由, 判决结果等信息', '输出的字段': ['关联公司', '标题', '案号', '文书类型', '原告', '被告', '原告律师事务所', '被告律师事务所', '案由', '涉案金额', '判决结果', '审理日期', '案件发生年度', '文件名']}
{'function_name': 'get_court_info', 'description': '根据法院名称查找法院名录相关信息。', '输出的字段': ['法院负责人', '成立日期', '法院地址', '法院联系电话', '法院官网']}
{'function_name': 'get_court_code', 'description': '根据法院名称、法院代字、案号查询法院相关信息。根据案号查询法院名称等信息;通过案号查询审理法院名称', '输出的字段': ['法院名称', '行政级别', '法院级别', '法院代字', '区划代码', '级别']}
{'function_name': 'get_lawfirm_info_log', 'description': '通过律师事务所名称查询律师事务所信息，如根据通过律师事务所名称查询律师事务所地址等', '输出的字段': ['律师事务所唯一编码', '律师事务所负责人', '事务所注册资本', '事务所成立日期', '律师事务所地址', '通讯电话', '通讯邮箱', '律所登记机关', '业务量排名', '服务已上市公司', '报告期间所服务上市公司违规事件', '报告期所服务上市公司接受立案调查']}
{'function_name': 'get_address_info', 'description': '根据地址查询对应的省份城市区县信息,地址样式如：上海市闵行区新骏环路138号1幢401室', '输出的字段': ['省份', '城市', '区县']}
{'function_name': 'get_address_code', 'description': '根据省份、城市、区县查询对应的区划代码。', '输出的字段': ['城市区划代码', '区县区划代码']}
{'function_name': 'get_temp_info', 'description': '根据日期、省份、城市查询对应的天气相关信息。', '输出的字段': ['天气', '最高温度', '最低温度', '湿度']}
{'function_name': 'get_legal_abstract', 'description': '根据案号查询对应的法律文档文本摘要。', '输出的字段': ['文本摘要']}
{'function_name': 'get_xzgxf_info', 'description': '根据案号查询对应的限制高消费相关信息。案号格式如(2019)川01民初1949号', '输出的字段': ['限制高消费企业名称', '法定代表人', '申请人', '涉案金额', '执行法院', '立案日期', '限高发布日期']}
{'function_name': 'get_xzgxf_info_list', 'description': '根据企业名称查询对应的所有限制高消费相关信息列表。', '输出的字段': ['案号', '法定代表人', '申请人', '涉案金额', '执行法院', '立案日期', '限高发布日期']}
{'function_name': 'check_company', 'description': '根据公司名称判断是否为上市公司'，'输出的字段': ['是', '否']}
{'function_name': 'func8', 'description': '根据公司名称查询统计某个公司子公司数量及投资总额,根据公司名称查询旗下多少家子公司,投资总额是多少'，'输出的字段': ['子公司数量', '子公司投资总额']}
{'function_name': 'function_11', 'description': '通过公司名称查询的涉案次数、涉案金额，通过公司名称查询某公司作为被起诉人（被告）、原告的涉案次数、涉案金额，及相关案号。'，'输出的字段': ['涉案金额', '涉案次数','相关案号']}
{'function_name': 'get_top_companies_by_capital', 'description': '根据母公司名称和指定的排名类型或特定排名位置，通过公司名称查询特定条件子公司名称、投资金额。'输出的字段': ['投资金额最高的子公司(公司名称)', '最高投资金额']}
{'function_name': 'check_restriction_and_max_amount', 'description': '根据企业名称判断对应的公司是否被限制高消费，并返回涉及的最大金额及相应案号。'，'输出的字段': ['限制高消费企业名称', '案号','最大涉案金额']}
{'function_name': 'calculate_total_amount_and_count_simple', 'description': '根据公司名称查询限制高消费(限高)的总次数以及涉案总金额。'，'输出的字段': ['限高涉案总金额'，'限高总数']}
{'function_name': 'get_highest_legal_document_by_companyname', 'description': '获取指定公司名称的最高或第几高涉案金额的法律文件信息。可以查询最高涉案金额的案号, 文书类型, 原告, 被告, 原告律师事务所, 被告律师事务所, 案由, 涉案金额, 判决结果,审理日期, 案件发生年度等 查询涉案金额最高的案件信息时优先使用此功能'，'输出的字段': ['关联公司', '原告', '被告', '原告律师事务所', '被告律师事务所', '案由', '涉案金额', '判决结果', '日期'(使用审理日期时注意，这个日期就是审理日期), '文件名', '标题', '文书类型']}


小技巧：
公司代码格式为6个数字,样例如300006,如果写成330000116644重叠的你应该给他修正变为300164；案号的格式样例为(2021)辽01民终16020号。
当查询某公司参与的案件有涉案金额的有哪些,涉案金额总和为,被起诉次数等时，应当优先直接调用function_11这个函数。这个函数参数有(company, role='both', year=None, amount_range=None,phase=None),role可以是["defendant"(查询被告、被起诉), "plaintiff"(查询原告), "both"(查询全部涉诉,全部)],当查询被起诉次数时应设置为defendant,不能遗漏,记住要根据问题正确选择role,year默认为None可以设置年度,如year=2019,amount_range指定的金额区间，如[0, 10000]，表示查询涉案金额在该区间内的案件,注意当查询有涉案金额的或者涉案金额不为零条件应当设置[0.0001,1000000000000000],phase为审理阶段，如'民事初审', '民事终审','执行'等，默认为'None',cause特定的案由，如'劳务及劳务者纠纷'、'劳动合同纠纷','合同纠纷','财产损害'等，当不确定是什么纠纷时，可以不提供，则查询全部。;
当公司名称只要三个字或四个字的时候,像'安利股份'、'妙可蓝多'、'中持股份'、'金迪克'等三个、四个的时候，他们代表公司简称，一定只能调用get_company_info,获取公司全称后才能进行后续查询;
当查询涉案金额最高或第几高的案件信息,查询某个公司涉及案件最高或第几高的申请人等，优先使用get_highest_legal_document_by_companyname,如果原告被告都查就不需要设置role;
根据案号查询法院名称,只能使用get_court_code,获取法院名称只有get_court_code这个接口；
查询法院成立日期要调用get_court_info,get_court_info,使用get_court_info获取信息记得需要提供法院名称;
涉案金额为0案号也是有效的，可以用来查询相关法院信息;
获取天气数据时只能使用get_temp_info，在使用get_temp_info查询天气时，注意传入格式，正确格式如{"date": "2020年1月4日", "province": "北京市", "city": "北京市"};
全资子公司上市公司参股比例为100,为了方便设置函数参数可以直接获得某个公司投资过亿的全资子公司get_sub_company_info_list(company_name,only_wholly_owned=True,investment_amount_above=100000000);
当需要获取案件审理日期时，通过案号使用get_legal_document查询获得的日期就是审理日期;
当有些公司名称不太正确，你记得进行简单修正后再进行查询，如陕西建设机械股份有限公公，修正为陕西建设机械股份有限公司；如河南龙马环境产业有有有有限限限限公公公公司司司司，修正为河南龙马环境产业有限公司。
在判断谁是胜诉方谁是败诉方时，特别注意：如果 判决结果 里面包含"驳回"，那么败诉方就是原告，胜诉方就是被告;如果 判决结果 里面包含"限被告"，那么胜诉方就是原告，败诉放就是被告。



我有上面的这些api工具  你可以告诉我怎么分步调用上面的api，解决这个问题吗？
问题：保定市天威西路2222号地址对应的省市区县分别是？>>解题参考：
我们现在开始查询，你分步告诉下一步我需要做什么，我把查询结果告诉你，你再告诉我下一步，你告我的问题要方便函数调用(应当清晰描述告诉我去做什么，应当有'使用'、'查询'等字样，便于我理解)，注意如果我返回的结果为空或者错误影响下一步调用，请重新告诉我这一步需要做什么。
等你全部回答完成，不需要进行下一步调用时，记得提示我：<全部完成，答案如下>,将答案总结以json格式给我。如```json{"全部完成，答案如下": <引用模板填充,如,经查询,>}```,模板：<地址>对应的省份是<填充>，城市是<填充>，区县是<填充>。。还需注意模板供参照，如果问题和模板不完全对应，可以适当调整模板以更好回答问题。
-------------------------第0对话-------------------
好的，我们开始逐步解决这个问题。

### 第一步：查询地址信息
**操作描述**：使用 `get_address_info` 函数查询地址 "保定市天威西路2222号" 对应的省份、城市和区县信息。

**具体操作**：
```python
response = get_address_info("保定市天威西路2222号")
```

**你需要做的**：执行上述代码，并将查询结果告诉我。

请执行这一步并告诉我结果。如果结果为空或错误，请告知我，我会重新指导你这一步的操作。
['get_address_info']
0
CompletionMessage(content=None, role='assistant', tool_calls=[CompletionMessageToolCall(id='call_-9144589554179764151', function=Function(arguments='{"address": "保定市天威西路2222号"}', name='get_address_info'), type='function', index=0)])
-----------123--------------
------------------args-----------------
{"address": "保定市天威西路2222号"}
--------第1次---接口调用查询返回结果---------[{'地址': '保定市天威西路2222号', '省份': '河北省', '城市': '保定市', '区县': '竞秀区'}]
[{'role': 'user', 'content': '好的，我们开始逐步解决这个问题。\n\n### 第一步：查询地址信息\n**操作描述**：使用 `get_address_info` 函数查询地址 "保定市天威西路2222号" 对应的省份、城市和区县信息。\n\n**具体操作**：\n```python\nresponse = get_address_info("保定市天威西路2222号")\n```\n\n**你需要做的**：执行上述代码，并将查询结果告诉我。\n\n请执行这一步并告诉我结果。如果结果为空或错误，请告知我，我会重新指导你这一步的操作。'}, {'role': 'tool', 'content': "[{'地址': '保定市天威西路2222号', '省份': '河北省', '城市': '保定市', '区县': '竞秀区'}]", 'tool_call_id': 'call_-9144589554179764151'}]
0
### 第二步：分析查询结果
**操作描述**：分析上一步查询到的地址信息，提取省份、城市和区县的具体名称。

**具体操作**：
- 从查询结果中提取省份、城市和区县的名称。

**分析结果**：
- 省份：河北省
- 城市：保定市
- 区县：竞秀区

**下一步计划**：根据提取的信息，我们可以进行下一步的操作，比如进一步查询该地区的详细信息或者进行其他相关的操作。

请确认上述分析结果是否正确，然后我们可以继续进行下一步。如果有任何疑问或需要调整的地方，请告诉我。
CompletionMessage(content='### 第二步：分析查询结果\n**操作描述**：分析上一步查询到的地址信息，提取省份、城市和区县的具体名称。\n\n**具体操作**：\n- 从查询结果中提取省份、城市和区县的名称。\n\n**分析结果**：\n- 省份：河北省\n- 城市：保定市\n- 区县：竞秀区\n\n**下一步计划**：根据提取的信息，我们可以进行下一步的操作，比如进一步查询该地区的详细信息或者进行其他相关的操作。\n\n请确认上述分析结果是否正确，然后我们可以继续进行下一步。如果有任何疑问或需要调整的地方，请告诉我。', role='assistant', tool_calls=None)
[[{'地址': '保定市天威西路2222号', '省份': '河北省', '城市': '保定市', '区县': '竞秀区'}]]
很好，查询结果已经成功获取。

### 第二步：提取并整理结果
**操作描述**：从查询结果中提取省份、城市和区县信息，并整理成JSON格式。

**具体操作**：
1. 从结果中提取所需信息：
   ```python
   result = response[0][0]  # 提取第一层列表中的第一个字典
   province = result["省份"]
   city = result["城市"]
   district = result["区县"]
   ```

2. 整理成JSON格式：
   ```json
   {
     "全部完成，答案如下": "经查询，保定市天威西路2222号对应的省份是河北省，城市是保定市，区县是竞秀区。"
   }
   ```

**你需要做的**：确认以上信息无误。

### 最终答案
```json
{
  "全部完成，答案如下": "经查询，保定市天威西路2222号对应的省份是河北省，城市是保定市，区县是竞秀区。"
}
```

<全部完成，答案如下>
Attempt 1: Failed to parse JSON, reason: Extra data: line 4 column 4 (char 74). Retrying...
模型的最终答案是： 很好，查询结果已经成功获取。

### 第二步：提取并整理结果
**操作描述**：从查询结果中提取省份、城市和区县信息，并整理成JSON格式。

**具体操作**：
1. 从结果中提取所需信息：
   ```python
   result = response[0][0]  # 提取第一层列表中的第一个字典
   province = result["省份"]
   city = result["城市"]
   district = result["区县"]
   ```

2. 整理成JSON格式：
   ```json
   {
     "全部完成，答案如下": "经查询，保定市天威西路2222号对应的省份是河北省，城市是保定市，区县是竞秀区。"
   }
   ```

**你需要做的**：确认以上信息无误。

### 最终答案
```json
{
  "全部完成，答案如下": "经查询，保定市天威西路2222号对应的省份是河北省，城市是保定市，区县是竞秀区。"
}
```

<全部完成，答案如下>

进程已结束，退出代码为 0

````



# 优化方向





## 实体提取

### 中间表示（Intermediate Representation）

中间表示（IR）是NL查询和SQL查询之间的桥梁，它是一个结构化但灵活的语法，捕捉NL查询的基本组成部分和关系，而无需SQL的严格语法规则。

- SQL-like 语法语言：将用户查询转换为中间的SQL-like表达式。
- SQL-like 草图结构：构建草图规则，将NL映射到SQL-like框架中。



## 表召回

当前baseline的表召回直接输入全量表描述，过多的无关信息会产生干扰，因此考虑减少无关信息，精炼表描述从而提高表召回

解决方法：对表进一步划分，划分的前提是匹配范围对问题具有完备性，即划分的区间要能够满足问题的范围

如何确定每个问题涉及的表范围

库:表=1:n

表:字段=1:n

表:表=n:n



## SQL语句生成



## 表描述优化

获取表描述之后大模型进一步优化

## 任务分解

大问题拆成小问题，小问题再生成SQL拼接结果

text2agent2sql

参考lawglm



准出条件

### SQL校正策略（SQL Correction Strategies）

- 目的：修正由模型生成的SQL中的语法错误。
- 方法：例如DIN-SQL提出的自我校正模块，通过不同的提示指导模型识别和纠正错误。

https://www.51cto.com/aigc/1851.html









