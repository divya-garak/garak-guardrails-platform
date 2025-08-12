Garak Detect Reports
===================

The Garak Detect API provides comprehensive reporting capabilities for security evaluation results, with support for multiple formats and persistent storage.

Report Formats
--------------

**HTML Reports**

Interactive HTML reports with:
* Executive summary with pass/fail statistics
* Detailed probe results with evidence
* Vulnerability categorization and severity scoring
* Charts and visualizations for analysis

**JSON Reports**

Machine-readable structured data including:
* Raw evaluation results and probe outputs
* Metadata about the evaluation run
* Model response data and analysis
* Timestamps and configuration details

**JSONL Reports**

Line-delimited JSON for streaming and processing:
* One evaluation result per line
* Suitable for data pipeline integration
* Compatible with BigQuery and other analytics tools

Report Endpoints
----------------

**Download Report**

.. http:get:: /reports/(run_id)/(format)

   Download a completed evaluation report

   :param run_id: The unique identifier for the evaluation run
   :param format: Report format (html, json, jsonl)

   **Example Request:**
   
   .. code-block:: http

      GET /reports/garak_20250115_103000/html HTTP/1.1
      Host: your-detect-domain.com

   **Response:**
   
   Returns the report file with appropriate content-type headers

**List Reports**

.. http:get:: /reports

   List all available reports for the authenticated user

   **Query Parameters:**
   
   * ``limit`` (optional): Maximum number of reports to return (default: 50)
   * ``offset`` (optional): Pagination offset (default: 0)
   * ``status`` (optional): Filter by report status (completed, failed, running)

   **Response:**
   
   .. code-block:: json

      {
        "reports": [
          {
            "run_id": "garak_20250115_103000",
            "created_at": "2025-01-15T10:30:00Z",
            "completed_at": "2025-01-15T10:45:00Z",
            "status": "completed",
            "model_name": "http://localhost:8000/v1/chat/completions",
            "probes": ["promptinject", "jailbreak"],
            "total_evaluations": 100,
            "failed_evaluations": 15,
            "pass_rate": 85.0,
            "formats": ["html", "json", "jsonl"]
          }
        ],
        "total": 1,
        "limit": 50,
        "offset": 0
      }

**Report Metadata**

.. http:get:: /reports/(run_id)/metadata

   Get metadata about a specific report

   :param run_id: The unique identifier for the evaluation run

   **Response:**
   
   .. code-block:: json

      {
        "run_id": "garak_20250115_103000",
        "created_at": "2025-01-15T10:30:00Z",
        "completed_at": "2025-01-15T10:45:00Z",
        "status": "completed",
        "configuration": {
          "model_type": "rest",
          "model_name": "http://localhost:8000/v1/chat/completions",
          "probes": ["promptinject", "jailbreak"],
          "generations": 10,
          "parallel": 1
        },
        "results_summary": {
          "total_evaluations": 100,
          "passed_evaluations": 85,
          "failed_evaluations": 15,
          "pass_rate": 85.0,
          "high_severity_issues": 3,
          "medium_severity_issues": 7,
          "low_severity_issues": 5
        },
        "file_info": {
          "html_size": "2.1MB",
          "json_size": "892KB",
          "jsonl_size": "1.3MB"
        }
      }

**Delete Report**

.. http:delete:: /reports/(run_id)

   Delete a report and all associated files

   :param run_id: The unique identifier for the evaluation run

   **Response:**
   
   .. code-block:: json

      {
        "message": "Report deleted successfully",
        "run_id": "garak_20250115_103000"
      }

BigQuery Integration
--------------------

**Automatic Upload**

When configured, reports are automatically uploaded to BigQuery for long-term storage and analysis:

* **Dataset:** ``garak_security_evaluations``
* **Table:** ``evaluation_results``
* **Schema:** Structured evaluation data with probe results, model responses, and metadata

**Query Examples**

.. code-block:: sql

   -- Get pass rates by model over time
   SELECT 
     model_name,
     DATE(created_at) as evaluation_date,
     AVG(pass_rate) as avg_pass_rate
   FROM `project.garak_security_evaluations.evaluation_results`
   GROUP BY model_name, evaluation_date
   ORDER BY evaluation_date DESC

   -- Find high-severity vulnerabilities
   SELECT 
     run_id,
     probe_name,
     vulnerability_type,
     severity,
     model_response
   FROM `project.garak_security_evaluations.evaluation_results`
   WHERE severity = 'HIGH'
   ORDER BY created_at DESC

Storage Configuration
---------------------

**Local Storage**

Default configuration stores reports locally:

.. code-block:: bash

   DATA_DIR=/app/data
   REPORT_DIR=/app/reports

**GCS Integration**

For production deployments with persistent storage:

.. code-block:: bash

   # Environment variables
   DATA_DIR=/mnt/gcs-storage/data
   REPORT_DIR=/mnt/gcs-storage/reports
   
   # GCS bucket mounting
   gcsfuse garak-persistent-storage /mnt/gcs-storage

**PostgreSQL Database**

Report metadata is stored in PostgreSQL:

.. code-block:: bash

   # Database configuration
   DATABASE_URL=postgresql://user:pass@localhost:5432/garak_detect

Report Structure
----------------

**HTML Report Sections**

1. **Executive Summary**
   - Overall pass/fail statistics
   - Risk assessment and recommendations
   - Key findings and critical vulnerabilities

2. **Detailed Results**
   - Probe-by-probe analysis
   - Individual test case results
   - Model responses and evidence

3. **Appendices**
   - Configuration details
   - Raw data exports
   - Methodology documentation

**JSON Report Schema**

.. code-block:: json

   {
     "metadata": {
       "run_id": "string",
       "created_at": "timestamp",
       "configuration": {...}
     },
     "summary": {
       "total_evaluations": "integer",
       "pass_rate": "float",
       "severity_breakdown": {...}
     },
     "results": [
       {
         "probe": "string",
         "test_case": "string",
         "passed": "boolean",
         "severity": "string",
         "model_response": "string",
         "evidence": "string"
       }
     ]
   }

Error Handling
--------------

**Common Errors**

* ``404`` - Report not found
* ``410`` - Report expired or deleted
* ``422`` - Invalid format requested
* ``500`` - Report generation failed
* ``503`` - Storage service unavailable

**Error Response Format**

.. code-block:: json

   {
     "error": "report_not_found",
     "message": "Report with ID garak_20250115_103000 not found",
     "run_id": "garak_20250115_103000"
   }