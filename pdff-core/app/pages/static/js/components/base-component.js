// pdff-core/app/pages/static/js/components/base-component.js

export class BaseComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._listeners = new Map();
  }

  // Lifecycle
  connectedCallback() {
    this.render();
    this.setupEventListeners();
  }

  disconnectedCallback() {
    this.cleanupEventListeners();
  }

  // Event handling helpers
  setupEventListeners() {
    // Override in child classes
  }

  cleanupEventListeners() {
    this._listeners.forEach((listener, element) => {
      element.removeEventListener(...listener);
    });
    this._listeners.clear();
  }

  addListener(element, event, handler) {
    element.addEventListener(event, handler);
    this._listeners.set(element, [event, handler]);
  }

  // Emit custom events
  emit(eventName, detail = null) {
    this.dispatchEvent(new CustomEvent(eventName, {
      detail,
      bubbles: true,
      composed: true
    }));
  }

  // Default render (override in child)
  render() {
    this.shadowRoot.innerHTML = '';
  }

  // Utility: Create style element
  createStyles(css) {
    const style = document.createElement('style');
    style.textContent = css;
    return style;
  }
}