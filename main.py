from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(title="Data Bundle Hub API")

# --------------------
# DATABASE (TEMP → CAN MOVE TO SQLITE LATER)
# --------------------
USERS = {}
WALLETS = {}
TRANSACTIONS = []

# --------------------
# MODELS
# --------------------
class UserSignup(BaseModel):
    phone: str
    password: str

class WalletTopUp(BaseModel):
    phone: str
    amount: float

class DataRequest(BaseModel):
    network: str
    bundle_id: str
    phone: str

# --------------------
# DATA BUNDLES
# --------------------
BUNDLES = {
    "mtn": {
        "mtn_500mb": {"price": 5, "size": "500MB"},
        "mtn_1gb": {"price": 10, "size": "1GB"},
        "mtn_2gb": {"price": 18, "size": "2GB"},
    },
    "telecel": {
        "tel_1gb": {"price": 9, "size": "1GB"},
        "tel_3gb": {"price": 25, "size": "3GB"},
    }
}

# --------------------
# HEALTH CHECK
# --------------------
@app.get("/")
def health():
    return {"status": "running"}

# --------------------
# REGISTER
# --------------------
@app.post("/api/v1/register")
def register(user: UserSignup):
    if user.phone in USERS:
        raise HTTPException(status_code=400, detail="User already exists")

    USERS[user.phone] = user.password
    WALLETS[user.phone] = 0.0

    return {"message": "User registered successfully"}

# --------------------
# GET BUNDLES
# --------------------
@app.get("/api/v1/bundles")
def get_bundles():
    return BUNDLES

# --------------------
# WALLET TOPUP
# --------------------
@app.post("/api/v1/wallet/topup")
def wallet_topup(data: WalletTopUp):
    if data.phone not in USERS:
        raise HTTPException(status_code=404, detail="User not found")

    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid amount")

    WALLETS[data.phone] += data.amount

    TRANSACTIONS.append({
        "phone": data.phone,
        "type": "TOPUP",
        "amount": data.amount,
        "time": datetime.utcnow()
    })

    return {
        "message": "Wallet topped up",
        "balance": WALLETS[data.phone]
    }

# --------------------
# BUY BUNDLE
# --------------------
@app.post("/api/v1/buy-bundle")
def buy_bundle(req: DataRequest):
    if req.phone not in USERS:
        raise HTTPException(status_code=404, detail="User not found")

    network = BUNDLES.get(req.network)
    if not network:
        raise HTTPException(status_code=404, detail="Network not found")

    bundle = network.get(req.bundle_id)
    if not bundle:
        raise HTTPException(status_code=404, detail="Bundle not found")

    price = bundle["price"]
    if WALLETS[req.phone] < price:
        raise HTTPException(status_code=400, detail="Insufficient wallet balance")

    WALLETS[req.phone] -= price

    TRANSACTIONS.append({
        "phone": req.phone,
        "type": "BUNDLE_PURCHASE",
        "bundle": req.bundle_id,
        "amount": price,
        "time": datetime.utcnow()
    })

    return {
        "message": "Bundle purchase successful",
        "bundle": bundle,
        "remaining_balance": WALLETS[req.phone]
    }

# --------------------
# TRANSACTION HISTORY
# --------------------
@app.get("/api/v1/transactions/{phone}")
def get_transactions(phone: str):
    return [t for t in TRANSACTIONS if t["phone"] == phone]
