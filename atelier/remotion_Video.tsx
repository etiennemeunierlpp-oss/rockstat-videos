import React from "react";
import {
  AbsoluteFill, Audio, OffthreadVideo, Sequence, staticFile, useCurrentFrame,
  useVideoConfig, interpolate, spring, Easing, continueRender, delayRender, Img, random,
} from "remotion";

// ---------------------------------------------------------------- types
export type Shot = { src: string; from: number; dur: number; startFrom: number; fit?: boolean; cut: "hard" | "section"; trans?: string; pos?: number };
export type Group = { text: string; start: number; end: number };
export type Item = { n: number; total: number; start: number; end: number; header?: string };
export type Sfx = { src: string; frame: number; volume: number };
export type Fx = { type: string; start: number; dur: number; [k: string]: any };
export type Card = { start: number; end: number; header?: string; n?: number; total?: number };
export type Props = {
  fps: number; durationInFrames: number;
  shots: Shot[]; groups: Group[]; items: Item[]; sfx: Sfx[]; fx: Fx[]; cards: Card[];
  title: { start: number; end: number; lines: string[] } | null;
  voice: string; music: string; musicStartFrom: number; musicVolume: number;
  logo?: string | null; handle?: string | null;
  duck: [number, number][];
};

const PINK = "#FF4FA3";
const BLUE = "#4FC8FF";
const PURPLE = "#8A4DFF";
const YELLOW = "#FFD84F";

// ---------------------------------------------------------------- polices
const fontHandle = typeof window !== "undefined" ? delayRender("fonts") : 0;
if (typeof window !== "undefined") {
  const faces = [
    new FontFace("MBlack", `url(${staticFile("fonts/Montserrat-Black.ttf")})`),
    new FontFace("MXBI", `url(${staticFile("fonts/Montserrat-ExtraBoldItalic.ttf")})`),
  ];
  Promise.all(faces.map((f) => f.load())).then((loaded) => {
    loaded.forEach((f) => (document as any).fonts.add(f));
    continueRender(fontHandle);
  }).catch(() => continueRender(fontHandle));
}

const stroke = (px: number) => ({ WebkitTextStroke: `${px}px black`, paintOrder: "stroke fill" as any });
const pop = (f: number, fps: number, delay = 0, damping = 10) =>
  spring({ frame: f - delay, fps, config: { damping, stiffness: 220, mass: 0.6 } });

// ---------------------------------------------------------------- vidéo d'un plan
const Clip: React.FC<{ shot: Shot; cover?: boolean }> = ({ shot, cover = true }) => (
  <OffthreadVideo src={staticFile(shot.src)} startFrom={shot.startFrom} muted
    style={{ width: "100%", height: "100%", objectFit: shot.fit || !cover ? "contain" : "cover", objectPosition: `${shot.pos ?? 50}% 50%` }} />
);

