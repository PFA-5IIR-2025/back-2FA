from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
import pyotp
import qrcode
import io

app = FastAPI()

class VerifyRequest(BaseModel):
    secret: str
    code: str

class TOTPResponse(BaseModel):
    secret: str
    url: str

@app.post("/generate")
async def generate_totp():
    # Generate random secret
    secret = pyotp.random_base32()
    
    # Generate TOTP URL
    totp = pyotp.TOTP(secret)
    url = totp.provisioning_uri("username", issuer_name="OCR")
    
    return JSONResponse({
        "secret": secret,
        "url": url
    })

@app.get("/qr/{secret}")
async def get_qr(secret: str):
    try:
        # Generate TOTP URL
        totp = pyotp.TOTP(secret)
        url = totp.provisioning_uri("username", issuer_name="OCR")
        
        # Generate QR code
        qr = qrcode.make(url)
        
        # Save QR code to bytes
        img_byte_array = io.BytesIO()
        qr.save(img_byte_array, format='PNG')
        img_byte_array.seek(0)
        
        return Response(content=img_byte_array.getvalue(), media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/verify")
async def verify_totp(request: VerifyRequest):
    try:
        totp = pyotp.TOTP(request.secret)
        is_valid = totp.verify(request.code, valid_window=1)
        
        return {
            "valid": is_valid
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))