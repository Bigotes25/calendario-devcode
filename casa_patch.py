from pathlib import Path
import argparse
import hashlib
import re
import shutil

p = argparse.ArgumentParser()
p.add_argument('stage', choices=['tests', 'production'])
args = p.parse_args()
root = Path('GPTWake')
main = root/'app/src/main/java/com/desmond/gptwake'
tests = root/'app/src/test/java/com/desmond/gptwake'

def replace(path, old, new):
    text = path.read_text()
    assert text.count(old) == 1, (str(path), old[:80], text.count(old))
    path.write_text(text.replace(old, new, 1))

if args.stage == 'tests':
    shutil.copyfile('casa/GptLauncherCasaTest.java', tests/'GptLauncherCasaTest.java')
else:
    protected = [p for p in main.rglob('*') if p.is_file()
                 and p.name not in {'GptLauncher.java', 'WakeController.java'}]
    before = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    launcher = main/'GptLauncher.java'
    replace(launcher, '    public static boolean launchDirect(Context context) {', '''    public static boolean launchProjectVoice(Context context) {
        try {
            context.startActivity(new Intent(Intent.ACTION_VIEW,
                    Uri.parse("https://chatgpt.com/g/g-p-6aaaa3638f5081919f0455cc3f848b8f-sebastian-casa/project?mode=voice"))
                    .setPackage(GPT_PACKAGE)
                    .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
            // Dispatch is not proof that ChatGPT opened the project or started Voice.
            L.i("CASA_PROJECT_LINK_DISPATCHED contextUnverified=true");
            return true;
        } catch (Throwable t) {
            L.e("CASA_PROJECT_LINK_REJECTED", t);
            return false;
        }
    }

    public static boolean launchDirect(Context context) {''')
    replace(launcher, 'return launchDirect(context) || launchDeeplink(context);',
            'return launchProjectVoice(context) || launchDirect(context) || launchDeeplink(context);')
    controller = main/'WakeController.java'
    replace(controller, '    private boolean deeplinkTried;',
            '    private boolean deeplinkTried;\n    private boolean projectPending;')
    replace(controller, '''        deeplinkTried = false;
        L.i("CHATGPT_LAUNCH_ATTEMPT route=AssistantActivity");''', '''        deeplinkTried = false;
        L.i("CHATGPT_LAUNCH_ATTEMPT route=CasaProjectVoice");
        projectPending = GptLauncher.launchProjectVoice(ctx);
        if (projectPending) {
            later(this::checkVoiceConfirm, DEEPLINK_CONFIRM_MS);
        } else {
            launchLegacyVoice();
        }
    }

    private void launchLegacyVoice() {
        projectPending = false;
        L.i("CASA_FALLBACK projectContextNotGuaranteed=true");
        L.i("CHATGPT_LAUNCH_ATTEMPT route=AssistantActivity");''')
    replace(controller, '        if (!deeplinkTried) {', '''        if (projectPending) {
            L.i("CASA_PROJECT_VOICE_UNCONFIRMED fallingBack=true");
            launchLegacyVoice();
            return;
        }
        if (!deeplinkTried) {''')
    test = tests/'WakeControllerTest.java'
    text = test.read_text()
    pos = text.rfind('\n}')
    assert pos > 0
    test.write_text(text[:pos] + '\n' + Path('casa/controller-tests.txt').read_text() + text[pos:])
    for strings in (root/'app/src/main/res').glob('values*/strings.xml'):
        text = strings.read_text()
        text = re.sub(r'(<string name="app_name">)[^<]*(</string>)', r'\g<1>Sebastián · Casa\2', text)
        text = text.replace('GPTWake is listening for the wake word', 'Sebastián · Casa is listening for Ey Sebas')
        strings.write_text(text)
    gradle = root/'app/build.gradle.kts'
    replace(gradle, 'versionCode = 101', 'versionCode = 102')
    replace(gradle, '1.1.0-sebastian-0.2', '1.1.0-sebastian-casa-0.3')
    after = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    assert before == after, 'Unexpected change outside launcher/controller'
    Path('casa-detector-preservation.txt').write_text(
        'PASS: all main Java/Kotlin files except GptLauncher and WakeController are byte-identical to the Spanish v0.2 build before Casa branding.\n'
        + '\n'.join(f'{digest}  {path}' for path, digest in after.items()) + '\n')
    print('Applied Casa launch target; detector and Spanish engine unchanged')
