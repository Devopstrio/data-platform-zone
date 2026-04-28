import logging
import time
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from pythonjsonlogger import jsonlogger

# Logger setup
logger = logging.getLogger("zone-api")
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

app = FastAPI(title="Data Platform Zone API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"Path: {request.url.path} Duration: {duration:.4f}s Status: {response.status_code}")
    return response

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/zones")
def get_zones():
    return [
        {"id": "zone-us-east-hub", "name": "Global Hub: US East", "cloud": "Azure", "status": "ACTIVE", "workspaces": 45},
        {"id": "zone-eu-west-hub", "name": "Regional Hub: EMEA", "cloud": "AWS", "status": "ACTIVE", "workspaces": 12},
        {"id": "zone-ap-south-spoke", "name": "Domain Spoke: APAC", "cloud": "GCP", "status": "PROVISIONING", "workspaces": 0}
    ]

@app.get("/governance/summary")
def get_governance_summary():
    return {
        "active_policies": 142,
        "compliance_score": 0.984,
        "violations_24h": 0,
        "drift_status": "NONE"
    }

@app.get("/costs/summary")
def get_costs_summary():
    return {
        "monthly_burn": "$142.5K",
        "top_spender": "Azure Finance Spoke",
        "budget_variance": "-2.4%",
        "efficiency_score": 0.91
    }

@app.get("/dashboard/summary")
def get_dashboard_summary():
    return {
        "total_zones": 14,
        "active_workspaces": 156,
        "platform_uptime": "99.994%",
        "security_incidents": 0
    }

@app.post("/zones/create")
def create_zone(blueprint_id: str, region: str):
    logger.info(f"Triggering foundation zone creation for blueprint: {blueprint_id} in region: {region}")
    return {"status": "Provisioning Job Enqueued", "job_id": "job_zone_456"}
