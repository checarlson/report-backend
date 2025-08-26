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
#                 margin: 1cm; /* Correctly sets the page margin */
#             }}
#             body {{
#                 zoom: {zoom};
#                 /*
#                   Setting transform-origin to 'top left' ensures the content
#                   scales inward from the margins, preserving the space.
#                 */
#                 transform-origin: top left;
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



# from fastapi import FastAPI, Request
# from fastapi.responses import JSONResponse
# from fastapi.middleware.cors import CORSMiddleware
# from jinja2 import Environment, FileSystemLoader
# from weasyprint import HTML
# import io
# import base64
# import pprint

# app = FastAPI()

# # ✅ Allow all origins for now (can be restricted later)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # ✅ Load HTML templates
# env = Environment(loader=FileSystemLoader("templates"))

# @app.get("/")
# def read_root():
#     return {"status": "FastAPI is live", "endpoint": "/generate-report"}

# @app.post("/generate-report")
# async def generate_report(request: Request):
#     data = await request.json()

#     # Debug: log the incoming data
#     print("📥 Incoming JSON:")
#     pprint.pprint(data)

#     students = data.get("students", [])

#     # Render template
#     template = env.get_template("report_card.html")
#     html_content = template.render(students=students, data=data)

#     # PDF scaling loop
#     zoom = 0.8
#     base64_pdf = None
#     max_attempts = 10
#     attempt = 0

#     while attempt < max_attempts:
#         attempt += 1

#         # Inject CSS scale & margins
#         scale_css = f"""
#         <style>
#             @page {{
#                 size: A4;
#                 margin: 1cm; /* ✅ consistent margins */
#             }}
#             body {{
#                 zoom: {zoom};
#                 transform-origin: top left;
#             }}
#         </style>
#         """

#         # Merge CSS into HTML
#         final_html = html_content.replace("</head>", scale_css + "</head>")

#         # Generate PDF
#         pdf_buffer = io.BytesIO()
#         HTML(string=final_html).write_pdf(pdf_buffer)
#         pdf_buffer.seek(0)
#         pdf_data = pdf_buffer.read()
#         base64_pdf = base64.b64encode(pdf_data).decode("utf-8")

#         # ✅ Stop when PDF fits one page (size < ~1MB)
#         if len(pdf_data) < 1_000_000:
#             break

#         # Reduce zoom by 5% and retry
#         zoom -= 0.1
#         if zoom <= 0.5:  # stop if zoom too small
#             break

#     return JSONResponse(content={"pdf_base64": base64_pdf})



from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
import io
import base64
import pprint
from PyPDF2 import PdfReader
from translations import translations  # import your dictionary

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

# @app.post("/generate-report")
# async def generate_report(request: Request):
#     data = await request.json()

#     print("📥 Incoming JSON:")
#     pprint.pprint(data)

#     students = data.get("students", [])
#     zoom = 1.0  # Start with no zoom
#     base64_pdf = None

#     while True:
#         # Render the HTML template
#         template = env.get_template("report_card.html")
#         html_content = template.render(students=students, data=data)

#         # Generate a separate CSS with zoom for better control
#         zoom_css = CSS(string=f"""
#             body {{
#                 zoom: {zoom};
#                 transform-origin: top left;
#             }}
#         """)

#         pdf_buffer = io.BytesIO()

#         # Generate the PDF with explicit margins
#         HTML(string=html_content).write_pdf(
#             pdf_buffer,
#             stylesheets=[zoom_css], # Apply the zoom CSS
#             presentational_hints=True,
#             # ✅ SET MARGINS HERE!
#             # The order is: top, right, bottom, left
#             # This is a much more direct way to set margins
#             margin_top='1cm',
#             margin_right='1cm',
#             margin_bottom='1cm',
#             margin_left='1cm',
#         )
#         pdf_buffer.seek(0)

#         # Check page count
#         reader = PdfReader(pdf_buffer)
#         page_count = len(reader.pages)

