# Aldis Lamp

Speak, and a signal lamp says it in Morse → **[aldis.carino.systems](https://aldis.carino.systems)**

An Aldis lamp is a handheld signalling lamp with a trigger-operated shutter, used
at sea to talk between ships without a radio. This page puts one behind your
voice: speech is transcribed by the browser, spelled out in Morse, and flashed at
a signalling speed a human can actually read — on screen, across the whole
screen, on the phone's torch, and as a sidetone in your ear.

Point the camera at a lamp and it reads one back.

Everything runs in the browser. Audio goes through the browser's own speech
engine, camera frames never leave the page, nothing is uploaded, and there are no
external requests of any kind.

## What it does

- **Voice → Morse, live.** Continuous speech recognition; each finished word is
  queued and keyed. The readout shows what has been sent, what is going out right
  now, and what is still waiting, with the current character's dots and dashes
  lighting up one element at a time.
- **Four outputs, any combination.** The on-screen lamp (shutter blades that open
  on key-down, with the light spilling past the lens), a fullscreen white strobe
  so a laptop or phone becomes a real signalling light, the **device torch** via
  the camera track's `torch` constraint, and a ramped WebAudio **sidetone** — the
  way an operator monitors their own sending.
- **A camera receiver.** Brightness inside an aim window is thresholded against a
  decaying envelope, edges are timed, and the timings are decoded back to text.
  It finds the sender's speed on its own; there is a live scope and a contrast
  meter so you can tell "too dim" from "wrong aim".
- **Procedure signals.** AA · K · AS · R · T · BT · AR · SK · HH · SOS, each sent
  as one unbroken character the way a prosign actually is. They can also be typed
  inline: `<AR>`.
- **Three alphabets.** ITU Latin (with the accented letters the ITU list really
  carries), Russian Cyrillic, and **Wabun** (和文) for kana — hiragana is lifted
  to katakana, small kana are sent full size, and voiced kana split into the kana
  plus its `゛` mark, which the decoder folds back in.

## Timing

PARIS timing: one unit is `1200 / WPM` ms, a dash is three units, the gap inside
a character is one, between characters three, between words seven.

**Farnsworth** spacing is separate: the characters keep the speed set above while
the gaps stretch to a slower overall speed — one PARIS word must take `60/f`
seconds while its 31 units of key-down still run at the character speed `c`, so
the 19 units of spacing share what is left:

```
spacing = 60/f − 37.2/c        (seconds per word)
character gap = spacing × 3/19
word     gap = spacing × 7/19
```

Real Aldis work sits around 6–12 WPM, which is where the default is.

The schedule advances on absolute timestamps rather than chained timeouts, so a
late timer never accumulates drift; coming back from a throttled background tab
fast-forwards instead of replaying a burst of flashes.

## Decoding

Two things make the receiver work on a signal whose speed is unknown:

1. **The unit is the shortest thing on the wire**, and both a dot and the gap
   *inside* a character are exactly one unit — so the estimate comes from the
   median of the shortest cluster of *both* kinds of interval. Timing only the
   lit pulses misleads: three dots and three dashes look identical until
   something shorter turns up.
2. **Nothing is classified until the character ends.** Raw durations are held and
   turned into dots and dashes at the character boundary, by which point every
   interval of that character has fed the estimate. Deciding at each edge instead
   commits to a speed guess made from a single sample, and loses the opening
   character of every transmission.

The first flash of a transmission still tells you nothing about its speed, so the
estimator weights early evidence heavily and then settles down, and the silence
before the first flash is deliberately not counted as an interval.

## Browsers

Speech recognition needs Chrome, Edge or Safari; Firefox has none, so the mic
button is disabled there and the text box does the same job. The torch needs a
device that exposes `torch` in its camera track capabilities — Android Chrome,
mostly — and the button says so when it does not.

## Keyboard

<kbd>M</kbd> microphone · <kbd>F</kbd> fullscreen strobe · <kbd>Space</kbd> pause
or resume · <kbd>Esc</kbd> stop or leave the strobe.

## Files

| File | What it is |
|---|---|
| `index.html` | the whole app — markup, styles, and the lamp/keyer/decoder |
| `i18n.js` | EN · ES · PT-BR · JA · RU strings (English source strings are the keys) |
| `carino-navbar.js`, `carino-clock.js`, `carino-lang.js` | the shared fleet header |
| `fonts/` | self-hosted IBM Plex Mono/Sans + Red Hat Display |

`window.Aldis` exposes the tables, `encode`, `timing` and the decoder step for
poking at from the console.
