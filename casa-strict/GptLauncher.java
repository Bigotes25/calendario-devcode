package com.desmond.gptwake;
import android.content.*;
import android.net.Uri;
public final class GptLauncher {
 public static boolean launchProjectVoice(Context context) {
  if(!CasaAccessibilityService.available(context)) {
   L.i("CASA_ACCESSIBILITY_REQUIRED");
   try {context.startActivity(new Intent(context,CasaSetupActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));}
   catch(Exception e){L.e("CASA_SETUP_FAILED",e);}
   return false;
  }
  try {
   CasaAccessibilityService.arm();
   context.startActivity(new Intent(Intent.ACTION_VIEW,Uri.parse("https://chatgpt.com/g/g-p-6aaaa3638f5081919f0455cc3f848b8f-sebastian-casa/project"))
    .setPackage("com.openai.chatgpt").addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
   L.i("CASA_PROJECT_OPEN waitingForVerifiedProjectScreen=true");return true;
  } catch(Exception e){CasaAccessibilityService.cancel();L.e("CASA_PROJECT_OPEN_FAILED",e);return false;}
 }
 public static boolean launch(Context context){return launchProjectVoice(context);}
}
