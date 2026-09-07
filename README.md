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

**It works with the radio off** — see [Offline](#offline), which is the point of
the thing.

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

## On a phone

A signalling lamp is a thing you hold up one-handed outdoors, so the phone
layout is not the desktop one reflowed. Stacking the three panels came to
3290px of scroll — the microphone was below the fold and the settings four
screens down. Under 760px it becomes:

- **one panel at a time**, behind sticky Send / Receive / Setup tabs, which
  brings each one to 1465–1680px and puts the mic button on the first screen;
- **a thumb bar** pinned to the bottom with Mic, Strobe and Stop, sized for a
  thumb rather than a cursor, and clear of the home indicator;
- **a compact stage** — the lamp stays visible at 104px beside the readout
  instead of owning the screen.

The same three actions live in the **shared fleet navbar** on wider screens:
`[data-carino-actions]` is what `carino-navbar.js` relocates into `.cn-right`,
and they hide on phones where the thumb bar has them. Every copy of an action
is dispatched by `data-act` and repainted by `syncActs()`, so pressing Strobe
in the navbar lights the one in the thumb bar too. Note that the navbar's own
injected `#carinoNav .cn-actions { display: flex }` outranks any class-only
rule and lands later in the cascade, so hiding a relocated control needs the id
and `!important`.

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

## Offline

A signal lamp is what you reach for when there is no network, so a page that has
to be fetched before it can run is not offline-capable however local its code is.
Two pieces close that gap, and both are things you do **before** you leave:

**The app caches itself.** `sw.js` precaches every shipped asset on install and
serves cache-first; open the site once over https, or add it to the home screen,
and it opens afterwards with nothing at all. The precache list and `VERSION` are
derived from the repo by `tools/build_sw.py` — a hash of the shipped bytes, not a
number anyone has to remember to bump:

```
python3 tools/build_sw.py            # rewrite the generated block
python3 tools/build_sw.py --check    # non-zero if it has drifted
```

Run it after changing any shipped file. A file that ships but is not precached is
a shipped bug, and a stale `VERSION` is a build that every existing install
ignores forever. The worker also re-reads `index.html`, the manifest and the font
CSS at install time and caches whatever those declare, so a forgotten run costs
less than it otherwise would.

**Speech is the one part that is not local by default.** Chrome streams audio to
Google's servers and fails with `error: 'network'` when it cannot reach them.
Chrome 139 can run recognition on-device instead, once a language pack has been
downloaded — so *Prepare for offline* in the settings panel shows both rows and
offers the download while you still have a connection. With the pack installed
the audio never leaves the device and the microphone works with no network.

Where the pack is not available, the app says so rather than pretending: the mic
button disables itself, and the hint points at the text box, which never needed a
network. The lamp, the strobe, the torch, the sidetone, the camera receiver and
typed text are all offline from the start.

Icons are drawn by `tools/make_icons.py` rather than kept as hand-maintained
binaries.

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
| `sw.js`, `manifest.webmanifest` | the offline cache and the installable app |
| `tools/build_sw.py` | regenerates the precache list and `VERSION`; `--check` gates it |
| `tools/make_icons.py` | draws the launcher icons |

`window.Aldis` exposes the tables, `encode`, `timing` and the decoder step for
poking at from the console.
