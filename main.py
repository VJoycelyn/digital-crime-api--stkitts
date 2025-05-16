from payments import PaymentRequest, initiate_payment


from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for all origins (dev mode)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecordRequest(BaseModel):
    fullName: str = Field(..., min_length=3)
    passportNumber: str = Field(..., pattern="^K\\d{8}$")
    dateOfBirth: str
    purpose: str

    def validate_date(self):
        try:
            datetime.strptime(self.dateOfBirth, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

@app.post("/records/apply")
async def apply_for_record(request: RecordRequest):
    request.validate_date()

   # Simulate payment URL generation
    payment_url: f"https://sandbox.paymentprovider.com/pay?ref={request.fullName}&amount=10.00"
    
    return {
        "applicationId": "APP-2025-001",
        "status": "Received",
        "message": f"Application for {request.fullName} received successfully.",
        "payment_url": payment_url
    }

@app.post("/identity/upload-id")
async def upload_id(passportNumber: str, file: UploadFile = File(...)):
    return {
        "passportNumber": passportNumber,
        "filename": file.filename,
        "content_type": file.content_type,
        "message": "File uploaded successfully (simulation)."
    }
@app.get("/")
def read_root():
    return {"message": "Welcome to the Digital Crime Management System API"}
from fpdf import FPDF
from fastapi.responses import FileResponse
import datetime

@app.post("/generate-certificate")
def generate_certificate(fullName: str, passportNumber: str, dateOfBirth: str, purpose: str):
    record_status = "No Criminal Record Found"
    digital_signature = "GovStack-DCRS-Signature-Verified"
    issue_date = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"{passportNumber}_Certificate.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Criminal Record Certificate", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)

    pdf.cell(200, 10, txt=f"Applicant Name: {fullName}", ln=True)
    pdf.cell(200, 10, txt=f"Passport Number: {passportNumber}", ln=True)
    pdf.cell(200, 10, txt=f"Date of Birth: {dateOfBirth}", ln=True)
    pdf.cell(200, 10, txt=f"Purpose: {purpose}", ln=True)
    pdf.cell(200, 10, txt=f"Issue Date: {issue_date}", ln=True)
    pdf.cell(200, 10, txt=f"Record Status: {record_status}", ln=True)
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt="This certificate is issued as part of the Digital Criminal Record System (GovStack compliant). It verifies that the above-named applicant does not have a criminal record registered with the National Law Enforcement Agency.")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Digital Signature: {digital_signature}", ln=True)

    pdf.output(filename)
    return FileResponse(path=filename, media_type='application/pdf', filename=filename)

from payments import router as payments_router
app.include_router(payments_router)

