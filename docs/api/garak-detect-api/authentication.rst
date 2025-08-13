Authentication
==============

Most API endpoints require authentication using API keys. This page describes how to obtain
and use API keys for accessing the Garak Detect  API.

API Key Types
-------------

The API supports different permission levels:

* **read** - Can view scans, generators, and probes
* **write** - Can create and modify scans  
* **admin** - Full system access including API key management

Authentication Methods
----------------------

Header Authentication
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Authorization header
   curl -H "Authorization: Bearer your_api_key_here" \
        https://garak-dashboard-765684604189.us-central1.run.app/api/v1/scans

   # X-API-Key header
   curl -H "X-API-Key: your_api_key_here" \
        https://garak-dashboard-765684604189.us-central1.run.app/api/v1/scans

Query Parameter Authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. code-block:: bash

   curl "https://garak-dashboard-765684604189.us-central1.run.app/api/v1/scans?api_key=your_api_key_here"

Bootstrap Setup
---------------

For first-time setup, create an initial admin API key:

.. code-block:: bash

   curl -X POST https://garak-dashboard-765684604189.us-central1.run.app/api/v1/admin/bootstrap

This endpoint is only available when no admin keys exist in the system.

Response:

.. code-block:: json

   {
     "api_key": "your_admin_api_key_here",
     "key_info": {
       "id": 1,
       "key_prefix": "your_key_prefix",
       "name": "Initial Admin Key",
       "permissions": ["read", "write", "admin"]
     },
     "message": "Bootstrap admin key created successfully. Store this key securely - it will not be shown again.",
     "next_steps": [
       "Store the API key in a secure location",
       "Use this key to create additional API keys with appropriate permissions",
       "Consider setting up rate limiting and monitoring"
     ]
   }

Creating Additional Keys
------------------------

Use your admin key to create additional keys with appropriate permissions:

**Rate limit:** 10/minute

.. code-block:: bash

   curl -X POST https://garak-dashboard-765684604189.us-central1.run.app/api/v1/admin/api-keys \
        -H "X-API-Key: your_admin_key" \
        -H "Content-Type: application/json" \
        -d '{
          "name": "Scan API Key",
          "description": "For automated security scans", 
          "permissions": ["read", "write"]
        }'

**Optional fields:**
- ``rate_limit`` - Requests per minute (default: 100, range: 1-10000)
- ``expires_days`` - Days until expiration (default: no expiration, range: 1-365)

Key Management
--------------

List API Keys
~~~~~~~~~~~~~

.. http:get:: /api/v1/admin/api-keys

   List all API keys in the system.

   **Admin required:** Yes
   **Rate limit:** 100/minute

   .. code-block:: bash

      curl -X GET https://garak-dashboard-765684604189.us-central1.run.app/api/v1/admin/api-keys \
           -H "X-API-Key: your_admin_key"

   **Response:**

   .. code-block:: json

      [
        {
          "id": 1,
          "name": "Production API Key",
          "key_prefix": "garak_prod_",
          "created_at": "2025-01-15T10:30:00Z",
          "last_used": "2025-01-15T14:22:00Z",
          "status": "active",
          "rate_limit": 100,
          "expires_at": null,
          "permissions": ["read", "write"]
        },
        {
          "id": 2,
          "name": "Development Key",
          "key_prefix": "garak_dev_",
          "created_at": "2025-01-14T09:15:00Z",
          "last_used": null,
          "status": "revoked",
          "rate_limit": 50,
          "expires_at": "2025-02-15T09:15:00Z",
          "permissions": ["read"]
        }
      ]

   .. note::
      **Security:** Full API key values are never returned for security reasons. Only the key prefix is shown to help identify keys.

Get API Key Details
~~~~~~~~~~~~~~~~~~~

.. http:get:: /api/v1/admin/api-keys/(int:key_id)

   Get details of a specific API key.

   **Admin required:** Yes
   **Rate limit:** 200/minute

   .. code-block:: bash

      # Replace 123 with the actual numeric ID of the API key
      curl -X GET https://garak-dashboard-765684604189.us-central1.run.app/api/v1/admin/api-keys/123 \
           -H "X-API-Key: your_admin_key"

**Response:**

.. code-block:: json

   {
     "id": 2,
     "name": "Production API Key",
     "key_prefix": "garak_prod_",
     "created_at": "2025-01-15T10:30:00Z",
     "last_used": "2025-01-15T14:22:00Z",
     "status": "active",
     "rate_limit": 100,
     "expires_at": null,
     "permissions": ["read", "write"]
   }

Revoke API Key
~~~~~~~~~~~~~~

.. http:post:: /api/v1/admin/api-keys/(int:key_id)/revoke

   Revoke an API key (makes it unusable).

   **Admin required:** Yes
   **Rate limit:** 50/minute

   .. code-block:: bash

      # Replace 123 with the actual numeric ID of the API key to revoke
      curl -X POST https://garak-dashboard-765684604189.us-central1.run.app/api/v1/admin/api-keys/123/revoke \
           -H "X-API-Key: your_admin_key"

Delete API Key
~~~~~~~~~~~~~~

.. http:delete:: /api/v1/admin/api-keys/(int:key_id)

   Permanently delete an API key.

   **Admin required:** Yes
   **Rate limit:** 20/minute

   .. code-block:: bash

      # Replace 123 with the actual numeric ID of the API key to delete
      curl -X DELETE https://garak-dashboard-765684604189.us-central1.run.app/api/v1/admin/api-keys/123 \
           -H "X-API-Key: your_admin_key"

Check Rate Limit Usage
~~~~~~~~~~~~~~~~~~~~~~

.. http:get:: /api/v1/admin/api-keys/(int:key_id)/rate-limit

   Get current rate limit usage for a specific API key.

   **Admin required:** Yes
   **Rate limit:** 100/minute

   .. code-block:: bash

      # Replace 123 with the actual numeric ID of the API key
      curl -X GET https://garak-dashboard-765684604189.us-central1.run.app/api/v1/admin/api-keys/123/rate-limit \
           -H "X-API-Key: your_admin_key"

   **Response:**

   .. code-block:: json

      {
        "api_key_id": 123,
        "current_usage": {
          "requests_in_window": 45,
          "limit": 100,
          "remaining": 55,
          "reset_time": "2024-01-15T10:32:00Z"
        }
      }

System Statistics
~~~~~~~~~~~~~~~~~

.. http:get:: /api/v1/admin/stats

   Get system statistics and API usage metrics.

   **Admin required:** Yes
   **Rate limit:** 50/minute

   .. code-block:: bash

      curl -X GET https://garak-dashboard-765684604189.us-central1.run.app/api/v1/admin/stats \
           -H "X-API-Key: your_admin_key"

   **Response:**

   .. code-block:: json

      {
        "system": {
          "total_api_keys": 15,
          "active_api_keys": 12,
          "total_scans": 1247,
          "scans_this_month": 89
        },
        "usage": {
          "requests_last_24h": 2456,
          "top_endpoints": [
            {
              "endpoint": "/api/v1/scans",
              "method": "POST", 
              "count": 45
            }
          ]
        }
      }