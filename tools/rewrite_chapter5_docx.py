from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import re

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


SRC_NAME = "project_current-1_蓝本整合修改版.docx"
OUT_NAME = "project_current-1_第五章重排修改版.docx"


def paragraph_text(element) -> str:
    return "".join(t.text or "" for t in element.iter(qn("w:t"))).strip()


def paragraph_style_id(element) -> str | None:
    p_pr = element.find(qn("w:pPr"))
    if p_pr is None:
        return None
    p_style = p_pr.find(qn("w:pStyle"))
    if p_style is None:
        return None
    return p_style.get(qn("w:val"))


def has_drawing(element) -> bool:
    return bool(element.xpath(".//w:drawing"))


def make_paragraph(text: str, style_id: str | None = None) -> OxmlElement:
    p = OxmlElement("w:p")
    p_pr = OxmlElement("w:pPr")
    if style_id:
        p_style = OxmlElement("w:pStyle")
        p_style.set(qn("w:val"), style_id)
        p_pr.append(p_style)
    p.append(p_pr)

    r = OxmlElement("w:r")
    r_pr = OxmlElement("w:rPr")
    r_fonts = OxmlElement("w:rFonts")
    r_fonts.set(qn("w:ascii"), "Times New Roman")
    r_fonts.set(qn("w:hAnsi"), "Times New Roman")
    r_fonts.set(qn("w:eastAsia"), "宋体")
    r_pr.append(r_fonts)
    if style_id is None:
        sz = OxmlElement("w:sz")
        sz.set(qn("w:val"), "24")
        r_pr.append(sz)
        sz_cs = OxmlElement("w:szCs")
        sz_cs.set(qn("w:val"), "24")
        r_pr.append(sz_cs)
    r.append(r_pr)
    t = OxmlElement("w:t")
    t.set(qn("xml:space"), "preserve")
    t.text = text
    r.append(t)
    p.append(r)
    return p


def make_caption(text: str) -> OxmlElement:
    p = make_paragraph(text)
    p_pr = p.find(qn("w:pPr"))
    jc = OxmlElement("w:jc")
    jc.set(qn("w:val"), "center")
    p_pr.append(jc)
    return p


def set_run_latin_font_and_body_size(doc: Document) -> None:
    body_style_names = {"Normal", "Body Text"}
    for para in doc.paragraphs:
        is_body = para.style and para.style.name in body_style_names
        for run in para.runs:
            text = run.text or ""
            if not re.search(r"[A-Za-z]", text):
                continue
            run.font.name = "Times New Roman"
            run._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
            run._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
            if is_body:
                run.font.size = None
                sz = run._element.rPr.find(qn("w:sz"))
                if sz is None:
                    sz = OxmlElement("w:sz")
                    run._element.rPr.append(sz)
                sz.set(qn("w:val"), "24")
                sz_cs = run._element.rPr.find(qn("w:szCs"))
                if sz_cs is None:
                    sz_cs = OxmlElement("w:szCs")
                    run._element.rPr.append(sz_cs)
                sz_cs.set(qn("w:val"), "24")


def find_chapter_bounds(body) -> tuple[OxmlElement, OxmlElement, OxmlElement]:
    start = end = None
    first_subheading = None
    for child in body.iterchildren():
        if child.tag != qn("w:p"):
            continue
        text = paragraph_text(child)
        if text == "系统核心功能实现":
            start = child
        elif start is not None and first_subheading is None and text == "登录认证与权限控制":
            first_subheading = child
        elif start is not None and text == "系统测试":
            end = child
            break
    if start is None or end is None or first_subheading is None:
        raise RuntimeError("未能定位第五章或第六章标题")
    return start, first_subheading, end


def collect_figure_blocks(body, start, end) -> dict[str, tuple[OxmlElement, OxmlElement]]:
    children = list(body.iterchildren())
    s = children.index(start)
    e = children.index(end)
    result: dict[str, tuple[OxmlElement, OxmlElement]] = {}
    for i in range(s, e - 1):
        cur = children[i]
        nxt = children[i + 1]
        if cur.tag == qn("w:p") and nxt.tag == qn("w:p") and has_drawing(cur):
            caption = paragraph_text(nxt)
            if caption:
                result[caption] = (deepcopy(cur), deepcopy(nxt))
    return result


def append_fig(blocks: list[OxmlElement], figures, caption: str, intro: str, figure_no: int) -> None:
    blocks.append(make_paragraph(intro))
    if caption not in figures:
        raise RuntimeError(f"未找到图片：{caption}")
    image_p, _caption_p = figures[caption]
    blocks.append(deepcopy(image_p))
    blocks.append(make_caption(f"图5-{figure_no} {caption}"))


