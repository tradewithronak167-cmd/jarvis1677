"""Network monitoring for HI ROLEX."""

from __future__ import annotations


class NetworkMonitor:
    """Reads simple network connectivity status."""

    def get_network_status(self) -> str:
        """Return whether at least one network adapter is active."""
        try:
            import psutil

            stats = psutil.net_if_stats()
            active_adapters = [
                name
                for name, adapter in stats.items()
                if adapter.isup and not name.casefold().startswith("loopback")
            ]
            if active_adapters:
                return f"Connected ({active_adapters[0]})"
            return "Disconnected"
        except Exception:
            return "Unavailable"
