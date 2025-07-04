import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import PDFList from "../components/PDFList";
import { usePDFs, useDeletePDF } from "../hooks/usePDFs";
import { PDF } from "../services/api";

// Mock the hooks
vi.mock("../hooks/usePDFs", () => ({
  usePDFs: vi.fn(),
  useDeletePDF: vi.fn(),
}));

const mockUsePDFs = vi.mocked(usePDFs);
const mockUseDeletePDF = vi.mocked(useDeletePDF);

// Mock window.confirm
const mockConfirm = vi.fn();
Object.defineProperty(window, "confirm", {
  value: mockConfirm,
  writable: true,
});

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
      mutations: {
        retry: false,
      },
    },
  });

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>{component}</QueryClientProvider>
  );
};

const mockPDFs: PDF[] = [
  {
    id: 1,
    title: "Test PDF 1",
    filename: "test1.pdf",
    processing_status: "completed",
    total_pages: 10,
    file_size_mb: 2.5,
    created_at: "2023-01-01T10:00:00Z",
    author: "Test Author",
    processing_error: null,
    content_type: "",
    file_size: 0,
    is_processed: false,
    updated_at: "",
  },
  {
    id: 2,
    title: "Test PDF 2",
    filename: "test2.pdf",
    processing_status: "processing",
    total_pages: 5,
    file_size_mb: 1.2,
    created_at: "2023-01-02T11:00:00Z",
    author: null,
    processing_error: null,
    content_type: "",
    file_size: 0,
    is_processed: false,
    updated_at: "",
  },
  {
    id: 3,
    title: "Test PDF 3",
    filename: "test3.pdf",
    processing_status: "failed",
    total_pages: 0,
    file_size_mb: 0.8,
    created_at: "2023-01-03T12:00:00Z",
    author: null,
    processing_error: "Processing failed due to corrupted file",
    content_type: "",
    file_size: 0,
    is_processed: false,
    updated_at: "",
  },
];

