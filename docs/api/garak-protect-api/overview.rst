Overview
========

The Garak Protect API adds safety filters to AI chat applications. Send messages to get safe responses.

Key Features
------------

* **Input Filtering** - Block harmful messages before processing
* **Output Filtering** - Check AI responses for safety issues
* **Content Safety** - Detect and block harmful content
* **Jailbreak Protection** - Prevent attempts to bypass safety rules
* **Real-time Processing** - Instant safety checking

API Endpoints
-------------

* **Chat** - ``POST /v1/chat/completions`` - Send messages, get safe responses
* **Health** - ``GET /health`` - Check if API is working
* **Config** - ``GET /v1/rails/configs`` - View safety settings

Use Cases
---------

* **Chat Applications** - Add safety to customer-facing AI
* **Content Moderation** - Filter harmful messages in real-time
* **Compliance** - Meet safety requirements for AI systems