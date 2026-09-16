package com.desmond.gptwake;
import android.accessibilityservice.AccessibilityService;
import android.content.*;
import android.os.*;
import android.provider.Settings;
import android.view.accessibility.*;
import android.widget.Toast;
import java.util.*;

/** A bounded, user-triggered action scoped to ChatGPT's Casa project screen. */
public final class CasaAccessibilityService extends AccessibilityService {
 private static final Handler MAIN=new Handler(Looper.getMainLooper());
 private static volatile CasaAccessibilityService instance;
 private static volatile long generation;
 private static volatile boolean armed;
 private static long deadline;
 private long stableSince;
 public static boolean available(Context c) {
  String enabled=Settings.Secure.getString(c.getContentResolver(),Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES);
  String own=new ComponentName(c,CasaAccessibilityService.class).flattenToString();
  return instance!=null && enabled!=null && Arrays.asList(enabled.split(":")).contains(own);
 }
 public static void arm() {
  long request=++generation;
  armed=true;
  MAIN.post(()->{
   if(request!=generation||!armed)return;
   deadline=SystemClock.uptimeMillis()+25000;
   if(instance!=null)instance.stableSince=0;
   poll(request);
  });
 }
 public static void cancel() {armed=false;generation++;}
 private static void poll(long request) {
  if(!armed||request!=generation)return;
  CasaAccessibilityService s=instance;
  if(SystemClock.uptimeMillis()>=deadline) {
   cancel(); L.i("CASA_UI_TIMEOUT noGenericFallback=true");
   if(s!=null)Toast.makeText(s,"No se pudo iniciar voz dentro de Casa. Abre ChatGPT y vuelve a intentarlo.",Toast.LENGTH_LONG).show();
   return;
  }
  if(s!=null)s.inspect();
  if(armed&&request==generation)MAIN.postDelayed(()->poll(request),250);
 }
 @Override protected void onServiceConnected(){instance=this;L.i("CASA_ACCESSIBILITY_READY");}
 @Override public void onAccessibilityEvent(AccessibilityEvent e) { /* Bounded polling while armed only. */ }
 @Override public void onInterrupt(){cancel();}
 @Override public void onDestroy(){if(instance==this)instance=null;cancel();super.onDestroy();}
 private static String value(CharSequence c){return c==null?"":c.toString();}
 private void inspect() {
  AccessibilityNodeInfo root=getRootInActiveWindow();if(root==null){stableSince=0;return;}
  List<AccessibilityNodeInfo> nodes=new ArrayList<>();
  try {
   collect(root,nodes);
   List<CasaScreen.Item> items=new ArrayList<>();
   for(AccessibilityNodeInfo n:nodes)items.add(new CasaScreen.Item(value(n.getText()),value(n.getContentDescription()),n.isVisibleToUser()&&n.isEnabled()));
   int index=CasaScreen.voiceIndex(value(root.getPackageName()),items);
   if(index<0){stableSince=0;return;}
   long now=SystemClock.uptimeMillis();
   if(stableSince==0){stableSince=now;return;}
   if(now-stableSince<600)return;
   AccessibilityNodeInfo target=AccessibilityNodeInfo.obtain(nodes.get(index));
   try {
    for(int depth=0;target!=null&&depth<5;depth++) {
     if(target.isClickable()&&target.isEnabled()) {
      // Disarm before the action, so subsequent window events can never click twice.
      cancel();
      boolean clicked=target.performAction(AccessibilityNodeInfo.ACTION_CLICK);
      L.i("CASA_UI_VOICE_CLICK success="+clicked+" projectLandingVerified=true");
      if(!clicked)Toast.makeText(this,"No se pudo pulsar voz en Casa.",Toast.LENGTH_LONG).show();
      return;
     }
     AccessibilityNodeInfo parent=target.getParent();target.recycle();target=parent;
    }
   } finally {if(target!=null)target.recycle();}
  } finally {for(AccessibilityNodeInfo n:nodes)n.recycle();}
 }
 private void collect(AccessibilityNodeInfo n,List<AccessibilityNodeInfo> nodes) {
  nodes.add(n);
  for(int i=0;i<n.getChildCount();i++){AccessibilityNodeInfo child=n.getChild(i);if(child!=null)collect(child,nodes);}
 }
}
