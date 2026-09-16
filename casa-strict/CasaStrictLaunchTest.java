package com.desmond.gptwake;
import static org.junit.Assert.*;
import android.content.*;
import java.util.*;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.robolectric.*;
import org.robolectric.annotation.Config;
@RunWith(RobolectricTestRunner.class)
@Config(sdk=33)
public class CasaStrictLaunchTest {
 @Test public void unavailableProjectNeverLaunchesGenericVoice() {
  List<Intent> launched=new ArrayList<>();
  Context ctx=new ContextWrapper(RuntimeEnvironment.getApplication()) {
   @Override public void startActivity(Intent i) {
    launched.add(i);
    if(i.getDataString()!=null && i.getDataString().contains("/project"))
      throw new ActivityNotFoundException();
   }
  };
  assertFalse("Cannot report success by opening Voice outside Casa", GptLauncher.launch(ctx));
  for(Intent i:launched) {
   assertNotEquals("https://chat.com/?mode=voice",i.getDataString());
   if(i.getComponent()!=null) assertNotEquals("com.openai.voice.assistant.AssistantActivity",i.getComponent().getClassName());
  }
 }
}
