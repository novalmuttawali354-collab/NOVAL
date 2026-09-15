package com.antokon.pkmobile;

import java.util.Locale;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public final class TextCleaner {
    private TextCleaner() {}

    public static String clean(String input) {
        if (input == null) return "";

        String x = input
                .replace("\u0000", "")
                .replace("<ent__>", "\n")
                .replace("\r\n", "\n")
                .replace('\r', '\n')
                .replace("\uFEFF", "")
                .trim();

        Matcher macroPrefix = Pattern.compile("(?is)text#macro\\s*:").matcher(x);
        if (macroPrefix.find()) {
            x = x.substring(macroPrefix.end()).trim();
        }

        x = decodeHtmlEntities(x);

        String low = x.toLowerCase(Locale.ROOT);
        if (looksHtml(low)) {
            Matcher body = Pattern.compile("(?is)<body\\b[^>]*>(.*?)</body\\s*>").matcher(x);
            if (body.find()) {
                x = body.group(1);
            } else {
                x = x.replaceAll("(?is)<head\\b[^>]*>.*?</head\\s*>", "");
            }

            x = x.replaceAll("(?i)<br\\s*/?>", "\n");
            x = x.replaceAll("(?i)</?(p|div|li|tr|td|h[1-6])\\b[^>]*>", "\n");
            x = x.replaceAll("(?is)<[^>]+>", "");
        }

        x = decodeHtmlEntities(x);

        x = x.replaceFirst("(?is)^\\s*text#macro\\s*:\\s*", "");
        x = x.replaceAll("(?is)</?(html|head|body)\\b[^>]*>", "");
        x = x.replaceAll("(?is)<meta\\b[^>]*>", "");
        x = x.replaceAll("(?i)<br\\s*/?>", "\n");

        x = x.replace('\u00A0', ' ');
        x = x.replaceAll("[ \\t]+\\n", "\n");
        x = x.replaceAll("\\n[ \\t]+", "\n");
        x = x.replaceAll("\\n{3,}", "\n\n");
        return x.trim();
    }

    private static boolean looksHtml(String low) {
        return low.contains("<html") || low.contains("<head") || low.contains("<body") ||
                low.contains("<meta") || low.contains("<br") || low.contains("</html") ||
                low.contains("</body") || low.contains("</head");
    }

    public static boolean dirty(String input) {
        if (input == null || input.isEmpty()) return false;
        String s = input.toLowerCase(Locale.ROOT);
        return Pattern.compile("(?is)text#macro\\s*:").matcher(s).find() || looksHtml(s);
    }

    private static String decodeHtmlEntities(String value) {
        String x = value
                .replace("&nbsp;", " ")
                .replace("&#160;", " ")
                .replace("&amp;", "&")
                .replace("&lt;", "<")
                .replace("&gt;", ">")
                .replace("&quot;", "\"")
                .replace("&#39;", "'")
                .replace("&apos;", "'");

        Matcher m = Pattern.compile("&#(x?[0-9A-Fa-f]+);").matcher(x);
        StringBuffer out = new StringBuffer();
        while (m.find()) {
            try {
                String n = m.group(1);
                int cp = (n.startsWith("x") || n.startsWith("X"))
                        ? Integer.parseInt(n.substring(1), 16)
                        : Integer.parseInt(n, 10);
                m.appendReplacement(out, Matcher.quoteReplacement(new String(Character.toChars(cp))));
            } catch (Exception ex) {
                m.appendReplacement(out, Matcher.quoteReplacement(m.group(0)));
            }
        }
        m.appendTail(out);
        return out.toString();
    }
}
