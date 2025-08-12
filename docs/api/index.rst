Garak API Reference
===================

The Garak Dashboard API provides programmatic access to LLM security scanning capabilities.

Overview
--------

The Garak API is a RESTful interface that enables developers to integrate AI red-teaming 
capabilities into their workflows. The API allows you to create, monitor, and manage security 
scans of language models, testing for vulnerabilities including jailbreaking attacks, prompt 
injection, data leakage, toxicity generation, and other security weaknesses.

.. toctree::
   :maxdepth: 3
   :caption: Garak Detect API

   garak-detect-api/authentication
   garak-detect-api/quickstart
   garak-detect-api/api-keys-reference
   garak-detect-api/endpoints/index
   garak-detect-api/endpoints/scan-management
   garak-detect-api/endpoints/discovery
   garak-detect-api/endpoints/reports
   garak-detect-api/rate-limiting
   garak-detect-api/python-sdk

.. toctree::
   :maxdepth: 1
   :hidden:

   README