package com.desmond.gptwake;

import android.content.Context;
import android.content.res.AssetManager;
import java.io.File;
import java.io.FileOutputStream;
import org.json.JSONObject;
import org.vosk.Model;
import org.vosk.Recognizer;

/** Offline Spanish recognition. Calls are serialized by KwsEngine. */
final class SpanishWakeEngine {
    private final Model model;
    private Recognizer recognizer;

    private SpanishWakeEngine(Model model) { this.model = model; }

    static SpanishWakeEngine load(Context context) throws Exception {
        File directory = new File(context.getNoBackupFilesDir(), "vosk-es-0.42");
        File ready = new File(directory, ".complete");
        if (!ready.isFile()) {
            copyAssets(context.getAssets(), "vosk-es", directory);
            if (!ready.createNewFile() && !ready.isFile()) {
                throw new java.io.IOException("Cannot mark Spanish model ready");
            }
        }
        SpanishWakeEngine engine = new SpanishWakeEngine(new Model(directory.getAbsolutePath()));
        L.i("ES_MODEL_READY model=vosk-small-es-0.42");
        return engine;
    }

    private static void copyAssets(AssetManager assets, String source, File target) throws Exception {
        String[] children = assets.list(source);
        if (children != null && children.length > 0) {
            if (!target.isDirectory() && !target.mkdirs()) {
                throw new java.io.IOException("Cannot create Spanish model directory");
            }
            for (String child : children) copyAssets(assets, source + "/" + child, new File(target, child));
        } else {
            try (var in = assets.open(source); var out = new FileOutputStream(target)) {
                byte[] buffer = new byte[65536];
                int count;
                while ((count = in.read(buffer)) != -1) out.write(buffer, 0, count);
            }
        }
    }

    void newStream() throws java.io.IOException {
        releaseStream();
        recognizer = new Recognizer(model, 16000f, SpanishWakePhrase.GRAMMAR);
        L.i("ES_LISTENING phrase=ey_sebas");
    }

    String accept(float[] samples, int sampleRate) {
        if (recognizer == null) return null;
        if (sampleRate != 16000) throw new IllegalArgumentException("Spanish audio requires 16000 Hz");
        short[] pcm = new short[samples.length];
        for (int i = 0; i < samples.length; i++) {
            pcm[i] = (short) Math.max(-32768, Math.min(32767, Math.round(samples[i] * 32768f)));
        }
        // Use completed utterances, not unstable partials that can cause false activations.
        if (!recognizer.acceptWaveForm(pcm, pcm.length)) return null;
        String result = recognizer.getResult();
        try {
            if (SpanishWakePhrase.matches(new JSONObject(result).optString("text", ""))) {
                recognizer.reset();
                return "ey_sebas";
            }
        } catch (org.json.JSONException error) {
            L.e("ES_RESULT_INVALID", error);
        }
        return null;
    }

    void releaseStream() {
        if (recognizer != null) { recognizer.close(); recognizer = null; }
    }
    void release() { releaseStream(); model.close(); }
}
