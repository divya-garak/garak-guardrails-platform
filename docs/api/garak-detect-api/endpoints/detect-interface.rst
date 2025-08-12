Garak Detect Interface
=====================

The Garak Detect API provides a web-based interface for running security evaluations against language models using the Garak vulnerability scanner.

**Base URL:** ``https://your-detect-domain.com``

Core Features
-------------

**Interactive Dashboard**

* Web interface for configuring and running Garak security scans
* Real-time progress monitoring with live output streaming
* Support for multiple model providers and probe categories
* BigQuery integration for long-term report storage and analysis

**Security Evaluation**

* Comprehensive LLM vulnerability testing
* Jailbreak detection and prompt injection testing
* Content safety evaluation
* Custom probe configuration and execution

**Report Management**

* HTML, JSON, and JSONL report generation
* Persistent storage with GCS integration
* Report history and analysis tools

API Endpoints
-------------

**Dashboard Interface**

.. http:get:: /

   Main dashboard interface for running security evaluations

   **Response:**
   
   Returns the web interface HTML

**Health Check**

.. http:get:: /health

   Check the health status of the Detect API service

   **Response:**
   
   .. code-block:: json

      {
        "status": "healthy",
        "timestamp": "2025-01-15T10:30:00Z",
        "version": "1.0.0"
      }

**Run Evaluation**

.. http:post:: /run

   Start a new security evaluation

   **Request Body:**
   
   .. code-block:: json

      {
        "model_type": "rest",
        "model_name": "http://localhost:8000/v1/chat/completions",
        "probes": ["promptinject", "jailbreak"],
        "config": {
          "generations": 10,
          "parallel": 1
        }
      }

   **Response:**
   
   .. code-block:: json

      {
        "run_id": "garak_20250115_103000",
        "status": "started",
        "timestamp": "2025-01-15T10:30:00Z"
      }

**Evaluation Status**

.. http:get:: /status/(run_id)

   Get the current status of a running evaluation

   :param run_id: The unique identifier for the evaluation run

   **Response:**
   
   .. code-block:: json

      {
        "run_id": "garak_20250115_103000",
        "status": "running",
        "progress": 45,
        "started_at": "2025-01-15T10:30:00Z",
        "estimated_completion": "2025-01-15T10:45:00Z"
      }

**Live Output**

.. http:get:: /output/(run_id)

   Stream live output from a running evaluation

   :param run_id: The unique identifier for the evaluation run

   **Response:**
   
   Server-sent events stream with real-time evaluation output

Authentication
--------------

The Detect API supports Firebase authentication and can be configured to bypass authentication for development environments.

**Environment Variables:**

* ``DISABLE_AUTH=true`` - Bypass authentication (development only)
* ``FIREBASE_API_KEY`` - Firebase API key for authentication
* ``FIREBASE_PROJECT_ID`` - Firebase project identifier

Rate Limiting
-------------

* **Evaluation creation:** 5 concurrent runs per user
* **Status checks:** 100/minute per user
* **Output streaming:** No limit (real-time)

Configuration
-------------

**Model Providers**

Supported model types:
* ``rest`` - REST API endpoints
* ``openai`` - OpenAI API compatible
* ``huggingface`` - HuggingFace models
* ``anthropic`` - Anthropic Claude models

**Probe Categories**

Available security probes:
* ``promptinject`` - Prompt injection attacks
* ``jailbreak`` - Jailbreak attempts
* ``encoding`` - Encoding-based attacks
* ``malwaregen`` - Malware generation attempts
* ``misleading`` - Misleading information generation

Error Handling
--------------

All errors return consistent JSON format:

.. code-block:: json

   {
     "error": "evaluation_failed",
     "message": "Failed to connect to target model endpoint",
     "details": {
       "model_name": "http://localhost:8000/v1/chat/completions",
       "error_code": "CONNECTION_REFUSED"
     }
   }

**Common Error Codes:**

* ``400`` - Invalid request parameters
* ``401`` - Authentication required
* ``403`` - Insufficient permissions
* ``404`` - Evaluation run not found
* ``429`` - Rate limit exceeded
* ``500`` - Internal server error