def main() -> None:
    src = Path(SRC_NAME)
    out = Path(OUT_NAME)
    doc = Document(src)
    body = doc.element.body

    start, first_subheading, end = find_chapter_bounds(body)
    figures = collect_figure_blocks(body, start, end)
    h1 = paragraph_style_id(start)
    h2 = paragraph_style_id(first_subheading)

    blocks: list[OxmlElement] = []
    blocks.append(make_paragraph("系统核心功能实现", h1))

    blocks.append(make_paragraph("登录认证与权限控制", h2))
    blocks.append(make_paragraph(
        "登录认证与权限控制模块需要同时兼顾页面体验和接口安全，前端在用户完成登录后会保存 token，并按照角色把用户引导到对应首页；后端通过 JWT 过滤器解析请求身份，再由服务层判断当前业务能否继续执行。这样处理后，一方面能减少用户进入无关页面的情况，另一方面也能把真正的权限边界放到服务端完成校验，从而形成较完整的访问控制链路[20]。"
    ))
    figure_no = 1

    append_fig(blocks, figures, "JWT认证过滤器关键代码",
               "下面的关键代码说明了 JWT 过滤器的认证处理过程，系统会从 Authorization 请求头中取出 token，经过格式检查和有效性校验后，再把用户编号和角色信息写入 Spring Security 上下文。",
               figure_no); figure_no += 1
    blocks.append(make_paragraph(
        "在实际运行中，token 过期、用户主动退出和接口返回未授权状态都需要被统一处理，前端会在响应拦截器中清理本地登录信息并跳转到登录页；对于管理员接口、咨询师处理预约接口等敏感业务，后端不能只相信前端传来的角色，而要根据 token 解析结果再次校验用户身份和数据归属。"
    ))
    append_fig(blocks, figures, "登录认证流程图",
               "登录认证流程图进一步表现了账号校验、JWT 签发、角色路由和业务接口访问之间的关系，其中前端路由负责页面跳转，后端过滤器负责身份确认，两部分共同保证了访问过程的连续性。",
               figure_no); figure_no += 1

    blocks.append(make_paragraph("心理测评与风险分析实现", h2))
    blocks.append(make_paragraph(
        "心理测评模块把量表加载、答案提交、特征解析、模型推理和记录保存串联在一起，用户在页面中完成作答后，前端会把答案 JSON 提交到接口；后端先判断量表是否启用，再把答案转换为模型能够识别的特征变量，随后调用 CatBoost 推理或 Java 回退逻辑，最终把风险概率、风险等级、分析文本和主要影响因素保存到数据库。"
    ))
    append_fig(blocks, figures, "心理测评提交与风险结果保存关键代码",
               "下面的核心代码体现了测评提交后的主要处理步骤，包括量表校验、答案解析、预测器调用和测评记录保存，这些步骤使测评结果既能被用户查看，也能被管理员用于后续风险监测。",
               figure_no); figure_no += 1
    blocks.append(make_paragraph(
        "主要影响因素以 leadingFactors 形式返回给前端，每个因素包含名称、得分、影响度、方向和说明，页面可以把风险项与保护项分开展示；需要说明的是，该贡献度反映的是模型预测中的变量重要性，不能被直接理解为医学诊断结论，因此系统只把它作为辅助参考。"
    ))
    append_fig(blocks, figures, "心理测评与风险分析流程图",
               "心理测评与风险分析流程图说明了从量表选择到风险结果生成的完整过程，流程中既包含前端动态渲染题目的步骤，也包含后端模型推理和记录留存的步骤。",
               figure_no); figure_no += 1

    blocks.append(make_paragraph("预约咨询与在线聊天实现", h2))
    blocks.append(make_paragraph(
        "预约咨询功能是连接普通用户和心理咨询师的关键环节，用户会先浏览咨询师资料，再填写预约时间、咨询方式、咨询时长和问题描述；系统保存预约记录后把状态设置为待确认，咨询师登录后只能处理属于自己的预约申请，待确认状态会被确认或拒绝，已确认预约才会开放后续沟通入口[26-31]。"
    ))
    append_fig(blocks, figures, "预约确认与拒绝状态流转关键代码",
               "以下关键代码说明了预约状态控制的实现要点，系统会先确认预约归属和当前状态，再根据咨询师操作把记录更新为已确认或已拒绝，从而避免已经处理过的预约被重复操作。",
               figure_no); figure_no += 1
    append_fig(blocks, figures, "预约咨询流程图",
               "预约咨询流程图展示了从用户提交申请到咨询师处理结果的状态变化，预约状态、提醒状态和聊天入口会同步变化，使预约业务和在线沟通之间保持一致。",
               figure_no); figure_no += 1
    blocks.append(make_paragraph(
        "在线聊天模块不是简单地保存文本内容，而是会先判断双方是否具有可沟通关系；若双方没有确认过的预约关系，也没有既有消息记录，系统会拒绝发送，在允许发送后还会进行敏感词检测与脱敏处理，并把审核状态一同写入消息记录。"
    ))
    append_fig(blocks, figures, "聊天准入与敏感词处理关键代码",
               "下面的关键代码体现了聊天准入和敏感词处理过程，系统先检查双方关系，再完成消息保存和审核状态标记，这样能把咨询沟通和预约流程有效衔接起来。",
               figure_no); figure_no += 1
    blocks.append(make_paragraph(
        "消息保存后再推送是该模块比较重要的设计，一方面，数据库持久化能保证历史记录可追溯，另一方面，WebSocket 实时推送能提升在线咨询的及时性；当实时连接暂时不可用时，系统仍然保留 REST API 发送和加载历史记录的能力。"
    ))
    append_fig(blocks, figures, "在线聊天功能流程图",
               "在线聊天功能流程图说明了联系人加载、历史消息读取、WebSocket 连接、消息保存和实时推送之间的关系，流程中对连接异常和离线接收也做了处理。",
               figure_no); figure_no += 1

    blocks.append(make_paragraph("后台管理与数据看板实现", h2))
    blocks.append(make_paragraph(
        "后台管理功能主要面向平台运营和风险管理，管理员可以维护用户、咨询师、文章和通知，也能查看测评记录和数据看板；数据看板通过后端统计接口汇总用户数量、咨询师数量、预约数量、测评数量和高风险记录数量，并把风险分布等信息交给前端图表显示。"
    ))
    blocks.append(make_paragraph(
        "看板数据需要注意统计口径的一致性，例如用户数量应按照有效账号统计，预约数量应明确是否包含已取消记录，测评风险分布也应说明按照最新记录还是全部记录计算；虽然毕业设计阶段可以采用相对简单的统计方式，但指标含义需要在论文中说明清楚，这样数据看板才不只是页面装饰，而能具备一定的管理参考价值。"
    ))

    blocks.append(make_paragraph("前端展示", h2))
    blocks.append(make_paragraph(
        "前端展示统一放在本章最后一节进行说明，这样前面的实现章节可以集中解释业务逻辑、状态流转和核心代码，后面的界面截图则集中表现系统最终运行效果。用户端、咨询师端和管理员端的页面分别对应不同角色的工作入口，一方面能体现平台的多角色协同特点，另一方面也能说明 Vue 3、Vue Router、Pinia、Element Plus、Axios 和 ECharts 等前端技术在页面组织中的实际作用[24-25]。"
    ))
    append_fig(blocks, figures, "用户端服务首页界面",
               "用户端首页把心理测评、预约咨询、心理文章和在线沟通放在较醒目的位置，并配合通知信息展示当前用户需要关注的内容，这种布局能够让普通用户进入平台后较快找到常用服务。",
               figure_no); figure_no += 1
    append_fig(blocks, figures, "咨询师端服务首页界面",
               "咨询师端页面围绕预约处理和资料维护展开，咨询师可以查看预约申请、确认或拒绝预约，并在预约确认后进入在线沟通页面，减少了多个功能之间来回切换的成本。",
               figure_no); figure_no += 1
    append_fig(blocks, figures, "管理员平台总览界面",
               "管理员端总览页面主要表现平台运行情况和风险监控结果，统计卡片、风险分布和管理入口集中显示，方便管理员快速了解用户规模、预约情况和测评风险状态。",
               figure_no); figure_no += 1
    append_fig(blocks, figures, "心理测评功能界面",
               "心理测评页面通过动态题目渲染、滑块作答、草稿保存和结果展示来完成用户自助评估，提交后页面会显示风险等级、风险概率、模型名称、分析文本和主要影响因素。",
               figure_no); figure_no += 1
    append_fig(blocks, figures, "在线聊天功能界面",
               "在线聊天页面由联系人列表、消息展示区和消息输入区组成，前端会根据当前会话插入或更新消息，同时在 WebSocket 连接异常时保留接口收发能力，以保证沟通过程的基本可用性。",
               figure_no); figure_no += 1

    children = list(body.iterchildren())
    s = children.index(start)
    e = children.index(end)
    for child in children[s:e]:
        body.remove(child)
    insert_at = list(body.iterchildren()).index(end)
    for offset, block in enumerate(blocks):
        body.insert(insert_at + offset, block)

    set_run_latin_font_and_body_size(doc)
    doc.save(out)
    print(out)


if __name__ == "__main__":
    main()
