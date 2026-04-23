from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bakong_khqr import KHQR

app = FastAPI()

# IMPORTANT: Allow your frontend to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Change "*" to your live frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize with your actual Bakong token
khqr = KHQR("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7ImlkIjoiNmE1YTBhNGQ1OWNkNDA4ZSJ9LCJpYXQiOjE3NzY2NTQ2NTgsImV4cCI6MTc4NDQzMDY1OH0.MFbX-GEJYgIUSdk9y35tNVf6r0dm0BCu7pVuTZlmh-Q")

class PaymentRequest(BaseModel):
    amount: float

class VerifyRequest(BaseModel):
    md5: str

@app.post("/api/checkout")
def checkout(req: PaymentRequest):
    try:
        qr_string = khqr.create_qr(
            bank_account='rathana_kongchhun@bkrt',
            merchant_name='KONGCHHUN RATHANA',
            merchant_city='Phnom Penh',
            amount=req.amount,
            currency='KHR',
            store_label='DUC Permission System'
        )
        md5_hash = khqr.generate_md5(qr_string)
        return {"qr": qr_string, "md5": md5_hash}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/verify")
def verify(req: VerifyRequest):
    try:
        payment_status = khqr.check_payment(req.md5)
        if payment_status != "UNPAID": 
            return {"responseCode": 0, "status": payment_status}
        else:
            return {"responseCode": 1, "status": "UNPAID"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))