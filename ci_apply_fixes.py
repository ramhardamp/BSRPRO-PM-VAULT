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

def replace_region(path: Path, start_marker: str, end_marker: str, replacement: str) -> None:
    text = path.read_text(encoding="utf-8")
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f"PATCH FAILED {path}: start marker not found")
    end = text.find(end_marker, start)
    if end < 0 or end <= start:
        raise SystemExit(f"PATCH FAILED {path}: end marker not found")
    updated = text[:start] + replacement + text[end:]
    if updated == text:
        print(f"UNCHANGED REGION {path}")
    else:
        path.write_text(updated, encoding="utf-8")
        print(f"PATCHED REGION {path}")

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

    drawer = root / "app/src/main/java/pro/babasitaram/vault/presentation/components/AppDrawer.kt"
    drawer_text = drawer.read_text(encoding="utf-8")
    if "import androidx.compose.material.icons.Icons" not in drawer_text:
        marker = "import androidx.compose.material3."
        idx = drawer_text.find(marker)
        if idx >= 0:
            line_start = drawer_text.rfind("\n", 0, idx) + 1
            drawer_text = drawer_text[:line_start] + "import androidx.compose.material.icons.Icons\nimport androidx.compose.material.icons.filled.Lock\n" + drawer_text[line_start:]
        else:
            drawer_text = drawer_text.replace(
                "package pro.babasitaram.vault.presentation.components\n",
                "package pro.babasitaram.vault.presentation.components\n\nimport androidx.compose.material.icons.Icons\nimport androidx.compose.material.icons.filled.Lock\n",
                1,
            )
    if "imageVector = androidx.compose.material.icons.Icons.Default.Lock" in drawer_text:
        drawer_text = drawer_text.replace(
            "imageVector = androidx.compose.material.icons.Icons.Default.Lock",
            "imageVector = Icons.Default.Lock",
        )
    if "imageVector = Icons.Default.Lock" not in drawer_text:
        raise SystemExit(f"PATCH FAILED {drawer}: lock icon reference missing")
    if "import androidx.compose.material.icons.Icons" not in drawer_text:
        raise SystemExit(f"PATCH FAILED {drawer}: Icons import missing")
    if "import androidx.compose.material.icons.filled.Lock" not in drawer_text:
        raise SystemExit(f"PATCH FAILED {drawer}: Lock import missing")
    drawer.write_text(drawer_text, encoding="utf-8")
    print("PATCHED AppDrawer.kt")

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

    # Test-source compiler fixes exposed after production sources compile.
    autofill_test = root / "app/src/test/java/pro/babasitaram/vault/autofill/AutofillParserTest.kt"
    replace_required(
        autofill_test,
        [
            (
                "class AutofillParserNativeWordsTest {\n",
                "class AutofillParserNativeWordsTest {\n"
                "    private val numberPassword = 0x12\n"
                "    private fun c(h: FieldHints) = AutofillParser.classify(h)\n",
            )
        ],
        ["private val numberPassword = 0x12", "private fun c(h: FieldHints)"],
    )

    interop_test = root / "app/src/test/java/pro/babasitaram/vault/core/crypto/ExtensionAndroidV3InteropTest.kt"
    replace_required(
        interop_test,
        [
            (
                "import kotlinx.serialization.json.jsonObject\n",
                "import pro.babasitaram.vault.core.model.VaultJson\n"
                "import kotlinx.serialization.json.jsonObject\n",
            )
        ],
        ["import pro.babasitaram.vault.core.model.VaultJson"],
    )

    failure_test = root / "app/src/test/java/pro/babasitaram/vault/data/FileVaultBlobStoreFailureInjectionTest.kt"
    replace_required(
        failure_test,
        [
            (
                'VaultWriteHooks.Step.ATOMIC_MOVE -> throw java.nio.file.AtomicMoveNotSupportedException("injected")',
                'VaultWriteHooks.Step.ATOMIC_MOVE -> throw java.nio.file.AtomicMoveNotSupportedException("vault.blob.tmp", "vault.blob", "injected")',
            )
        ],
        ['AtomicMoveNotSupportedException("vault.blob.tmp", "vault.blob", "injected")'],
    )

    settings_test = root / "app/src/test/java/pro/babasitaram/vault/domain/SettingsAndBackupUseCasesTest.kt"
    replace_required(
        settings_test,
        [
            (
                "fun err(o: String, n: String, c: String) =",
                "suspend fun err(o: String, n: String, c: String) =",
            )
        ],
        ["suspend fun err(o: String, n: String, c: String)"],
    )

    gradle_file = root / "app/build.gradle.kts"
    gradle_text = gradle_file.read_text(encoding="utf-8")
    if "testImplementation(kotlin(\"test\"))" not in gradle_text:
        anchor = "    testImplementation(libs.junit5.api)\n"
        if anchor not in gradle_text:
            raise SystemExit(f"PATCH FAILED {gradle_file}: test dependency anchor missing")
        gradle_text = gradle_text.replace(
            anchor,
            anchor + "    testImplementation(kotlin(\"test\"))\n",
            1,
        )
        gradle_file.write_text(gradle_text, encoding="utf-8")
        print("PATCHED app/build.gradle.kts: kotlin test dependency")
    else:
        print("UNCHANGED app/build.gradle.kts: kotlin test dependency already present")

    editor = root / "app/src/main/java/pro/babasitaram/vault/presentation/editor/EntryEditorScreen.kt"
    editor_import_text = editor.read_text(encoding="utf-8") if editor.is_file() else ""
    if "import androidx.compose.foundation.shape.RoundedCornerShape\n" not in editor_import_text:
        editor_import_text = editor_import_text.replace(
            "import androidx.compose.foundation.layout.Arrangement\n",
            "import androidx.compose.foundation.layout.Arrangement\nimport androidx.compose.foundation.shape.RoundedCornerShape\n",
            1,
        )
        editor.write_text(editor_import_text, encoding="utf-8")
        print("PATCHED EntryEditor RoundedCornerShape import")
    if "import pro.babasitaram.vault.presentation.components.AppElevation\n" not in editor_import_text:
        editor_import_text = editor_import_text.replace(
            "import pro.babasitaram.vault.presentation.components.AppDimens\n",
            "import pro.babasitaram.vault.presentation.components.AppDimens\n"
            "import pro.babasitaram.vault.presentation.components.AppElevation\n"
            "import pro.babasitaram.vault.presentation.components.AppShapes\n",
            1,
        )
        editor.write_text(editor_import_text, encoding="utf-8")
        print("PATCHED EntryEditor imports")
    replace_region(
        editor,
        "    Column(verticalArrangement = Arrangement.spacedBy(AppDimens.Xxs)) {",
        "        OutlinedButton(onClick = { query = \"\"; dialogOpen = true }, modifier = Modifier.fillMaxWidth()) {",
        """    Column(verticalArrangement = Arrangement.spacedBy(AppDimens.Xxs)) {
        Surface(
            modifier = Modifier
                .fillMaxWidth()
                .clickable { dialogOpen = true },
            shape = RoundedCornerShape(AppShapes.Small),
            tonalElevation = AppElevation.Card
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(AppDimens.Medium),
                horizontalArrangement = Arrangement.spacedBy(AppDimens.Small),
                verticalAlignment = androidx.compose.ui.Alignment.CenterVertically
            ) {
                if (selectedPackage.isNotBlank()) {
                    val selectedIcon = remember(context, selectedPackage) {
                        runCatching {
                            context.packageManager
                                .getApplicationIcon(selectedPackage)
                                .toBitmap(96, 96)
                        }.getOrNull()
                    }
                    if (selectedIcon != null) {
                        Image(
                            selectedIcon.asImageBitmap(),
                            contentDescription = selectedName.ifBlank { selectedPackage },
                            modifier = Modifier.size(AppDimens.SmallFieldIcon)
                        )
                    } else {
                        Icon(
                            Icons.Default.Android,
                            contentDescription = selectedName.ifBlank { selectedPackage },
                            modifier = Modifier.size(AppDimens.IconSize)
                        )
                    }
                } else {
                    Icon(
                        Icons.Default.Android,
                        contentDescription = null,
                        modifier = Modifier.size(AppDimens.IconSize)
                    )
                }
                Column(Modifier.weight(1f)) {
                    Text(
                        text = if (selectedName.isBlank() && selectedPackage.isBlank()) {
                            stringResource(R.string.p17_loc_196)
                        } else {
                            selectedName.ifBlank { selectedPackage }
                        },
                        style = MaterialTheme.typography.bodyLarge
                    )
                    Text(
                        text = when {
                            selectedPackage.isNotBlank() -> selectedPackage
                            selectedName.isNotBlank() -> stringResource(R.string.p17_entry_relink_app)
                            else -> stringResource(R.string.p17_entry_select_android_app)
                        },
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        }
""",
    )

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
