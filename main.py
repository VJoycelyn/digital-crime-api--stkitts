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

   # Trigger mock payment
    payment_response = {
        "payment_url": f"https://sandbox.paymentprovider.com/pay?ref={request.fullName}&amount=10.00"
    }

   
    return {
        "applicationId": "APP-2025-001",
        "status": "Received",
        "message": f"Application for {request.fullName} received successfully."
        "payment_url": payment_response["payment_url"]
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

from payments import router as payments_router
app.include_router(payments_router)