// transitions d'entrée : whip, zoomblur, glitch, swipeup, spin, punch
const ShotView: React.FC<{ shot: Shot; index: number }> = ({ shot, index }) => {
  const f = useCurrentFrame();
  const kb = interpolate(f, [0, shot.dur], [1.0, 1.08]);
  const IN = shot.trans === "zoomin" ? 14 : shot.cut === "section" ? 8 : 5;
  const t = interpolate(f, [0, IN], [0, 1], { extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const kind = shot.trans || (shot.cut === "section" ? "whip" : "punch");
  let transform = "", filter = "", extra: React.ReactNode = null;
  const dir = index % 2 === 0 ? 1 : -1;
  switch (kind) {
    case "whip":
      transform = `translateX(${(1 - t) * dir * 320}px) scale(${1 + (1 - t) * 0.3})`;
      filter = `blur(${(1 - t) * 24}px)`; break;
    case "zoomin": // ouverture : zoom avant rapide + flou
      transform = `scale(${1 + (1 - t) * 0.9})`; filter = `blur(${(1 - t) * 26}px)`; break;
    case "zoomblur":
      transform = `scale(${1 + (1 - t) * 0.6})`; filter = `blur(${(1 - t) * 30}px) brightness(${1 + (1 - t) * 0.8})`; break;
    case "swipeup":
      transform = `translateY(${(1 - t) * 700}px)`; filter = `blur(${(1 - t) * 18}px)`; break;
    case "spin":
      transform = `rotate(${(1 - t) * dir * 14}deg) scale(${1 + (1 - t) * 0.45})`; filter = `blur(${(1 - t) * 16}px)`; break;
    case "glitch": {
      const g = f < 7 ? 1 : 0;
      transform = `translateX(${g * (random(`g${f}`) - 0.5) * 60}px)`;
      filter = g ? `hue-rotate(${random(`h${f}`) * 90}deg) saturate(2)` : "";
      extra = g ? (
        <>
          <AbsoluteFill style={{ mixBlendMode: "screen", opacity: 0.6, transform: "translateX(-14px)", filter: "url(#r)" }}><Clip shot={shot} /></AbsoluteFill>
          <AbsoluteFill style={{ background: `repeating-linear-gradient(0deg, rgba(255,255,255,0.08) 0 3px, transparent 3px 9px)` }} />
        </>
      ) : null;
      break;
    }
    default:
      transform = `scale(${1 + (1 - t) * 0.18})`; filter = shot.fit ? "" : `blur(${(1 - t) * 10}px)`;
  }
  return (
    <AbsoluteFill style={{ transform: `${transform} scale(${kb})`, filter: `${filter} saturate(1.15) contrast(1.05)` }}>
      {shot.fit ? (
        <>
          {/* un seul lecteur vidéo par plan : deux OffthreadVideo du même fichier sortaient noirs */}
          <AbsoluteFill style={{ background: "radial-gradient(circle at 50% 45%, #3a1030 0%, #12060f 70%)" }} />
          <AbsoluteFill style={{ justifyContent: "center" }}><Clip shot={shot} /></AbsoluteFill>
        </>
      ) : <Clip shot={shot} />}
      {extra}
    </AbsoluteFill>
  );
};

const Flash: React.FC<{ color?: string }> = ({ color = "white" }) => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{ background: color, opacity: interpolate(f, [0, 2, 7], [0, 0.7, 0], { extrapolateRight: "clamp" }) }} />;
};

