Discovery Endpoints
==================

Find available generators and security probes.

List Generators
---------------

.. http:get:: /api/v1/generators

   List available model providers.

   **Rate limit:** 100 requests/minute

   .. code-block:: bash

      curl -H "X-API-Key: your_api_key_here" \
           https://scans.garaksecurity.com/api/v1/generators

   **Response:**

   .. code-block:: json

      {
        "generators": [
          {
            "name": "openai",
            "display_name": "OpenAI",
            "requires_api_key": true,
            "supported_models": ["gpt-4", "gpt-3.5-turbo"]
          },
          {
            "name": "huggingface",
            "display_name": "Hugging Face", 
            "requires_api_key": false,
            "supported_models": ["gpt2", "microsoft/DialoGPT-medium"]
          }
        ]
      }

List Probes
-----------

.. http:get:: /api/v1/probes

   List security probe categories.

   **Rate limit:** 100 requests/minute

   .. code-block:: bash

      curl -H "X-API-Key: your_api_key_here" \
           https://scans.garaksecurity.com/api/v1/probes

   **Response:**

   .. code-block:: json

      {
        "categories": [
          {
            "name": "hallucination",
            "display_name": "Hallucination Tests",
            "probes": [
              {
                "name": "misleading.FalseAssertion",
                "display_name": "False Assertion",
                "description": "Tests for factual inaccuracies"
              }
            ]
          },
          {
            "name": "security",
            "display_name": "Security Vulnerabilities",
            "probes": [
              {
                "name": "packagehallucination.JavaScript", 
                "display_name": "Package Hallucination",
                "description": "Tests for fake package suggestions"
              }
            ]
          }
        ]
      }

Get Generator Details
--------------------

.. http:get:: /api/v1/generators/(str:generator_name)

   Get details about a specific generator.

   **Rate limit:** 100 requests/minute

   .. code-block:: bash

      curl -H "X-API-Key: your_api_key_here" \
           https://scans.garaksecurity.com/api/v1/generators/openai

   **Response:**

   .. code-block:: json

      {
        "name": "openai",
        "display_name": "OpenAI",
        "requires_api_key": true,
        "supported_models": ["gpt-4", "gpt-3.5-turbo", "gpt-4o"]
      }

Get Generator Models
--------------------

.. http:get:: /api/v1/generators/(str:generator_name)/models

   Get all available models for a specific generator.

   **Rate limit:** 100 requests/minute

   .. code-block:: bash

      curl -H "X-API-Key: your_api_key_here" \
           https://scans.garaksecurity.com/api/v1/generators/openai/models

   **Response:**

   .. code-block:: json

      {
        "generator": "openai",
        "models": [
          "gpt-4",
          "gpt-4-turbo", 
          "gpt-4o",
          "gpt-4o-mini",
          "gpt-3.5-turbo",
          "gpt-3.5-turbo-instruct"
        ],
        "total": 6
      }

Get Category Probes
-------------------

.. http:get:: /api/v1/probes/(str:category_name)

   Get all probes in a category.

   **Rate limit:** 100 requests/minute

   .. code-block:: bash

      curl -H "X-API-Key: your_api_key_here" \
           https://scans.garaksecurity.com/api/v1/probes/hallucination

   **Response:**

   .. code-block:: json

      {
        "category": "hallucination",
        "display_name": "Hallucination Tests",
        "probes": [
          {
            "name": "misleading.FalseAssertion",
            "display_name": "False Assertion",
            "description": "Tests for factual inaccuracies"
          }
        ]
      }


Notes
-----

* **Discovery first:** Always check these endpoints before creating scans
* **Dynamic content:** Available generators/probes depend on your Garak installation
* **Test mode fallback:** Missing API keys trigger test mode with local models