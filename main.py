import os

import uvicorn
from bakong_khqr import KHQR
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Allow the frontend to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

khqr = KHQR(os.environ.get("KHQR_TOKEN"))


class PaymentRequest(BaseModel):
    amount: float


class VerifyRequest(BaseModel):
    md5: str


@app.get("/")
def read_root():
    return {"status": "success", "message": "KHQR API is running correctly!"}


@app.head("/")
def head_root():
    return {}


@app.post("/api/checkout")
def checkout(req: PaymentRequest):
    try:
        qr_string = khqr.create_qr(
            bank_account="rathana_kongchhun@bkrt",
            merchant_name="KONGCHHUN RATHANA",
            merchant_city="Phnom Penh",
            amount=req.amount,
            currency="KHR",
            store_label="DUC Permission System",
        )
        md5_hash = khqr.generate_md5(qr_string)
        return {"qr": qr_string, "md5": md5_hash}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/verify")
def verify(req: VerifyRequest):
    try:
        payment_status = khqr.check_payment(req.md5)
        return {"status": payment_status}
    except Exception as e:
        error_message = str(e)
        print("ERROR:", error_message)
        if "Cambodia IP" in error_message or "IP may be blocked" in error_message:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Bakong verification requires a Cambodia-based server IP. "
                    "Deploy this API on Cambodia hosting or route only Bakong API "
                    "requests through a Cambodia-based proxy/VPS."
                ),
            )
        raise HTTPException(status_code=500, detail=error_message)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
