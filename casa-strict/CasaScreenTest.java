package com.desmond.gptwake;
import static org.junit.Assert.*;
import java.util.*;
import org.junit.Test;
public class CasaScreenTest {
 private List<CasaScreen.Item> landing() {
  return new ArrayList<>(Arrays.asList(
   new CasaScreen.Item("🏠 Sebastián · Casa","",true),
   new CasaScreen.Item("Chats","",true),new CasaScreen.Item("Fuentes","",true),
   new CasaScreen.Item("","Nuevo chat",true),
   new CasaScreen.Item("","Iniciar una conversación de voz",true)));
 }
 @Test public void projectLandingSelectsVoiceButton() {
  assertEquals(4,CasaScreen.voiceIndex("com.openai.chatgpt",landing()));
 }
 @Test public void otherProjectCannotLaunchVoice() {
  List<CasaScreen.Item> a=landing(); a.set(0,new CasaScreen.Item("Otro proyecto","",true));
  assertEquals(-1,CasaScreen.voiceIndex("com.openai.chatgpt",a));
 }
 @Test public void existingChatCannotBeMistakenForNewProjectChat() {
  List<CasaScreen.Item> a=landing();a.remove(1);
  assertEquals(-1,CasaScreen.voiceIndex("com.openai.chatgpt",a));
 }
 @Test public void otherAppAndHiddenControlsCannotLaunch() {
  assertEquals(-1,CasaScreen.voiceIndex("other.app",landing()));
  List<CasaScreen.Item> a=landing();a.set(4,new CasaScreen.Item("","Iniciar una conversación de voz",false));
  assertEquals(-1,CasaScreen.voiceIndex("com.openai.chatgpt",a));
 }
 @Test public void ambiguousVoiceButtonsFailClosed() {
  List<CasaScreen.Item> a=landing();a.add(a.get(4));
  assertEquals(-1,CasaScreen.voiceIndex("com.openai.chatgpt",a));
 }
}
