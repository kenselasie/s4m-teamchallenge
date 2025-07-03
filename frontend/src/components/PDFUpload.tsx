import React, { useState, useCallback } from "react";
import {
  Box,
  Button,
  Paper,
  Typography,
  LinearProgress,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from "@mui/material";
import { CloudUpload, PictureAsPdf } from "@mui/icons-material";
import { useUploadPDF } from "../hooks/usePDFs";
import { useNotification } from "../context/NotificationContext";

const PDFUpload = () => {
  const uploadPDF = useUploadPDF();
  const { showNotification } = useNotification();
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);

  // Handle drag events
  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  // Handle drop
  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);

      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        const file = e.dataTransfer.files[0];
        if (file.type === "application/pdf") {
          setSelectedFile(file);
          setTitle(file.name.replace(".pdf", ""));
          setUploadDialogOpen(true);
        } else {
          // Show error for non-PDF files
          showNotification("Please select a PDF file", "error");
        }
      }
    },
    [showNotification]
  );

  // Handle file input change
  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files && e.target.files[0]) {
        const file = e.target.files[0];
        if (file.type === "application/pdf") {
          setSelectedFile(file);
          setTitle(file.name.replace(".pdf", ""));
          setUploadDialogOpen(true);
        } else {
          // Show error for non-PDF files
          showNotification("Please select a PDF file", "error");
        }
      }
    },
    [showNotification]
  );

  // Handle upload
  const handleUpload = useCallback(async () => {
    if (!selectedFile) return;

    uploadPDF.mutate(
      { file: selectedFile, title },
      {
        onSuccess: () => {
          setUploadDialogOpen(false);
          setSelectedFile(null);
          setTitle("");
        },
      }
    );
  }, [selectedFile, title, uploadPDF]);

  // Handle dialog close
  const handleDialogClose = useCallback(() => {
    setUploadDialogOpen(false);
    setSelectedFile(null);
    setTitle("");
  }, []);

  return (
    <>
      <Paper
        elevation={3}
        sx={{
          p: 4,
          border: dragActive ? "2px dashed #1976d2" : "2px dashed #ccc",
          backgroundColor: dragActive ? "#f5f5f5" : "transparent",
          textAlign: "center",
          cursor: "pointer",
          transition: "all 0.3s ease",
          "&:hover": {
            backgroundColor: "#f9f9f9",
            borderColor: "#1976d2",
          },
        }}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          accept="application/pdf"
          style={{ display: "none" }}
          id="pdf-upload-input"
          type="file"
          onChange={handleFileChange}
        />
        <label htmlFor="pdf-upload-input">
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 2,
            }}
          >
            <CloudUpload sx={{ fontSize: 64, color: "#1976d2" }} />
            <Typography variant="h6" gutterBottom>
              Drop PDF files here or click to browse
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Supports PDF files up to 10MB
            </Typography>
            <Button
              variant="contained"
              component="span"
              startIcon={<CloudUpload />}
              disabled={uploadPDF.isPending}
            >
              Choose PDF File
            </Button>
          </Box>
        </label>

        {uploadPDF.isPending && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" gutterBottom>
              Uploading and processing...
            </Typography>
            <LinearProgress />
          </Box>
        )}
      </Paper>

      {/* Upload Confirmation Dialog */}
      <Dialog
        open={uploadDialogOpen}
        onClose={handleDialogClose}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <PictureAsPdf color="error" />
          Upload PDF
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary">
              File: {selectedFile?.name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Size:{" "}
              {selectedFile ? (selectedFile.size / 1024 / 1024).toFixed(2) : 0}{" "}
              MB
            </Typography>
          </Box>
          <TextField
            fullWidth
            label="PDF Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Enter a title for this PDF"
            helperText="Optional: Provide a custom title for better organization"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDialogClose} disabled={uploadPDF.isPending}>
            Cancel
          </Button>
          <Button
            onClick={handleUpload}
            variant="contained"
            disabled={uploadPDF.isPending || !selectedFile}
            startIcon={<CloudUpload />}
          >
            {uploadPDF.isPending ? "Uploading..." : "Upload"}
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default PDFUpload;
