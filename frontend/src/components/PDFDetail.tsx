import React, { useState, useCallback } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  IconButton,
  Pagination,
  Skeleton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Paper,
} from "@mui/material";
import {
  ArrowBack,
  PictureAsPdf,
  CheckCircle,
  Error,
  HourglassEmpty,
  ExpandMore,
  Person,
  DateRange,
  Description,
  Subject,
  Label,
} from "@mui/icons-material";
import { usePDF, usePDFChunks } from "../hooks/usePDFs";
import { PDF } from "../services/api";

interface PDFDetailProps {
  pdf: PDF;
  onBack: () => void;
}

const PDFDetail: React.FC<PDFDetailProps> = ({ pdf, onBack }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const chunksPerPage = 10;

  // Load PDF details
  const { data: pdfDetail } = usePDF(pdf.id);

  // Load PDF chunks with pagination
  const { data: chunksResponse, isLoading: chunksLoading } = usePDFChunks({
    pdfId: pdf.id,
    page: currentPage,
    size: chunksPerPage,
  });

  // Handle chunk page change - load chunks on demand
  const handleChunkPageChange = useCallback(
    (_event: React.ChangeEvent<unknown>, page: number) => {
      setCurrentPage(page);
    },
    []
  );

  // Get status info
  const getStatusInfo = (status: string) => {
    switch (status) {
      case "completed":
        return {
          color: "success" as const,
          icon: <CheckCircle />,
          text: "Processed",
        };
      case "failed":
        return { color: "error" as const, icon: <Error />, text: "Failed" };
      case "processing":
        return {
          color: "warning" as const,
          icon: <HourglassEmpty />,
          text: "Processing",
        };
      default:
        return {
          color: "default" as const,
          icon: <HourglassEmpty />,
          text: "Pending",
        };
    }
  };

  // Format date
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const statusInfo = getStatusInfo(pdf.processing_status);
  const displayPdf = pdfDetail || pdf; // Use detailed PDF if available, fallback to prop

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: "flex", alignItems: "center", mb: 3 }}>
        <IconButton onClick={onBack} sx={{ mr: 2 }}>
          <ArrowBack />
        </IconButton>
        <PictureAsPdf color="error" sx={{ mr: 1 }} />
        <Typography variant="h5" sx={{ flex: 1 }}>
          {displayPdf.title}
        </Typography>
        <Chip
          icon={statusInfo.icon}
          label={statusInfo.text}
          color={statusInfo.color}
        />
      </Box>

      {/* PDF Metadata */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Document Information
          </Typography>

          <Box
            sx={{
              display: "grid",
              gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" },
              gap: 2,
            }}
          >
            <Box>
              <Box
                sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}
              >
                <Description sx={{ fontSize: 20 }} />
                <Typography variant="body1">
                  <strong>Filename:</strong> {displayPdf.filename}
                </Typography>
              </Box>

              <Box
                sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}
              >
                <Description sx={{ fontSize: 20 }} />
                <Typography variant="body1">
                  <strong>Pages:</strong> {displayPdf.total_pages}
                </Typography>
              </Box>

              <Box
                sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}
              >
                <Description sx={{ fontSize: 20 }} />
                <Typography variant="body1">
                  <strong>Size:</strong> {displayPdf.file_size_mb} MB
                </Typography>
              </Box>

              <Box
                sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}
              >
                <DateRange sx={{ fontSize: 20 }} />
                <Typography variant="body1">
                  <strong>Uploaded:</strong> {formatDate(displayPdf.created_at)}
                </Typography>
              </Box>
            </Box>

            <Box>
              {displayPdf.author && (
                <Box
                  sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}
                >
                  <Person sx={{ fontSize: 20 }} />
                  <Typography variant="body1">
                    <strong>Author:</strong> {displayPdf.author}
                  </Typography>
                </Box>
              )}

              {displayPdf.subject && (
                <Box
                  sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1 }}
                >
                  <Subject sx={{ fontSize: 20 }} />
                  <Typography variant="body1">
                    <strong>Subject:</strong> {displayPdf.subject}
                  </Typography>
                </Box>
              )}

              {displayPdf.keywords && (
                <Box
                  sx={{
                    display: "flex",
                    alignItems: "flex-start",
                    gap: 1,
                    mb: 1,
                  }}
                >
                  <Label sx={{ fontSize: 20, mt: 0.2 }} />
                  <Typography variant="body1">
                    <strong>Keywords:</strong> {displayPdf.keywords}
                  </Typography>
                </Box>
              )}
            </Box>
          </Box>

          {displayPdf.processing_error && (
            <Box sx={{ mt: 2, p: 2, bgcolor: "error.light", borderRadius: 1 }}>
              <Typography variant="body2" color="error.dark">
                <strong>Processing Error:</strong> {displayPdf.processing_error}
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Content Chunks */}
      {displayPdf.processing_status === "completed" && (
        <Card>
          <CardContent>
            <Box
              sx={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                mb: 2,
              }}
            >
              <Typography variant="h6">
                Document Content{" "}
                {chunksResponse && "total" in chunksResponse
                  ? `(${chunksResponse.total} chunks)`
                  : ""}
              </Typography>
              {chunksResponse &&
              "pages" in chunksResponse &&
              chunksResponse.pages > 1 ? (
                <Typography variant="body2" color="text.secondary">
                  Showing page {currentPage} of {chunksResponse.pages} (
                  {chunksPerPage} chunks per page)
                </Typography>
              ) : null}
            </Box>

            {chunksLoading ? (
              <Box>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 2, textAlign: "center" }}
                >
                  Loading chunks...
                </Typography>
                {[...Array(5)].map((_, index) => (
                  <Box key={index} sx={{ mb: 2 }}>
                    <Skeleton variant="text" height={30} sx={{ mb: 1 }} />
                    <Skeleton variant="rectangular" height={80} />
                  </Box>
                ))}
              </Box>
            ) : !chunksResponse ||
              !("items" in chunksResponse) ||
              !chunksResponse.items?.length ? (
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ textAlign: "center", py: 4 }}
              >
                No content chunks available
              </Typography>
            ) : (
              <>
                <Box sx={{ mb: 3 }}>
                  {("items" in chunksResponse ? chunksResponse.items : []).map(
                    (chunk: any) => (
                      <Accordion key={chunk.id} sx={{ mb: 1 }}>
                        <AccordionSummary expandIcon={<ExpandMore />}>
                          <Box
                            sx={{
                              display: "flex",
                              alignItems: "center",
                              width: "100%",
                            }}
                          >
                            <Typography variant="subtitle1" sx={{ flex: 1 }}>
                              Chunk {chunk.chunk_number} - Page{" "}
                              {chunk.page_number}
                            </Typography>
                            <Box sx={{ display: "flex", gap: 1, mr: 2 }}>
                              <Chip
                                label={`${chunk.word_count} words`}
                                size="small"
                                variant="outlined"
                              />
                              <Chip
                                label={chunk.content_type}
                                size="small"
                                color="primary"
                                variant="outlined"
                              />
                            </Box>
                          </Box>
                        </AccordionSummary>
                        <AccordionDetails>
                          <Paper sx={{ p: 2, bgcolor: "grey.50" }}>
                            <Typography
                              variant="body2"
                              sx={{
                                whiteSpace: "pre-wrap",
                                lineHeight: 1.6,
                                fontFamily: "monospace",
                              }}
                            >
                              {chunk.content}
                            </Typography>
                          </Paper>

                          <Box
                            sx={{
                              mt: 2,
                              display: "flex",
                              gap: 2,
                              flexWrap: "wrap",
                            }}
                          >
                            <Typography
                              variant="caption"
                              color="text.secondary"
                            >
                              Words: {chunk.word_count}
                            </Typography>
                            <Typography
                              variant="caption"
                              color="text.secondary"
                            >
                              Characters: {chunk.character_count}
                            </Typography>
                            {chunk.chunk_metadata && (
                              <Typography
                                variant="caption"
                                color="text.secondary"
                              >
                                Page size: {chunk.chunk_metadata.page_width} ×{" "}
                                {chunk.chunk_metadata.page_height}
                              </Typography>
                            )}
                          </Box>
                        </AccordionDetails>
                      </Accordion>
                    )
                  )}
                </Box>

                {chunksResponse &&
                "pages" in chunksResponse &&
                chunksResponse.pages > 1 ? (
                  <Box
                    sx={{
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      mt: 3,
                    }}
                  >
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{ mb: 1 }}
                    >
                      Click page numbers to load more chunks
                    </Typography>
                    <Pagination
                      count={
                        "pages" in chunksResponse ? chunksResponse.pages : 0
                      }
                      page={currentPage}
                      onChange={handleChunkPageChange}
                      color="primary"
                      disabled={chunksLoading}
                      showFirstButton
                      showLastButton
                    />
                  </Box>
                ) : null}
              </>
            )}
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default PDFDetail;
