package com.desmond.gptwake;
import java.util.List;
/** Matches only the observed Casa project landing page, never an existing chat. */
final class CasaScreen {
 static final class Item {
  final String text, description; final boolean usable;
  Item(String t,String d,boolean u){text=t;description=d;usable=u;}
 }
 static int voiceIndex(String pkg,List<Item> items) {
  if(!"com.openai.chatgpt".equals(pkg))return -1;
  boolean title=false,chats=false,sources=false,fresh=false;int voice=-1;
  for(int i=0;i<items.size();i++) {
   Item n=items.get(i);if(!n.usable)continue;
   title|="🏠 Sebastián · Casa".equals(n.text);
   chats|="Chats".equals(n.text);
   sources|="Fuentes".equals(n.text);
   fresh|="Nuevo chat".equals(n.description);
   if("Iniciar una conversación de voz".equals(n.description)) {
    if(voice>=0)return -1;voice=i;
   }
  }
  return title&&chats&&sources&&fresh?voice:-1;
 }
}
