# ♻️ Automated Report Triage (Azure Function App)

## 📘 Overview

**Automated Report Triage** is an Azure-based automation solution designed to eliminate the daily manual reconciliation process of vendor reports.  
Our team previously spent **up to one hour per day** downloading and organizing reconciliation reports sent via email.  
This automation frees up **250+ hours per year**, reduces manual errors, and ensures consistent organization of reports in **SharePoint**.

---

## 🚀 Problem Statement

### The Problem: Manual Reconciliation Workflow
Currently, team members must:
1. Open vendor emails.
2. Manually download attachments.
3. Save them into the correct vendor folder in SharePoint.

This **manual process**:
- Consumes up to **1 hour per day**.
- Introduces **risk of human error** (misplaced files, missed attachments).
- Pulls time away from **core reconciliation tasks**.

---

## 💡 Our Solution: Automated Report Triage

The proposed **Azure Function App** automates the initial, repetitive tasks of the reconciliation workflow.

### 🔄 How It Works

1. **Email Ingestion**  
   - The azure function is granted access to a designated **Microsoft 365 mailbox**.  
   - Vendors send reconciliation reports to this mailbox.  

2. **Smart Triaging**  
   - The azure function identifies the vendor by **email domain** (e.g. `@redtiger.com`).  
   - Automatically **downloads attachments**.  
   - Uploads them to the **correct vendor folder** in **SharePoint**.

3. **Daily Summary Report (4:00 PM)**  
   - A **timer-triggered Azure Function** generates a daily summary.  
   - The summary lists all vendors from whom reports were received.  
   - Sent via email to stakeholders for visibility.

---

### 🧩 Core Components

| Component               | Description                                                        |
| ----------------------- | ------------------------------------------------------------------ |
| **Azure Function App**  | Hosts logic for email ingestion, triaging, and report summary.     |
| **Microsoft Graph API** | Handles email retrieval, attachment download, and OneDrive upload. |
| **OneDrive Online**     | Stores vendor-specific reconciliation reports.                     |
| **Timer Trigger**       | Sends summary report every day at 4 p.m.                           |

### ⏱ Back-of-the-Envelope Calculations

| Item                          | Value                               | Explanation                                            |
| ----------------------------- | ----------------------------------- | ------------------------------------------------------ |
| **Time spent daily (manual)** | 60 minutes                          | Team manually downloads and organizes reports each day |
| **Working days/year**         | 250 days                            | Approximate number of workdays in a year               |
| **Total annual time**         | 60 min ¡Á 250 = **15,000 minutes**   | = **250 hours/year** saved                             |
| **Hourly cost estimate**      | $40/hour                            | Approximate fully loaded team cost                     |
| **Annual labor savings**      | 250 hrs ¡Á $40/hr = **$10,000/year** | Direct labor cost reduction                            |
| **Automation runtime**        | <5 min/day                          | Negligible Azure consumption cost                      |


## ⚙️ Architecture

```mermaid
flowchart TD
    A[Vendor Email Sent] --> B[Designated Outlook Inbox]
    B --> C[Azure Function: Email Processor]
    C --> D[Identify Vendor by Domain]
    D --> E[Download Attachments]
    E --> F[Upload to OneDrive Vendor Folder]
    C --> G[Log Vendor Activity]
    H[Timer Trigger 4 PM] --> I[Generate Daily Summary Report]
    I --> J[Send Summary Email to Team]



