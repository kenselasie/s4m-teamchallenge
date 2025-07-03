/**
 * Custom hooks for PDF operations using TanStack Query
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, PDF, PDFListResponse, PDFDetailResponse, PDFChunkListResponse, PDFChunkSearchResponse } from '../services/api';
import { useNotification } from '../context/NotificationContext';

// Query keys
export const pdfKeys = {
  all: ['pdfs'] as const,
  lists: () => [...pdfKeys.all, 'list'] as const,
  list: (params: { page: number; size: number }) => [...pdfKeys.lists(), params] as const,
  details: () => [...pdfKeys.all, 'detail'] as const,
  detail: (id: number) => [...pdfKeys.details(), id] as const,
  chunks: (id: number) => [...pdfKeys.detail(id), 'chunks'] as const,
  chunkList: (params: { id: number; page: number; size: number }) => [...pdfKeys.chunks(params.id), { page: params.page, size: params.size }] as const,
  search: (params: { query: string; pdfId?: number; page?: number; size?: number }) => [...pdfKeys.all, 'search', params] as const,
};

// Hook for fetching PDFs list
export const usePDFs = (params: { page?: number; size?: number } = {}) => {
  const { page = 1, size = 10 } = params;
  return useQuery<PDFListResponse>({
    queryKey: pdfKeys.list({ page, size }),
    queryFn: () => apiClient.getPDFs(page, size),
    placeholderData: (previousData) => previousData,
  });
};

// Hook for fetching single PDF
export const usePDF = (id: number) => {
  return useQuery<PDFDetailResponse>({
    queryKey: pdfKeys.detail(id),
    queryFn: () => apiClient.getPDF(id),
    enabled: !!id,
  });
};

// Hook for fetching PDF chunks
export const usePDFChunks = (params: { pdfId: number; page?: number; size?: number }) => {
  const { pdfId, page = 1, size = 10 } = params;
  return useQuery<PDFChunkListResponse>({
    queryKey: pdfKeys.chunkList({ id: pdfId, page, size }),
    queryFn: () => apiClient.getPDFChunks(pdfId, page, size),
    enabled: !!pdfId,
    placeholderData: (previousData) => previousData,
  });
};

// Hook for searching PDF content
export const useSearchPDFContent = (params: { query: string; pdfId?: number; page?: number; size?: number }) => {
  const { query, pdfId, page = 1, size = 20 } = params;
  return useQuery<PDFChunkSearchResponse>({
    queryKey: pdfKeys.search({ query, pdfId, page, size }),
    queryFn: () => apiClient.searchPDFContent(query, pdfId, page, size),
    enabled: !!query && query.length > 0,
    placeholderData: (previousData) => previousData,
  });
};

// Hook for uploading PDF
export const useUploadPDF = () => {
  const queryClient = useQueryClient();
  const { showNotification } = useNotification();

  return useMutation<PDF, Error, { file: File; title?: string }>({
    mutationFn: ({ file, title }: { file: File; title?: string }) => 
      apiClient.uploadPDF(file, title),
    onSuccess: () => {
      // Invalidate and refetch PDF lists
      queryClient.invalidateQueries({ queryKey: pdfKeys.lists() });
      showNotification('PDF uploaded and processed successfully!', 'success');
    },
    onError: (error: Error) => {
      showNotification(`Upload failed: ${error.message}`, 'error');
    },
  });
};

// Hook for deleting PDF
export const useDeletePDF = () => {
  const queryClient = useQueryClient();
  const { showNotification } = useNotification();

  return useMutation<{ message: string }, Error, number>({
    mutationFn: (id: number) => apiClient.deletePDF(id),
    onSuccess: (_, deletedId) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: pdfKeys.detail(deletedId) });
      queryClient.removeQueries({ queryKey: pdfKeys.chunks(deletedId) });
      // Invalidate lists
      queryClient.invalidateQueries({ queryKey: pdfKeys.lists() });
      showNotification('PDF deleted successfully!', 'success');
    },
    onError: (error: Error) => {
      showNotification(`Delete failed: ${error.message}`, 'error');
    },
  });
};

// Hook for PDF stats
export const usePDFStats = (id: number) => {
  return useQuery<any>({
    queryKey: [...pdfKeys.detail(id), 'stats'],
    queryFn: () => apiClient.getPDFStats(id),
    enabled: !!id,
  });
};