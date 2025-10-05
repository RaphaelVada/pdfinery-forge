// pdff-core/app/pages/static/js/components/pdff-status-indicator.js

import { BaseComponent } from './base-component.js';

class PdffStatusIndicator extends BaseComponent {
  static get observedAttributes() {
    return ['status', 'filename'];
  }

  constructor() {
    super();
    this.statusConfig = {
      'unsaved': { 
        color: 'var(--status-unsaved)', 
        text: 'Nicht gespeichert',
        pulse: true 
      },
      'saved': { 
        color: 'var(--status-saved)', 
        text: 'Gespeichert',
        pulse: false 
      },
      'changed': { 
        color: 'var(--status-changed)', 
        text: 'Geändert',
        pulse: true 
      },
      'not-generatable': { 
        color: 'var(--status-error)', 
        text: 'Nicht generierbar',
        pulse: false 
      },
      'loading': { 
        color: 'var(--status-neutral)', 
        text: 'Lädt...',
        pulse: true 
      }
    };
  }

  get status() {
    return this.getAttribute('status') || 'not-generatable';
  }

  set status(val) {
    this.setAttribute('status', val);
  }

  get filename() {
    return this.getAttribute('filename') || '---';
  }

  set filename(val) {
    this.setAttribute('filename', val);
  }

  attributeChangedCallback(name, oldValue, newValue) {
    if (oldValue !== newValue) {
      this.render();
    }
  }

  render() {
    const config = this.statusConfig[this.status] || this.statusConfig['not-generatable'];
    
    this.shadowRoot.innerHTML = `
      ${this.createStyles(this.styles).outerHTML}
      <div class="status-container">
        <div class="status-badge ${this.status}">
          <span class="status-dot ${config.pulse ? 'pulse' : ''}"></span>
          <span class="status-text">${config.text}</span>
        </div>
        <div class="filename-display">
          <div class="filename-text ${this.status}">${this.filename}</div>
          <slot name="action"></slot>
        </div>
      </div>
    `;
  }

  get styles() {
    return `
      :host {
        display: block;
      }

      .status-container {
        background: var(--bg-glass, rgba(255, 255, 255, 0.08));
        border-radius: var(--radius-md, 8px);
        padding: var(--space-xl, 1.5rem);
        border: 1px solid var(--border-glass, rgba(255, 255, 255, 0.15));
      }

      .status-badge {
        display: inline-flex;
        align-items: center;
        gap: var(--space-sm, 0.5rem);
        padding: var(--space-sm, 0.5rem) var(--space-lg, 1rem);
        border-radius: var(--radius-sm, 6px);
        font-size: 0.85rem;
        font-weight: 500;
        margin-bottom: var(--space-lg, 1rem);
        transition: all var(--transition-base, 0.3s ease);
      }

      .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        transition: background-color var(--transition-base, 0.3s ease);
      }

      .status-dot.pulse {
        animation: pulse 2s infinite;
      }

      @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
      }

      .status-text {
        color: currentColor;
      }

      /* Status variations */
      .status-badge.unsaved {
        background: rgba(251, 191, 36, 0.2);
        color: var(--status-unsaved);
      }

      .status-badge.saved {
        background: rgba(16, 185, 129, 0.2);
        color: var(--status-saved);
      }

      .status-badge.changed {
        background: rgba(59, 130, 246, 0.2);
        color: var(--status-changed);
      }

      .status-badge.not-generatable {
        background: rgba(239, 68, 68, 0.2);
        color: var(--status-error);
      }

      .status-badge.loading {
        background: rgba(107, 114, 128, 0.2);
        color: var(--status-neutral);
      }

      /* Filename display */
      .filename-display {
        display: flex;
        align-items: center;
        gap: var(--space-lg, 1rem);
      }

      .filename-text {
        flex: 1;
        font-family: var(--font-mono, monospace);
        font-size: 0.95rem;
        color: var(--text-primary, white);
        word-break: break-all;
        padding: var(--space-md, 0.75rem);
        background: var(--bg-glass-dark, rgba(0, 0, 0, 0.2));
        border-radius: var(--radius-sm, 6px);
        border: 2px solid transparent;
        transition: all var(--transition-base, 0.3s ease);
      }

      .filename-text.unsaved {
        border-color: rgba(251, 191, 36, 0.5);
        background: rgba(251, 191, 36, 0.1);
      }

      .filename-text.changed {
        border-color: rgba(59, 130, 246, 0.5);
        background: rgba(59, 130, 246, 0.1);
      }

      .filename-text.saved {
        border-color: rgba(16, 185, 129, 0.5);
        background: rgba(16, 185, 129, 0.1);
      }

      .filename-text.not-generatable {
        border-color: rgba(239, 68, 68, 0.5);
        background: rgba(239, 68, 68, 0.1);
      }

      /* Action slot */
      ::slotted(*) {
        flex-shrink: 0;
      }
    `;
  }
}

customElements.define('pdff-status-indicator', PdffStatusIndicator);
export default PdffStatusIndicator;