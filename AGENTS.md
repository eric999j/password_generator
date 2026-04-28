# 強密碼產生器 — Agent Instructions

## Project Overview
Cross-platform Python password manager with system-level authentication, encrypted storage, and tkinter GUI.
See [README.md](README.md) for full feature descriptions and usage.

## Architecture

Layered structure under `src/`:

| Layer | Path | Responsibility |
|-------|------|----------------|
| Entry | `app.py` | Auth gate → launch GUI |
| Auth | `src/auth/` | System auth (Windows LogonUser / Unix PAM), encrypted session state |
| Crypto | `src/crypto/` | Fernet encryption, DPAPI/Keyring key protection, SecureString |
| Database | `src/database/` | SQLite with connection pooling via `PasswordRepository` |
| Services | `src/services/` | Password generation and strength evaluation |
| GUI | `src/gui/app.py` | ttkbootstrap dark-theme UI |
| Config | `src/config.py` | All paths, constants, and platform detection |

**Key design constraints:**
- `_EncryptionManager` is a singleton — never re-instantiate or reset it manually; key loss means permanent data loss.
- Authentication state is stored encrypted in memory (`SessionManager`) — not as a plain boolean.
- All file paths come from `Config` (never hardcode paths).

## Build & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run in development
python app.py

# Package (must run on target platform — PyInstaller does not cross-compile)
pyinstaller --clean 強密碼產生器.spec
```

## Testing

```bash
pytest tests/
```

Tests live in `tests/test_core.py`. When adding tests, insert `sys.path.insert(0, str(Path(__file__).parent.parent))` at the top (already present) so imports resolve without installation.

## Platform Notes

- Use `Config.IS_WINDOWS / IS_MAC / IS_LINUX` for any platform-specific branching.
- Data directory: `%LOCALAPPDATA%\.password_generator\` (Windows) or `~/.password_generator/` (macOS/Linux).
- Key protection: DPAPI on Windows, system Keyring on macOS/Linux.
- `pamela` dependency is Linux/macOS only (`sys_platform != 'win32'`); `SecretStorage` is Linux only.

## Security Conventions

- Never log or print plaintext passwords or keys.
- Use `SecureString` (from `src/crypto/secure_string`) for in-memory sensitive values.
- Do not auto-generate a new key if key decryption fails — raise `RuntimeError` instead (see `encryption.py`).
- GUI exports to CSV include plaintext passwords — warn users before export.
