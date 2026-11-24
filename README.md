# PulseLink — URL Shortener & Analytics API

A lightweight, containerized REST API built with **FastAPI**, **PostgreSQL**, and **Redis**, implementing cache-aside resolution, IP-based rate limiting, and API key authentication.

## Architecture

Client ──► FastAPI (Validation, Auth, Rate Limit)
              ├──► Redis (Cache-Aside Lookup & Sliding Rate Counter)
              └──► PostgreSQL (Persistent Link Storage & Metadata)

## Key Engineering Decisions
- **Cache-Aside Pattern:** Redirect lookups hit Redis first (`TTL 1h`), falling back to PostgreSQL only on cache misses to minimize read latency.
- **Sliding Window Rate Limiting:** Protects public redirect and creation endpoints using atomic Redis `INCR` + `EXPIRE` counters.
- **Layered Structure:** Strict separation between HTTP transport (`api/`), validation (`schemas/`), business logic (`services/`), and persistence (`models/`).

## Quick Start

1. Copy environment variables:
   ```bash
   cp .env.example .env
