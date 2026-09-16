package com.desmond.gptwake;
import static org.junit.Assert.*;
import static org.mockito.Mockito.*;
import static org.mockito.ArgumentMatchers.*;
import android.content.*;
import java.util.*;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.MockedStatic;
import org.robolectric.*;
import org.robolectric.annotation.Config;
@RunWith(RobolectricTestRunner.class)
@Config(sdk={32,33})
public class CasaEnabledLaunchTest {
 @Test public void enabledServiceRejectedProjectNeverLaunchesGenericVoice() {
  List<Intent> launched=new ArrayList<>();
  Context ctx=new ContextWrapper(RuntimeEnvironment.getApplication()) {
   @Override public void startActivity(Intent i){launched.add(i);throw new ActivityNotFoundException();}
  };
  try(MockedStatic<CasaAccessibilityService> service=mockStatic(CasaAccessibilityService.class)) {
   service.when(()->CasaAccessibilityService.available(any())).thenReturn(true);
   assertFalse(GptLauncher.launch(ctx));
   assertEquals(1,launched.size());
   assertEquals("https://chatgpt.com/g/g-p-6aaaa3638f5081919f0455cc3f848b8f-sebastian-casa/project",launched.get(0).getDataString());
   assertEquals("com.openai.chatgpt",launched.get(0).getPackage());
   service.verify(CasaAccessibilityService::cancel);
  }
 }
 @Test public void enabledServiceArmsAndOpensOnlyProjectLanding() {
  List<Intent> launched=new ArrayList<>();
  Context ctx=new ContextWrapper(RuntimeEnvironment.getApplication()) {
   @Override public void startActivity(Intent i){launched.add(i);}
  };
  try(MockedStatic<CasaAccessibilityService> service=mockStatic(CasaAccessibilityService.class)) {
   service.when(()->CasaAccessibilityService.available(any())).thenReturn(true);
   assertTrue(GptLauncher.launch(ctx));
   assertEquals(1,launched.size());
   assertEquals("https://chatgpt.com/g/g-p-6aaaa3638f5081919f0455cc3f848b8f-sebastian-casa/project",launched.get(0).getDataString());
   assertEquals("com.openai.chatgpt",launched.get(0).getPackage());
   service.verify(CasaAccessibilityService::arm);
  }
 }
}
