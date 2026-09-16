from pathlib import Path
import argparse,shutil,hashlib
p=argparse.ArgumentParser();p.add_argument('stage',choices=['tests','production']);a=p.parse_args()
r=Path('GPTWake/app/src');m=r/'main/java/com/desmond/gptwake';t=r/'test/java/com/desmond/gptwake'
if a.stage=='tests':
 shutil.copyfile('casa-strict/CasaStrictLaunchTest.java',t/'CasaStrictLaunchTest.java')
else:
 protected={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in m.rglob('*') if f.is_file() and f.name not in ['GptLauncher.java','WakeController.java','MainActivity.kt']}
 for name in ['CasaScreen','CasaAccessibilityService','CasaSetupActivity','GptLauncher']:
  shutil.copyfile('casa-strict/'+name+'.java',m/(name+'.java'))
 c=m/'WakeController.java';s=c.read_text()
 start=s.index('        deeplinkTried = false;',s.index('private void launchChatGpt()'))
 end=s.index('    private void scheduleVoiceConfirm',start)
 s=s[:start]+'''        L.i("CHATGPT_LAUNCH_ATTEMPT route=CasaScreenVoice");
        if (GptLauncher.launchProjectVoice(ctx)) {
            scheduleVoiceConfirm(30000);
        } else {
            CasaAccessibilityService.cancel();
            reacquire();
        }
    }

'''+s[end:]
 start=s.index('        if (projectPending) {',s.index('private void checkVoiceConfirm'))
 end=s.index('        reacquire();',start)
 s=s[:start]+'''        L.i("CASA_VOICE_TIMEOUT noGenericFallback=true");
        CasaAccessibilityService.cancel();
'''+s[end:]
 s=s.replace('    private boolean deeplinkTried;\n','').replace('    private boolean projectPending;\n','')
 s=s.replace('    private void confirmVoice() {','    private void confirmVoice() {\n        CasaAccessibilityService.cancel();')
 s=s.replace('        if (!stopped.compareAndSet(false, true)) return;','        if (!stopped.compareAndSet(false, true)) return;\n        CasaAccessibilityService.cancel();')
 c.write_text(s)
 activity=m/'MainActivity.kt';s=activity.read_text();needle='        enableEdgeToEdge()'
 assert s.count(needle)==1
 s=s.replace(needle,needle+'''\n        if (!CasaAccessibilityService.available(this)) {
            startActivity(android.content.Intent(this, CasaSetupActivity::class.java))
        }''');activity.write_text(s)
 manifest=r/'main/AndroidManifest.xml';s=manifest.read_text();needle='        <service\n            android:name=".WakeService"'
 assert s.count(needle)==1
 s=s.replace(needle,'''        <activity android:name=".CasaSetupActivity" android:exported="false" />
        <service android:name=".CasaAccessibilityService" android:exported="true"
            android:label="@string/app_name" android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE">
            <intent-filter><action android:name="android.accessibilityservice.AccessibilityService" /></intent-filter>
            <meta-data android:name="android.accessibilityservice" android:resource="@xml/casa_accessibility" />
        </service>

'''+needle);manifest.write_text(s)
 (r/'main/res/xml/casa_accessibility.xml').write_text('''<accessibility-service xmlns:android="http://schemas.android.com/apk/res/android"
 android:accessibilityEventTypes="typeWindowStateChanged|typeWindowContentChanged"
 android:packageNames="com.openai.chatgpt" android:accessibilityFeedbackType="feedbackGeneric"
 android:notificationTimeout="100" android:canRetrieveWindowContent="true"
 android:description="@string/casa_accessibility_description" />''')
 (r/'main/res/values/casa.xml').write_text('''<resources><string name="casa_accessibility_description">Inicia voz desde un chat nuevo de Sebastián · Casa al decir Ey Sebas. Solo examina ChatGPT durante una activación y no guarda ni envía el contenido.</string></resources>''')
 # Replace obsolete fallback tests with strict project-only behavior tests.
 (t/'GptLauncherCasaTest.java').unlink()
 test=t/'WakeControllerTest.java';s=test.read_text();start=s.index('    @Test\n    public void casaProjectTimeoutPreservesBothExistingFallbacks()')
 s=s[:start]+Path('casa-strict/controller-tests.txt').read_text()+'\n}\n'
 s=s.replace('        launcher = mockStatic(GptLauncher.class);','        launcher = mockStatic(GptLauncher.class);\n        launcher.when(() -> GptLauncher.launchProjectVoice(any())).thenReturn(true);')
 test.write_text(s)
 shutil.copyfile('casa-strict/CasaScreenTest.java',t/'CasaScreenTest.java')
 gradle=Path('GPTWake/app/build.gradle.kts');s=gradle.read_text().replace('versionCode = 102','versionCode = 103').replace('1.1.0-sebastian-casa-0.3','1.1.0-sebastian-casa-0.4');gradle.write_text(s)
 assert all(hashlib.sha256(Path(f).read_bytes()).hexdigest()==h for f,h in protected.items())
 Path('casa-detector-preservation.txt').write_text('PASS: existing sources except launcher, controller and MainActivity setup prompt unchanged by strict Casa patch. Recognition code unchanged.\n')
 print('Applied Casa project-screen Voice action; generic Voice routes removed')
