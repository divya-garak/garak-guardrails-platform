(tracing)=

# Tracing

Tracing enhances the observability of guardrails execution. This section explains the configuration process for implementing tracing with NeMo Guardrails.

With tracing, you can:

- Track which rails are activated during conversations.
- Monitor LLM calls and their performance.
- Debug flow execution and identify bottlenecks.
- Analyze conversation patterns and errors.

## Contents

- [](quick-start.md) - Minimal setup to enable tracing using the OpenTelemetry SDK
- [](adapter-configurations.md) - Detailed configuration for FileSystem, OpenTelemetry, and Custom adapters
- [](opentelemetry-integration.md) - Production-ready OpenTelemetry setup and ecosystem compatibility
- [](common-integrations.md) - Setup examples for Jaeger, Zipkin, and OpenTelemetry Collector
- [](troubleshooting.md) - Common issues and solutions

```{toctree}
:hidden:

quick-start
adapter-types
adapter-configurations
opentelemetry-integration
common-integrations
troubleshooting
```
