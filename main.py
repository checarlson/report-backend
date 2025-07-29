from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import io
import base64

app = FastAPI()

# ✅ Allow all origins for now — restrict later if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["https://your-app.web.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Load HTML template from /templates folder
env = Environment(loader=FileSystemLoader("templates"))

@app.get("/")
def read_root():
    return {"status": "FastAPI is live", "endpoint": "/generate-report"}

@app.post("/generate-report")
async def generate_report(request: Request):
    # ✅ Load incoming JSON
    data = await request.json()

    # ✅ Pass both 'students' and full 'data' to the template
    template = env.get_template("report_card.html")
    html_content = template.render(
        students=data.get("students", []),
        data=data
    )

    # ✅ Render PDF to memory
    pdf_buffer = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)

    # ✅ Convert PDF to base64 and return in JSON
    base64_pdf = base64.b64encode(pdf_buffer.read()).decode("utf-8")
    return JSONResponse(content={"pdf_base64": base64_pdf})
