// pdff-core/app/pages/static/js/editor-controller.js

import { ApiClient } from './api-client.js';

export class EditorController {
  constructor(apiUrl, documentId) {
    this.api = new ApiClient(apiUrl);
    this.documentId = documentId;
    this.currentDocument = null;
    this.navigationData = null;
    this.previewTimer = null;
    
    // Cache DOM elements (will be set in init)
    this.elements = {};
  }

  async init() {
    try {
      // Cache all elements
      this.cacheElements();
      
      // Setup event listeners
      this.setupEventListeners();
      
      // Load initial data
      await Promise.all([
        this.loadDocument(),
        this.loadNavigation()
      ]);
      
      console.log('Editor initialized for document:', this.documentId);
    } catch (error) {
      this.showError('Initialisierung fehlgeschlagen: ' + error.message);
    }
  }

  cacheElements() {
    // Input fields
    this.elements.correspondent = document.querySelector('pdff-input-field[name="correspondent"]');
    this.elements.documentType = document.querySelector('pdff-input-field[name="document_type"]');
    this.elements.topic = document.querySelector('pdff-input-field[name="topic"]');
    this.elements.customerId = document.querySelector('pdff-input-field[name="customer_id"]');
    this.elements.documentNumber = document.querySelector('pdff-input-field[name="document_number"]');
    this.elements.documentDate = document.querySelector('pdff-input-field[name="document_date"]');
    
    // Status & Display
    this.elements.statusIndicator = document.querySelector('pdff-status-indicator');
    this.elements.currentFilename = document.getElementById('currentFilename');
    this.elements.pageTitle = document.querySelector('title');
    
    // Navigation
    this.elements.navPosition = document.getElementById('navPosition');
    this.elements.btnPrevious = document.getElementById('btnPrevious');
    this.elements.btnNext = document.getElementById('btnNext');
    this.elements.previousInfo = document.getElementById('previousInfo');
    this.elements.nextInfo = document.getElementById('nextInfo');
    
    // Actions
    this.elements.saveBtn = document.getElementById('saveBtn');
    this.elements.pdfViewer = document.getElementById('pdfViewer');
    this.elements.errorBox = document.getElementById('errorBox');
  }

  setupEventListeners() {
    // Input change events
    const inputFields = document.querySelectorAll('pdff-input-field');
    inputFields.forEach(field => {
      field.addEventListener('value-changed', (e) => this.handleInputChange(e));
    });
    
    // Save button
    this.elements.saveBtn?.addEventListener('click', () => this.handleSave());
    
    // Navigation buttons
    this.elements.btnPrevious?.addEventListener('click', () => this.navigateToPrevious());
    this.elements.btnNext?.addEventListener('click', () => this.navigateToNext());
    
    // Browser navigation (back/forward)
    window.addEventListener('popstate', (event) => {
      if (event.state?.documentId) {
        this.documentId = event.state.documentId;
        this.resetForm();
        this.loadDocument();
        this.loadNavigation();
      }
    });
  }

  async loadDocument() {
    try {
      // Set loading state
      this.elements.statusIndicator.status = 'loading';
      
      // Fetch document data
      const data = await this.api.getDocument(this.documentId);
      this.currentDocument = data;
      
      // Update PDF viewer
      if (this.elements.pdfViewer) {
        this.elements.pdfViewer.src = this.api.getPdfUrl(this.documentId);
      }
      
      // Update header
      this.elements.currentFilename.textContent = data.current_filename;
      this.elements.pageTitle.textContent = `${data.current_filename} - PDFF Core`;
      
      // Set form values
      this.elements.correspondent?.setOriginalValue(data.metadata.correspondent || '');
      this.elements.documentType?.setOriginalValue(data.metadata.document_type || '');
      this.elements.topic?.setOriginalValue(data.metadata.topic || '');
      this.elements.customerId?.setOriginalValue(data.metadata.customer_id || '');
      this.elements.documentNumber?.setOriginalValue(data.metadata.document_number || '');
      this.elements.documentDate?.setOriginalValue(data.metadata.document_date || '');
      
      // Update filename preview
      await this.updateFilenamePreview();
      
    } catch (error) {
      this.showError('Dokument konnte nicht geladen werden: ' + error.message);
    }
  }

  async loadNavigation() {
    try {
      this.navigationData = await this.api.getNavigation(this.documentId, 'unprocessed');
      this.updateNavigationUI();
    } catch (error) {
      console.error('Navigation konnte nicht geladen werden:', error);
    }
  }