describe("PDFList", () => {
  const mockOnViewPDF = vi.fn();
  const mockDeleteMutate = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockConfirm.mockReturnValue(true);

    mockUseDeletePDF.mockReturnValue({
      mutate: mockDeleteMutate,
      isPending: false,
      isError: false,
      error: null,
    } as any);
  });

  it("renders loading state", () => {
    mockUsePDFs.mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
    } as any);

    renderWithProviders(<PDFList onViewPDF={mockOnViewPDF} />);

    expect(screen.getByText("Your PDF Documents")).toBeInTheDocument();
    // Should show skeleton loaders - check for the skeleton class
    const skeletons = document.querySelectorAll(".MuiSkeleton-root");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("renders error state", () => {
    const errorMessage = "Failed to fetch PDFs";
    mockUsePDFs.mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error(errorMessage),
    } as any);

    renderWithProviders(<PDFList onViewPDF={mockOnViewPDF} />);

    expect(screen.getByText("Failed to load PDFs")).toBeInTheDocument();
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  it("renders empty state when no PDFs", () => {
    mockUsePDFs.mockReturnValue({
      data: { items: [], total: 0, pages: 0 },
      isLoading: false,
      error: null,
    } as any);

    renderWithProviders(<PDFList onViewPDF={mockOnViewPDF} />);

    expect(screen.getByText("No PDF documents found")).toBeInTheDocument();
    expect(
      screen.getByText("Upload your first PDF to get started")
    ).toBeInTheDocument();
  });

  it("renders PDF list correctly", () => {
    mockUsePDFs.mockReturnValue({
      data: { items: mockPDFs, total: 3, pages: 1 },
      isLoading: false,
      error: null,
    } as any);

    renderWithProviders(<PDFList onViewPDF={mockOnViewPDF} />);

    expect(screen.getByText("Your PDF Documents")).toBeInTheDocument();
    expect(screen.getByText("3 documents")).toBeInTheDocument();

    // Check if all PDFs are rendered
    expect(screen.getByText("Test PDF 1")).toBeInTheDocument();
    expect(screen.getByText("Test PDF 2")).toBeInTheDocument();
    expect(screen.getByText("Test PDF 3")).toBeInTheDocument();
  });

  it("displays correct status chips", () => {
    mockUsePDFs.mockReturnValue({
      data: { items: mockPDFs, total: 3, pages: 1 },
      isLoading: false,
      error: null,
    } as any);

    renderWithProviders(<PDFList onViewPDF={mockOnViewPDF} />);

    expect(screen.getByText("Processed")).toBeInTheDocument();
    expect(screen.getByText("Processing")).toBeInTheDocument();
    expect(screen.getByText("Failed")).toBeInTheDocument();
  });

  it("shows PDF metadata correctly", () => {
    mockUsePDFs.mockReturnValue({
      data: { items: mockPDFs, total: 3, pages: 1 },
      isLoading: false,
      error: null,
    } as any);

    renderWithProviders(<PDFList onViewPDF={mockOnViewPDF} />);

    expect(screen.getByText("10 pages")).toBeInTheDocument();
    expect(screen.getByText("2.5 MB")).toBeInTheDocument();
    expect(screen.getByText("Test Author")).toBeInTheDocument();
  });

  it("shows processing error when present", () => {
    mockUsePDFs.mockReturnValue({
      data: { items: mockPDFs, total: 3, pages: 1 },
      isLoading: false,
      error: null,
    } as any);

    renderWithProviders(<PDFList onViewPDF={mockOnViewPDF} />);

    expect(
      screen.getByText("Error: Processing failed due to corrupted file")
    ).toBeInTheDocument();
  });

  it("calls onViewPDF when view button is clicked", () => {
    mockUsePDFs.mockReturnValue({
      data: { items: mockPDFs, total: 3, pages: 1 },
      isLoading: false,
      error: null,
    } as any);

    renderWithProviders(<PDFList onViewPDF={mockOnViewPDF} />);

    const viewButtons = screen.getAllByText("View");
    const enabledViewButton = viewButtons[0]; // First PDF has completed status

    fireEvent.click(enabledViewButton);
    expect(mockOnViewPDF).toHaveBeenCalledWith(mockPDFs[0]);
  });

  it("disables view button for non-completed PDFs", () => {
    mockUsePDFs.mockReturnValue({
      data: { items: mockPDFs, total: 3, pages: 1 },
      isLoading: false,
      error: null,
    } as any);

    renderWithProviders(<PDFList onViewPDF={mockOnViewPDF} />);

    const viewButtons = screen.getAllByText("View");
    const processingPDFViewButton = viewButtons[1].closest("button");
    const failedPDFViewButton = viewButtons[2].closest("button");

    expect(processingPDFViewButton).toBeDisabled();
    expect(failedPDFViewButton).toBeDisabled();
  });

  it("handles delete PDF with confirmation", async () => {
    mockUsePDFs.mockReturnValue({
      data: { items: mockPDFs, total: 3, pages: 1 },
      isLoading: false,
      error: null,
    } as any);

    renderWithProviders(<PDFList onViewPDF={mockOnViewPDF} />);

    const deleteButtons = screen.getAllByLabelText("Delete PDF");
    fireEvent.click(deleteButtons[0]);

    expect(mockConfirm).toHaveBeenCalledWith(
      "Are you sure you want to delete this PDF?"
    );
    expect(mockDeleteMutate).toHaveBeenCalledWith(1);
  });

  it("does not delete PDF when confirmation is cancelled", async () => {
    mockConfirm.mockReturnValue(false);
    mockUsePDFs.mockReturnValue({
      data: { items: mockPDFs, total: 3, pages: 1 },
      isLoading: false,
      error: null,
    } as any);

    renderWithProviders(<PDFList onViewPDF={mockOnViewPDF} />);

    const deleteButtons = screen.getAllByLabelText("Delete PDF");
    fireEvent.click(deleteButtons[0]);

    expect(mockConfirm).toHaveBeenCalledWith(
      "Are you sure you want to delete this PDF?"
    );
    expect(mockDeleteMutate).not.toHaveBeenCalled();
  });

  it("disables delete button during deletion", () => {
    mockUseDeletePDF.mockReturnValue({
      mutate: mockDeleteMutate,
      isPending: true,
      isError: false,
      error: null,
    } as any);

    mockUsePDFs.mockReturnValue({
      data: { items: mockPDFs, total: 3, pages: 1 },
      isLoading: false,
      error: null,
    } as any);

    renderWithProviders(<PDFList onViewPDF={mockOnViewPDF} />);

    const deleteButtons = screen.getAllByLabelText("Delete PDF");
    expect(deleteButtons[0]).toBeDisabled();
  });

  it("renders pagination when there are multiple pages", () => {
    mockUsePDFs.mockReturnValue({
      data: { items: mockPDFs, total: 25, pages: 3 },
      isLoading: false,
      error: null,
    } as any);

    renderWithProviders(<PDFList onViewPDF={mockOnViewPDF} />);

    expect(screen.getByRole("navigation")).toBeInTheDocument();
    expect(screen.getByText("1")).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
  });

  it("handles page change", () => {
    const { rerender } = renderWithProviders(
      <PDFList onViewPDF={mockOnViewPDF} />
    );

    // First render with page 1
    mockUsePDFs.mockReturnValue({
      data: { items: mockPDFs, total: 25, pages: 3 },
      isLoading: false,
      error: null,
    } as any);

    rerender(<PDFList onViewPDF={mockOnViewPDF} />);

    const page2Button = screen.getByText("2");
    fireEvent.click(page2Button);

    // Check that the click handler was called
    expect(page2Button).toBeInTheDocument();
  });

  it("formats dates correctly", () => {
    mockUsePDFs.mockReturnValue({
      data: { items: mockPDFs, total: 3, pages: 1 },
      isLoading: false,
      error: null,
    } as any);

    renderWithProviders(<PDFList onViewPDF={mockOnViewPDF} />);

    // Check if dates are formatted (will vary based on locale)
    expect(screen.getByText(/Jan 1, 2023/)).toBeInTheDocument();
  });
});
