import { app } from "../../scripts/app.js";

const NODE_CLASS = "LfggPromptWildcard";
const NO_SELECTION = "<select wildcard>";

function getWidget(node, name) {
  return node.widgets?.find((item) => item.name === name);
}

function appendTokenToText(node, token) {
  const textWidget = getWidget(node, "wildcard_text");
  if (!textWidget) {
    return;
  }

  let value = textWidget.value ?? "";
  if (value && !value.endsWith(" ")) {
    value += " ";
  }
  value += token;
  textWidget.value = value;

  if (typeof node.onWidgetChanged === "function") {
    node.onWidgetChanged("wildcard_text", value, textWidget);
  }
  if (typeof textWidget.callback === "function") {
    textWidget.callback(value);
  }
  node.setDirtyCanvas(true, true);
}

function resetWildcardSelect(widget) {
  widget.value = NO_SELECTION;
  if (typeof widget.callback === "function") {
    widget.callback(NO_SELECTION);
  }
}

function updatePopulatedText(node, output) {
  const modeWidget = getWidget(node, "mode");
  if (modeWidget && modeWidget.value !== "populate") {
    return;
  }
  const textValue = output?.text?.[0] ?? output?.text;
  if (typeof textValue !== "string") {
    return;
  }

  const populatedWidget = getWidget(node, "populated_text");
  if (!populatedWidget) {
    return;
  }
  populatedWidget.value = textValue;
  if (typeof populatedWidget.callback === "function") {
    populatedWidget.callback(textValue);
  }
  if (typeof node.onWidgetChanged === "function") {
    node.onWidgetChanged("populated_text", textValue, populatedWidget);
  }
  node.setDirtyCanvas(true, true);
}

app.registerExtension({
  name: "lfgg.prompt-wildcard.append",
  nodeCreated(node) {
    if (node.constructor?.comfyClass !== NODE_CLASS) {
      return;
    }

    const selectWidget = getWidget(node, "add_wildcard");
    if (!selectWidget || selectWidget.__lfggWildcardHooked) {
      return;
    }

    const originalCallback = selectWidget.callback;
    selectWidget.callback = (value, ...args) => {
      if (typeof originalCallback === "function") {
        originalCallback(value, ...args);
      }
      if (!value || value === NO_SELECTION) {
        return;
      }
      const token = `__${value}__`;
      appendTokenToText(node, token);
      resetWildcardSelect(selectWidget);
    };
    selectWidget.__lfggWildcardHooked = true;

    const originalOnExecuted = node.onExecuted;
    node.onExecuted = function onExecuted(output) {
      if (typeof originalOnExecuted === "function") {
        originalOnExecuted.call(this, output);
      }
      updatePopulatedText(node, output);
    };
  },
});
