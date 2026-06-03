import { app } from "../../scripts/app.js";

const NODE_CLASS = "LfggLatentSizeByRatio";
const STYLE_ID = "lfgg-latent-ratio-preview-styles";
const DEFAULT_RATIO = { w: 1, h: 1 };

const RATIO_PRESETS = {
  "1:1 (Square)": { w: 1, h: 1 },
  "4:3": { w: 4, h: 3 },
  "3:2": { w: 3, h: 2 },
  "16:9": { w: 16, h: 9 },
  "9:16": { w: 9, h: 16 },
  Custom: null,
};

function ensureStyles() {
  if (document.getElementById(STYLE_ID)) {
    return;
  }

  const style = document.createElement("style");
  style.id = STYLE_ID;
  style.textContent = `
    .lfgg-ratio-preview {
      display: flex;
      flex-direction: column;
      gap: 8px;
      padding: 10px;
      border-radius: 10px;
      border: 1px solid rgba(120, 120, 120, 0.35);
      background: rgba(20, 20, 20, 0.2);
    }
    .lfgg-ratio-preview__header {
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      opacity: 0.7;
    }
    .lfgg-ratio-preview__box {
      width: 140px;
      height: 140px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 12px;
      border: 1px dashed rgba(140, 140, 140, 0.4);
      background:
        repeating-linear-gradient(
          0deg,
          rgba(220, 220, 220, 0.08),
          rgba(220, 220, 220, 0.08) 1px,
          transparent 1px,
          transparent 14px
        ),
        repeating-linear-gradient(
          90deg,
          rgba(220, 220, 220, 0.08),
          rgba(220, 220, 220, 0.08) 1px,
          transparent 1px,
          transparent 14px
        ),
        linear-gradient(135deg, rgba(64, 64, 64, 0.2), rgba(32, 32, 32, 0.6));
      position: relative;
    }
    .lfgg-ratio-preview__frame {
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 8px;
      border: 1px solid rgba(200, 200, 200, 0.85);
      background: rgba(140, 140, 140, 0.18);
      box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
      transition: width 0.12s ease, height 0.12s ease;
    }
    .lfgg-ratio-preview__text {
      font-size: 14px;
      font-weight: 600;
      letter-spacing: 0.03em;
      color: rgba(240, 240, 240, 0.9);
    }
    .lfgg-ratio-preview__hint {
      font-size: 11px;
      opacity: 0.6;
    }
  `;
  document.head.appendChild(style);
}

function getWidgetValue(node, name) {
  const widget = node.widgets?.find((item) => item.name === name);
  return widget ? widget.value : undefined;
}

function toPositiveInt(value, fallback) {
  const parsed = Number.parseInt(value, 10);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

function resolveRatio(node) {
  const preset = getWidgetValue(node, "ratio_preset");
  if (preset === "Custom") {
    return {
      w: toPositiveInt(getWidgetValue(node, "custom_ratio_w"), DEFAULT_RATIO.w),
      h: toPositiveInt(getWidgetValue(node, "custom_ratio_h"), DEFAULT_RATIO.h),
    };
  }

  if (preset && RATIO_PRESETS[preset]) {
    return RATIO_PRESETS[preset];
  }

  if (typeof preset === "string" && preset.includes(":")) {
    const [left, right] = preset.split(":");
    return {
      w: toPositiveInt(left, DEFAULT_RATIO.w),
      h: toPositiveInt(right, DEFAULT_RATIO.h),
    };
  }

  return DEFAULT_RATIO;
}

function updatePreview(node, elements) {
  const ratio = resolveRatio(node) ?? DEFAULT_RATIO;
  const safeW = ratio.w || DEFAULT_RATIO.w;
  const safeH = ratio.h || DEFAULT_RATIO.h;
  const value = safeW / safeH;

  const boxSize = Math.min(
    elements.box.clientWidth || 140,
    elements.box.clientHeight || 140
  );

  let frameWidth;
  let frameHeight;

  if (value >= 1) {
    frameWidth = boxSize;
    frameHeight = Math.max(12, Math.round(boxSize / value));
  } else {
    frameHeight = boxSize;
    frameWidth = Math.max(12, Math.round(boxSize * value));
  }

  elements.frame.style.width = `${frameWidth}px`;
  elements.frame.style.height = `${frameHeight}px`;
  elements.text.textContent = `${safeW}:${safeH}`;
  elements.hint.textContent =
    safeW === DEFAULT_RATIO.w && safeH === DEFAULT_RATIO.h
      ? "Ratio preview"
      : `Ratio preview (${safeW}:${safeH})`;
}

function hookWidget(widget, onUpdate) {
  if (!widget || widget.__lfggRatioHooked) {
    return;
  }

  const originalCallback = widget.callback;
  widget.callback = (...args) => {
    if (typeof originalCallback === "function") {
      originalCallback(...args);
    }
    onUpdate();
  };
  widget.__lfggRatioHooked = true;
}

function addRatioPreview(node) {
  ensureStyles();

  const container = document.createElement("div");
  container.className = "lfgg-ratio-preview";

  const header = document.createElement("div");
  header.className = "lfgg-ratio-preview__header";
  header.textContent = "Ratio Preview";

  const box = document.createElement("div");
  box.className = "lfgg-ratio-preview__box";

  const frame = document.createElement("div");
  frame.className = "lfgg-ratio-preview__frame";

  const text = document.createElement("div");
  text.className = "lfgg-ratio-preview__text";

  const hint = document.createElement("div");
  hint.className = "lfgg-ratio-preview__hint";

  frame.appendChild(text);
  box.appendChild(frame);
  container.appendChild(header);
  container.appendChild(box);
  container.appendChild(hint);

  const widget = node.addDOMWidget("lfgg_ratio_preview", "ratio_preview", container, {
    serialize: false,
    hideOnZoom: false,
    getMinHeight: () => 200,
  });

  const update = () => updatePreview(node, { box, frame, text, hint });
  let lastSignature = "";

  const poll = () => {
    const ratio = resolveRatio(node) ?? DEFAULT_RATIO;
    const signature = `${ratio.w}:${ratio.h}:${node.size?.[0]}:${node.size?.[1]}`;
    if (signature !== lastSignature) {
      lastSignature = signature;
      update();
    }
  };

  hookWidget(node.widgets?.find((item) => item.name === "ratio_preset"), update);
  hookWidget(node.widgets?.find((item) => item.name === "custom_ratio_w"), update);
  hookWidget(node.widgets?.find((item) => item.name === "custom_ratio_h"), update);

  const originalOnWidgetChanged = node.onWidgetChanged;
  node.onWidgetChanged = function onWidgetChanged(name, value, widget) {
    if (typeof originalOnWidgetChanged === "function") {
      originalOnWidgetChanged.apply(this, [name, value, widget]);
    }
    if (
      name === "ratio_preset" ||
      name === "custom_ratio_w" ||
      name === "custom_ratio_h"
    ) {
      update();
    }
  };

  requestAnimationFrame(update);

  const [width, height] = node.size;
  node.setSize([Math.max(width, 260), Math.max(height, 280)]);

  const pollTimer = window.setInterval(poll, 200);

  widget.onRemove = () => {
    window.clearInterval(pollTimer);
    container.remove();
  };
}

app.registerExtension({
  name: "lfgg.latent-size-by-ratio.preview",
  nodeCreated(node) {
    if (node.constructor?.comfyClass !== NODE_CLASS) {
      return;
    }
    addRatioPreview(node);
  },
});
