from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import io

app = FastAPI()

env = Environment(loader=FileSystemLoader('templates'))

@app.post("/generate-report")
async def generate_report(request: Request):
    data = await request.json()

    template = env.get_template('report_card.html')
    html_content = template.render(data=data)

    pdf_file = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_file)
    pdf_file.seek(0)

    return StreamingResponse(
        pdf_file,
        media_type="application/pdf",
        headers={"Content-Disposition": "inline; filename=class_report.pdf"}
    )
