from fastapi import FastAPI
from app.database import engine, Base

from app.routes.auth_routes import router as auth_router
from app.routes.test_routes import router as test_router
from app.routes.xero_routes import router as xero_router
from app.routes.erpnext_routes import router as erpnext_router
from app.jobs.sync_jobs import scheduler
from app.models import tenant, user
from app.routes.dashboard_routes import router as dashboard_router
from app.routes.customer_routes import (router as customer_router)
from app.routes.tenant_routes import (router as tenant_router)
from app.routes.invoice_routes import (router as invoice_router)
from app.routes.item_routes import (router as item_router)
from app.routes.integration_routes import (router as integration_router)
from app.routes.mapping_routes import router as mapping_router

from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(test_router)
app.include_router(xero_router)
app.include_router(tenant_router)
app.include_router(erpnext_router)
app.include_router(dashboard_router)
app.include_router(customer_router)
app.include_router(invoice_router)
app.include_router(item_router)
app.include_router(integration_router)
app.include_router(mapping_router)


@app.get("/")
def home():
    return {"message": "Connector Platform Running"}

@app.get("/db-test")
def db_test():
    return {"database": str(engine.url)}