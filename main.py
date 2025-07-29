import base64
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from fastapi.middleware.cors import CORSMiddleware
import io
from fastapi.responses import JSONResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For testing. Replace with real domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

env = Environment(loader=FileSystemLoader('templates'))

@app.get("/")
def read_root():
    return {"status": "FastAPI is live", "endpoint": "/generate-report"}

""" @app.post("/generate-report")
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
    ) """

@app.post("/generate-report")
async def generate_report(request: Request):
    data = await request.json()
    template = env.get_template('report_card.html')
    # html_content = template.render(data=data)
    html_content = template.render(students=data.get("students", []), data=data)

    
    pdf_buffer = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)

    base64_pdf = base64.b64encode(pdf_buffer.read()).decode('utf-8')

    return JSONResponse(content={"pdf_base64": base64_pdf})
