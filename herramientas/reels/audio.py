"""Pistas originales sintetizadas (sin derechos de terceros) para los reels.
uso: python3 audio.py <estilo> <duracion> <salida.wav> [sfx:tiempo,sfx:tiempo...]"""
import sys, numpy as np, wave
SR = 44100
style, dur, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
sfx = []
if len(sys.argv) > 4 and sys.argv[4]:
    for it in sys.argv[4].split(','):
        k, v = it.split(':'); sfx.append((k, float(v)))
N = int(SR * dur)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)

def f(m): return 440 * 2 ** ((m - 69) / 12)
def add(sig, t, pan=0.0, g=1.0):
    i = int(t * SR)
    if i >= N: return
    s = sig[: N - i] * g
    L[i:i + len(s)] += s * (1 - pan) ** .5 if pan > 0 else s
    R[i:i + len(s)] += s * (1 + pan) ** .5 if pan < 0 else s
def env(n, a=0.005, d=0.3):
    t = np.arange(n) / SR
    return np.minimum(t / a, 1) * np.exp(-t / d)
def bell(m, ln=2.5, d=0.9):
    n = int(ln * SR); t = np.arange(n) / SR; fr = f(m)
    s = (np.sin(2*np.pi*fr*t) + .45*np.sin(2*np.pi*fr*2.76*t)*np.exp(-t/.25) + .25*np.sin(2*np.pi*fr*5.4*t)*np.exp(-t/.08))
    return s * env(n, .002, d) * .32
def piano(m, ln=2.2, d=0.8):
    n = int(ln * SR); t = np.arange(n) / SR; fr = f(m)
    s = sum(np.sin(2*np.pi*fr*k*t) * (0.6 ** k) * np.exp(-t*k*.8) for k in range(1, 6))
    return s * env(n, .004, d) * .22
def pluck(m, ln=0.35):
    n = int(ln * SR); t = np.arange(n) / SR; fr = f(m)
    s = np.sign(np.sin(2*np.pi*fr*t)) * .5 + np.sin(2*np.pi*fr*t)
    return s * env(n, .002, .09) * .1
def kick(g=1):
    n = int(.35*SR); t = np.arange(n)/SR
    ph = 2*np.pi*(45*t + 90*(1-np.exp(-t*30))/30)
    return np.sin(ph)*np.exp(-t/.12)*.9*g
def snare():
    n = int(.25*SR); t = np.arange(n)/SR
    return (rng.standard_normal(n)*.5 + np.sin(2*np.pi*190*t)*.4)*np.exp(-t/.07)*.45
def hat():
    n = int(.06*SR); t = np.arange(n)/SR
    x = rng.standard_normal(n); x = np.diff(np.concatenate([[0], x]))
    return x*np.exp(-t/.015)*.12
def bass(m, ln):
    n = int(ln*SR); t = np.arange(n)/SR; fr = f(m)
    s = np.sin(2*np.pi*fr*t) + .3*np.sin(4*np.pi*fr*t)
    return s*np.minimum(t/.01, 1)*np.exp(-t/(ln*.8))*.35
def pad(ms, ln):
    n = int(ln*SR); t = np.arange(n)/SR
    s = sum(np.sin(2*np.pi*f(m)*t + np.sin(2*np.pi*.3*t)*.5) for m in ms)/len(ms)
    a = np.minimum(t/.8, 1)*np.minimum((ln-t)/.8, 1)
    return s*np.clip(a, 0, 1)*.12

if style == 'musicbox':
    bpm = 84; b = 60/bpm
    mel = [69,72,76,75, 76,72,69,68, 69,72,76,77, 76,75,71,72, 69,72,76,75, 76,72,69,71, 72,71,69,68, 69,None,None,None]
    t = 0.0; i = 0
    while t < dur - .5:
        m = mel[i % len(mel)]
        if m: add(bell(m+12), t, pan=.15*np.sin(i))
        if i % 3 == 0: add(bell(m-12 if m else 57, 3, 1.6)*.6, t)
        t += b; i += 1
    for k in range(int(dur/4)+1): add(pad([45, 52, 57], 4.4)*1.4, k*4)
