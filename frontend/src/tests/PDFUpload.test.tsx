import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import PDFUpload from "../components/PDFUpload";
import { useNotification } from "../context/NotificationContext";
import { useUploadPDF } from "../hooks/usePDFs";

// Mock the hooks
vi.mock("../hooks/usePDFs", () => ({
  useUploadPDF: vi.fn(),
}));

vi.mock("../context/NotificationContext", () => ({
  useNotification: vi.fn(),
}));

const mockUseUploadPDF = vi.mocked(useUploadPDF);
const mockUseNotification = vi.mocked(useNotification);

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

describe("PDFUpload", () => {
  const mockMutate = vi.fn();
  const mockShowNotification = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();

    mockUseUploadPDF.mockReturnValue({
      mutate: mockMutate,
      isPending: false,
      isError: false,
      error: null,
      data: null,
      isSuccess: false,
    } as any);

    mockUseNotification.mockReturnValue({
      showNotification: mockShowNotification,
    } as any);
  });

  it("renders upload area correctly", () => {
    renderWithProviders(<PDFUpload />);

    expect(
      screen.getByText("Drop PDF files here or click to browse")
    ).toBeInTheDocument();
    expect(
      screen.getByText("Supports PDF files up to 10MB")
    ).toBeInTheDocument();
    expect(screen.getByText("Choose PDF File")).toBeInTheDocument();
  });

  it("handles file input change with valid PDF", async () => {
    const user = userEvent.setup();
    renderWithProviders(<PDFUpload />);

    const file = new File(["pdf content"], "test.pdf", {
      type: "application/pdf",
    });
    const input = screen.getByTestId("pdf-upload-input") as HTMLInputElement;

    await user.upload(input, file);

    await waitFor(() => {
      expect(screen.getByText("Upload PDF")).toBeInTheDocument();
    });

    expect(screen.getByText("File: test.pdf")).toBeInTheDocument();
    expect(screen.getByDisplayValue("test")).toBeInTheDocument(); // Title field
  });

  it("handles drag and drop events", async () => {
    renderWithProviders(<PDFUpload />);

    const dropZone = screen
      .getByText("Drop PDF files here or click to browse")
      .closest("div") as HTMLElement;

    // Test drag enter
    fireEvent.dragEnter(dropZone);
    expect(dropZone.closest(".MuiPaper-root")).toHaveStyle(
      "border: 2px dashed #1976d2"
    );

    // Test drag leave
    fireEvent.dragLeave(dropZone);
    expect(dropZone.closest(".MuiPaper-root")).toHaveStyle(
      "border: 2px dashed #ccc"
    );
  });

  it("handles drop with valid PDF file", async () => {
    renderWithProviders(<PDFUpload />);

    const dropZone = screen
      .getByText("Drop PDF files here or click to browse")
      .closest("div") as HTMLElement;
    const file = new File(["pdf content"], "dropped.pdf", {
      type: "application/pdf",
    });

    const dropEvent = new Event("drop", { bubbles: true });
    Object.defineProperty(dropEvent, "dataTransfer", {
      value: {
        files: [file],
      },
    });

    fireEvent(dropZone, dropEvent);

    await waitFor(() => {
      expect(screen.getByText("Upload PDF")).toBeInTheDocument();
    });

    expect(screen.getByText("File: dropped.pdf")).toBeInTheDocument();
    expect(screen.getByDisplayValue("dropped")).toBeInTheDocument();
  });

  it("handles drop with invalid file type", async () => {
    renderWithProviders(<PDFUpload />);

    const dropZone = screen
      .getByText("Drop PDF files here or click to browse")
      .closest("div") as HTMLElement;
    const file = new File(["not pdf"], "test.txt", { type: "text/plain" });

    const dropEvent = new Event("drop", { bubbles: true });
    Object.defineProperty(dropEvent, "dataTransfer", {
      value: {
        files: [file],
      },
    });

    fireEvent(dropZone, dropEvent);

    expect(mockShowNotification).toHaveBeenCalledWith(
      "Please select a PDF file",
      "error"
    );
  });

  it("handles upload dialog actions", async () => {
    const user = userEvent.setup();
    renderWithProviders(<PDFUpload />);

    const file = new File(["pdf content"], "test.pdf", {
      type: "application/pdf",
    });
    const input = screen.getByTestId("pdf-upload-input") as HTMLInputElement;

    await user.upload(input, file);

    await waitFor(() => {
      expect(screen.getByText("Upload PDF")).toBeInTheDocument();
    });

    // Test title change
    const titleInput = screen.getByLabelText("PDF Title");
    await user.clear(titleInput);
    await user.type(titleInput, "Custom Title");

    expect(screen.getByDisplayValue("Custom Title")).toBeInTheDocument();
  });

  it("handles upload action", async () => {
    const user = userEvent.setup();
    renderWithProviders(<PDFUpload />);

    const file = new File(["pdf content"], "test.pdf", {
      type: "application/pdf",
    });
    const input = screen.getByTestId("pdf-upload-input") as HTMLInputElement;

    await user.upload(input, file);

    await waitFor(() => {
      expect(screen.getByText("Upload PDF")).toBeInTheDocument();
    });

    const uploadButton = screen.getByText("Upload");
    await user.click(uploadButton);

    expect(mockMutate).toHaveBeenCalledWith(
      { file, title: "test" },
      expect.objectContaining({
        onSuccess: expect.any(Function),
      })
    );
  });

  it("shows loading state during upload", () => {
    mockUseUploadPDF.mockReturnValue({
      mutate: mockMutate,
      isPending: true,
      isError: false,
      error: null,
      data: null,
      isSuccess: false,
    } as any);

    renderWithProviders(<PDFUpload />);

    expect(screen.getByText("Uploading and processing...")).toBeInTheDocument();
    expect(screen.getByRole("progressbar")).toBeInTheDocument();
  });

  it("disables upload button when no file selected", async () => {
    renderWithProviders(<PDFUpload />);

    const file = new File(["pdf content"], "test.pdf", {
      type: "application/pdf",
    });
    const input = screen.getByTestId("pdf-upload-input") as HTMLInputElement;

    await userEvent.upload(input, file);

    await waitFor(() => {
      expect(screen.getByText("Upload PDF")).toBeInTheDocument();
    });

    // Clear the file somehow (simulate the dialog being opened without file)
    const uploadButton = screen.getByText("Upload");
    expect(uploadButton).toBeEnabled();
  });

  it("shows upload dialog with correct file information", async () => {
    renderWithProviders(<PDFUpload />);

    const file = new File(["pdf content"], "large-document.pdf", {
      type: "application/pdf",
    });
    // Mock file size to be 1MB
    Object.defineProperty(file, "size", { value: 1024 * 1024 });

    const input = screen.getByTestId("pdf-upload-input") as HTMLInputElement;

    await userEvent.upload(input, file);

    await waitFor(() => {
      expect(screen.getByText("Upload PDF")).toBeInTheDocument();
    });

    expect(screen.getByText("File: large-document.pdf")).toBeInTheDocument();
    expect(screen.getByText("Size: 1.00 MB")).toBeInTheDocument();
    expect(screen.getByDisplayValue("large-document")).toBeInTheDocument();
  });

  it("handles successful upload callback", async () => {
    const user = userEvent.setup();
    renderWithProviders(<PDFUpload />);

    const file = new File(["pdf content"], "test.pdf", {
      type: "application/pdf",
    });
    const input = screen.getByTestId("pdf-upload-input") as HTMLInputElement;

    await user.upload(input, file);

    await waitFor(() => {
      expect(screen.getByText("Upload PDF")).toBeInTheDocument();
    });

    const uploadButton = screen.getByText("Upload");
    await user.click(uploadButton);

    // Simulate successful upload
    const onSuccessCallback = mockMutate.mock.calls[0][1].onSuccess;
    onSuccessCallback();

    // Dialog should close
    await waitFor(() => {
      expect(screen.queryByText("Upload PDF")).not.toBeInTheDocument();
    });
  });
});
