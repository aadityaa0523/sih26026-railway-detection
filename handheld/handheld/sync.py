"""
MqttPublisher: pushes a scan event to the dashboard over MQTT.

This class does one thing -- try to publish, report whether it worked. It does NOT manage
an offline queue; that's eventlog.py's job (the other agent's module). main.py is the glue:
try publish(), and on False/exception leave the event as still-pending in the EventLog.

CRITICAL: paho-mqtt must not be required to `import handheld.sync` on a dev machine.
Import happens lazily in __init__.
"""


class MqttPublisher:
    def __init__(self, broker_host: str, broker_port: int = 1883, topic: str = "senseguard/events",
                 client_id: str = "senseguard-handheld", connect_timeout: float = 3.0):
        try:
            import paho.mqtt.client as mqtt
        except ImportError as e:
            raise ImportError(
                "paho-mqtt is required for MqttPublisher. Install with: pip install paho-mqtt. "
                "On a dev machine, main.py --simulate skips MQTT and just prints publish attempts."
            ) from e
        self._topic = topic
        self._client = mqtt.Client(client_id=client_id)
        try:
            self._client.connect(broker_host, broker_port, keepalive=int(connect_timeout) or 1)
        except OSError:
            # No broker reachable (offline / wrong Wi-Fi) -- publish() will fail per-call below,
            # which is exactly the offline-queue trigger eventlog.py handles.
            pass

    def publish(self, event: dict) -> bool:
        """Publishes `event` as JSON to the configured topic. True on confirmed delivery,
        False on any failure (broker unreachable, not connected, publish rejected).

        Caller (main.py) decides retry/queue behavior on False -- this class is stateless
        about pending events.
        """
        import json

        try:
            payload = json.dumps(event)
            result = self._client.publish(self._topic, payload, qos=1)
            result.wait_for_publish(timeout=3.0)
            return result.is_published()
        except Exception:
            # Broker unreachable, not connected, timed out, etc. -- any failure here just
            # means "still pending"; main.py leaves it in the EventLog queue for the next
            # sync pass rather than trying to distinguish failure modes.
            return False

    def close(self):
        self._client.disconnect()
