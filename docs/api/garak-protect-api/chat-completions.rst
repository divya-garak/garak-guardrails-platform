Chat Completions
================

The core endpoint for protected chat interactions through NeMo Guardrails.

Protected Chat Interface
-------------------------

.. http:post:: /v1/chat/completions

   Send chat messages through real-time guardrails protection.

   **Headers:**
   
   * ``Content-Type: application/json`` (required)

   **Request Body:**

   .. code-block:: json

      {
        "messages": [
          {
            "role": "user",
            "content": "Your message here"
          }
        ],
        "config_id": "main"
      }

   **Required Fields:**

   * ``messages`` - Array of message objects with ``role`` and ``content``

   **Optional Fields:**

   * ``config_id`` - Guardrail configuration to use (default: "main")
   * ``temperature`` - Response randomness 0.0-1.0
   * ``max_tokens`` - Maximum response length

   **Example Request:**

   .. code-block:: bash

      curl -X POST https://api.garaksecurity.com/v1/chat/completions \
           -H "Content-Type: application/json" \
           -d '{
             "messages": [
               {
                 "role": "user",
                 "content": "What are the benefits of renewable energy?"
               }
             ],
             "temperature": 0.7,
             "max_tokens": 500
           }'

   **Success Response (200):**

   .. code-block:: json

      {
        "messages": [
          {
            "role": "assistant",
            "content": "Renewable energy offers several key benefits: 1) Environmental protection through reduced greenhouse gas emissions, 2) Energy independence and security, 3) Long-term cost savings, 4) Job creation in green industries, and 5) Sustainable resource utilization for future generations."
          }
        ]
      }

Message Roles
--------------

Supported message roles in conversation history:

* **user** - Messages from the end user
* **assistant** - Previous AI responses  
* **system** - System instructions (optional)

Multi-turn Conversations
-------------------------

Maintain conversation context by including message history:

.. code-block:: bash

   curl -X POST https://api.garaksecurity.com/v1/chat/completions \
        -H "Content-Type: application/json" \
        -d '{
          "messages": [
            {
              "role": "user",
              "content": "What is machine learning?"
            },
            {
              "role": "assistant", 
              "content": "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed."
            },
            {
              "role": "user",
              "content": "Can you give me an example?"
            }
          ]
        }'

Guardrail Protection Levels
----------------------------

The API automatically applies multiple protection layers:

**Input Rails**
  * Jailbreak detection and blocking
  * Harmful content filtering
  * PII detection and masking
  * Prompt injection prevention

**Output Rails**
  * Content safety validation
  * Factual accuracy checks
  * Toxicity filtering
  * Response length limits

**Dialog Rails**
  * Conversation flow control
  * Topic boundary enforcement
  * Context maintenance
  * Session management

Content Blocking
----------------

When harmful content is detected, the API returns a safe response:

**Content Blocked (200):**

.. code-block:: json

   {
     "messages": [
       {
         "role": "assistant",
         "content": "I cannot provide information on that topic as it may be harmful. Is there something else I can help you with?"
       }
     ]
   }

Status Codes
------------

* **200** - Success (including blocked content responses)
* **400** - Bad Request (malformed input)
* **500** - Internal Server Error
* **503** - Service Unavailable (maintenance mode)

Red Team Challenges
-------------------

.. http:get:: /v1/challenges

   Get available red team challenges for testing guardrails.

   **Authentication:** Not required

   .. code-block:: bash

      curl https://api.garaksecurity.com/v1/challenges

   **Response:**

   .. code-block:: json

      []

   **Note:** This endpoint returns available red team challenges that can be used to test guardrail effectiveness. Currently returns an empty array, indicating no pre-configured challenges are available.

Best Practices
--------------

**Message History**
  Include conversation context for better guardrail decisions

**Error Handling**
  Always check for blocked content in successful (200) responses

**Content Validation**
  The API will automatically filter harmful content - no additional validation needed