package com.desmond.gptwake;
import android.app.*;
import android.content.*;
import android.os.Bundle;
import android.provider.Settings;
public final class CasaSetupActivity extends Activity {
 @Override protected void onCreate(Bundle state) {
  super.onCreate(state);
  new AlertDialog.Builder(this).setTitle("Activar Sebastián · Casa")
   .setMessage("Para iniciar una conversación nueva dentro de Casa, Sebastián necesita pulsar el botón de voz de ChatGPT.\n\nActiva Sebastián · Casa en Accesibilidad → Aplicaciones instaladas. Solo examina ChatGPT durante los 25 segundos posteriores a Ey Sebas y no guarda ni envía el contenido de la pantalla.")
   .setPositiveButton("Abrir accesibilidad",(d,w)->{startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS));finish();})
   .setNegativeButton("Ahora no",(d,w)->finish()).setOnCancelListener(d->finish()).show();
 }
}
