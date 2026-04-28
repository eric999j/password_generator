---
description: "Use when writing or reviewing code that handles passwords, keys, tokens, or authentication. Covers secure memory handling, logging safety, encryption rules, and export warnings."
applyTo: "src/**/*.py"
---
# Security Conventions

## Sensitive Data in Memory
- Wrap all in-memory passwords, keys, and tokens with `SecureString` from `src/crypto/secure_string`.
- Never store sensitive values as plain `str` in class attributes or module globals.

## Logging & Output
- Never use `print()`, `logging`, or any other output mechanism with plaintext passwords, encryption keys, or session tokens.
- Redact or omit sensitive fields in all error messages and exceptions.

## Encryption
- Always encrypt/decrypt via the module-level `encrypt()` / `decrypt()` functions in `src/crypto/encryption.py` — do not instantiate `_EncryptionManager` directly.
- If key decryption fails, raise `RuntimeError`; never auto-generate a replacement key (permanent data loss risk).

## Authentication State
- Authentication state must be stored encrypted via `SessionManager` — never as a plain boolean or string attribute.
- Call `session.is_authenticated()` to check state; do not read internal fields directly.

## CSV Export
- Any feature that exports data to CSV (or another plaintext format) must display a confirmation warning to the user before writing, because exported files contain plaintext passwords.

## Platform Key Protection
- Use DPAPI on Windows and system Keyring on macOS/Linux for key protection — never write raw key bytes to disk unprotected.
- Branch with `Config.IS_WINDOWS / IS_MAC / IS_LINUX`; never use `platform.system()` directly.
