from pathlib import Path
import re

root = Path('PKMobileExpanderV3')
pkg = root / 'app/src/main/java/com/antokon/pkmobile'

# Install the cleaner into the Android source tree.
(pkg / 'TextCleaner.java').write_text(Path('scripts/TextCleaner.java').read_text())

# Parser: clean at extraction, helper, and final insertion.
p = pkg / 'PerfectKeyboard4pkParser.java'
s = p.read_text()
old = 'String replacement = cleanupContent(lines[s + 49]);'
if old not in s:
    raise SystemExit('Parser extraction line not found')
s = s.replace(old, 'String replacement = TextCleaner.clean(cleanupContent(lines[s + 49]));', 1)

old_cleanup = '''    private static String cleanupContent(String s) {
        if (s == null) return "";
        String x = s.replace("<ent__>", "\\n");
        // Trim hanya newline/spasi di ujung; isi di tengah tidak diubah.
        int a = 0, b = x.length();
        while (a < b && Character.isWhitespace(x.charAt(a))) a++;
        while (b > a && Character.isWhitespace(x.charAt(b - 1))) b--;
        return x.substring(a, b);
    }'''
new_cleanup = '''    private static String cleanupContent(String s) {
        return TextCleaner.clean(s);
    }'''
if old_cleanup not in s:
    raise SystemExit('cleanupContent block not found')
s = s.replace(old_cleanup, new_cleanup, 1)

old_put = '        map.put(key, replacement);'
new_put = '''        String clean = TextCleaner.clean(replacement);
        if (clean.isEmpty()) return;
        if (TextCleaner.dirty(clean)) throw new IllegalStateException("HTML Perfect Keyboard masih tersisa pada trigger " + key);
        map.put(key, clean);'''
if old_put not in s:
    raise SystemExit('Parser addUnique put not found')
s = s.replace(old_put, new_put, 1)
p.write_text(s)

# Repository: clean every way replacement text can enter/leave.
p = pkg / 'MacroRepository.java'
s = p.read_text()
replacements = [
    ('String replacement = o.optString("replacement", "");', 'String replacement = TextCleaner.clean(o.optString("replacement", ""));'),
    ('o.put("replacement", e.getValue());', 'String clean = TextCleaner.clean(e.getValue());\n            if (TextCleaner.dirty(clean)) throw new IllegalStateException("HTML Perfect Keyboard masih tersisa pada trigger " + e.getKey());\n            o.put("replacement", clean);'),
    ('String replacement = s.optString("replacement", "");', 'String replacement = TextCleaner.clean(s.optString("replacement", ""));'),
    ('String replacement = trimBlankLines(content.toString());', 'String replacement = TextCleaner.clean(trimBlankLines(content.toString()));'),
    ('s.put("replacement", e.getValue());', 'String clean = TextCleaner.clean(e.getValue());\n            if (TextCleaner.dirty(clean)) throw new IllegalStateException("HTML Perfect Keyboard masih tersisa pada trigger " + e.getKey());\n            s.put("replacement", clean);'),
]
for old, new in replacements:
    if old not in s:
        raise SystemExit('Repository patch target not found: ' + old)
    s = s.replace(old, new, 1)

old_export = 'root.put("exportedAt", System.currentTimeMillis());'
new_export = '''java.text.SimpleDateFormat iso = new java.text.SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'", java.util.Locale.US);
        iso.setTimeZone(java.util.TimeZone.getTimeZone("UTC"));
        root.put("exportedAt", iso.format(new java.util.Date()));'''
if old_export not in s:
    raise SystemExit('exportedAt target not found')
s = s.replace(old_export, new_export, 1)

old_return = '        return root.toString(2);'
new_return = '''        String json = root.toString(2);
        String lowerJson = json.toLowerCase(java.util.Locale.ROOT);
        if (lowerJson.contains("text#macro:") || lowerJson.contains("<html") ||
                lowerJson.contains("<head") || lowerJson.contains("<body") || lowerJson.contains("<meta")) {
            throw new IllegalStateException("JSON dibatalkan karena wrapper HTML Perfect Keyboard masih terdeteksi");
        }
        return json;'''
if old_return not in s:
    raise SystemExit('JSON return target not found')
s = s.replace(old_return, new_return, 1)
p.write_text(s)

# Converter-only manifest.
p = root / 'app/src/main/AndroidManifest.xml'
manifest = p.read_text()
manifest = re.sub(r'\n\s*<service[\s\S]*?</service>\s*', '\n', manifest, count=1)
p.write_text(manifest)

# Separate package/version so this cannot be confused with older builds.
p = root / 'app/build.gradle.kts'
s = p.read_text()
s = s.replace('applicationId = "com.antokon.pkmobile"', 'applicationId = "com.antokon.pkconverterv8"')
s = s.replace('versionCode = 3', 'versionCode = 80')
s = s.replace('versionName = "3.0"', 'versionName = "8.0"')
p.write_text(s)

# Converter-only UI and unmistakable V8 identity.
p = pkg / 'MainActivity.java'
s = p.read_text().replace('PK Mobile Expander V3', 'PK Converter V8 CLEAN')
s = s.replace('Button accessBtn = button("BUKA PENGATURAN AKSESIBILITAS");', 'Button accessBtn = button("BUKA PENGATURAN AKSESIBILITAS");\n        accessBtn.setVisibility(View.GONE);')
s = s.replace('enabledSwitch.setText("Aktifkan text expander");', 'enabledSwitch.setText("Aktifkan text expander");\n        enabledSwitch.setVisibility(View.GONE);')
s = s.replace('spaceSwitch.setText("Jalankan shortcut saat tekan spasi / Enter");', 'spaceSwitch.setText("Jalankan shortcut saat tekan spasi / Enter");\n        spaceSwitch.setVisibility(View.GONE);')
s = s.replace('i.putExtra(Intent.EXTRA_TITLE, "PKMobile_Hasil_Convert.json");', 'i.putExtra(Intent.EXTRA_TITLE, "PKConverter_V8_CLEAN.json");')
s = s.replace('        boolean service = isAccessibilityServiceEnabled();\n        statusText.setText(service ? "Layanan: AKTIF ✓" : "Layanan: BELUM AKTIF");\n        statusText.setTextColor(service ? Color.rgb(25, 120, 70) : Color.rgb(180, 55, 55));', '        statusText.setText("Mode: CONVERTER V8 CLEAN ✓");\n        statusText.setTextColor(Color.rgb(25, 120, 70));')
p.write_text(s)

p = root / 'app/src/main/res/values/strings.xml'
p.write_text(p.read_text().replace('PK Mobile Expander V3', 'PK Converter V8 CLEAN'))
