#!/usr/bin/env python3
from pathlib import Path
import argparse

p = argparse.ArgumentParser()
p.add_argument("stage", choices=["tests", "production"])
args = p.parse_args()
root = Path("GPTWake")


def replace_once(path: Path, old: str, new: str):
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"Expected text not found in {path}: {old[:80]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def insert_before_last_brace(path: Path, block: str):
    text = path.read_text(encoding="utf-8")
    pos = text.rfind("\n}")
    if pos < 0:
        raise SystemExit(f"Could not find final brace in {path}")
    path.write_text(text[:pos] + "\n" + block.rstrip() + text[pos:], encoding="utf-8")


if args.stage == "tests":
    test = root / "app/src/test/java/com/desmond/gptwake/WakeWordTokenizerTest.java"
    marker = "spanishSebasUsesTunedPhonemeVariants"
    if marker not in test.read_text(encoding="utf-8"):
        insert_before_last_brace(test, r'''
    @Test
    public void spanishSebasUsesTunedPhonemeVariants() {
        var result = tokenizer.convert("ey sebas");
        assertTrue(result.ok);
        assertEquals(WakeWordTokenizer.Err.NONE, result.err);
        assertEquals(3, result.errCount);
        assertTrue(result.keywordLine.contains("EY1 S EH1 B AA0 S @ey_sebas"));
        assertTrue(result.keywordLine.contains("EY1 S EY1 B AA0 S @ey_sebas_alt1"));
        assertTrue(result.keywordLine.contains("EY1 S EH1 B AH0 S @ey_sebas_alt2"));
        assertTrue(result.keywordLine.contains("EY1 S EH1 B AE0 S @ey_sebas_alt3"));
    }
''')
    print("Added failing Ey Sebas tokenizer test")

elif args.stage == "production":
    tokenizer = root / "app/src/main/java/com/desmond/gptwake/WakeWordTokenizer.java"
    text = tokenizer.read_text(encoding="utf-8")
    marker = "SPANISH_SEBAS_PRIMARY"
    if marker not in text:
        old = '''        if (p.isEmpty()) return Result.fail(Err.EMPTY, null);\n\n        List<String> tokens = new ArrayList<>();'''
        new = '''        if (p.isEmpty()) return Result.fail(Err.EMPTY, null);\n\n        // Sebastian edition: the bundled acoustic model is Chinese/English, but these CMU-phone\n        // variants deliberately approximate Spanish \"Ey Sebas\". Arming several close variants\n        // improves recall for a Spanish speaker without adding cloud services or another model.\n        if (\"ey sebas\".equalsIgnoreCase(p) || \"hey sebas\".equalsIgnoreCase(p)) {\n            final String SPANISH_SEBAS_PRIMARY = \"EY1 S EH1 B AA0 S\";\n            String keywordLines = SPANISH_SEBAS_PRIMARY + \" @ey_sebas\\n\"\n                    + \"EY1 S EY1 B AA0 S @ey_sebas_alt1\\n\"\n                    + \"EY1 S EH1 B AH0 S @ey_sebas_alt2\\n\"\n                    + \"EY1 S EH1 B AE0 S @ey_sebas_alt3\";\n            return new Result(true, SPANISH_SEBAS_PRIMARY, SPANISH_SEBAS_PRIMARY,\n                    keywordLines, Err.NONE, null, 3);\n        }\n\n        List<String> tokens = new ArrayList<>();'''
        replace_once(tokenizer, old, new)

    store = root / "app/src/main/java/com/desmond/gptwake/WakeWordStore.java"
    replace_once(store,
        '    public static final String DEFAULT_PHRASE = "芝麻开门";\n    /** Matches assets/kws/keywords.txt, used when nothing custom is stored. */\n    public static final String DEFAULT_LINE = "zh ī m á k āi m én @芝麻开门";',
        '    public static final String DEFAULT_PHRASE = "ey sebas";\n    /** Tuned Spanish-accent variants for the dedicated Sebastian build. */\n    public static final String DEFAULT_LINE = "EY1 S EH1 B AA0 S @ey_sebas\\n"\n            + "EY1 S EY1 B AA0 S @ey_sebas_alt1\\n"\n            + "EY1 S EH1 B AH0 S @ey_sebas_alt2\\n"\n            + "EY1 S EH1 B AE0 S @ey_sebas_alt3";')

    engine = root / "app/src/main/java/com/desmond/gptwake/KwsEngine.java"
    replace_once(engine, '    public static volatile float keywordsScore = 1.5f;\n    public static final float DEFAULT_THRESHOLD = 0.40f;',
                       '    public static volatile float keywordsScore = 1.8f;\n    public static final float DEFAULT_THRESHOLD = 0.28f;')

    gradle = root / "app/build.gradle.kts"
    replace_once(gradle, '        applicationId = "com.desmond.gptwake"',
                         '        applicationId = "com.desmond.gptwake.sebastian"')
    replace_once(gradle, '        versionCode = 3\n        versionName = "1.1.0"',
                         '        versionCode = 100\n        versionName = "1.1.0-sebastian-0.1"')

    strings = root / "app/src/main/res/values/strings.xml"
    replace_once(strings, '<string name="app_name">GPTWake</string>',
                          '<string name="app_name">Sebastián Wake</string>')
    replace_once(strings, '<string name="tagline">Offline wake word · opens ChatGPT voice</string>',
                          '<string name="tagline">“Ey Sebas” · abre ChatGPT Voice</string>')
    replace_once(strings, '<string name="wake_word_hint">Use a different wake word (Chinese or English)</string>',
                          '<string name="wake_word_hint">Escribe “ey sebas” para el detector optimizado</string>')

    # Keep the upstream replacement test explicit about its sensitivity fixture.
    # The edition changes the default phrase, not the custom-replaces-default contract.
    engine_test = root / "app/src/test/java/com/desmond/gptwake/KwsEngineTest.java"
    replace_once(engine_test,
        '        KwsEngine.keywordsThreshold = KwsEngine.DEFAULT_THRESHOLD;',
        '        KwsEngine.keywordsThreshold = 0.40f;')
    replace_once(engine_test,
        '        assertEquals("zh ī m á k āi m én :1.5 #0.4 @芝麻开门", Spotter.keywords);',
        '        assertEquals("EY1 S EH1 B AA0 S :1.5 #0.4 @ey_sebas\\n"\n'
        '                + "EY1 S EY1 B AA0 S @ey_sebas_alt1\\n"\n'
        '                + "EY1 S EH1 B AH0 S @ey_sebas_alt2\\n"\n'
        '                + "EY1 S EH1 B AE0 S @ey_sebas_alt3", Spotter.keywords);')

    print("Applied Sebastian production patch")
