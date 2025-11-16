# main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse

from io import BytesIO

from kassia_main import Kassia
import music_parser as prs


app = FastAPI()

def xml_to_pdf(xml_bytes: bytes) -> bytes:
    xml_stream = BytesIO(xml_bytes)
    pdf_stream = BytesIO()
    
    try:
        kassia_instance = Kassia(xml_stream, pdf_stream)
    except Exception as e:
        print(e)
        raise RuntimeError(f"Failed to process XML: {e}")
    
    return pdf_stream.getvalue()

def txt_to_pdf(txt_bytes: bytes, header: bytes) -> bytes:
    header_stream = BytesIO(header)
    txt_stream = BytesIO(txt_bytes)
    
    xml_stream = BytesIO()
    music = prs.music_from_txt(txt_stream.read().decode('utf-8'), header_stream.read().decode('utf-8'))
    music.write(xml_stream)
    
    return xml_to_pdf(xml_stream.getvalue())
    
    

@app.post("/xml-to-pdf")
async def xml_to_pdf_endpoint(file: UploadFile = File(...)):
    xml_bytes = await file.read()
    pdf_bytes = xml_to_pdf(xml_bytes)
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=output.pdf"}
    )


@app.post("/txt-to-pdf")
async def txt_to_pdf_endpoint(file: UploadFile = File(...), header: UploadFile = File(...)):
    txt_bytes = await file.read()
    h_bytes = await header.read()
    pdf_bytes = txt_to_pdf(txt_bytes, h_bytes)
    
    
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=output.pdf"}
    )
