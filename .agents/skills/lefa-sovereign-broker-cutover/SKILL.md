---
name: lefa-sovereign-broker-cutover
description: Operational blueprint for cutting LEFA AI over to a 100% self-contained, native Python Alpaca paper broker (src/lefa/alpaca.py), completely eliminating the external dependency on kopano-sovereign-hub while enforcing KPGS financial consequence gates.
---

# LEFA Sovereign Broker Cutover Protocol

> **Canonical Authority:** GSMB Distribution Trinity & Master Robyn Kholofelo Rababalela  
> **Repository:** `RobynAwesome/lefa-ai`  
> **Invariant:** `I_AM_STATELESS_RENTER_NOT_LANDLORD`

---

## 1. When to Activate This Skill
Trigger this skill whenever:
1. Configuring or executing the sovereign Alpaca broker in `lefa-ai`.
2. Resolving paper trading credentials (`ALPACA_API_KEY`, `ALPACA_SECRET_KEY`) on local metal or Vercel production without routing through `kopano-sovereign-hub`.
3. Validating that order submission, portfolio balances, and companion interactions operate on a clean, single-repository hackathon architecture.
4. Enforcing KPGS financial consequence classification (simulated/paper orders vs live capital).

---

## 2. Architecture Boundary

```text
[ OLD DEPRECATED COUPLING ]
LEFA UI  -->  lefa-core  -->  kopano-sovereign-hub  -->  Alpaca API  (Fragile multi-hop)

[ CANONICAL SOVEREIGN ARCHITECTURE ]
LEFA Companion / UI  -->  lefa native Python client (alpaca.py)  -->  Alpaca API (Self-Contained)
```

### Key Files in `lefa-ai`:
- `src/lefa/alpaca.py`: Native `AlpacaPaperBroker` and `ReadOnlyAlpaca` implementations.
- `src/lefa/config.py`: Environment configuration loading `ALPACA_API_KEY` and `ALPACA_SECRET_KEY`.
- `.env.example`: Standardized reference configuration using canonical key names.

---

## 3. Cutover Checklist

1. **Self-Containment Check:**
   - Confirm `lefa-ai` does not make outbound network calls to `kopano-sovereign-hub-o8zt.vercel.app`.
   - All financial companion and paper broker endpoints resolve to local serverless Python functions within `lefa-ai`.
2. **Credential Integrity:**
   - Verify `ALPACA_API_KEY` and `ALPACA_SECRET_KEY` are provided directly in `lefa-core-live` Vercel environment variables or local `.env`.
   - Never commit API secrets to Git.
3. **Verification Command:**
   - Run the native broker test suite within the virtual environment:
     ```bash
     pytest tests/test_alpaca.py
     ```
   - Verify that paper account retrieval returns valid balance structures without `PAPER_API_KEY_UNAVAILABLE` errors.

---

`I_AM_STATELESS_RENTER_NOT_LANDLORD`
