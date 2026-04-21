from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class CatalogItem:
    code: str
    sun_code: str
    title: str
    category: str
    function: str
    ports: int
    flow_lpm: int
    pressure_bar: int
    cavity: str
    structure: str
    symbol: str
    summary: str
    tags: tuple[str, ...]
    features: tuple[str, ...]
    applications: tuple[str, ...]
    replacement_note: str

    @property
    def flow_bucket(self) -> str:
        if self.flow_lpm < 30:
            return "0-30"
        if self.flow_lpm < 60:
            return "30-60"
        if self.flow_lpm <= 120:
            return "60-120"
        return "120+"

    @property
    def pressure_bucket(self) -> str:
        if self.pressure_bar <= 240:
            return "240"
        if self.pressure_bar <= 350:
            return "350"
        return "420"


CATALOG_ITEMS: tuple[CatalogItem, ...] = (
    CatalogItem(
        code="RPEP-25",
        sun_code="RPEI",
        title="电比例溢流阀 - 无命令时最高压力设定",
        category="电比例阀",
        function="压力控制",
        ports=2,
        flow_lpm=95,
        pressure_bar=350,
        cavity="T-13A",
        structure="电比例 / 溢流 / 常闭",
        symbol="relief",
        summary="适用于需要远程调节压力上限的液压回路，断电或无命令时保持最高压力设定。",
        tags=("电比例", "溢流", "常闭", "压力可调"),
        features=("比例信号调压", "适合泵保护与压力限制", "与 T-13A 插孔方案匹配"),
        applications=("泵站压力保护", "比例压力控制", "试验台"),
        replacement_note="用于对标 SUN RPEI 类电比例溢流阀，选型前需复核线圈、电气接口和压力范围。",
    ),
    CatalogItem(
        code="DTAF-28",
        sun_code="DTAF",
        title="FLeX 系列 2通直动式电磁锥阀换向阀",
        category="电磁控制阀",
        function="方向控制",
        ports=2,
        flow_lpm=28,
        pressure_bar=350,
        cavity="T-8A",
        structure="2通 / 直动式 / 锥阀",
        symbol="directional",
        summary="小流量二通开关控制，适合先导油路、卸荷和紧凑阀块中的开闭控制。",
        tags=("2通", "直动式", "电磁", "FLeX"),
        features=("响应直接", "结构紧凑", "适用于 T-8A 插孔"),
        applications=("先导控制", "卸荷回路", "紧凑阀组"),
        replacement_note="用于对标 SUN DTAF 系列，需确认常开/常闭状态与线圈电压。",
    ),
    CatalogItem(
        code="DTBF-34",
        sun_code="DTBF",
        title="FLeX 系列 2通直动式电磁锥阀换向阀",
        category="电磁控制阀",
        function="方向控制",
        ports=2,
        flow_lpm=34,
        pressure_bar=350,
        cavity="T-162A",
        structure="2通 / 直动式 / 锥阀",
        symbol="directional",
        summary="面向中小流量油路的二通电磁开关控制，可用于旁通、锁止和先导切换。",
        tags=("2通", "直动式", "电磁", "FLeX"),
        features=("中等流量", "锥阀密封", "适用于 T-162A 插孔"),
        applications=("油路切换", "旁通控制", "执行器锁止"),
        replacement_note="用于对标 SUN DTBF 系列，需按实际工况复核压降与通电状态。",
    ),
    CatalogItem(
        code="FDEP-120",
        sun_code="FDEP",
        title="2通直动式电比例压力补偿流量控制阀",
        category="电比例阀",
        function="流量控制",
        ports=2,
        flow_lpm=120,
        pressure_bar=350,
        cavity="T-16A",
        structure="2通 / 压力补偿 / 带逆流单向阀",
        symbol="flow",
        summary="在负载变化时维持相对稳定的设定流量，并允许反向自由流回路设计。",
        tags=("电比例", "压力补偿", "逆流单向阀", "2通"),
        features=("比例流量调节", "压力补偿", "带反向流通能力"),
        applications=("执行器速度控制", "工程机械调速", "自动化油缸"),
        replacement_note="用于对标 SUN FDEP 系列，需确认流量控制方向、插孔和线圈配置。",
    ),
    CatalogItem(
        code="FREL-120",
        sun_code="FREL",
        title="3通全程可调旁路/节流优先流量控制阀",
        category="流量控制阀",
        function="流量控制",
        ports=3,
        flow_lpm=120,
        pressure_bar=350,
        cavity="T-17A",
        structure="3通 / 优先流量 / 旁路节流",
        symbol="priority",
        summary="优先保证主执行机构流量，多余流量旁通，适合需要稳定优先油路的系统。",
        tags=("3通", "优先流量", "旁路", "节流"),
        features=("优先流量稳定", "全程可调", "旁路卸流降低发热"),
        applications=("转向优先", "夹具速度控制", "辅助油路分配"),
        replacement_note="用于对标 SUN FREL 系列，需结合泵流量和优先口需求复核。",
    ),
    CatalogItem(
        code="FREP-120",
        sun_code="FREP",
        title="FLeX Series 3通电比例优先流量控制阀",
        category="电比例阀",
        function="流量控制",
        ports=3,
        flow_lpm=120,
        pressure_bar=350,
        cavity="T-17A",
        structure="3通 / 电比例 / 优先流量",
        symbol="priority",
        summary="通过比例信号控制优先口流量，适合多执行器系统中的动态流量分配。",
        tags=("电比例", "3通", "优先流量", "FLeX"),
        features=("比例优先流量", "旁路口泄流", "适合动态控制"),
        applications=("转向系统", "农业机械", "移动设备"),
        replacement_note="用于对标 SUN FREP 系列，需确认控制信号、阀块空间和散热条件。",
    ),
    CatalogItem(
        code="FNUC-40",
        sun_code="FNUC",
        title="4通3位电比例电磁操作方向阀",
        category="方向阀",
        function="方向控制",
        ports=4,
        flow_lpm=40,
        pressure_bar=250,
        cavity="SC-10-04",
        structure="4通 / 3位 / 共用插孔",
        symbol="spool",
        summary="用于双作用执行器方向与速度控制，适合紧凑共用插孔阀块方案。",
        tags=("4通", "3位", "电比例", "共用插孔"),
        features=("三位方向控制", "比例调节", "共用插孔结构"),
        applications=("双作用油缸", "小型执行器", "比例换向"),
        replacement_note="用于对标 SUN FNUC 系列，需复核中位机能、供电和最大工作压力。",
    ),
    CatalogItem(
        code="FMDF-34",
        sun_code="FMDF",
        title="电比例 3通流量控制阀 - 进口节流",
        category="电比例阀",
        function="流量控制",
        ports=3,
        flow_lpm=34,
        pressure_bar=350,
        cavity="T-11A",
        structure="3通 / 740系列 / 进口节流",
        symbol="flow",
        summary="用于小中流量比例节流控制，适合对执行器入口流量进行精细调节。",
        tags=("电比例", "3通", "进口节流", "740系列"),
        features=("入口节流", "比例调速", "紧凑插孔"),
        applications=("小型油缸调速", "辅助机构", "试验设备"),
        replacement_note="用于对标 SUN FMDF 系列，需确认 740 系列线圈和电控接口。",
    ),
    CatalogItem(
        code="DMBD-15",
        sun_code="DMBD",
        title="FLeX Series 3通电磁操作方向滑阀",
        category="电磁控制阀",
        function="方向控制",
        ports=3,
        flow_lpm=15,
        pressure_bar=210,
        cavity="T-150A",
        structure="3通 / 滑阀 / 低压控制",
        symbol="spool",
        summary="小流量三通滑阀式电磁换向，适合先导、泄压和信号油路。",
        tags=("3通", "滑阀", "电磁", "3000 psi"),
        features=("滑阀换向", "低流量控制", "适合先导回路"),
        applications=("先导油路", "信号切换", "低压控制"),
        replacement_note="用于对标 SUN DMBD 系列，需复核允许内泄和中位状态。",
    ),
    CatalogItem(
        code="CBCA-60",
        sun_code="CBCA",
        title="3通先导开启平衡阀",
        category="负载保持阀",
        function="负载保持",
        ports=3,
        flow_lpm=60,
        pressure_bar=350,
        cavity="T-11A",
        structure="3通 / 平衡阀 / 先导开启",
        symbol="counterbalance",
        summary="用于控制负载下降、防止失速和管路破裂后的非预期运动。",
        tags=("负载保持", "3通", "先导开启", "平衡阀"),
        features=("负载保持", "防失速下降", "适用于双作用执行器"),
        applications=("起重机构", "高空平台", "夹紧油缸"),
        replacement_note="用于对标 SUN CBCA 类平衡阀，需按负载压力、先导比和背压详细计算。",
    ),
    CatalogItem(
        code="CXJA-610",
        sun_code="CXJA",
        title="2通鼻端到侧面自由流单向阀",
        category="方向阀",
        function="单向控制",
        ports=2,
        flow_lpm=610,
        pressure_bar=350,
        cavity="T-18A",
        structure="2通 / 单向阀 / 高流量",
        symbol="check",
        summary="大流量单向控制，适用于需要低泄漏和低压降的旁路或补油回路。",
        tags=("2通", "单向阀", "高流量", "低泄漏"),
        features=("大通流能力", "低泄漏", "鼻端至侧面自由流"),
        applications=("补油回路", "旁路保护", "大流量单向隔离"),
        replacement_note="用于对标 SUN CXJA 系列，需确认流向、插孔和密封材料。",
    ),
    CatalogItem(
        code="RDDA-80",
        sun_code="RDDA",
        title="2通直动式溢流阀",
        category="压力控制阀",
        function="压力控制",
        ports=2,
        flow_lpm=80,
        pressure_bar=350,
        cavity="T-10A",
        structure="2通 / 直动式 / 溢流",
        symbol="relief",
        summary="基础压力限制元件，用于保护泵、执行器和阀块支路免受过压冲击。",
        tags=("2通", "直动式", "溢流", "压力限制"),
        features=("结构直接", "压力设定清晰", "适合作为支路保护"),
        applications=("泵出口保护", "支路限压", "夹具保压"),
        replacement_note="用于对标 SUN RDDA 系列，需复核设定范围、调节方式和最大流量。",
    ),
)


