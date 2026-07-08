"""Memory tests for HI ROLEX."""

from memory.memory_manager import MemoryManager


def test_memory_database_initializes(tmp_path) -> None:
    """Memory database is created."""
    database_path = tmp_path / "memory.db"
    MemoryManager(database_path)

    assert database_path.exists()


def test_safe_memory_can_be_added(tmp_path) -> None:
    """Safe memory saves successfully."""
    manager = MemoryManager(tmp_path / "memory.db")

    assert manager.add_memory("profile", "name", "Rahul")
    assert manager.get_memory("name") == "Rahul"


def test_sensitive_memory_is_rejected(tmp_path) -> None:
    """Sensitive memory is not stored."""
    manager = MemoryManager(tmp_path / "memory.db")

    assert not manager.add_memory("secret", "password", "my password is 12345")
