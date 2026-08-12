from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_ROOT / "data" / "raw" / "设备报警处理补充手册.pdf"
FONT_PATH = Path("C:/Windows/Fonts/msyh.ttc")


pdfmetrics.registerFont(TTFont("MicrosoftYaHei", FONT_PATH))

pdf = canvas.Canvas(str(OUTPUT_PATH), pagesize=A4)
pdf.setFont("MicrosoftYaHei", 14)

page_one_lines = [
    "AstraSort AS-200 设备报警处理补充手册",
    "",
    "本文档为虚构设备运维资料，仅用于 OpsAtlas 项目演示。",
    "",
    "一、E101 扫码器通信异常",
    "处理要点：检查扫码器电源、通信线缆和镜面清洁状态。",
    "问题仍未恢复时，应通知维修工程师。",
]

page_two_lines = [
    "AstraSort AS-200 设备报警处理补充手册",
    "",
    "二、E205 输送带电机过热",
    "处理要点：立即停止设备运行，等待电机自然冷却。",
    "检查输送带是否卡滞、负载是否过大，以及散热区域是否被遮挡。",
    "报警重复出现时，应创建维修工单。",
]

# 先画第 1 页
y = 780

for line in page_one_lines:
    pdf.drawString(60, y, line)
    y -= 28

# 结束第 1 页，并新建第 2 页
pdf.showPage()
pdf.setFont("MicrosoftYaHei", 14)

# 再画第 2 页
y = 780

for line in page_two_lines:
    pdf.drawString(60, y, line)
    y -= 28

# 两页全部写完后保存
pdf.save()

print(f"已生成 PDF：{OUTPUT_PATH}")