Quick Start
===========

This guide gets you started with the Garak Detect  API in minutes.

Base URL
--------

All API requests are made to:

.. code-block:: text

   https://garak-dashboard-765684604189.us-central1.run.app/api/v1

Step 1: Get an API Key
----------------------

Create your first admin API key:

.. http:post:: /api/v1/admin/bootstrap

   Create initial admin API key for system setup.

   **Authentication:** Not required (bootstrap only)

   .. code-block:: bash

      curl -X POST https://garak-dashboard-765684604189.us-central1.run.app/api/v1/admin/bootstrap

Save the returned API key securely - you'll need it for all future requests.

Step 2: Test API Access
-----------------------

Verify your API key works:

.. http:get:: /api/v1/health

   Check API health status.

   **Authentication:** Optional

   .. code-block:: bash

      export API_KEY="your_api_key_here"
      curl -H "X-API-Key: $API_KEY" https://garak-dashboard-765684604189.us-central1.run.app/api/v1/health

Expected response:

.. code-block:: json

   {
     "status": "healthy",
     "version": "1.0.0",
     "services": {
       "database": "healthy",
       "job_system": "healthy"
     }
   }

You can also check API information:

.. http:get:: /api/v1/info

   Get API information and capabilities.

   **Authentication:** Not required

   .. code-block:: bash

      curl https://garak-dashboard-765684604189.us-central1.run.app/api/v1/info

**Response:**

.. code-block:: json

   {
     "name": "Garak Security API",
     "version": "1.0.0",
     "description": "LLM security scanning and vulnerability detection API",
     "documentation": "https://docs.garaksecurity.com/api",
     "contact": "support@garaksecurity.com",
     "rate_limits": {
       "default": "100/minute",
       "scan_creation": "10/minute"
     }
   }

Step 3: Discover Available Options
----------------------------------

List available model generators:

.. http:get:: /api/v1/generators

   Get available model providers.

   **Rate limit:** 100/minute

   .. code-block:: bash

      curl -H "X-API-Key: $API_KEY" https://garak-dashboard-765684604189.us-central1.run.app/api/v1/generators

List available security probes:

.. http:get:: /api/v1/probes

   Get available security probe categories.

   **Rate limit:** 100/minute

   .. code-block:: bash

      curl -H "X-API-Key: $API_KEY" https://garak-dashboard-765684604189.us-central1.run.app/api/v1/probes

Step 4: Create Your First Scan
-------------------------------

Create a security scan of GPT-2 for hallucination vulnerabilities:

.. http:post:: /api/v1/scans

   Create a new security scan.

   **Rate limit:** 10/minute

   .. code-block:: bash

      curl -X POST https://garak-dashboard-765684604189.us-central1.run.app/api/v1/scans \
           -H "X-API-Key: $API_KEY" \
           -H "Content-Type: application/json" \
           -d '{
             "generator": "huggingface",
             "model_name": "gpt2", 
             "probe_categories": ["hallucination"],
             "name": "My First Security Scan",
             "description": "Testing GPT-2 for hallucination vulnerabilities"
           }'

For models requiring API access, include the ``api_keys`` field:

.. code-block:: bash

   curl -X POST https://garak-dashboard-765684604189.us-central1.run.app/api/v1/scans \
        -H "X-API-Key: $API_KEY" \
        -H "Content-Type: application/json" \
        -d '{
          "generator": "openai",
          "model_name": "gpt-3.5-turbo",
          "probe_categories": ["hallucination"],
          "name": "OpenAI Security Scan", 
          "description": "Testing GPT-3.5 for vulnerabilities",
          "api_keys": {
            "openai_api_key": "sk-your_openai_key_here"
          }
        }'

**API Keys**: 

- **Local models** (``huggingface`` with ``gpt2``, etc.): Run directly without API keys
- **Cloud providers**: Require API keys, but will fall back to **test mode** with HuggingFace GPT-2 if missing  

**Get API tokens**:

- `OpenAI <https://platform.openai.com/api-keys>`_ (``openai_api_key``)
- `Anthropic <https://console.anthropic.com/>`_ (``anthropic_api_key``) 
- `HuggingFace <https://huggingface.co/settings/tokens>`_ (``huggingface_api_key``)
- `Cohere <https://dashboard.cohere.ai/api-keys>`_ (``cohere_api_key``)
- `Google AI <https://makersuite.google.com/app/apikey>`_ (``google_api_key`` for Gemini)
- `Mistral AI <https://console.mistral.ai/>`_ (``mistral_api_key``)
- `Replicate <https://replicate.com/account/api-tokens>`_ (``replicate_api_token``)
- `Google Cloud <https://console.cloud.google.com/apis/credentials>`_ (``gcp_credentials_path`` for VertexAI)

The response includes a ``scan_id`` for tracking the scan.

Step 5: Monitor Scan Progress
-----------------------------

Check scan status (replace ``{scan_id}`` with your actual scan ID from Step 4):

.. http:get:: /api/v1/scans/(str:scan_id)/status

   Get current status of a scan.

   **Rate limit:** 500/minute

   .. code-block:: bash

      curl -H "X-API-Key: $API_KEY" \
           https://garak-dashboard-765684604189.us-central1.run.app/api/v1/scans/{scan_id}/status

Get detailed progress:

.. http:get:: /api/v1/scans/(str:scan_id)/progress

   Get detailed progress information for a running scan.

   **Rate limit:** 500/minute

   .. code-block:: bash

      curl -H "X-API-Key: $API_KEY" \
           https://garak-dashboard-765684604189.us-central1.run.app/api/v1/scans/{scan_id}/progress

Step 6: Download Results
------------------------

Once the scan completes, download the report:

.. http:get:: /api/v1/scans/(str:scan_id)/reports/json

   Download JSON format report.

   **Rate limit:** 50/minute

   .. code-block:: bash

      # JSON report
      curl -H "X-API-Key: $API_KEY" \
           https://garak-dashboard-765684604189.us-central1.run.app/api/v1/scans/{scan_id}/reports/json \
           -o scan_report.json

.. http:get:: /api/v1/scans/(str:scan_id)/reports/html

   Download HTML format report.

   **Rate limit:** 50/minute

   .. code-block:: bash

      # HTML report  
      curl -H "X-API-Key: $API_KEY" \
           https://garak-dashboard-765684604189.us-central1.run.app/api/v1/scans/{scan_id}/reports/html \
           -o scan_report.html

Next Steps
----------

* Read the :doc:`endpoints/index` for complete API reference
* Review :doc:`rate-limiting` for API usage limits
* Optional: Use the :doc:`python-sdk` for Python applications (or build your own HTTP client)

Common Issues
-------------

**HTTP 401 Unauthorized**
  Your API key is missing or invalid. Ensure your key starts with ``garak_`` and is included in the ``X-API-Key`` header.

**HTTP 400 Bad Request**  
  Invalid request parameters. Use ``/api/v1/generators`` and ``/api/v1/probes`` to check valid values.

**Scan fails immediately**
  Missing API keys for cloud providers. Check the logs in the progress endpoint for specific error messages.

**HTTP 429 Too Many Requests**
  You've exceeded the rate limit. Wait and retry, or contact support to increase your limits.