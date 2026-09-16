package com.desmond.gptwake;

import java.util.Locale;

/** Whole-word matching; a name on its own must never activate the assistant. */
public final class SpanishWakePhrase {
    static final String GRAMMAR = "[\"ey sebas\",\"hey sebas\",\"eh sebas\",\"[unk]\"]";
    public static boolean isSelected(String phrase) {
        String p = normalize(phrase);
        return p.equals("ey sebas") || p.equals("hey sebas") || p.equals("eh sebas");
    }
    static boolean matches(String text) {
        String words = " " + normalize(text) + " ";
        return words.contains(" ey sebas ") || words.contains(" hey sebas ")
                || words.contains(" eh sebas ");
    }
    private static String normalize(String value) {
        return value == null ? "" : value.trim().toLowerCase(Locale.ROOT).replaceAll("\\s+", " ");
    }
}
