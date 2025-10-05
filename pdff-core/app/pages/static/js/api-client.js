// pdff-core/app/pages/static/js/api-client.js

export class ApiClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
  }

  // Generic fetch wrapper with error handling
  async _fetch(url, options = {}) {
    try {
      const response = await fetch(`${this.baseUrl}${url}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        }
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      return response;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  // Document operations
  async getDocument(documentId) {
    const response = await this._fetch(`/documents/${documentId}`);
    return response.json();
  }

  async updateMetadata(documentId, metadata) {
    const response = await this._fetch(`/documents/${documentId}`, {
      method: 'PATCH',
      body: JSON.stringify(metadata)
    });
    return response.json();
  }

  async saveDocument(documentId) {
    const response = await this._fetch(`/documents/${documentId}/save`, {
      method: 'POST'
    });
    return response.json();
  }

  async previewFilename(documentId, metadata) {
    const response = await this._fetch(`/documents/${documentId}/preview-filename`, {
      method: 'POST',
      body: JSON.stringify(metadata)
    });
    return response.json();
  }

  // Navigation
  async getNavigation(documentId, filter = 'unprocessed') {
    const response = await this._fetch(`/documents/${documentId}/navigation?filter=${filter}`);
    return response.json();
  }

  // PDF URL helper
  getPdfUrl(documentId) {
    return `${this.baseUrl}/documents/${documentId}/pdf`;
  }
}