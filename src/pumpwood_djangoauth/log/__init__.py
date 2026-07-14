"""Request logging middleware and helpers for Pumpwood Auth.

When ``PUMPWOOD_AUTH_IS_RABBITMQ_LOG`` is enabled, authenticated consumer
requests are queued on RabbitMQ. Otherwise logs are written to stdout.
"""
