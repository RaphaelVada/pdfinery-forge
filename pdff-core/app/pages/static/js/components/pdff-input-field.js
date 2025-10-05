// pdff-core/app/pages/static/js/components/pdff-input-field.js

import { BaseComponent } from './base-component.js';

class PdffInputField extends BaseComponent {
  static get observedAttributes() {
    return ['label', 'type', 'value', 'placeholder', 'required', 'state'];
  }

  constructor() {
    super();
    this._originalValue = '';
    this._debounceTimer = null;
  }

  // Getters/Setters
  get value() {
    return this.getAttribute('value') || '';
  }

  set value(val) {
    this.setAttribute('value', val);
  }

  get label() {
    return this.getAttribute('label') || '';
  }

  get type() {
    return this.getAttribute('type') || 'text';
  }

  get required() {
    return this.hasAttribute('required');
  }

  get state() {
    return this.getAttribute('state') || 'empty';
  }

  set state(val) {
    this.setAttribute('state', val);
  }

  // Lifecycle
  connectedCallback() {
    super.connectedCallback();
    this._originalValue = this.value;
  }

  attributeChangedCallback(name, oldValue, newValue) {
    if (oldValue !== newValue) {
      this.render();
    }
  }

  // Setup events
  setupEventListeners() {
    const input = this.shadowRoot.querySelector('input');
    if (input) {
      this.addListener(input, 'input', (e) => this.handleInput(e));
      this.addListener(input, 'focus', () => this.handleFocus());
      this.addListener(input, 'blur', () => this.handleBlur());
    }
  }

  handleInput(event) {
    const newValue = event.target.value;
    this.setAttribute('value', newValue);
    
    // Update state
    if (newValue && newValue !== this._originalValue) {
      this.state = 'changed';
    } else if (newValue) {
      this.state = 'filled';
    } else {
      this.state = 'empty';
    }

    // Debounced emit
    clearTimeout(this._debounceTimer);
    this._debounceTimer = setTimeout(() => {
      this.emit('value-changed', { 
        value: newValue,
        field: this.getAttribute('name') || this.label.toLowerCase().replace(/\s+/g, '_')
      });
    }, 300);
  }

  handleFocus() {
    this.shadowRoot.querySelector('.form-group').classList.add('focused');
  }

  handleBlur() {
    this.shadowRoot.querySelector('.form-group').classList.remove('focused');
  }

  // Reset to original value
  reset() {
    this.value = '';
    this.state = 'empty';
    this._originalValue = '';
    this.render();
  }

  // Set original value (for change detection)
  setOriginalValue(val) {
    this._originalValue = val;
    this.value = val;
    this.state = val ? 'filled' : 'empty';
    this.render();
  }

  render() {
    const stateClass = this.state ? `state-${this.state}` : '';
    
    this.shadowRoot.innerHTML = `
      ${this.createStyles(this.styles).outerHTML}
      <div class="form-group ${stateClass}">
        <label>${this.label}</label>
        <input 
          type="${this.type}"
          value="${this.value}"
          placeholder="${this.getAttribute('placeholder') || ''}"
          ${this.required ? 'required' : ''}
        />
      </div>
    `;

    this.setupEventListeners();
  }

  get styles() {
    return `
      :host {
        display: block;
        margin-bottom: var(--space-xl, 1.5rem);
      }

      .form-group {
        position: relative;
      }

      label {
        display: block;
        font-weight: 500;
        color: var(--text-secondary, rgba(255, 255, 255, 0.9));
        margin-bottom: var(--space-sm, 0.5rem);
        font-size: 0.95rem;
      }

      input {
        width: 100%;
        padding: var(--space-md, 0.75rem);
        background: var(--bg-glass, rgba(255, 255, 255, 0.1));
        border: 1px solid var(--border-light, rgba(255, 255, 255, 0.2));
        border-radius: var(--radius-md, 8px);
        color: var(--text-primary, white);
        font-size: 0.95rem;
        transition: all var(--transition-base, 0.3s ease);
        font-family: inherit;
      }

      input:focus {
        outline: none;
        background: var(--bg-glass-hover, rgba(255, 255, 255, 0.15));
        border-color: var(--border-focus, rgba(16, 185, 129, 0.6));
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
      }

      /* State variations */
      .state-changed input {
        background: rgba(59, 130, 246, 0.15);
        border-color: rgba(59, 130, 246, 0.5);
      }

      .state-error input {
        background: rgba(239, 68, 68, 0.15);
        border-color: rgba(239, 68, 68, 0.5);
      }

      /* Date input specific */
      input[type="date"]::-webkit-calendar-picker-indicator {
        filter: invert(1);
        cursor: pointer;
      }
    `;
  }
}

customElements.define('pdff-input-field', PdffInputField);
export default PdffInputField;