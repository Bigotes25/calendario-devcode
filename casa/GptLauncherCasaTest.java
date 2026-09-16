package com.desmond.gptwake;

import static org.junit.Assert.*;
import static org.robolectric.Shadows.shadowOf;

import android.content.ActivityNotFoundException;
import android.content.ContextWrapper;
import android.content.Intent;
import android.content.pm.ActivityInfo;
import java.util.ArrayList;
import java.util.List;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.robolectric.RobolectricTestRunner;
import org.robolectric.RuntimeEnvironment;
import org.robolectric.annotation.Config;

@RunWith(RobolectricTestRunner.class)
@Config(sdk = {32, 33})
public class GptLauncherCasaTest {
    private static final String CASA = "https://chatgpt.com/g/g-p-6aaaa3638f5081919f0455cc3f848b8f-sebastian-casa/project?mode=voice";

    private static final class LaunchContext extends ContextWrapper {
        final List<Intent> attempts = new ArrayList<>();
        boolean rejectProject, rejectDirect, rejectGeneric;
        LaunchContext() {
            super(RuntimeEnvironment.getApplication());
            ActivityInfo info = new ActivityInfo();
            info.packageName = "com.openai.chatgpt";
            info.name = "com.openai.voice.assistant.AssistantActivity";
            info.exported = true;
            shadowOf(getPackageManager()).addOrUpdateActivity(info);
        }
        @Override public void startActivity(Intent intent) {
            attempts.add(intent);
            boolean project = CASA.equals(intent.getDataString());
            boolean direct = intent.getComponent() != null;
            if ((project && rejectProject) || (direct && rejectDirect)
                    || (!project && !direct && rejectGeneric)) {
                throw new ActivityNotFoundException("Route unavailable in test");
            }
        }
    }

    @Test public void launchPrioritizesCasaProjectVoice() {
        LaunchContext context = new LaunchContext();
        assertTrue(GptLauncher.launch(context));
        assertEquals(1, context.attempts.size());
        Intent intent = context.attempts.get(0);
        assertEquals(CASA, intent.getDataString());
        assertEquals(Intent.ACTION_VIEW, intent.getAction());
        assertEquals("com.openai.chatgpt", intent.getPackage());
        assertTrue((intent.getFlags() & Intent.FLAG_ACTIVITY_NEW_TASK) != 0);
    }
    @Test public void rejectedProjectUsesExistingDirectVoice() {
        LaunchContext context = new LaunchContext();
        context.rejectProject = true;
        assertTrue(GptLauncher.launch(context));
        assertEquals(2, context.attempts.size());
        assertEquals(CASA, context.attempts.get(0).getDataString());
        assertEquals("com.openai.voice.assistant.AssistantActivity",
                context.attempts.get(1).getComponent().getClassName());
    }
    @Test public void rejectedProjectAndDirectUseExistingVoiceLink() {
        LaunchContext context = new LaunchContext();
        context.rejectProject = true;
        context.rejectDirect = true;
        assertTrue(GptLauncher.launch(context));
        assertEquals(3, context.attempts.size());
        assertEquals("https://chat.com/?mode=voice", context.attempts.get(2).getDataString());
        assertEquals("com.openai.chatgpt", context.attempts.get(2).getPackage());
    }
    @Test public void allRoutesUnavailableReturnFailure() {
        LaunchContext context = new LaunchContext();
        context.rejectProject = true;
        context.rejectDirect = true;
        context.rejectGeneric = true;
        assertFalse(GptLauncher.launch(context));
        assertEquals(3, context.attempts.size());
    }
}