FLOW_BUCKET_LABELS = {
    "0-30": "0-30 L/min",
    "30-60": "30-60 L/min",
    "60-120": "60-120 L/min",
    "120+": "120 L/min 以上",
}

PRESSURE_BUCKET_LABELS = {
    "240": "240 bar 以下",
    "350": "350 bar",
    "420": "420 bar",
}


def all_catalog_items() -> tuple[CatalogItem, ...]:
    return CATALOG_ITEMS


def get_catalog_item(code: str) -> CatalogItem | None:
    normalized = code.strip().upper()
    return next((item for item in CATALOG_ITEMS if item.code == normalized), None)


def _contains_any(values: Iterable[str], needle: str) -> bool:
    target = needle.lower()
    return any(target in value.lower() for value in values)


def filter_catalog(args) -> tuple[list[CatalogItem], dict[str, list[str]], str]:
    selected = {
        "category": [value for value in args.getlist("category") if value],
        "function": [value for value in args.getlist("function") if value],
        "ports": [value for value in args.getlist("ports") if value],
        "cavity": [value for value in args.getlist("cavity") if value],
        "flow": [value for value in args.getlist("flow") if value],
        "pressure": [value for value in args.getlist("pressure") if value],
        "tag": [value for value in args.getlist("tag") if value],
    }
    query = args.get("q", "").strip()
    sort = args.get("sort", "default")

    items = list(CATALOG_ITEMS)
    if query:
        items = [
            item
            for item in items
            if query.lower() in " ".join(
                (
                    item.code,
                    item.sun_code,
                    item.title,
                    item.category,
                    item.function,
                    item.cavity,
                    item.summary,
                    " ".join(item.tags),
                )
            ).lower()
        ]

    if selected["category"]:
        items = [item for item in items if item.category in selected["category"]]
    if selected["function"]:
        items = [item for item in items if item.function in selected["function"]]
    if selected["ports"]:
        items = [item for item in items if str(item.ports) in selected["ports"]]
    if selected["cavity"]:
        items = [item for item in items if item.cavity in selected["cavity"]]
    if selected["flow"]:
        items = [item for item in items if item.flow_bucket in selected["flow"]]
    if selected["pressure"]:
        items = [item for item in items if item.pressure_bucket in selected["pressure"]]
    if selected["tag"]:
        items = [item for item in items if any(tag in item.tags for tag in selected["tag"])]

    if sort == "model":
        items.sort(key=lambda item: item.code)
    elif sort == "flow":
        items.sort(key=lambda item: item.flow_lpm, reverse=True)
    elif sort == "pressure":
        items.sort(key=lambda item: item.pressure_bar, reverse=True)
    elif sort == "cavity":
        items.sort(key=lambda item: item.cavity)

    return items, selected, query


def facet_values() -> dict[str, list[str]]:
    items = CATALOG_ITEMS
    tags = sorted({tag for item in items for tag in item.tags})
    return {
        "category": sorted({item.category for item in items}),
        "function": sorted({item.function for item in items}),
        "ports": [str(value) for value in sorted({item.ports for item in items})],
        "cavity": sorted({item.cavity for item in items}),
        "flow": list(FLOW_BUCKET_LABELS.keys()),
        "pressure": list(PRESSURE_BUCKET_LABELS.keys()),
        "tag": tags[:16],
    }


def selected_label(group: str, value: str) -> str:
    if group == "flow":
        return FLOW_BUCKET_LABELS.get(value, value)
    if group == "pressure":
        return PRESSURE_BUCKET_LABELS.get(value, value)
    if group == "ports":
        return f"{value} 通"
    return value
