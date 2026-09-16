"""Native recognition regression using synthetic Spanish speech, not microphone simulation."""
import json
from pathlib import Path
import sys
import wave
import re
from vosk import Model, KaldiRecognizer, SetLogLevel

root = Path(sys.argv[1])
fixtures = Path(sys.argv[2])
SetLogLevel(-1)
model = Model(str(root))
grammar = json.dumps(['ey sebas', 'hey sebas', 'eh sebas', '[unk]'])
failures = []
files = sorted(fixtures.glob('*.wav'))
assert len(files) == 10, f'Expected 10 audio fixtures, found {len(files)}'
assert sum(p.name.startswith('positive-') for p in files) == 5
assert sum(p.name.startswith('negative-') for p in files) == 5
for wav in files:
    recognizer = KaldiRecognizer(model, 16000, grammar)
    hits = []
    with wave.open(str(wav)) as f:
        assert (f.getframerate(), f.getnchannels(), f.getsampwidth()) == (16000, 1, 2)
        pcm = f.readframes(f.getnframes()) + bytes(16000 * 2 * 2)
    for start in range(0, len(pcm), 2560):
        if recognizer.AcceptWaveform(pcm[start:start+2560]):
            text = json.loads(recognizer.Result())['text']
            if re.search(r'(?:^| )(?:ey|hey|eh) sebas(?: |$)', text):
                hits.append(text)
                recognizer.Reset()
    expected = wav.name.startswith('positive-')
    ok = bool(hits) == expected
    print(('PASS' if ok else 'FAIL'), wav.name, hits, flush=True)
    if not ok: failures.append(wav.name)
assert not failures, failures
print('PASS: native Spanish positive/negative audio regression')
