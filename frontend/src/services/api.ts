const API_BASE_URL = "http://localhost:8000";

// Types for API responses
export interface PDF {
  id: number;
  title: string;
  filename: string;
  content_type: string;
  file_size: number;
  total_pages: number;
  processing_status: string;
  processing_error?: string | null;
  author?: string | null;
  subject?: string;
  keywords?: string;
  file_size_mb: number;
  is_processed: boolean;
  created_at: string;
  updated_at: string;
}

export interface PDFChunk {
  id: number;
  pdf_id: number;
  chunk_number: number;
  page_number: number;
  content: string;
  content_type: string;
  word_count: number;
  character_count: number;
  chunk_metadata?: any;
  preview: string;
  created_at: string;
  updated_at: string;
}

export interface PDFListResponse {
  items: PDF[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface PDFDetailResponse extends PDF {
  chunks: PDFChunk[];
}

export interface PDFChunkListResponse {
  items: PDFChunk[];
  total: number;
  page: number;
  size: number;
  pages: number;
  pdf_id: number;
}

export interface PDFChunkSearchResponse {
  items: PDFChunk[];
  total: number;
  page: number;
  size: number;
  pages: number;
  query: string;
  pdf_id?: number;
}

// API client class
class ApiClient {
  private baseURL: string;

  constructor(baseURL: string) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    const config: RequestInit = {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    };

    // Add auth token if available
    const token = localStorage.getItem("token");
    if (token) {
      config.headers = {
        ...config.headers,
        Authorization: `Bearer ${token}`,
      };
    }

    const response = await fetch(url, config);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail || `HTTP error! status: ${response.status}`
      );
    }

    return response.json();
  }

  // Authentication
  async login(
    username: string,
    password: string
  ): Promise<{ access_token: string; token_type: string }> {
    const formData = new FormData();
    formData.append("username", username);
    formData.append("password", password);

    const response = await fetch(`${this.baseURL}/token`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || "Login failed");
    }

    return response.json();
  }

  // PDF endpoints
  async uploadPDF(file: File, title?: string): Promise<PDF> {
    const formData = new FormData();
    formData.append("file", file);
    if (title) {
      formData.append("title", title);
    }

    const token = localStorage.getItem("token");
    const response = await fetch(`${this.baseURL}/api/pdfs/upload`, {
      method: "POST",
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || "Upload failed");
    }

    return response.json();
  }

  async getPDFs(page: number = 1, size: number = 10): Promise<PDFListResponse> {
    const skip = (page - 1) * size;
    return this.request<PDFListResponse>(
      `/api/pdfs/?skip=${skip}&limit=${size}`
    );
  }

  async getPDF(id: number): Promise<PDFDetailResponse> {
    return this.request<PDFDetailResponse>(`/api/pdfs/${id}`);
  }

  async getPDFChunks(
    pdfId: number,
    page: number = 1,
    size: number = 20
  ): Promise<PDFChunkListResponse> {
    const skip = (page - 1) * size;
    return this.request<PDFChunkListResponse>(
      `/api/pdfs/${pdfId}/chunks?skip=${skip}&limit=${size}`
    );
  }

  async searchPDFContent(
    query: string,
    pdfId?: number,
    page: number = 1,
    size: number = 20
  ): Promise<PDFChunkSearchResponse> {
    const skip = (page - 1) * size;
    const params = new URLSearchParams({
      q: query,
      skip: skip.toString(),
      limit: size.toString(),
    });

    if (pdfId) {
      params.append("pdf_id", pdfId.toString());
    }

    return this.request<PDFChunkSearchResponse>(
      `/api/pdfs/search/content?${params}`
    );
  }

  async deletePDF(id: number): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/api/pdfs/${id}`, {
      method: "DELETE",
    });
  }
}

// Export singleton instance
export const apiClient = new ApiClient(API_BASE_URL);