  updateNavigationUI() {
    if (!this.navigationData) return;
    
    // Previous button
    if (this.navigationData.previous) {
      this.elements.btnPrevious.disabled = false;
      this.elements.previousInfo.textContent = this.navigationData.previous.id.substring(0, 8) + '...';
    } else {
      this.elements.btnPrevious.disabled = true;
      this.elements.previousInfo.textContent = '---';
    }
    
    // Next button
    if (this.navigationData.next) {
      this.elements.btnNext.disabled = false;
      this.elements.nextInfo.textContent = this.navigationData.next.id.substring(0, 8) + '...';
    } else {
      this.elements.btnNext.disabled = true;
      this.elements.nextInfo.textContent = '---';
    }
    
    // Position indicator
    this.elements.navPosition.textContent = 
      `(${this.navigationData.current_position} von ${this.navigationData.total_unprocessed})`;
  }

  handleInputChange(event) {
    // Debounce preview update
    clearTimeout(this.previewTimer);
    this.previewTimer = setTimeout(() => {
      this.updateFilenamePreview();
    }, 500);
  }

  async updateFilenamePreview() {
    try {
      const metadata = this.collectMetadata();
      const preview = await this.api.previewFilename(this.documentId, metadata);
      
      // Update status indicator
      this.elements.statusIndicator.filename = preview.preview_filename;
      
      // Determine status
      let status = 'not-generatable';
      if (preview.is_complete) {
        if (!this.currentDocument.is_saved) {
          status = 'unsaved';
        } else if (preview.preview_filename !== this.currentDocument.current_filename) {
          status = 'changed';
        } else {
          status = 'saved';
        }
      }
      
      this.elements.statusIndicator.status = status;
      
      // Enable/disable save button
      this.elements.saveBtn.disabled = !preview.is_complete || status === 'saved';
      
    } catch (error) {
      console.error('Preview fehlgeschlagen:', error);
    }
  }

  collectMetadata() {
    return {
      correspondent: this.elements.correspondent?.value || null,
      document_type: this.elements.documentType?.value || null,
      topic: this.elements.topic?.value || null,
      customer_id: this.elements.customerId?.value || null,
      document_number: this.elements.documentNumber?.value || null,
      document_date: this.elements.documentDate?.value || null
    };
  }

  async handleSave() {
    const saveBtn = this.elements.saveBtn;
    const originalText = saveBtn.textContent;
    
    try {
      // Set loading state
      saveBtn.textContent = '⏳ Speichere...';
      saveBtn.disabled = true;
      this.elements.statusIndicator.status = 'loading';
      
      // Collect and update metadata
      const metadata = this.collectMetadata();
      await this.api.updateMetadata(this.documentId, metadata);
      
      // Save document
      const saveResult = await this.api.saveDocument(this.documentId);
      
      // Update UI with success
      this.currentDocument.current_filename = saveResult.generated_filename;
      this.currentDocument.is_saved = true;
      
      this.elements.currentFilename.textContent = saveResult.generated_filename;
      this.elements.pageTitle.textContent = `${saveResult.generated_filename} - PDFF Core`;
      this.elements.statusIndicator.filename = saveResult.generated_filename;
      this.elements.statusIndicator.status = 'saved';
      
      // Reset field states
      document.querySelectorAll('pdff-input-field').forEach(field => {
        field.state = field.value ? 'filled' : 'empty';
      });
      
      // Reload navigation (document is now processed)
      await this.loadNavigation();
      
      // Success feedback
      saveBtn.textContent = '✓ Gespeichert!';
      setTimeout(() => {
        saveBtn.textContent = originalText;
      }, 2000);
      
    } catch (error) {
      this.showError('Speichern fehlgeschlagen: ' + error.message);
      saveBtn.textContent = originalText;
      saveBtn.disabled = false;
      this.elements.statusIndicator.status = 'changed';
    }
  }

  navigateToPrevious() {
    if (this.navigationData?.previous) {
      this.navigateToDocument(this.navigationData.previous.id);
    }
  }

  navigateToNext() {
    if (this.navigationData?.next) {
      this.navigateToDocument(this.navigationData.next.id);
    }
  }

  navigateToDocument(documentId) {
    // Update URL without reload
    const newUrl = `/editor?document_id=${documentId}`;
    window.history.pushState({documentId}, '', newUrl);
    
    // Update controller state
    this.documentId = documentId;
    
    // Reset and reload
    this.resetForm();
    this.loadDocument();
    this.loadNavigation();
  }

  resetForm() {
    // Reset all input fields
    document.querySelectorAll('pdff-input-field').forEach(field => {
      field.reset();
    });
    
    // Reset status
    this.elements.statusIndicator.status = 'not-generatable';
    this.elements.statusIndicator.filename = '---';
    this.elements.saveBtn.disabled = true;
  }

  showError(message) {
    if (this.elements.errorBox) {
      this.elements.errorBox.textContent = message;
      this.elements.errorBox.style.display = 'block';
      
      setTimeout(() => {
        this.elements.errorBox.style.display = 'none';
      }, 5000);
    }
    console.error(message);
  }
}