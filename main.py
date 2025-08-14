""" from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import io
import base64
import pprint  # For pretty-printing JSON in logs

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
    data = await request.json()

    # ✅ Print to logs
    print("📥 Incoming JSON:")
    pprint.pprint(data)

    students = data.get("students", []) #[:3] # Limit to first 1 students

    template = env.get_template("report_card.html")
    html_content = template.render(
        students=students,
        data=data
    )

    pdf_buffer = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_buffer)
    pdf_buffer.seek(0)
    base64_pdf = base64.b64encode(pdf_buffer.read()).decode("utf-8")

    return JSONResponse(content={"pdf_base64": base64_pdf})


 """

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import io
import base64
import pprint

app = FastAPI()

# ✅ Allow all origins for now — restrict later if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    data = await request.json()

    print("📥 Incoming JSON:")
    pprint.pprint(data)

    students = data.get("students", [])
    zoom = 1.0
    base64_pdf = None

    while True:
        # Inject CSS scale into HTML dynamically
        scale_css = f"""
        <style>
            @page {{
                size: A4;
                margin: 0.5cm;
                transform: scale({zoom});
                transform-origin: top left;
            }}
            body {{
                zoom: {zoom};
            }}
        </style>
        """

        template = env.get_template("report_card.html")
        html_content = scale_css + template.render(students=students, data=data)

        pdf_buffer = io.BytesIO()
        HTML(string=html_content).write_pdf(pdf_buffer)
        pdf_buffer.seek(0)

        # Read PDF and check page count
        from PyPDF2 import PdfReader
        reader = PdfReader(pdf_buffer)
        page_count = len(reader.pages)

        if page_count <= 1 or zoom <= 0.5:
            base64_pdf = base64.b64encode(pdf_buffer.getvalue()).decode("utf-8")
            break

        zoom -= 0.05  # Reduce zoom by 5% and retry

    return JSONResponse(content={"pdf_base64": base64_pdf})
