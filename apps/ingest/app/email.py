from __future__ import annotations

import logging

import httpx

logger = logging.getLogger("apps.ingest.email")


def send_alert_email(
    resend_api_key: str,
    to: str,
    player_name: str,
    stat_name: str,
    stat_value: float,
    direction: str,
    threshold: float,
) -> None:
    direction_word = "above" if direction == "up" else "below"
    try:
        httpx.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {resend_api_key}"},
            json={
                "from": "alerts@diamonddepartures.com",
                "to": [to],
                "subject": f"Alert: {player_name} {stat_name} {direction_word} {threshold}",
                "text": (
                    f"{player_name}'s {stat_name} is now {stat_value:.3f}, "
                    f"which is {direction_word} your threshold of {threshold}.\n\n"
                    "View the board: https://diamonddepartures.com"
                ),
            },
            timeout=10,
        )
    except Exception as exc:
        logger.warning("failed to send alert email to %s: %s", to, exc)
