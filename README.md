## 🏗️ Architecture

Project 1 uses a **two-layer AWS architecture** designed to separate persistent knowledge/data infrastructure from deployable application infrastructure.

This separation allows the AI application to be destroyed and recreated without losing the RAG knowledge base, vector index, policy documents, or business data.

### System Architecture

![Customer Support AI Agent Architecture](architecture-diagram.png)

### Architecture Layers

| Layer | Purpose | Terraform State | Lifecycle |
|---|---|---|---|
| **Foundation / Persistent** | S3 documents, S3 Vectors, Bedrock Knowledge Base, DynamoDB and Bedrock IAM | `terraform/foundation` | Persistent |
| **Application / Deployable** | Lambda AI Agent, API Gateway and Lambda IAM | `terraform/application` | Destroy / Recreate |

### Foundation Layer — Persistent

The Foundation layer contains resources that should survive application deployments and application teardown:

- **Amazon S3** — stores customer-support policy documents
- **Amazon S3 Vectors** — stores vector embeddings
- **Amazon Bedrock Knowledge Base** — RAG retrieval layer
- **Bedrock Data Source** — connects the Knowledge Base to S3
- **Amazon DynamoDB**
  - Customers
  - Orders
  - Shipments
- **IAM** — permissions required by the Bedrock Knowledge Base

The Foundation state is intentionally isolated from the application state.

### Application Layer — Deployable

The Application layer contains resources that can safely be destroyed and recreated:

- **Amazon API Gateway HTTP API**
- **AWS Lambda AI Agent**
- **Lambda execution IAM role**
- **Bedrock model invocation permissions**
- **Knowledge Base retrieval permissions**
- **DynamoDB shipment lookup permissions**
- API Gateway → Lambda integration
- `POST /chat` route
- Lambda invocation permission

### Request Flow

```text
Customer
   │
   ▼
API Gateway
   │
   ▼
Lambda AI Agent
   │
   ├─────────────── Policy / General Question ───────────────┐
   │                                                         ▼
   │                                             Amazon Bedrock
   │                                                         │
   │                                                         ▼
   │                                             Knowledge Base
   │                                                 /         \
   │                                                /           \
   │                                               ▼             ▼
   │                                             S3          S3 Vectors
   │                                          Documents      Vector Index
   │
   └────────────── Shipment Question ────────────────────────►
                                                               │
                                                               ▼
                                                           DynamoDB
                                                           Shipments