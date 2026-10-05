#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

def replace_required(path: Path, replacements: list[tuple[str, str]], required: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    original = text
    for old, new in replacements:
        if old in text:
            text = text.replace(old, new)
    missing = [m for m in required if m not in text]
    if missing:
        raise SystemExit(f"PATCH FAILED {path}: missing markers {missing}")
    if text == original:
        print(f"UNCHANGED {path}")
    else:
        path.write_text(text, encoding="utf-8")
        print(f"PATCHED {path}")

def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: ci_apply_fixes.py <project-root>")
    root = Path(sys.argv[1]).resolve()
    if not (root / "settings.gradle.kts").is_file():
        raise SystemExit(f"Invalid project root: {root}")

    replace_required(
        root / "app/src/main/java/pro/babasitaram/vault/core/security/BiometricAuthenticator.kt",
        [(
            "import androidx.biometric.BiometricManager\n",
            "import androidx.biometric.BiometricManager\n"
            "import androidx.biometric.BiometricManager.Authenticators.BIOMETRIC_STRONG\n",
        )],
        ["Authenticators.BIOMETRIC_STRONG", "setAllowedAuthenticators(BIOMETRIC_STRONG)"],
    )

    replace_required(
        root / "app/src/main/java/pro/babasitaram/vault/core/security/BiometricSessionKeyStore.kt",
        [
            ("KeyProperties.AUTH_BIOMETRIC_WEAK", "KeyProperties.AUTH_BIOMETRIC_STRONG"),
            ("const val AUTH_WINDOW_SECONDS = 24 * 60 * 60",
             "const val AUTH_WINDOW_SECONDS: Int = 24 * 60 * 60"),
        ],
        ["KeyProperties.AUTH_BIOMETRIC_STRONG", "const val AUTH_WINDOW_SECONDS: Int"],
    )

    replace_required(
        root / "app/src/main/java/pro/babasitaram/vault/presentation/about/AboutScreen.kt",
        [
            ("import pro.babasitaram.vault.BuildConfig\n",
             "import pro.babasitaram.vault.BuildConfig\n"
             "import pro.babasitaram.vault.R\n"),
            (
                'error != null -> AppErrorState(stringResource(R.string.b5_state_error), error ?: stringResource(R.string.b5_state_error_message), stringResource(R.string.b5_state_retry)) { error = null }',
                'error != null -> AppErrorState(\n'
                '                title = stringResource(R.string.b5_state_error),\n'
                '                message = error ?: stringResource(R.string.b5_state_error_message),\n'
                '                retryLabel = stringResource(R.string.b5_state_retry),\n'
                '                onRetry = { error = null }\n'
                '            )',
            ),
        ],
        ["import pro.babasitaram.vault.R", "onRetry = { error = null }"],
    )

    replace_required(
        root / "app/src/main/java/pro/babasitaram/vault/presentation/components/AppBottomSheet.kt",
        [
            ("import androidx.compose.material3.ModalBottomSheet\n",
             "import androidx.compose.material3.ModalBottomSheet\n"
             "import androidx.compose.material3.MaterialTheme\n"),
            ("color = BottomSheetDefaults.dragHandleColor",
             "color = MaterialTheme.colorScheme.onSurfaceVariant"),
        ],
        ["MaterialTheme.colorScheme.onSurfaceVariant"],
    )

    replace_required(
        root / "app/src/main/java/pro/babasitaram/vault/presentation/components/AppDrawer.kt",
        [
            ("import androidx.compose.material3.HorizontalDivider\n",
             "import androidx.compose.material.icons.Icons\n"
             "import androidx.compose.material.icons.filled.Lock\n"
             "import androidx.compose.material3.HorizontalDivider\n"),
            ("imageVector = androidx.compose.material.icons.Icons.Default.Lock",
             "imageVector = Icons.Default.Lock"),
        ],
        ["import androidx.compose.material.icons.filled.Lock", "imageVector = Icons.Default.Lock"],
    )

    replace_required(
        root / "app/src/main/java/pro/babasitaram/vault/presentation/components/AppScreenState.kt",
        [
            ("import androidx.compose.ui.Modifier\n",
             "import androidx.compose.ui.Modifier\n"
             "import androidx.compose.ui.semantics.heading\n"),
            ("androidx.compose.ui.semantics.heading()", "heading()"),
        ],
        ["import androidx.compose.ui.semantics.heading", "heading()"],
    )

    editor = root / "app/src/main/java/pro/babasitaram/vault/presentation/editor/EntryEditorScreen.kt"
    if not editor.is_file():
        raise SystemExit(f"Missing source: {editor}")
    text = editor.read_text(encoding="utf-8")
    for kind in ("Uri", "Email", "Number", "Phone"):
        text = text.replace(
            f"keyboardOptions = androidx.compose.foundation.text.KeyboardOptions(keyboardType = KeyboardType.{kind})",
            f"keyboardType = KeyboardType.{kind}",
        )
    if "keyboardOptions = androidx.compose.foundation.text.KeyboardOptions" in text:
        raise SystemExit("PATCH FAILED EntryEditorScreen.kt: AppTextField keyboardOptions remain")
    editor.write_text(text, encoding="utf-8")
    print("PATCHED EntryEditorScreen.kt")

if __name__ == "__main__":
    main()