elif style in ('beat', 'beat-soft'):
    bpm = 120; b = .5; soft = style == 'beat-soft'
    prog = [(57, [69,72,76]), (53, [69,72,77]), (48, [67,72,76]), (55, [67,71,74])]
    nb = int(dur/b)
    for k in range(nb):
        t = k*b; root, ch = prog[(k//4) % 4]
        if not (k >= nb-2):
            add(kick(.7 if soft else 1), t)
            if k % 2 == 1: add(snare()*(.5 if soft else 1), t)
            add(hat(), t+.25, pan=.3); add(hat()*.6, t, pan=-.3)
            add(bass(root-12, .45), t+(0 if k % 2 == 0 else .25)*0)
            for j, m in enumerate(ch): add(pluck(m+(0 if j % 2 else 12)), t + .25*(j % 2), pan=.4*(j-1))
    add(pad([69, 73, 76], 2.5)*1.5, dur-2.5)
elif style == 'lofi':
    bpm = 80; b = .75
    chords = [[53,57,60,64],[52,55,59,62],[50,53,57,60],[48,52,55,59]]
    nb = int(dur/b)
    for k in range(nb):
        t = k*b; ch = chords[(k//4) % 4]
        if k % 4 == 0:
            for j, m in enumerate(ch): add(piano(m+12, 3.2, 1.4), t+j*.03)
            add(bass(ch[0]-12, 2.8)*.8, t)
        if k % 2 == 0: add(kick(.45), t)
        else: add(snare()*.35, t)
        add(hat()*.7, t+b/2)
        if k % 4 in (1, 3): add(piano(ch[-1]+24, 1.5, .6)*.6, t+b/2)
    noise = rng.standard_normal(N)*.006
    crack = (rng.random(N) > .9997)*rng.standard_normal(N)*.25
    L += noise+crack; R += noise+crack
elif style == 'tick':
    b = .5; nb = int(dur/b)
    for k in range(nb):
        t = k*b
        n = int(.04*SR); tt = np.arange(n)/SR
        tk = np.sin(2*np.pi*(1800 if k % 2 else 1300)*tt)*np.exp(-tt/.008)*.18
        add(tk, t)
        if k % 2 == 0: add(kick(.55), t)
        if k % 8 == 0: add(pad([57, 60, 64], 4.2), t)

# efectos
for k, t in sfx:
    if k == 'pop':
        n = int(.12*SR); tt = np.arange(n)/SR
        add(np.sin(2*np.pi*(600+1400*tt/.12)*tt)*np.exp(-tt/.03)*.35, t)
    elif k == 'ding':
        add(bell(84, 1.5, .5)*1.6, t); add(bell(91, 1.5, .4)*1.0, t+.08)
    elif k == 'buzz':
        n = int(.35*SR); tt = np.arange(n)/SR
        add(np.sign(np.sin(2*np.pi*110*tt))*np.exp(-tt/.2)*.18, t)
    elif k == 'whoosh':
        n = int(.5*SR); tt = np.arange(n)/SR
        x = rng.standard_normal(n); a = np.sin(np.pi*tt/.5)**2
        add(np.convolve(x, np.ones(30)/30, 'same')*a*.6, t)
    elif k == 'boom':
        add(kick(1.3), t); add(pad([33, 40], 2.0)*2, t)
    elif k == 'tap':
        n = int(.03*SR); tt = np.arange(n)/SR
        add(np.sin(2*np.pi*2400*tt)*np.exp(-tt/.006)*.25, t)

# eco suave y master
dl = int(.23*SR)
for ch in (L, R):
    ch[dl:] += ch[:-dl]*.22
fade = np.ones(N); fl = int(.8*SR); fade[-fl:] = np.linspace(1, 0, fl)
st = np.stack([L*fade, R*fade], 1)
st = np.tanh(st*1.3)/np.tanh(1.3); st /= max(1e-9, np.abs(st).max()); st *= .89
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st*32767).astype('<i2').tobytes())
print('ok', out)
