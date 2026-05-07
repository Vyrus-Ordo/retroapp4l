# 💠 RetroApp 4L — Vyrus Ordo

> **"Retrospectives with Traceability. Zero Noise."**

[![License: MIT](https://img.shields.io/badge/License-MIT-00f2ff.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![Stack: Django + Nuxt](https://img.shields.io/badge/Stack-Django%20%7C%20Nuxt-050505.svg?style=flat-square&logo=django&logoColor=white)](https://retroapp4l.privo.app.br/)
[![PRD: v8.0](https://img.shields.io/badge/PRD-v8.0--MVP-blueviolet.svg?style=flat-square)](docs/RetroApp_4L_PRD_v8.md)

**RetroApp 4L** is not just another board with colorful sticky notes. It is an execution engine for engineering teams using the **4Ls framework (Liked, Learned, Lacked, Longed For)**. Designed for sobriety, speed, and above all, ensuring that last sprint's learnings actually turn into next sprint's actions.

[**Explore the Demo**](https://retroapp4l.privo.app.br/) | [**Technical Specs (PRD)**](docs/RetroApp_4L_PRD_v8.md)

---

## 🏛️ The Philosophy: Bridging the Cycles

Most retrospective tools suffer from "Post-it Inertia"—what is discussed is immediately forgotten. RetroApp 4L solves this through a **Senior-first** approach:

* **Execution Enforcement:** The facilitator is required to review and update the status of Action Items from the previous cycle before starting a new one.
* **Methodological Rigor:** A strict state-machine flow (`Setup` → `Check` → `Write` → `Vote` → `Discuss` → `Close`) ensures no stage is skipped.
* **Zero Friction:** One-click participation via **Guest Access (JWT)**. No sign-up walls for the team, just pure collaboration.
* **Real-time Sovereignty:** Built on WebSockets for instantaneous card syncing and voting, keeping the team in perfect "battle-sync."

---

## 🛠️ Tech Stack & Architecture

Built with a distributed systems mindset, optimized for low latency and high reliability.

* **Frontend:** Nuxt 3 (Vue.js) + Tailwind CSS + Atomic Design principles.
* **Backend:** Django 5.2 + Django REST Framework (Robust ORM & Data Sovereignty).
* **Real-time:** Django Channels + Daphne (ASGI) for persistent WebSocket connections.
* **Async Processing:** Celery + Redis for task queuing and background workers (Beat).
* **Database:** PostgreSQL 16 (Relational integrity for complex action-item tracking).

---

## 🚀 Quick Start

### Via Docker (Recommended)

The fastest way to deploy your command center:

```bash
git clone [https://github.com/vyrusordo/retroapp4l.git](https://github.com/vyrusordo/retroapp4l.git)
cd retroapp4l
docker-compose up --build
```

Access `localhost:8000` and start bringing order to the chaos.

### Development Setup

If you prefer a manual approach for debugging:

1. **Backend:** `cd backend && pip install -r requirements.txt && python manage.py migrate`
2. **Workers:** `celery -A config worker --beat`
3. **Frontend:** `cd frontend && npm install && npm run dev`

---

## 🧬 Domain Structure

```bash
retroapp4l/
├── backend/
│   ├── apps/                 # Domain-driven apps (users, retrospectives, cards, actions)
│   ├── realtime/             # WebSocket consumers and signaling logic
│   ├── config/               # System settings, ASGI, and Celery config
│   └── Dockerfile            # Production-ready containerization
├── docs/                     # Engineering specs & PRDs
└── docker-compose.yml        # Multi-container orchestration
```

---

## 🛰️ Core API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/auth/login/` | JWT Authentication |
| `POST` | `/api/retrospectives/` | Initialize a new 4L session |
| `GET` | `/api/retrospectives/{id}/` | Full state sync for the board |
| `PATCH` | `/api/actions/{id}/` | Update Action Item status (Traceability) |

---

## 🤝 Contribution & Vision

This project is maintained under the **Vyrus Ordo** identity. We value clarity, precision, and intellectual honesty.

1. **Fork** the repository.
2. Follow the **Clean Code** conventions defined in the PRD.
3. Open a **Pull Request** explaining the *trade-offs* of your solution.

---
**Developed by Vyrus Ordo — 2026**