// ---------------------------------------------------------------- mise en page "carte" (style infos_gtavi)
const FLOAT_ICONS = ["🎮", "💰", "🚓", "⭐", "💎", "🔫", "🌴", "📱"];
const CardLayout: React.FC<{ card: Card; shot: Shot | undefined; animate: boolean }> = ({ card, shot, animate }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = animate ? pop(f, fps, 0, 13) : 1;
  if (!shot) return null;
  return (
    <AbsoluteFill>
      {/* fond flouté */}
      <AbsoluteFill style={{ filter: "blur(38px) brightness(0.45) saturate(1.3)", transform: "scale(1.25)" }}>
        <Clip shot={shot} />
      </AbsoluteFill>
      <AbsoluteFill style={{ background: "linear-gradient(180deg, rgba(40,10,60,0.35), rgba(10,10,30,0.55))" }} />
      {/* icônes flottantes */}
      {FLOAT_ICONS.map((ic, i) => {
        const x = 60 + random(`x${i}`) * 960, y0 = 200 + random(`y${i}`) * 1500;
        const y = y0 - ((f * (0.6 + random(`v${i}`))) % 300);
        return <div key={i} style={{ position: "absolute", left: x, top: y, fontSize: 54, opacity: 0.22, transform: `rotate(${f * (i % 2 ? 0.6 : -0.6)}deg)` }}>{ic}</div>;
      })}
      {/* en-tête numéroté */}
      {card.header ? (
        <div style={{ position: "absolute", top: 330, width: "100%", display: "flex", justifyContent: "center",
          transform: `scale(${interpolate(s, [0, 1], [0.4, 1])})` }}>
          <div style={{ display: "flex", alignItems: "center", gap: 18, fontFamily: "MBlack", fontSize: 66, color: "white", ...stroke(10) }}>
            {card.n ? <div style={{ width: 82, height: 82, borderRadius: 41, background: `linear-gradient(135deg, ${PINK}, ${PURPLE})`,
              display: "flex", alignItems: "center", justifyContent: "center", fontSize: 50, WebkitTextStroke: "0px", border: "5px solid white" }}>{card.n}</div> : null}
            <span style={{ textShadow: `0 0 26px ${PINK}` }}>{card.header}</span>
          </div>
        </div>
      ) : null}
      {/* carte vidéo */}
      <div style={{ position: "absolute", left: 60, top: 470, width: 960, height: 640, borderRadius: 38, overflow: "hidden",
        border: "7px solid transparent", background: `linear-gradient(#000,#000) padding-box, linear-gradient(135deg, ${PINK}, ${BLUE}) border-box`,
        boxShadow: `0 0 60px ${PINK}88`, transform: `translateY(${interpolate(s, [0, 1], [500, 0])}px) rotate(${interpolate(s, [0, 1], [-6, 0])}deg)` }}>
        <Clip shot={shot} />
      </div>
      {/* points de progression */}
      {card.total ? (
        <div style={{ position: "absolute", top: 1140, width: "100%", display: "flex", justifyContent: "center", gap: 14 }}>
          {Array.from({ length: card.total }).map((_, i) => (
            <div key={i} style={{ width: 44, height: 44, borderRadius: 22, fontFamily: "MBlack", fontSize: 24, color: "white",
              display: "flex", alignItems: "center", justifyContent: "center",
              background: i + 1 === card.n ? PINK : i + 1 < (card.n || 0) ? PURPLE : "rgba(255,255,255,0.15)",
              border: "3px solid rgba(255,255,255,0.7)", transform: i + 1 === card.n ? `scale(${1 + 0.25 * s})` : "none" }}>{i + 1}</div>
          ))}
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- sous-titres
const Caption: React.FC<{ text: string; y: number }> = ({ text, y }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = pop(f, fps, 0, 11);
  const parts = text.split(/(\d+)/);
  return (
    <AbsoluteFill style={{ alignItems: "center" }}>
      <div style={{ position: "absolute", top: y, fontFamily: "MXBI", fontSize: text.length > 13 ? 86 : 104, color: "white", whiteSpace: "nowrap",
        transform: `translateY(-50%) scale(${interpolate(s, [0, 1], [0.6, 1])}) rotate(${interpolate(s, [0, 1], [-4, 0])}deg)`,
        ...stroke(14), textShadow: "0 8px 0 rgba(0,0,0,0.55)", letterSpacing: 1 }}>
        {parts.map((p, i) => /\d+/.test(p) ? <span key={i} style={{ color: PINK }}>{p}</span> : <span key={i}>{p}</span>)}
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- compteur n/N (mode plein écran)
const Badge: React.FC<{ n: number; total: number }> = ({ n, total }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = pop(f, fps, 0, 9);
  const prog = interpolate(f, [0, 12], [(n - 1) / total, n / total], { extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const R = 92, C = 2 * Math.PI * R;
  return (
    <AbsoluteFill style={{ alignItems: "center", top: 130 }}>
      <div style={{ transform: `scale(${interpolate(s, [0, 1], [0.3, 1])})`, width: 230, height: 230, position: "relative" }}>
        <svg width={230} height={230} style={{ position: "absolute", filter: `drop-shadow(0 0 14px ${PINK})` }}>
          <circle cx={115} cy={115} r={R} fill="rgba(15,8,30,0.78)" stroke={BLUE} strokeOpacity={0.45} strokeWidth={8} />
          <circle cx={115} cy={115} r={R} fill="none" stroke={PINK} strokeWidth={13} strokeLinecap="round"
            strokeDasharray={C} strokeDashoffset={C * (1 - prog)} transform="rotate(-90 115 115)" />
        </svg>
        <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "MBlack" }}>
          <span style={{ fontSize: 86, color: PINK }}>{n}</span><span style={{ fontSize: 40, color: "white", marginTop: 26 }}>/{total}</span>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- carton titre
const Title: React.FC<{ lines: string[] }> = ({ lines }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const shake = f < 10 ? Math.sin(f * 2.3) * interpolate(f, [0, 10], [14, 0]) : 0;
  return (
    <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", transform: `translate(${shake}px, ${-shake / 2}px)` }}>
      <AbsoluteFill style={{ background: "radial-gradient(circle at 50% 45%, rgba(255,79,163,0.3), rgba(0,0,0,0.6) 70%)" }} />
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", marginTop: -180 }}>
        {lines.map((l, i) => {
          const s = pop(f, fps, i * 5, 12);
          return <div key={i} style={{ fontFamily: "MBlack", fontSize: i === 0 ? 178 : 112, lineHeight: 1.08, color: i === 0 ? PINK : "white", ...stroke(12),
            textShadow: i === 0 ? `0 0 40px ${PINK}, 0 10px 0 rgba(0,0,0,0.6)` : "0 8px 0 rgba(0,0,0,0.6)",
            transform: `translateY(${interpolate(s, [0, 1], [120, 0])}px) scale(${interpolate(s, [0, 1], [0.5, 1])})`,
            opacity: interpolate(s, [0, 0.3], [0, 1], { extrapolateRight: "clamp" }) }}>{l}</div>;
        })}
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- incrustations (style SNIR / Velko)
const FxView: React.FC<{ fx: Fx; logo?: string | null }> = ({ fx, logo }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = pop(f, fps);
  const out = interpolate(f, [fx.dur - 6, fx.dur], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const y = fx.y ?? 760;
  const wrap = (child: React.ReactNode, rot = 0) => (
    <AbsoluteFill style={{ alignItems: "center", opacity: out }}>
      <div style={{ position: "absolute", top: y, transform: `translateY(-50%) scale(${interpolate(s, [0, 1], [0.2, 1])}) rotate(${interpolate(s, [0, 1], [rot - 10, rot])}deg)` }}>{child}</div>
    </AbsoluteFill>
  );
  switch (fx.type) {
    case "label": // panneau mot-clé (Velko)
      return wrap(<div style={{ fontFamily: "MBlack", fontSize: Math.min(76, 1500 / Math.max(fx.text.length, 1)), whiteSpace: "nowrap", color: "white", background: "rgba(20,20,28,0.88)", padding: "14px 34px",
        borderRadius: 14, border: "5px solid white", boxShadow: `0 10px 0 rgba(0,0,0,0.5), 0 0 30px ${BLUE}88`, letterSpacing: 2 }}>{fx.text}</div>);
    case "sticker": // sticker penché
      return wrap(<div style={{ fontFamily: "MBlack", fontSize: Math.min(70, 1450 / Math.max(fx.text.length, 1)), whiteSpace: "nowrap", color: "white", background: `linear-gradient(135deg, ${PINK}, ${PURPLE})`,
        padding: "16px 34px", borderRadius: 18, border: "6px solid white", ...stroke(6), boxShadow: "0 12px 0 rgba(0,0,0,0.45)" }}>{fx.text}</div>, -5);
    case "big": // gros mot violet derrière (Velko "FOCUS")
      return <AbsoluteFill style={{ alignItems: "center", opacity: out }}>
        <div style={{ position: "absolute", top: y, transform: `translateY(-50%) scale(${interpolate(s, [0, 1], [2.2, 1])})`,
          fontFamily: "MBlack", fontSize: Math.min(230, 1250 / Math.max(fx.text.length, 1)), whiteSpace: "nowrap", color: PURPLE, textShadow: `0 0 50px ${PURPLE}, 0 14px 0 rgba(0,0,0,0.5)`, ...stroke(10),
          opacity: interpolate(s, [0, 0.4], [0, 1], { extrapolateRight: "clamp" }), letterSpacing: 4 }}>{fx.text}</div>
      </AbsoluteFill>;
    case "counter": { // chiffre qui défile (SNIR)
      const v = interpolate(f, [0, Math.min(24, fx.dur - 4)], [fx.from ?? 0, fx.to], { extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
      const txt = Number.isInteger(fx.to) ? String(Math.round(v)).replace(/\B(?=(\d{3})+(?!\d))/g, "\u00a0") : v.toFixed(1).replace(".", ","); // séparateur fixe (Etienne 21/11)
      return wrap(<div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
        <div style={{ fontFamily: "MBlack", fontSize: 190, color: PINK, fontVariantNumeric: "tabular-nums", whiteSpace: "nowrap", ...stroke(12), textShadow: `0 0 50px ${PINK}` }}>{txt}<span style={{ fontSize: 100, color: "white" }}>{fx.suffix || ""}</span></div>
        {fx.label ? <div style={{ fontFamily: "MBlack", fontSize: 50, color: "white", background: "rgba(0,0,0,0.6)", padding: "8px 26px", borderRadius: 40, marginTop: -10 }}>{fx.label}</div> : null}
      </div>);
    }
    case "clock": { // jauge circulaire (SNIR durée de vie)
      const v = interpolate(f, [0, Math.min(26, fx.dur - 4)], [0, fx.to], { extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
      const R = 150, C = 2 * Math.PI * R, max = fx.max || fx.to;
      return wrap(<div style={{ position: "relative", width: 360, height: 360 }}>
        <svg width={360} height={360} style={{ position: "absolute", filter: `drop-shadow(0 0 20px ${PINK})` }}>
          <circle cx={180} cy={180} r={R} fill="rgba(10,5,25,0.82)" stroke="white" strokeOpacity={0.3} strokeWidth={14} />
          <circle cx={180} cy={180} r={R} fill="none" stroke={PINK} strokeWidth={18} strokeLinecap="round" strokeDasharray={C}
            strokeDashoffset={C * (1 - v / max)} transform="rotate(-90 180 180)" />
        </svg>
        <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "MBlack", fontSize: 120, color: "white" }}>
          {Math.round(v)}<span style={{ fontSize: 70, color: PINK }}>{fx.suffix || ""}</span></div>
      </div>);
    }
    case "bars": { // comparaison (SNIR 50 vs 80)
      const max = Math.max(...fx.items.map((i: any) => i.value));
      return wrap(<div style={{ display: "flex", alignItems: "flex-end", gap: 60, padding: "40px 60px", background: "rgba(10,5,25,0.75)", borderRadius: 30, border: "4px solid rgba(255,255,255,0.4)" }}>
        {fx.items.map((it: any, i: number) => {
          const g = interpolate(f, [4 + i * 5, 22 + i * 5], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
          return <div key={i} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 10 }}>
            <div style={{ fontFamily: "MBlack", fontSize: 64, color: "white", ...stroke(6) }}>{Math.round(it.value * g)}{fx.unit || ""}</div>
            <div style={{ width: 170, height: 420 * (it.value / max) * g, borderRadius: 18, background: i === fx.items.length - 1 ? `linear-gradient(${PINK}, ${PURPLE})` : `linear-gradient(${BLUE}, #2a5bd7)`, position: "relative" }}>
              {it.cross && f > 28 ? <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 150, color: "#ff3b3b", fontFamily: "MBlack" }}>✕</div> : null}
            </div>
            <div style={{ fontFamily: "MBlack", fontSize: 44, color: "white" }}>{it.label}</div>
          </div>;
        })}
      </div>);
    }
    case "stars": // étoiles de recherche
      return wrap(<div style={{ display: "flex", gap: 14 }}>
        {Array.from({ length: fx.n || 5 }).map((_, i) => {
          const si = pop(f, fps, i * 3, 8);
          return <div key={i} style={{ fontSize: 110, color: "white", transform: `scale(${si})`, textShadow: `0 0 20px white, 0 8px 0 rgba(0,0,0,0.5)` }}>★</div>;
        })}
      </div>);
    case "source": { // pastille source (SNIR "Tom Henderson")
      const initials = (fx.name || "?").split(" ").map((w: string) => w[0]).join("").slice(0, 2).toUpperCase();
      return wrap(<div style={{ display: "flex", alignItems: "center", gap: 20, background: "rgba(15,15,20,0.92)", padding: "16px 36px 16px 16px", borderRadius: 70, border: "3px solid rgba(255,255,255,0.35)" }}>
        <div style={{ width: 96, height: 96, borderRadius: 48, background: `linear-gradient(135deg, ${BLUE}, ${PURPLE})`, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "MBlack", fontSize: 42, color: "white" }}>{initials}</div>
        <div style={{ display: "flex", flexDirection: "column" }}>
          <div style={{ fontFamily: "MBlack", fontSize: 50, color: "white" }}>{fx.name} <span style={{ color: BLUE }}>✔</span></div>
          {fx.sub ? <div style={{ fontFamily: "MBlack", fontSize: 32, color: "#aaa" }}>{fx.sub}</div> : null}
        </div>
      </div>);
    }
    case "alert": { // gyrophare + ALERTE
      const blink = Math.floor(f / 4) % 2 === 0;
      return wrap(<div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 6 }}>
        <div style={{ fontSize: 170, filter: blink ? "drop-shadow(0 0 40px red)" : "none" }}>🚨</div>
        <div style={{ fontFamily: "MBlack", fontSize: 92, color: blink ? "#ff3b3b" : "white", ...stroke(10) }}>{fx.text || "ALERTE"}</div>
      </div>);
    }
    case "emoji": // bulles de réaction (fin)
      return <AbsoluteFill style={{ opacity: out }}>
        {(fx.items || ["😱", "🔥"]).map((e: string, i: number) => {
          const si = pop(f, fps, i * 6, 8);
          return <div key={i} style={{ position: "absolute", left: 230 + i * 360, top: (fx.y ?? 820) - Math.sin((f + i * 10) / 8) * 20,
            width: 230, height: 230, borderRadius: 115, background: `linear-gradient(135deg, ${PURPLE}, ${PINK})`, display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 140, transform: `scale(${si})`, border: "6px solid white", boxShadow: `0 0 40px ${PINK}` }}>{e}</div>;
        })}
      </AbsoluteFill>;
    case "subscribe": { // bouton S'abonner cliqué
      const clicked = f > 20;
      const tap = interpolate(f, [8, 18, 22, 30], [80, 0, 0, 60], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
      const press = f >= 18 && f <= 23 ? 0.92 : 1;
      return wrap(<div style={{ position: "relative", display: "flex", alignItems: "center", gap: 22, background: "rgba(15,15,22,0.92)",
        padding: "18px 22px 18px 18px", borderRadius: 80, border: "3px solid rgba(255,255,255,0.3)", boxShadow: `0 0 40px ${PINK}66` }}>
        <div style={{ width: 104, height: 104, borderRadius: 52, background: `linear-gradient(135deg, ${PINK}, ${PURPLE})`, display: "flex",
          alignItems: "center", justifyContent: "center", fontFamily: "MBlack", fontSize: 44, color: "white", border: "4px solid white" }}>VI</div>
        <div style={{ fontFamily: "MBlack", fontSize: 46, color: "white" }}>{fx.handle || "@rockstat433"}</div>
        <div style={{ fontFamily: "MBlack", fontSize: 44, color: "white", padding: "16px 34px", borderRadius: 50, transform: `scale(${press})`,
          background: clicked ? "rgba(255,255,255,0.18)" : "#FE2C55" }}>{clicked ? "Abonné ✓" : "S'abonner"}</div>
        <div style={{ position: "absolute", right: 40, bottom: -70, fontSize: 90, transform: `translate(${tap}px, ${tap}px)`, opacity: f < 34 ? 1 : 0 }}>👆</div>
      </div>);
    }
    case "logo":
      return logo ? wrap(<Img src={staticFile(logo)} style={{ width: fx.width || 420, filter: "drop-shadow(0 10px 20px rgba(0,0,0,0.6))" }} />) : null;
    case "image": // image fournie (galerie officielle déposée sur le Drive)
      return wrap(<div style={{ width: 860, borderRadius: 30, overflow: "hidden", border: "7px solid white", boxShadow: "0 20px 50px rgba(0,0,0,0.6)" }}>
        <Img src={staticFile(fx.src)} style={{ width: "100%", display: "block" }} /></div>, -3);
    default:
      return null;
  }
};

// ---------------------------------------------------------------- éléments fixes
const Progress: React.FC = () => {
  const f = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  return <AbsoluteFill style={{ justifyContent: "flex-end" }}>
    <div style={{ height: 10, width: `${(f / durationInFrames) * 100}%`, background: `linear-gradient(90deg, ${BLUE}, ${PINK})` }} /></AbsoluteFill>;
};
const Handle: React.FC<{ text: string }> = ({ text }) => (
  <AbsoluteFill style={{ alignItems: "center" }}>
    <div style={{ position: "absolute", top: 62, fontFamily: "MBlack", fontSize: 30, color: "white", background: "rgba(0,0,0,0.45)", padding: "6px 20px", borderRadius: 30, display: "flex", gap: 10, alignItems: "center" }}>
      <span style={{ width: 18, height: 18, borderRadius: 9, background: PINK, display: "inline-block" }} />{text}</div>
  </AbsoluteFill>
);

// ---------------------------------------------------------------- composition
export const GtaVideo: React.FC<Props> = (p) => {
  const musicVol = (fr: number) => {
    const talking = p.duck.some(([a, b]) => fr >= a && fr <= b);
    const fadeOut = interpolate(fr, [p.durationInFrames - 36, p.durationInFrames], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
    const fadeIn = interpolate(fr, [0, 12], [0, 1], { extrapolateRight: "clamp" });
    return (talking ? p.musicVolume : p.musicVolume * 2.2) * fadeOut * fadeIn;
  };
  const inCard = (fr: number) => p.cards.some((c) => fr >= c.start && fr < c.end);
  return (
    <AbsoluteFill style={{ background: "black" }}>
      <svg width="0" height="0"><filter id="r"><feColorMatrix type="matrix" values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" /></filter></svg>
      {p.shots.map((s, i) => (
        <Sequence key={i} from={s.from} durationInFrames={s.dur} layout="none">
          <AbsoluteFill><ShotView shot={s} index={i} /></AbsoluteFill>
          {s.cut === "section" && i > 0 ? <Flash color={i % 3 === 0 ? PINK : "white"} /> : null}
        </Sequence>
      ))}
      <AbsoluteFill style={{ background: "radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(0,0,0,0.55) 100%)" }} />
      {/* cartes : un plan par carte, recouvre le plein écran */}
      {p.cards.map((c, i) => (
        <Sequence key={"card" + i} from={c.start} durationInFrames={c.end - c.start}>
          {p.shots.filter((s) => s.from < c.end && s.from + s.dur > c.start).map((s, k) => (
            <Sequence key={k} from={Math.max(s.from - c.start, 0)} durationInFrames={Math.min(s.from + s.dur, c.end) - Math.max(s.from, c.start)}>
              <CardLayout card={c} animate={k === 0} shot={{ ...s, startFrom: s.startFrom + Math.max(c.start - s.from, 0) }} />
            </Sequence>
          ))}
        </Sequence>
      ))}
      {p.title ? <Sequence from={p.title.start} durationInFrames={p.title.end - p.title.start}><Title lines={p.title.lines} /></Sequence> : null}
      {p.items.map((it) => inCard(it.start + 1) ? null : (
        <Sequence key={it.n} from={it.start} durationInFrames={it.end - it.start}><Badge n={it.n} total={it.total} /></Sequence>
      ))}
      {p.fx.map((x, i) => <Sequence key={"fx" + i} from={x.start} durationInFrames={x.dur}><FxView fx={x} logo={p.logo} /></Sequence>)}
      {p.groups.map((g, i) => (
        <Sequence key={i} from={g.start} durationInFrames={Math.max(g.end - g.start, 1)}>
          <Caption text={g.text} y={inCard(g.start) ? 1420 : 1220} />
        </Sequence>
      ))}
      {p.handle ? <Handle text={p.handle} /> : null}
      <Progress />
      <Audio src={staticFile(p.voice)} />
      <Audio src={staticFile(p.music)} startFrom={p.musicStartFrom} volume={musicVol} loop />
      {p.sfx.map((s, i) => (
        <Sequence key={"sfx" + i} from={Math.max(s.frame, 0)} layout="none"><Audio src={staticFile(s.src)} volume={s.volume} /></Sequence>
      ))}
    </AbsoluteFill>
  );
};
