# bet-ocr-app

## Overview

A FastAPI-based OCR application for processing sports betting slips. The system extracts text from uploaded betslip screenshots using Tesseract OCR, parses betting information (stakes, odds, results), calculates profits, and tracks performance statistics across different betting sets. Features role-based access control with admin and employee roles, where admins can manage users and sets while employees can upload betting slips.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Framework
- **FastAPI** with Python for REST API endpoints
- **SQLAlchemy 2.0** with Alembic for database ORM and migrations
- **PostgreSQL** database for persistent storage
- **Pydantic** for request/response validation and settings management

### Authentication & Authorization
- **JWT tokens** for stateless authentication using PyJWT
- **bcrypt password hashing** via passlib for secure credential storage
- **Role-based access control** with two roles: admin (full access) and employee (upload only)
- **Bearer token authentication** with FastAPI security utilities

### OCR Processing Pipeline
- **Tesseract OCR engine** for text extraction from uploaded images
- **OpenCV preprocessing** with adaptive thresholding and bilateral filtering
- **Modular parser system** with bookmaker-specific parsing logic
- **Common regex patterns** for extracting betting data (stakes, odds, results)

### File Management
- **Secure file uploads** with UUID-based filename generation
- **Local file storage** in configurable upload directory
- **Image preprocessing** for improved OCR accuracy

### Database Schema
- **Users table** with role-based permissions and authentication data
- **Bet sets table** for organizing betting campaigns
- **Bookmakers table** for supported betting platforms
- **Bets table** with comprehensive betting data, OCR results, and profit calculations

### Profit Calculation Engine
- **Multi-bookmaker support** with different calculation logic
- **Betfair lay betting** with commission handling
- **Cashout scenarios** with profit/loss calculations
- **Commission rates** configurable per bookmaker

### API Structure
- **Authentication endpoints** for login and token management
- **Admin endpoints** for user and set management
- **Bet upload endpoints** with OCR processing
- **Statistics endpoints** for performance tracking
- **File serving endpoints** for uploaded images

## External Dependencies

### Core Services
- **PostgreSQL database** (recommended: Neon for free hosting)
- **Tesseract OCR** system binary required on host

### Python Libraries
- **FastAPI ecosystem**: uvicorn, python-multipart for web framework
- **Database**: SQLAlchemy, Alembic, psycopg2-binary for PostgreSQL integration
- **OCR**: pytesseract, opencv-python-headless, pillow, numpy for image processing
- **Security**: passlib with bcrypt, PyJWT for authentication
- **Configuration**: pydantic-settings for environment-based configuration

### Deployment Environment
- **Replit hosting** with file-based secrets management
- **Environment variables** for database URL, JWT secrets, and OCR configuration
- **Default users** seeded for development (admin/employee accounts)

### Supported Bookmakers
- Ladbrokes, PointsBet, Sportsbet, TAB, bet365, Betfair
- Extensible parser system for additional bookmaker support