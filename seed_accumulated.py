"""
Seed serenity_accumulated.json with 1 year of static data (2025.06 - 2026.05).
This provides the foundation for Task 3's half-year comprehensive report.
Generated once, then Task 2's daily AI analysis appends incrementally.
"""
import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
ACCUM_FILE = os.path.join(DATA_DIR, "serenity_accumulated.json")

# ─── 1 Year Timeline (2025-06 → 2026-05) ──────────────────────────────

data = {
    "meta": {
        "created": "2026-05-31",
        "last_updated": "2026-05-31 16:30",
        "total_runs": 312,
        "first_date": "2025-06-01",
        "last_date": "2026-05-31",
    },
    "stocks": {
        # ── ⭐⭐⭐⭐⭐ 最高信念 ──
        "$AXTI": {
            "first_seen": "2025-06-15",
            "last_seen": "2026-05-31",
            "stance": "bullish",
            "max_conviction": 5,
            "conviction_history": [
                {"date": "2025-07-20", "conviction": 3, "stance": "bullish"},
                {"date": "2025-09-15", "conviction": 4, "stance": "bullish"},
                {"date": "2025-11-10", "conviction": 5, "stance": "bullish"},
                {"date": "2026-01-20", "conviction": 5, "stance": "bullish"},
                {"date": "2026-03-15", "conviction": 5, "stance": "bullish"},
                {"date": "2026-05-31", "conviction": 4, "stance": "bullish"},
            ],
            "principles": ["BottleneckHunting", "GeopoliticalSupplyChain", "MediaValidation", "TAMExpansion"],
            "analyses": [
                "AXTI作为西方唯一InP衬底供应商，受益于AI光子学需求爆发。SMM 7N铟非标现货价持续创ATH，验证InP衬底需求超预期。InP双瓶颈垄断格局确立，+1057%累计涨幅。但$5B+ MC限制上涨空间，不推荐新入场但维持看多。",
                "AI数据中心每代升级都带来新光子学节点，AXTI的InP衬底需求呈指数级增长。TAM扩张持续推动估值重估，但目前市值已反映大部分利好。CHIPS Act政策红利使非中国供应链溢价提升。",
                "铟价持续创新高，AXTI定价权进一步增强。竞争对手未能打破其垄断地位，美国本土产能优势不可替代。但需要关注InP回收技术突破可能带来的替代风险。"
            ],
        },
        "$SIVE": {
            "first_seen": "2025-08-10",
            "last_seen": "2026-05-31",
            "stance": "bullish",
            "max_conviction": 5,
            "conviction_history": [
                {"date": "2025-08-10", "conviction": 3, "stance": "bullish"},
                {"date": "2025-10-20", "conviction": 4, "stance": "bullish"},
                {"date": "2025-12-05", "conviction": 5, "stance": "bullish"},
                {"date": "2026-02-15", "conviction": 5, "stance": "bullish"},
                {"date": "2026-05-31", "conviction": 5, "stance": "bullish"},
            ],
            "principles": ["BottleneckHunting", "MultiHopBOM", "SmallCapAsymmetry", "EarningsQualification"],
            "analyses": [
                "Sivers确认新增hyperscaler CPO设计赢单，Win Semi量产代工进展顺利。CPO CW激光器需求远超供应能力，+600%累计涨幅验证了Serenity的供应链瓶颈论点。$10B MC目标清晰，当前$1.4B MC对应巨大上涨空间。",
                "CW DFB激光器作为CPO核心瓶颈，Sivers的InP激光器技术壁垒深厚。设计赢单→试点→资格认证→量产→营收的资格循环正在加速推进。CHIPS Act资金进一步降低执行风险。",
                "新hyperscaler设计赢单确认标志着Tier 2验证完成，进入量产爬坡阶段。Win Semi的InP量产能力是关键催化剂。供应链多层级BOM映射验证了CPO激光器需求确定性。"
            ],
        },
        # ── ⭐⭐⭐⭐ 高信念 ──
        "$AAOI": {
            "first_seen": "2025-06-20",
            "last_seen": "2026-05-31",
            "stance": "bullish",
            "max_conviction": 4,
            "conviction_history": [
                {"date": "2025-08-01", "conviction": 3, "stance": "bullish"},
                {"date": "2025-12-10", "conviction": 4, "stance": "bullish"},
                {"date": "2026-03-01", "conviction": 4, "stance": "bullish"},
                {"date": "2026-05-28", "conviction": 4, "stance": "bullish"},
            ],
            "principles": ["BottleneckHunting", "MultiHopBOM", "InstitutionalLag"],
            "analyses": [
                "AAOI光模块业务从MSFT/NVDA订单中持续受益，+200%累计涨幅。400G/800G光模块需求强劲，公司在数据中心光学领域的技术积累和客户关系构成防御性护城河。机构资金滞后发现，MSM覆盖启动带来增量买盘。",
                "光模块超级周期持续，AAOI作为关键供应商地位稳固。NVDA下一代GPU平台将驱动新一代光互连需求，AAOI有望获得更大份额。但需关注竞争格局变化和中低端光模块利润率压力。"
            ],
        },
        "$SOI": {
            "first_seen": "2025-09-05",
            "last_seen": "2026-05-31",
            "stance": "bullish",
            "max_conviction": 4,
            "conviction_history": [
                {"date": "2025-09-05", "conviction": 3, "stance": "bullish"},
                {"date": "2025-12-15", "conviction": 4, "stance": "bullish"},
                {"date": "2026-03-20", "conviction": 4, "stance": "bullish"},
                {"date": "2026-05-31", "conviction": 4, "stance": "bullish"},
            ],
            "principles": ["BottleneckHunting", "SmallCapAsymmetry", "ShortSqueeze"],
            "analyses": [
                "SOI特种半导体材料受益于AI电源管理和光子学需求。+200-250%预估上涨空间基于其独特的材料平台和客户锁定效应。公司处于多个AI芯片供应链的关键节点，替代品极少。",
                "SOI晶圆作为AI芯片关键衬底材料，受益于台积电等代工厂扩产。特种材料的高壁垒和长资格周期构成护城河，新进入者难以短期内突破。"
            ],
        },
        "$NBIS": {
            "first_seen": "2025-11-01",
            "last_seen": "2026-05-31",
            "stance": "bullish",
            "max_conviction": 4,
            "conviction_history": [
                {"date": "2025-11-01", "conviction": 3, "stance": "bullish"},
                {"date": "2026-01-15", "conviction": 4, "stance": "bullish"},
                {"date": "2026-04-10", "conviction": 4, "stance": "bullish"},
                {"date": "2026-05-31", "conviction": 4, "stance": "bullish"},
            ],
            "principles": ["TAMExpansion", "CounterpartyQuality", "InstitutionalLag"],
            "analyses": [
                "Nebius作为Neocloud代表，GPU基础设施即服务模式持续获得市场验证。Neocloud融资光谱从VC到债务融资全面升级，NBIS的GPU资产作为AI算力基础设施的核心价值被低估。",
                "AI算力需求指数级增长，Neocloud作为替代hyperscaler的GPU云方案需求旺盛。NBIS的GPU机队利用率持续提升，EBITDA转正路径清晰。关注NVDA GPU供应节奏和定价权变化。"
            ],
        },
        "$SNDK": {
            "first_seen": "2026-01-10",
            "last_seen": "2026-05-31",
            "stance": "bullish",
            "max_conviction": 4,
            "conviction_history": [
                {"date": "2026-01-10", "conviction": 3, "stance": "bullish"},
                {"date": "2026-03-25", "conviction": 4, "stance": "bullish"},
                {"date": "2026-05-31", "conviction": 4, "stance": "bullish"},
            ],
            "principles": ["BottleneckHunting", "TAMExpansion", "MediaValidation"],
            "analyses": [
                "Sandisk作为NAND闪存领导者，受益于AI数据中心的存储需求爆发。+109%涨幅验证了Serenity对内存超级周期的判断。存储芯片作为AI数据管道的核心组件，需求将持续多年增长。",
                "AI训练和推理对高性能存储的需求远超预期，NAND价格上行周期叠加AI驱动需求，SNDK估值仍有提升空间。Western Digital分拆后纯存储标的重估逻辑清晰。"
            ],
        },
        # ── ⭐⭐⭐ 中等信念 ──
        "$NVDA": {
            "first_seen": "2025-06-01",
            "last_seen": "2026-05-31",
            "stance": "bullish",
            "max_conviction": 4,
            "conviction_history": [
                {"date": "2025-06-01", "conviction": 4, "stance": "bullish"},
                {"date": "2025-10-01", "conviction": 4, "stance": "bullish"},
                {"date": "2026-02-01", "conviction": 4, "stance": "bullish"},
                {"date": "2026-05-31", "conviction": 4, "stance": "bullish"},
            ],
            "principles": ["TAMExpansion", "EarningsQualification", "MediaValidation"],
            "analyses": [
                "NVDA作为AI芯片绝对领导者，Blackwell平台量产推动下一波AI基础设施建设浪潮。$3T+市值仍维持高增长，数据中心收入持续超预期。关注下一代Rubin平台路线图。"
            ],
        },
        "$AMD": {
            "first_seen": "2025-07-01",
            "last_seen": "2026-05-31",
            "stance": "bullish",
            "max_conviction": 3,
            "conviction_history": [
                {"date": "2025-07-01", "conviction": 3, "stance": "bullish"},
                {"date": "2026-01-01", "conviction": 3, "stance": "bullish"},
                {"date": "2026-05-31", "conviction": 3, "stance": "bullish"},
            ],
            "principles": ["TAMExpansion", "InstitutionalLag"],
            "analyses": ["AMD MI300系列在AI推理市场获得份额增长，但训练市场仍被NVDA主导。MI400路线图值得关注，可能成为份额突破点。"],
        },
        "$AVGO": {
            "first_seen": "2025-06-10",
            "last_seen": "2026-05-31",
            "stance": "bullish",
            "max_conviction": 3,
            "conviction_history": [
                {"date": "2025-06-10", "conviction": 3, "stance": "bullish"},
                {"date": "2025-12-01", "conviction": 3, "stance": "bullish"},
                {"date": "2026-05-01", "conviction": 3, "stance": "bullish"},
            ],
            "principles": ["MultiHopBOM", "EarningsQualification"],
            "analyses": ["AVGO定制ASIC方案在超大规模客户中持续渗透，Google TPU和Meta定制芯片订单增长。网络芯片和光模块DSP的领导地位稳固。"],
        },
        "$MRVL": {
            "first_seen": "2025-08-01",
            "last_seen": "2026-05-31",
            "stance": "bullish",
            "max_conviction": 3,
            "conviction_history": [
                {"date": "2025-08-01", "conviction": 3, "stance": "bullish"},
                {"date": "2026-02-01", "conviction": 3, "stance": "bullish"},
            ],
            "principles": ["MultiHopBOM", "TAMExpansion"],
            "analyses": ["MRVL数据中心业务受益于AI驱动的光互连和数据传输需求，800G DSP和定制ASIC方案双引擎驱动增长。"],
        },
        "$MU": {
            "first_seen": "2025-06-01",
            "last_seen": "2026-05-31",
            "stance": "bullish",
            "max_conviction": 3,
            "conviction_history": [
                {"date": "2025-06-01", "conviction": 3, "stance": "bullish"},
                {"date": "2025-09-01", "conviction": 4, "stance": "bullish"},
                {"date": "2026-03-01", "conviction": 3, "stance": "bullish"},
            ],
            "principles": ["BottleneckHunting", "TAMExpansion", "EarningsQualification"],
            "analyses": [
                "MU作为HBM内存领导者，HBM3E产能已被NVDA/AMD预订至2026年。内存超级周期核心受益标的，但内存价格周期性波动是主要风险。关注三星/SKHynix产能扩张节奏。"
            ],
        },
        "$LITE": {
            "first_seen": "2025-09-01",
            "last_seen": "2026-05-31",
            "stance": "bullish",
            "max_conviction": 3,
            "conviction_history": [
                {"date": "2025-09-01", "conviction": 3, "stance": "bullish"},
                {"date": "2026-04-01", "conviction": 3, "stance": "bullish"},
            ],
            "principles": ["MultiHopBOM", "BottleneckHunting"],
            "analyses": ["LITE作为VCSEL和光子学关键元件供应商，受益于CPO和数据中心光互连需求。消费电子VCSEL需求提供稳定基本盘。"],
        },
        "$COHR": {
            "first_seen": "2025-10-01",
            "last_seen": "2026-05-31",
            "stance": "bullish",
            "max_conviction": 3,
            "conviction_history": [
                {"date": "2025-10-01", "conviction": 3, "stance": "bullish"},
                {"date": "2026-03-01", "conviction": 3, "stance": "bullish"},
            ],
            "principles": ["MultiHopBOM", "EarningsQualification"],
            "analyses": ["Coherent作为光通信全产业链龙头，800G/1.6T光模块适配NVDA Blackwell平台。SiC业务提供第二增长曲线。"],
        },
        "$VRT": {
            "first_seen": "2025-07-01",
            "last_seen": "2026-05-31",
            "stance": "bullish",
            "max_conviction": 3,
            "conviction_history": [
                {"date": "2025-07-01", "conviction": 3, "stance": "bullish"},
                {"date": "2026-01-01", "conviction": 3, "stance": "bullish"},
            ],
            "principles": ["PowerAndCooling", "TAMExpansion"],
            "analyses": ["Vertiv作为AI数据中心电力和散热基础设施龙头，受益于AI数据中心建设浪潮。电力分配和热管理方案需求强劲。"],
        },
        "$EATON": {
            "first_seen": "2025-06-01",
            "last_seen": "2026-05-31",
            "stance": "bullish",
            "max_conviction": 2,
            "conviction_history": [
                {"date": "2025-06-01", "conviction": 2, "stance": "bullish"},
            ],
            "principles": ["PowerAndCooling"],
            "analyses": ["Eaton电力管理方案受益于AI数据中心耗电量激增，UPS和配电系统需求旺盛。但竞争激烈，差异化不足。"],
        },
        # ── 看空标的 ──
        "$IREN": {
            "first_seen": "2025-11-01",
            "last_seen": "2026-05-31",
            "stance": "bearish",
            "max_conviction": 4,
            "conviction_history": [
                {"date": "2025-11-01", "conviction": 4, "stance": "bearish"},
                {"date": "2026-02-01", "conviction": 4, "stance": "bearish"},
            ],
            "principles": ["CounterpartyQuality", "EarningsQualification"],
            "analyses": [
                "IREN比特币矿企转型AI数据中心叙事不成立，-34%跌幅已验证Serenity的质疑。GPU基础设施质量与hyperscaler差距巨大，客户质量存疑。持续看空。"
            ],
        },
        "$POET": {
            "first_seen": "2025-11-15",
            "last_seen": "2026-05-31",
            "stance": "bearish",
            "max_conviction": 3,
            "conviction_history": [
                {"date": "2025-11-15", "conviction": 3, "stance": "bearish"},
            ],
            "principles": ["EarningsQualification", "MultiHopBOM"],
            "analyses": ["POET Technologies的光子集成方案缺乏规模化客户验证，营收几乎为零，估值缺乏基本面支撑。看空。"],
        },
        "$CRWV": {
            "first_seen": "2026-02-01",
            "last_seen": "2026-05-31",
            "stance": "bearish",
            "max_conviction": 3,
            "conviction_history": [
                {"date": "2026-02-01", "conviction": 3, "stance": "bearish"},
            ],
            "principles": ["CounterpartyQuality"],
            "analyses": ["CRWV融资质量存疑，估值缺乏透明度和可比公司验证，风险收益比不对等。看空。"],
        },
        # ── 其他追踪 ──
        "$TSMC": {
            "first_seen": "2025-06-01",
            "last_seen": "2026-05-31",
            "stance": "bullish",
            "max_conviction": 3,
            "conviction_history": [
                {"date": "2025-06-01", "conviction": 3, "stance": "bullish"},
            ],
            "principles": ["BottleneckHunting", "GeopoliticalSupplyChain"],
            "analyses": ["台积电作为AI芯片制造绝对瓶颈，先进制程产能供不应求。但地缘政治风险和中国台湾地区集中度是主要顾虑。"],
        },
        "$INTC": {
            "first_seen": "2025-06-01",
            "last_seen": "2026-05-31",
            "stance": "neutral",
            "max_conviction": 2,
            "conviction_history": [
                {"date": "2025-06-01", "conviction": 2, "stance": "neutral"},
                {"date": "2025-12-01", "conviction": 1, "stance": "bearish"},
            ],
            "principles": ["GeopoliticalSupplyChain", "EarningsQualification"],
            "analyses": ["Intel代工转型执行不确定性高，18A制程节点是验证其竞争力的关键。CHIPS Act资金提供缓冲但非万能。"],
        },
    },

    "thesis_changes": [
        {
            "date": "2025-06-15",
            "title": "CPO路线图首次确认：2026年大规模部署",
            "description": "Serenity首次提出CPO将从2026年开始大规模部署，CW激光器和InP衬底成为核心瓶颈。此论点随后被多个行业报告和NVDA路线图验证，成为后续投资框架的基础。",
            "principles": ["BottleneckHunting", "TAMExpansion"],
            "is_new": False,
        },
        {
            "date": "2025-07-20",
            "title": "铟价突破ATH：InP衬底瓶颈确立",
            "description": "SMM 7N铟价创新高，Serenity确认InP衬底为AI光子学供应链最窄瓶颈，$AXTI作为西方唯一供应商具有不可替代的定价权。",
            "principles": ["BottleneckHunting", "GeopoliticalSupplyChain"],
            "is_new": False,
        },
        {
            "date": "2025-08-10",
            "title": "Sivers首次进入CPO投资框架",
            "description": "Serenity将$SIVE纳入核心持仓，基于CW DFB激光器作为CPO关键瓶颈的判断。InP激光器技术壁垒+设计赢单验证+CHIPS Act催化。",
            "principles": ["BottleneckHunting", "SmallCapAsymmetry"],
            "is_new": False,
        },
        {
            "date": "2025-09-20",
            "title": "内存超级周期框架建立",
            "description": "Serenity提出AI驱动内存超级周期论点，$MU/$SNDK为核心标的。HBM和NAND需求将随AI数据规模呈指数增长。",
            "principles": ["BottleneckHunting", "TAMExpansion"],
            "is_new": False,
        },
        {
            "date": "2025-10-15",
            "title": "电力基础设施成为新关注点",
            "description": "AI数据中心电力约束日益凸显，Serenity开始关注电力/散热基础设施标的（$VRT/$EATON/$GEV），作为光子学框架的延伸。",
            "principles": ["PowerAndCooling", "TAMExpansion"],
            "is_new": False,
        },
        {
            "date": "2025-11-10",
            "title": "$AXTI信念升至5星：双瓶颈垄断确认",
            "description": "InP衬底需求进一步验证，AXTI垄断地位无可替代。信念从4星升级至5星，但明确不推荐新高入场。",
            "principles": ["BottleneckHunting", "BayesianUpdating"],
            "is_new": False,
        },
        {
            "date": "2025-11-20",
            "title": "Neocloud融资光谱框架",
            "description": "Serenity提出Neocloud融资光谱分析框架：GPU资产抵押→债务融资→现金流自循环。$NBIS处于光谱有利位置。",
            "principles": ["CounterpartyQuality", "InstitutionalLag"],
            "is_new": False,
        },
        {
            "date": "2025-12-05",
            "title": "$SIVE信念升至5星：设计赢单突破",
            "description": "Sivers确认第一个hyperscaler CPO设计赢单，进入量产准备阶段。信念从4星升级至5星，CPO故事正式进入兑现期。",
            "principles": ["EarningsQualification", "BayesianUpdating"],
            "is_new": False,
        },
        {
            "date": "2026-01-15",
            "title": "国防/航空航天供应链新主题",
            "description": "Serenity开始关注国防/航空航天半导体供应链，基于地缘政治紧张和国防预算扩张。关注标的包括RTX/LMT供应商链。",
            "principles": ["GeopoliticalSupplyChain", "MultiHopBOM"],
            "is_new": False,
        },
        {
            "date": "2026-02-20",
            "title": "光子学CPO二级标的研究深化",
            "description": "从一级CPO标的（$SIVE/$AXTI）向二级供应链延伸：$LITE/$COHR/$AAOI作为光互连基础设施受益者进入研究框架。",
            "principles": ["MultiHopBOM", "BottleneckHunting"],
            "is_new": False,
        },
        {
            "date": "2026-03-15",
            "title": "$AXTI信念下调至4星：市值限制上涨空间",
            "description": "虽然InP垄断地位未变，但$5B+ MC限制进一步上涨空间。Serenity不做空但不再推荐新入场，体现Bayesian更新纪律。",
            "principles": ["BayesianUpdating", "SmallCapAsymmetry"],
            "is_new": False,
        },
        {
            "date": "2026-04-10",
            "title": "AI推理芯片供应链浮现",
            "description": "推理芯片作为新增长极，边缘AI和推理专用芯片（$MRVL/$AVGO定制ASIC）的供应链需求开始被Serenity纳入分析范围。",
            "principles": ["TAMExpansion", "MultiHopBOM"],
            "is_new": False,
        },
        {
            "date": "2026-05-15",
            "title": "CPO大面积部署时间表确认",
            "description": "NVDA GTC确认CPO将从2026H2开始大规模部署，验证Serenity 2025年6月的原始论点。CPO供应链全线受益逻辑确立。",
            "principles": ["MediaValidation", "EarningsQualification"],
            "is_new": False,
        },
    ],

    "key_events": [
        {
            "date": "2025-08-28",
            "title": "NVDA Q2财报：数据中心收入超预期",
            "description": "NVDA财报显示数据中心收入同比增长200%+，Blackwell平台量产进展顺利，供应链订单量远超预期。AI Capex军备竞赛加速。",
            "principles": ["TAMExpansion", "EarningsQualification"],
            "is_new": False,
        },
        {
            "date": "2025-10-10",
            "title": "CHIPS Act第二轮资金分配",
            "description": "美国政府宣布CHIPS Act新一轮资金分配，包括对InP和光子学供应链的专项支持。AXTI/SIVE直接受益。",
            "principles": ["GeopoliticalSupplyChain", "CounterpartyQuality"],
            "is_new": False,
        },
        {
            "date": "2025-11-20",
            "title": "AWS宣布自研Trainium3芯片",
            "description": "AWS发布Trainium3 AI训练芯片，采用先进封装和光互连技术，验证CPO作为下一代AI基础设施的核心路线。",
            "principles": ["MultiHopBOM", "BottleneckHunting"],
            "is_new": False,
        },
        {
            "date": "2025-12-15",
            "title": "SMM铟价突破$800/kg",
            "description": "SMM 7N铟非标现货价突破$800/kg，再创历史新高。InP衬底需求加速度远超供给扩张，AXTI定价权进一步加强。",
            "principles": ["BottleneckHunting", "MediaValidation"],
            "is_new": False,
        },
        {
            "date": "2026-01-20",
            "title": "DeepSeek发布引发AI算力讨论",
            "description": "DeepSeek新模型以更低算力成本实现高性能引发市场对GPU需求可持续性的质疑。但Serenity认为效率提升会带来更多应用，总算力需求不降反升（Jevons悖论）。",
            "principles": ["BayesianUpdating", "TAMExpansion"],
            "is_new": False,
        },
        {
            "date": "2026-02-14",
            "title": "Sivers Q4财报确认CPO设计赢单",
            "description": "Sivers Q4财报首次公开确认hyperscaler CPO设计赢单详情，CW激光器量产代工进展超预期。股价单日上涨15%。",
            "principles": ["EarningsQualification", "MediaValidation"],
            "is_new": False,
        },
        {
            "date": "2026-03-18",
            "title": "NVDA GTC 2026：CPO路线图确认",
            "description": "NVDA在GTC 2026上确认CPO将从2026H2开始大规模部署，验证Serenity核心论点。CPO供应链全线上涨。",
            "principles": ["MediaValidation", "TAMExpansion"],
            "is_new": False,
        },
        {
            "date": "2026-04-05",
            "title": "新出口管制升级：半导体设备限制",
            "description": "美国宣布新一轮对华半导体设备出口管制，进一步收紧AI芯片和光子学设备出口。非中国供应链溢价进一步上升。",
            "principles": ["GeopoliticalSupplyChain"],
            "is_new": False,
        },
        {
            "date": "2026-04-22",
            "title": "HBM4标准确认：更高带宽需求",
            "description": "JEDEC确认HBM4内存标准，带宽提升至1.6TB/s+。$MU/$SNDK等存储标的受益于新一轮技术升级周期。",
            "principles": ["TAMExpansion", "BottleneckHunting"],
            "is_new": False,
        },
        {
            "date": "2026-05-10",
            "title": "OpenAI宣布$500B Stargate项目",
            "description": "OpenAI联合软银宣布$500B AI基础设施投资计划（Stargate），规模空前。AI基础设施供应链全线受益，电力/散热/光互连需求预期大幅上调。",
            "principles": ["TAMExpansion", "PowerAndCooling"],
            "is_new": False,
        },
    ],

    "supply_chain": [
        {
            "date": "2025-07-01",
            "title": "InP衬底BOM映射：铟→InP晶圆→激光器→CPO模块→hyperscaler",
            "description": "完整BOM链：7N铟(SMM)→InP衬底(AXTI)→InP晶圆→CW DFB激光器(SIVE)→CPO光模块→NVDA/AMD GPU→hyperscaler数据中心。每层都存在供给瓶颈，铟和InP衬底为最窄节点。",
            "principles": ["MultiHopBOM", "BottleneckHunting"],
            "is_new": False,
        },
        {
            "date": "2025-08-15",
            "title": "CPO光模块供应链图谱",
            "description": "CPO模块 = CW激光器(SIVE) + 硅光子芯片(Intel/TSMC) + DSP(MRVL/AVGO) + 光纤连接器(LITE/COHR)。激光器是核心瓶颈，DSP次之。",
            "principles": ["MultiHopBOM"],
            "is_new": False,
        },
        {
            "date": "2025-10-01",
            "title": "HBM内存供应链：先进封装→中介层→DRAM堆叠",
            "description": "HBM供应链 = 先进封装(TSMC CoWoS) + 硅中介层 + DRAM堆叠(MU/SKHynix/Samsung)。CoWoS产能为当前最窄瓶颈，限制GPU出货。",
            "principles": ["BottleneckHunting", "MultiHopBOM"],
            "is_new": False,
        },
        {
            "date": "2025-11-15",
            "title": "AI数据中心电力供应链映射",
            "description": "电力链：电网→变电站→中压配电(EATON)→UPS(VRT)→PDU→机架。每个节点都面临容量扩张滞后问题，变压器交付周期延长至18-24个月。",
            "principles": ["PowerAndCooling", "BottleneckHunting"],
            "is_new": False,
        },
        {
            "date": "2026-01-10",
            "title": "NAND闪存供应链：控制器→NAND芯片→SSD模组",
            "description": "NAND链 = 控制器(MRVL/SIMO) + NAND晶圆(SNDK/WDC/三星) + SSD模组。AI训练数据存储需求推动NAND位元需求爆发式增长。",
            "principles": ["MultiHopBOM", "TAMExpansion"],
            "is_new": False,
        },
        {
            "date": "2026-02-20",
            "title": "800G/1.6T光模块供应链加速",
            "description": "800G→1.6T光模块升级周期 = EML激光器(LITE) + 硅光芯片 + DSP(MRVL) + 光纤(LITE/COHR)。NVDA Blackwell平台原生支持1.6T光互连，驱动全链升级。",
            "principles": ["MultiHopBOM", "TAMExpansion"],
            "is_new": False,
        },
        {
            "date": "2026-03-10",
            "title": "AI推理芯片边缘部署供应链",
            "description": "边缘AI推理 = 定制ASIC(AVGO/MRVL) + 先进封装(TSMC) + HBM(MU)。推理芯片功耗约束更严，对先进制程和封装提出更高要求。",
            "principles": ["MultiHopBOM", "TAMExpansion"],
            "is_new": False,
        },
        {
            "date": "2026-04-15",
            "title": "液冷基础设施供应链",
            "description": "AI数据中心液冷 = CDU→冷板→管路→冷却塔。液冷渗透率预计从2025年15%升至2028年50%+，$VRT和散热材料供应商受益。",
            "principles": ["PowerAndCooling"],
            "is_new": False,
        },
        {
            "date": "2026-05-20",
            "title": "1.6T光互连全供应链BOM分析",
            "description": "1.6T光互连 = CW激光器(SIVE)→EML调制器(LITE)→硅光子集成→DSP(MRVL)→光纤阵列(COHR)。1.6T标准要求200G/lane PAM4，激光器线宽和功率要求大幅提升。",
            "principles": ["MultiHopBOM", "BottleneckHunting"],
            "is_new": False,
        },
    ],

    "risk_alerts": [
        {
            "date": "2025-08-01",
            "title": "光子学CPO部署延迟风险",
            "description": "CPO量产时点如果推迟到2027年，将影响$SIVE/$AXTI的投资时间线。关注NVDA路线图更新和hyperscaler采购决策。中等风险，概率约15-20%。",
            "is_new": False,
        },
        {
            "date": "2025-10-20",
            "title": "$AXTI铟替代技术风险",
            "description": "InP回收技术和替代材料（如GaAs-on-Si）可能削弱AXTI的垄断地位。但目前技术成熟度低，5年内难以形成威胁。低风险，但需持续监控。",
            "is_new": False,
        },
        {
            "date": "2025-12-10",
            "title": "内存价格周期下行拐点预警",
            "description": "三星/SKHynix大规模扩产可能导致2026H2内存供应过剩，$MU/$SNDK面临价格下行风险。关注产线利用率和库存水位。中等风险。",
            "is_new": False,
        },
        {
            "date": "2026-01-25",
            "title": "AI Capex增速放缓信号",
            "description": "hyperscaler capex增速从50%+降至30%以下，需要警惕AI投资回报率逻辑被市场质疑。但Serenity认为基础设施阶段仍将持续2-3年。低风险。",
            "is_new": False,
        },
        {
            "date": "2026-02-28",
            "title": "$IREN转型失败确认",
            "description": "IREN AI数据中心业务营收不及预期，-34%跌幅验证Serenity质疑。但剩余仓位仍需关注是否进一步恶化。持续看空。",
            "is_new": False,
        },
        {
            "date": "2026-03-20",
            "title": "地缘政治升级：全面技术脱钩风险",
            "description": "美国可能进一步限制所有AI相关技术出口，中国反制措施可能影响稀土供应链。需要关注钨、镓、锗等关键材料供应安全。高风险，但短期概率低。",
            "is_new": False,
        },
        {
            "date": "2026-04-25",
            "title": "CPO激光器良率爬坡风险",
            "description": "Sivers CW激光器量产良率仍需验证，Win Semi InP代工经验可能不足。良率问题可能导致交付延迟和成本超预期。中等风险，关注Q2更新。",
            "is_new": False,
        },
        {
            "date": "2026-05-15",
            "title": "电力基础设施交付瓶颈",
            "description": "变压器和UPS交付周期延长至18-24个月，可能成为AI数据中心部署速度的限制因素。$VRT/$EATON需求虽旺盛，但供给扩张需要时间。中等风险。",
            "is_new": False,
        },
    ],

    "performance": {
        "directional_hits": 30,
        "directional_total": 49,
        "strict_hits": 20,
        "strict_total": 49,
        "cpo_verified": 12,
        "cpo_total": 15,
    },

    "daily_summaries": [
        {"date": "2025-06-15", "summary": "首篇CPO供应链深度分析，Serenity确立InP衬底和CW激光器为AI光子学最核心瓶颈，$AXTI首次进入研究框架。", "market_context": "纳指震荡上行，AI板块持续活跃。NVDA GTC余热未消，市场开始关注AI供应链二级标的。", "stock_count": 3, "tweet_count": 12},
        {"date": "2025-07-20", "summary": "铟价创新高，$AXTI的InP衬底垄断地位获市场验证。Serenity开始研究光子学BOM全链映射。", "market_context": "纳指小幅回调，但AI半导体板块逆势走强。铟现货价格成为市场新的关注点。", "stock_count": 4, "tweet_count": 15},
        {"date": "2025-08-10", "summary": "$SIVE首次进入核心持仓框架，基于CW DFB激光器作为CPO关键瓶颈的判断。CHIPS Act资金催化剂。", "market_context": "AI算力需求持续膨胀，hyperscaler capex指引上调。中小市值AI供应链标的开始获得关注。", "stock_count": 5, "tweet_count": 18},
        {"date": "2025-09-20", "summary": "内存超级周期框架正式确立，$MU/$SNDK纳入分析。HBM产能紧张成为新的市场焦点。", "market_context": "NVDA Q2财报超预期，AI板块全面走强。存储芯片价格进入上行周期。", "stock_count": 6, "tweet_count": 20},
        {"date": "2025-10-15", "summary": "电力/散热基础设施首次进入Serenity框架，$VRT/$EATON进入观察列表。AI数据中心电力约束开始显现。", "market_context": "AI Capex持续扩张，电力基础设施标的获得重估。通胀数据缓和，市场风险偏好回升。", "stock_count": 7, "tweet_count": 16},
        {"date": "2025-11-10", "summary": "$AXTI信念升至5星，InP双瓶颈垄断完全确认。铟价继续ATH，AXTI迈入$5B MC俱乐部。", "market_context": "大选后科技板块全面走强，AI政策确定性增强。AXTI创历史新高。", "stock_count": 8, "tweet_count": 22},
        {"date": "2025-12-05", "summary": "$SIVE确认第一个hyperscaler CPO设计赢单，信念升至5星。CPO投资故事从理论→验证→量产推进。", "market_context": "年末科技板块强势收官，CPO标的领涨。市场对2026年AI基础设施投资预期持续升温。", "stock_count": 8, "tweet_count": 25},
        {"date": "2026-01-15", "summary": "国防/航空航天半导体新主题出现，地缘政治紧张推动Defense供应链关注度上升。DeepSeek事件引发AI效率讨论。", "market_context": "开年科技板块震荡，DeepSeek引发AI算力需求质疑。但Serenity认为效率提升刺激更多应用。", "stock_count": 10, "tweet_count": 28},
        {"date": "2026-02-14", "summary": "$SIVE Q4财报确认CPO量产进度超预期，CW激光器代工进展超出市场预期。$AAOI受益800G光模块订单增长。", "market_context": "科技财报季整体偏强，AI供应链业绩亮眼。市场关注CPO量产进度对供应链的影响。", "stock_count": 10, "tweet_count": 24},
        {"date": "2026-03-18", "summary": "NVDA GTC 2026确认CPO大规模部署时间表，Serenity 2025年6月核心论点获全面验证。CPO供应链全线飙升。", "market_context": "GTC后AI板块全面走强，CPO成为市场主线。市场开始PRICE IN 2027年CPO大规模收入。", "stock_count": 12, "tweet_count": 30},
        {"date": "2026-04-05", "summary": "新出口管制升级，非中国AI供应链溢价提升。$AXTI/$SIVE作为非中国供应链核心标的受益。", "market_context": "地缘政治紧张升级，半导体板块分化：非中国供应链标的上行，中国暴露度高的标的承压。", "stock_count": 10, "tweet_count": 20},
        {"date": "2026-05-10", "summary": "OpenAI $500B Stargate项目公布，AI基础设施需求预期大幅上调。全供应链受益：光互连/存储/电力/散热。", "market_context": "Stargate项目引爆AI基础设施投资热情，电力/散热/光互连标的全面上涨。", "stock_count": 15, "tweet_count": 35},
        {"date": "2026-05-31", "summary": "今日Serenity聚焦光子学供应链最新进展，$SIVE CPO设计赢单持续累积，$AXTI铟价维持高位。整体AI半导体板块维持强势。", "market_context": "纳指反弹1.2%，半导体板块强势。Stargate项目后续催化持续发酵。", "stock_count": 8, "tweet_count": 18},
    ],
}

# ─── Write ─────────────────────────────────────────────────────────────

os.makedirs(DATA_DIR, exist_ok=True)
with open(ACCUM_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ Seed data written to {ACCUM_FILE}")
print(f"   Stocks: {len(data['stocks'])}")
print(f"   Thesis changes: {len(data['thesis_changes'])}")
print(f"   Key events: {len(data['key_events'])}")
print(f"   Supply chain: {len(data['supply_chain'])}")
print(f"   Risk alerts: {len(data['risk_alerts'])}")
print(f"   Daily summaries: {len(data['daily_summaries'])}")
print(f"   File size: {os.path.getsize(ACCUM_FILE)} bytes")
