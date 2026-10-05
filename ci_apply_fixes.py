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

    session_key_store = root / "app/src/main/java/pro/babasitaram/vault/core/crypto/SessionKeyStore.kt"
    sks_text = session_key_store.read_text(encoding="utf-8")
    sks_text = sks_text.replace("import android.os.SystemClock\n", "")
    sks_text = sks_text.replace(
        "nowElapsedMs: Long = SystemClock.elapsedRealtime()",
        "nowElapsedMs: Long = monotonicNowMs()",
    )
    sks_text = sks_text.replace(
        "fun sessionRemainingMs(nowElapsedMs: Long = SystemClock.elapsedRealtime())",
        "fun sessionRemainingMs(nowElapsedMs: Long = monotonicNowMs())",
    )
    sks_text = sks_text.replace(
        "fun hasValidSession(nowElapsedMs: Long = SystemClock.elapsedRealtime())",
        "fun hasValidSession(nowElapsedMs: Long = monotonicNowMs())",
    )
    sks_text = sks_text.replace(
        "isExpiredLocked(SystemClock.elapsedRealtime())",
        "isExpiredLocked(monotonicNowMs())",
    )
    marker = "    private fun isExpiredLocked(nowElapsedMs: Long): Boolean =\n"
    if "private fun monotonicNowMs()" not in sks_text:
        if marker not in sks_text:
            raise SystemExit(f"PATCH FAILED {session_key_store}: helper marker missing")
        sks_text = sks_text.replace(
            marker,
            "    private fun monotonicNowMs(): Long = System.nanoTime() / 1_000_000L\n\n" + marker,
            1,
        )
    if "SystemClock.elapsedRealtime()" in sks_text:
        raise SystemExit(f"PATCH FAILED {session_key_store}: SystemClock remained")
    session_key_store.write_text(sks_text, encoding="utf-8")
    print("PATCHED SessionKeyStore.kt: JVM-safe monotonic clock")

    auto_lock = root / "app/src/main/java/pro/babasitaram/vault/core/security/AutoLockController.kt"
    al_text = auto_lock.read_text(encoding="utf-8")
    al_text = al_text.replace("import android.os.SystemClock\n", "")
    al_text = al_text.replace("internal var clock: () -> Long = { SystemClock.elapsedRealtime() }",
                              "internal var clock: () -> Long = { System.nanoTime() / 1_000_000L }")
    if "SystemClock.elapsedRealtime()" in al_text:
        raise SystemExit(f"PATCH FAILED {auto_lock}: SystemClock remained")
    auto_lock.write_text(al_text, encoding="utf-8")
    print("PATCHED AutoLockController.kt: JVM-safe monotonic clock")

    settings_store = root / "app/src/main/java/pro/babasitaram/vault/data/local/preferences/SettingsDataStore.kt"
    settings_text = settings_store.read_text(encoding="utf-8")
    old_assignment = "prefs[AUTO_LOCK] = n.backgroundGraceSeconds"
    if old_assignment in settings_text:
        settings_text = settings_text.replace(old_assignment, "prefs[AUTO_LOCK] = n.autoLockSeconds", 1)
        settings_store.write_text(settings_text, encoding="utf-8")
        print("PATCHED SettingsDataStore.kt: persist autoLockSeconds correctly")
    elif "prefs[AUTO_LOCK] = n.autoLockSeconds" in settings_text:
        print("UNCHANGED SettingsDataStore.kt: auto lock assignment already correct")
    else:
        raise SystemExit(f"PATCH FAILED {settings_store}: AUTO_LOCK assignment missing")

    backup_manager = root / "app/src/main/java/pro/babasitaram/vault/data/backup/AutoBackupManager.kt"
    backup_text = backup_manager.read_text(encoding="utf-8")
    old_managed = """    fun isManagedOldName(name: String, finalName: String): Boolean =
        isQuarantine(name) || isSafRecovery(name) || isStaging(name) || isCanonicalFamily(name, finalName)
"""
    new_managed = """    fun isManagedOldName(name: String, finalName: String): Boolean =
        !name.equals(finalName, ignoreCase = true) &&
            (isQuarantine(name) || isSafRecovery(name) || isStaging(name) || isNumberedDuplicate(name, finalName) || isLegacyDated(name))
"""
    if old_managed in backup_text:
        backup_text = backup_text.replace(old_managed, new_managed, 1)
        backup_manager.write_text(backup_text, encoding="utf-8")
        print("PATCHED AutoBackupManager.kt: final name excluded from old-name cleanup")
    elif new_managed in backup_text:
        print("UNCHANGED AutoBackupManager.kt: old-name predicate already fixed")
    else:
        raise SystemExit(f"PATCH FAILED {backup_manager}: managed-name predicate missing")

    # Test-source fixes: compare against the known-working Phase15V tests and keep new assertions,
    # but restore proper scope/imports/signatures rather than masking compiler failures.
    autofill_test = root / "app/src/test/java/pro/babasitaram/vault/autofill/AutofillParserTest.kt"
    autofill_text = autofill_test.read_text(encoding="utf-8")
    extra_start = autofill_text.find("    @Test fun `PIN field with no declared limit is still a PIN()`")
    if extra_start < 0:
        extra_start = autofill_text.find("    @Test fun `PIN field with no declared limit is still a PIN`")
    if extra_start >= 0:
        extra_end = autofill_text.find("\n}\n", extra_start)
        if extra_end < 0:
            raise SystemExit(f"PATCH FAILED {autofill_test}: extra test block end not found")
        extra_block = autofill_text[extra_start:extra_end]
        autofill_text = autofill_text[:extra_start] + autofill_text[extra_end:]
        first_class_end = autofill_text.find("\n}\n\n/** Extra field-name words")
        if first_class_end < 0:
            raise SystemExit(f"PATCH FAILED {autofill_test}: first class boundary not found")
        autofill_text = autofill_text[:first_class_end] + "\n" + extra_block + autofill_text[first_class_end:]
        autofill_test.write_text(autofill_text, encoding="utf-8")
        print("PATCHED AutofillParserTest.kt: moved new PIN tests into first test class")
    else:
        print("UNCHANGED AutofillParserTest.kt: no extra PIN block found")

    interop_test = root / "app/src/test/java/pro/babasitaram/vault/core/crypto/ExtensionAndroidV3InteropTest.kt"
    interop_text = interop_test.read_text(encoding="utf-8")
    if "import pro.babasitaram.vault.core.model.VaultJson" not in interop_text:
        interop_text = interop_text.replace(
            "import org.junit.jupiter.api.Test\n",
            "import org.junit.jupiter.api.Test\n"
            "import pro.babasitaram.vault.core.model.VaultJson\n",
            1,
        )
        interop_test.write_text(interop_text, encoding="utf-8")
        print("PATCHED ExtensionAndroidV3InteropTest.kt: VaultJson import")

    failure_test = root / "app/src/test/java/pro/babasitaram/vault/data/FileVaultBlobStoreFailureInjectionTest.kt"
    replace_required(
        failure_test,
        [
            (
                'AtomicMoveNotSupportedException("injected")',
                'AtomicMoveNotSupportedException("vault.blob.tmp", "vault.blob", "injected")',
            )
        ],
        ['AtomicMoveNotSupportedException("vault.blob.tmp", "vault.blob", "injected")'],
    )

    autobackup_test = root / "app/src/test/java/pro/babasitaram/vault/data/backup/AutoBackupNamesTest.kt"
    autobackup_text = autobackup_test.read_text(encoding="utf-8")
    autobackup_text = autobackup_text.replace("import kotlin.test.Test\n", "import org.junit.jupiter.api.Test\n")
    autobackup_text = autobackup_text.replace("import kotlin.test.assertEquals\n", "import org.junit.jupiter.api.Assertions.assertEquals\n")
    autobackup_text = autobackup_text.replace("import kotlin.test.assertFalse\n", "import org.junit.jupiter.api.Assertions.assertFalse\n")
    autobackup_text = autobackup_text.replace("import kotlin.test.assertTrue\n", "import org.junit.jupiter.api.Assertions.assertTrue\n")
    autobackup_test.write_text(autobackup_text, encoding="utf-8")
    print("PATCHED AutoBackupNamesTest.kt: JUnit5 imports")

    settings_test = root / "app/src/test/java/pro/babasitaram/vault/domain/SettingsAndBackupUseCasesTest.kt"
    replace_required(
        settings_test,
        [
            (
                "        fun err(o: String, n: String, c: String) = ((e.change(o.toCharArray(), n.toCharArray(), c.toCharArray())) as VaultResult.Failure).error",
                "        suspend fun err(o: String, n: String, c: String) = ((e.change(o.toCharArray(), n.toCharArray(), c.toCharArray())) as VaultResult.Failure).error",
            )
        ],
        ["        suspend fun err(o: String, n: String, c: String)"],
    )

    gradle_file = root / "app/build.gradle.kts"
    gradle_text = gradle_file.read_text(encoding="utf-8")
    if '    testImplementation(kotlin("test"))\n' in gradle_text:
        gradle_text = gradle_text.replace('    testImplementation(kotlin("test"))\n', "")
        gradle_file.write_text(gradle_text, encoding="utf-8")
        print("PATCHED app/build.gradle.kts: removed unnecessary kotlin-test dependency")

    editor_vm = root / "app/src/main/java/pro/babasitaram/vault/presentation/editor/EntryEditorViewModel.kt"
    vm_text = editor_vm.read_text(encoding="utf-8")
    old_type = """    type = (base?.type.orEmpty()).ifBlank {
        if (recordType == "login" || recordType.isBlank()) {
            if (appPackage.isNotBlank() && url.isBlank()) "app" else "website"
        } else ""
    },
"""
    new_type = """    type = base?.type.orEmpty().ifBlank {
        if (base == null && (recordType == "login" || recordType.isBlank())) {
            if (appPackage.isNotBlank() && url.isBlank()) "app" else "website"
        } else ""
    },
"""
    if old_type in vm_text:
        vm_text = vm_text.replace(old_type, new_type, 1)
        editor_vm.write_text(vm_text, encoding="utf-8")
        print("PATCHED EntryEditorViewModel.kt: preserve existing blank type on edit")
    elif new_type in vm_text:
        print("UNCHANGED EntryEditorViewModel.kt: type preservation already fixed")
    else:
        raise SystemExit(f"PATCH FAILED {editor_vm}: type assignment marker missing")

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
