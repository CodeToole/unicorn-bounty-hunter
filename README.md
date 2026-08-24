# Unicorn Bounty Hunter (UBH) — Official Collective & Studio Platform

![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python)
![FastHTML](https://img.shields.io/badge/Framework-FastHTML-gold)
![Datastar](https://img.shields.io/badge/Reactivity-Datastar_SSE-black)
![Firebase](https://img.shields.io/badge/Database-Firebase_Firestore-FFCA28?logo=firebase)
![GCP Cloud Run](https://img.shields.io/badge/Deployment-Google_Cloud_Run-4285F4?logo=googlecloud)
![Stripe](https://img.shields.io/badge/Payments-Stripe-635BFF?logo=stripe)

Official web platform for **Unicorn Bounty Hunter (UBH)**, an independent music collective, elite recording facility, and producers of the *Rap Funxtion* showcase series.

---

## 🎯 About The Project

This platform serves as the central digital hub for UBH, combining real-time studio scheduling, artist roster publishing, and official release distribution into a single high-performance web application. Built to support both creative operations and client bookings, it delivers a fast, responsive user experience backed by serverless cloud infrastructure.

---

## ⚙️ How It Was Built

The application was engineered using modern Python web standards and hypermedia-driven architecture:

- **FastHTML (Python 3.14)**: Powers the entire core backend and UI rendering pipeline for minimal latency and lightweight server execution.
- **Datastar (Server-Sent Events)**: Handles real-time frontend reactivity, allowing live studio schedule updates and dynamic feed loads without full-page refreshes.
- **Firebase Firestore**: Manages dual-mode data persistence for studio slot availability, artist posts, and subscriber lists.
- **Stripe Hosted Checkout**: Processes secure client transactions directly for studio sessions and broadcast packages.
- **Docker & Google Cloud Run**: Containerized using multi-stage builds (`linux/amd64`) and deployed to Cloud Run for scale-to-zero serverless hosting.
- **Firebase Hosting**: Serves static design assets and acts as the custom SSL proxy for the Cloud Run container.

---

## ✨ Platform Highlights

- **Interactive Studio Scheduling**: Real-time time-lock availability calendar for booking studio recording hours and *Shadow Talk* podcast packages without scheduling overlaps.
- **Dynamic Roster & Media Hub**: Dedicated artist profiles featuring YouTube showcase embeds, journal dispatches, and native social sharing tools.
- **News & Announcements Feed**: Live homepage news carousel featuring updates, release drops, and showcase news.
- **Rap Funxtion Event Showcase**: Event hub designed for streaming cyphers, lineup releases, and live venue announcements.
- **Community List Capture**: Integrated email registration for priority studio bookings, exclusive merch drops, and project releases.