#         # Success condition: if it fits on one page
#         if page_count <= 1:
#             base64_pdf = base64.b64encode(pdf_buffer.getvalue()).decode("utf-8")
#             break

#         # Failure condition: if zoom is too small
#         if zoom <= 0.5:
#             base64_pdf = base64.b64encode(pdf_buffer.getvalue()).decode("utf-8")
#             print("⚠️ Warning: Content still doesn't fit on one page even with maximum zoom out. PDF generated with multiple pages.")
#             break

#         zoom -= 0.05  # Reduce zoom by 5% and retry

#     return JSONResponse(content={"pdf_base64": base64_pdf})
@app.post("/generate-report")
async def generate_report(request: Request):
    data = await request.json()

    print("📥 Incoming JSON:")
    pprint.pprint(data)

    students = data.get("students", [])
    lang = data.get("lang", "fr")  # default English if not provided
    t = translations.get(lang, translations["fr"])  # fallback

    reportType = data.get("reportType", "third_term")  # default to "third_term"
    template_file = "report_card.html" if reportType == "third_term" else "annual_report_card.html"

    zoom = 1.0
    base64_pdf = None

    while True:
        template = env.get_template(template_file)
        html_content = template.render(students=students, data=data, t=t)

        zoom_css = CSS(string=f"""
            body {{
                zoom: {zoom};
                transform-origin: top left;
            }}
        """)

        pdf_buffer = io.BytesIO()

        HTML(string=html_content).write_pdf(
            pdf_buffer,
            stylesheets=[zoom_css],
            presentational_hints=True,
            margin_top='1cm',
            margin_right='1cm',
            margin_bottom='1cm',
            margin_left='1cm',
        )
        pdf_buffer.seek(0)

        reader = PdfReader(pdf_buffer)
        page_count = len(reader.pages)

        if page_count <= 1:
            base64_pdf = base64.b64encode(pdf_buffer.getvalue()).decode("utf-8")
            break

        if zoom <= 0.5:
            base64_pdf = base64.b64encode(pdf_buffer.getvalue()).decode("utf-8")
            print("⚠️ Still too long, generated multiple pages.")
            break

        zoom -= 0.05

    return JSONResponse(content={"pdf_base64": base64_pdf})






# from fastapi import FastAPI, Request
# from fastapi.responses import JSONResponse
# from fastapi.middleware.cors import CORSMiddleware
# from jinja2 import Environment, FileSystemLoader
# from weasyprint import HTML, CSS
# import io
# import base64
# import pprint
# from PyPDF2 import PdfReader

# app = FastAPI()

# # Allow all origins for now — restrict later if needed
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Load HTML template from /templates folder
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

#     # Step 1: Render PDF once at 100% zoom
#     template = env.get_template("report_card.html")
#     html_content = template.render(students=students, data=data)

#     css_margins = CSS(string="""
#         @page { size: A4; margin: 1cm; }
#         body { zoom: 1; }
#     """)

#     pdf_buffer = io.BytesIO()
#     HTML(string=html_content).write_pdf(pdf_buffer, stylesheets=[css_margins])
#     pdf_buffer.seek(0)

#     # Step 2: Check page count
#     reader = PdfReader(pdf_buffer)
#     page_count = len(reader.pages)

#     # Step 3: If more than 1 page, re-render at 80% zoom
#     if page_count > 1:
#         zoom_css = CSS(string="""
#             @page { size: A4; margin: 1cm; }
#             body { zoom: 0.8; transform-origin: top left; }
#         """)
#         pdf_buffer = io.BytesIO()
#         HTML(string=html_content).write_pdf(pdf_buffer, stylesheets=[zoom_css])
#         pdf_buffer.seek(0)

#     base64_pdf = base64.b64encode(pdf_buffer.read()).decode("utf-8")
#     return JSONResponse(content={"pdf_base64": base64_pdf})
