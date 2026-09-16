from pathlib import Path
import shutil

root = Path('GPTWake')
main = root / 'app/src/main/java/com/desmond/gptwake'
tests = root / 'app/src/test/java/com/desmond/gptwake'
def replace(path, old, new):
    s = path.read_text()
    assert old in s, (str(path), old[:80])
    path.write_text(s.replace(old, new))

for name in ['SpanishWakePhrase.java', 'SpanishWakeEngine.java']:
    shutil.copyfile(Path('spanish') / name, main / name)
shutil.copyfile('spanish/SpanishWakePhraseTest.java', tests / 'SpanishWakePhraseTest.java')

p = main / 'KwsEngine.java'
replace(p, '    private volatile JapaneseWakeEngine japanese;',
'''    private volatile JapaneseWakeEngine japanese;
    private volatile SpanishWakeEngine spanish;

    public synchronized void loadForContext(android.content.Context context) throws Exception {
        if (selection.language == WakeLanguage.ZH_EN && SpanishWakePhrase.isSelected(selection.phrase)) {
            if (spanish != null) return;
            release();
            spanish = SpanishWakeEngine.load(context);
            return;
        }
        if (spanish != null) release();
        load(context.getAssets());
    }''')
replace(p, 'return spotter != null || japanese != null;', 'return spotter != null || japanese != null || spanish != null;')
replace(p, '    public synchronized void newStream() {',
'''    public synchronized void newStream() {
        if (spanish != null) {
            try { spanish.newStream(); }
            catch (java.io.IOException e) { throw new IllegalStateException("Cannot start Spanish recognition", e); }
            return;
        }''')
replace(p, '    public synchronized String accept(float[] samples, int sampleRate) {',
'''    public synchronized String accept(float[] samples, int sampleRate) {
        if (spanish != null) {
            acceptCalls.incrementAndGet();
            return spanish.accept(samples, sampleRate);
        }''')
replace(p, '    public synchronized void releaseStream() {',
'''    public synchronized void releaseStream() {
        if (spanish != null) spanish.releaseStream();''')
replace(p, '    public synchronized void release() {',
'''    public synchronized void release() {
        SpanishWakeEngine es = spanish;
        spanish = null;
        if (es != null) es.release();''')
replace(main/'WakeController.java', 'kws.load(am);', 'kws.loadForContext(ctx);')
replace(main/'WakeController.java', 'kws.load(ctx.getAssets());', 'kws.loadForContext(ctx);')
replace(tests/'WakeControllerTest.java', '.load(any())', '.loadForContext(any())')
replace(root/'app/build.gradle.kts', 'versionCode = 100', 'versionCode = 101')
replace(root/'app/build.gradle.kts', '1.1.0-sebastian-0.1', '1.1.0-sebastian-0.2')
replace(root/'app/build.gradle.kts', 'dependencies {', '''dependencies {
    implementation("com.alphacephei:vosk-android:0.3.75@aar")
    implementation("net.java.dev.jna:jna:5.18.1@aar")''')
replace(root/'app/src/main/res/values/strings.xml', 'Escribe “ey sebas” para el detector optimizado',
        'Escribe “ey sebas” para el detector local en español')
print('Applied offline Spanish recognition for Ey Sebas')
