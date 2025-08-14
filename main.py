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

# from fastapi import FastAPI, Request
# from fastapi.responses import JSONResponse
# from fastapi.middleware.cors import CORSMiddleware
# from jinja2 import Environment, FileSystemLoader
# from weasyprint import HTML
# import io
# import base64
# import pprint

# app = FastAPI()

# # ✅ Allow all origins for now — restrict later if needed
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ✅ Load HTML template from /templates folder
# env = Environment(loader=FileSystemLoader("templates"))

# @app.get("/")
# def read_root():
#     return {"status": "FastAPI is live", "endpoint": "/generate-report"}


# @app.post("/generate-report")
# async def generate_report(request: Request):
#     data = await request.json()

#     print("📥 Incoming JSON:")
#     pprint.pprint(data)

#     students = data.get("students", [])
#     zoom = 1.0
#     base64_pdf = None

#     while True:
#         # Inject CSS scale into HTML dynamically
#         scale_css = f"""
#         <style>
#             @page {{
#                 size: A4;
#                 margin: 1cm;
#                 transform: scale({zoom});
#                 transform-origin: top left;
#             }}
#             body {{
#                 zoom: {zoom};
#             }}
#         </style>
#         """

#         template = env.get_template("report_card.html")
#         html_content = scale_css + template.render(students=students, data=data)

#         pdf_buffer = io.BytesIO()
#         HTML(string=html_content).write_pdf(pdf_buffer)
#         pdf_buffer.seek(0)

#         # Read PDF and check page count
#         from PyPDF2 import PdfReader
#         reader = PdfReader(pdf_buffer)
#         page_count = len(reader.pages)

#         if page_count <= 1 or zoom <= 0.5:
#             base64_pdf = base64.b64encode(pdf_buffer.getvalue()).decode("utf-8")
#             break

#         zoom -= 0.05  # Reduce zoom by 5% and retry

#     return JSONResponse(content={"pdf_base64": base64_pdf})

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import io
import base64
import pprint

app = FastAPI()

# ✅ Allow all origins for now (can be restricted later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Load HTML templates
env = Environment(loader=FileSystemLoader("templates"))

@app.get("/")
def read_root():
    return {"status": "FastAPI is live", "endpoint": "/generate-report"}

@app.post("/generate-report")
async def generate_report(request: Request):
    data = await request.json()

    # Debug: log the incoming data
    print("📥 Incoming JSON:")
    pprint.pprint(data)

    students = data.get("students", [])

    # Render template
    template = env.get_template("report_card.html")
    html_content = template.render(students=students, data=data)

    # PDF scaling loop
    zoom = 0.8
    base64_pdf = None
    max_attempts = 10
    attempt = 0

    while attempt < max_attempts:
        attempt += 1

        # Inject CSS scale & margins
        scale_css = f"""
        <style>
            @page {{
                size: A4;
                margin: 1cm; /* ✅ consistent margins */
            }}
            body {{
                zoom: {zoom};
                transform-origin: top left;
            }}
        </style>
        """

        # Merge CSS into HTML
        final_html = html_content.replace("</head>", scale_css + "</head>")

        # Generate PDF
        pdf_buffer = io.BytesIO()
        HTML(string=final_html).write_pdf(pdf_buffer)
        pdf_buffer.seek(0)
        pdf_data = pdf_buffer.read()
        base64_pdf = base64.b64encode(pdf_data).decode("utf-8")

        # ✅ Stop when PDF fits one page (size < ~1MB)
        if len(pdf_data) < 1_000_000:
            break

        # Reduce zoom by 5% and retry
        zoom -= 0.1
        if zoom <= 0.5:  # stop if zoom too small
            break

    return JSONResponse(content={"pdf_base64": base64_pdf})
