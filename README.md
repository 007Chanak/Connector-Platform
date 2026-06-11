# Connector Platform

A multi-tenant ERP integration and migration platform that enables businesses to synchronize, transform, map, and migrate data between different ERP systems through a unified data model.

## Overview

Connector Platform acts as a middleware layer between ERP systems, providing a centralized data model and synchronization engine that allows seamless movement of business data across platforms.

Currently supported systems:

* Xero
* ERPNext

The platform is designed with a multi-tenant architecture, allowing multiple organizations to securely manage their own integrations and data migrations.

---

## Features

### Authentication & Multi-Tenancy

* JWT-based authentication
* User registration and login
* Tenant-aware architecture
* Company-based user grouping
* Secure data isolation between organizations

### Integrations

#### Xero

* OAuth 2.0 authentication
* Automatic tenant association
* Connection status monitoring

#### ERPNext

* API Key & Secret authentication
* Tenant-level integration management
* Connection status monitoring

### Unified Data Model

Data from multiple ERP systems is normalized into a common schema.

Supported entities:

* Customers
* Suppliers
* Items
* Invoices
* Bills
* Sales Orders
* Purchase Orders
* Accounts

### Synchronization

Import data from:

* Xero → Unified Database
* ERPNext → Unified Database

Export data to:

* Unified Database → Xero
* Unified Database → ERPNext

### Dashboard

* Integration status tracking
* Entity management
* Migration center
* Centralized ERP visibility

---

## Architecture

```text
Xero
   │
   ▼
Unified Data Model
   ▲
   │
ERPNext
```

The Unified Data Model acts as an abstraction layer between source and destination ERP systems, reducing dependency on platform-specific schemas.

---

## Tech Stack

### Backend

* FastAPI
* PostgreSQL
* SQLAlchemy
* JWT Authentication
* Xero API
* ERPNext REST API

### Frontend

* React
* Vite
* React Router
* Tailwind CSS

---

## Multi-Tenant Design

Organizations are represented as tenants.

```text
Company A
├── User 1
└── User 2

Company B
└── User 3
```

Users belonging to the same company share:

* Xero integration
* ERPNext integration
* Unified data

Data remains isolated across tenants.

---

## Project Structure

```text
Connector-Platform
│
├── connector-backend
│   ├── app
│   ├── routes
│   ├── services
│   ├── models
│   └── schemas
│
└── connector-frontend
    ├── src
    ├── pages
    ├── components
    └── services
```

---

## Upcoming Features

### AI Mapping Engine

AI-powered schema mapping using LLMs to automatically identify equivalent fields between ERP systems.

Example:

```text
Xero.CustomerName
        ↓
AI Mapping
        ↓
ERPNext.customer_name
```

### Payment Synchronization

Support for payment import, transformation, and migration between ERP systems.

### Migration Automation

One-click migration workflows for:

* Xero → ERPNext
* ERPNext → Xero

---

## Author

Chanak Athmaraman

Built as an ERP Integration & Migration Platform project focused on multi-tenancy, interoperability, and AI-assisted data migration.
