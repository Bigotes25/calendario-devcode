package com.desmond.gptwake;

import static org.junit.Assert.*;
import org.junit.Test;

public class SpanishWakePhraseTest {
    @Test public void acceptsCompleteWakePhraseWithWordBoundaries() {
        assertTrue(SpanishWakePhrase.matches("ey sebas"));
        assertTrue(SpanishWakePhrase.matches("HEY   SEBAS"));
        assertTrue(SpanishWakePhrase.matches("[unk] eh sebas [unk]"));
    }
    @Test public void rejectsNamesAndNearMatches() {
        for (String text : new String[]{"", "sebas", "hey", "hola sebas", "que sepas",
                "te vas", "ey sebastian", "ey sebasito", "ayer sebas", "[unk] sebas"}) {
            assertFalse(text, SpanishWakePhrase.matches(text));
        }
        assertFalse(SpanishWakePhrase.matches(null));
    }
    @Test public void usesSpanishOnlyForTheDedicatedPhrase() {
        assertTrue(SpanishWakePhrase.isSelected(" Ey SEBAS "));
        assertFalse(SpanishWakePhrase.isSelected("open door"));
        assertFalse(SpanishWakePhrase.isSelected("hola sebas"));
    }
}
