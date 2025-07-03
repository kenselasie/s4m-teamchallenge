import React, { useState, useCallback } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  Chip,
  IconButton,
  Grid,
  Pagination,
  Skeleton,
  Tooltip,
  Button,
} from "@mui/material";
import {
  PictureAsPdf,
  Visibility,
  Delete,
  CheckCircle,
  Error,
  HourglassEmpty,
  Person,
  DateRange,
  Description,
} from "@mui/icons-material";
import { usePDFs, useDeletePDF } from "../hooks/usePDFs";
import { PDF } from "../services/api";

interface PDFListProps {
  onViewPDF: (pdf: PDF) => void;
}

const PDFList = ({ onViewPDF }: PDFListProps) => {
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  const {
    data: pdfResponse,
    isLoading,
    error,
  } = usePDFs({ page: currentPage, size: pageSize });
  const deletePDF = useDeletePDF();

  // Handle page change
  const handlePageChange = useCallback(
    (_event: React.ChangeEvent<unknown>, page: number) => {
      setCurrentPage(page);
    },
    []
  );

  // Handle delete PDF
  const handleDeletePDF = useCallback(
    async (pdfId: number) => {
      if (window.confirm("Are you sure you want to delete this PDF?")) {
        deletePDF.mutate(pdfId);
      }
    },
    [deletePDF]
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
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (error) {
    return (
      <Box sx={{ textAlign: "center", py: 4 }}>
        <Typography variant="h6" color="error" gutterBottom>
          Failed to load PDFs
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {error.message}
        </Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          mb: 3,
        }}
      >
        <Typography variant="h5" gutterBottom>
          Your PDF Documents
        </Typography>
        {pdfResponse && (
          <Typography variant="body2" color="text.secondary">
            {pdfResponse.total} documents
          </Typography>
        )}
      </Box>

      {isLoading ? (
        <Grid container spacing={2}>
          {[...Array(6)].map((_, index) => (
            <Grid item xs={12} md={6} key={index}>
              <Card>
                <CardContent>
                  <Skeleton variant="text" height={30} sx={{ mb: 1 }} />
                  <Skeleton variant="text" height={20} sx={{ mb: 1 }} />
                  <Skeleton variant="rectangular" height={40} />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      ) : !pdfResponse || !pdfResponse.items?.length ? (
        <Box sx={{ textAlign: "center", py: 8 }}>
          <PictureAsPdf sx={{ fontSize: 64, color: "text.secondary", mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No PDF documents found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Upload your first PDF to get started
          </Typography>
        </Box>
      ) : (
        <>
          <Grid container spacing={2}>
            {pdfResponse.items.map((pdf) => {
              const statusInfo = getStatusInfo(pdf.processing_status);

              return (
                <Grid item xs={12} md={6} key={pdf.id}>
                  <Card
                    sx={{
                      height: "100%",
                      display: "flex",
                      flexDirection: "column",
                      "&:hover": {
                        boxShadow: 3,
                      },
                    }}
                  >
                    <CardContent sx={{ flexGrow: 1 }}>
                      <Box
                        sx={{
                          display: "flex",
                          alignItems: "flex-start",
                          mb: 2,
                        }}
                      >
                        <PictureAsPdf color="error" sx={{ mr: 2, mt: 0.5 }} />
                        <Box sx={{ flexGrow: 1 }}>
                          <Typography variant="h6" component="h2" gutterBottom>
                            {pdf.title}
                          </Typography>
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            gutterBottom
                          >
                            {pdf.filename}
                          </Typography>
                        </Box>
                        <Chip
                          icon={statusInfo.icon}
                          label={statusInfo.text}
                          color={statusInfo.color}
                          size="small"
                        />
                      </Box>

                      <Box
                        sx={{
                          display: "flex",
                          flexWrap: "wrap",
                          gap: 1,
                          mb: 2,
                        }}
                      >
                        <Box
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            gap: 0.5,
                          }}
                        >
                          <Description sx={{ fontSize: 16 }} />
                          <Typography variant="caption">
                            {pdf.total_pages} pages
                          </Typography>
                        </Box>
                        <Box
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            gap: 0.5,
                          }}
                        >
                          <Description sx={{ fontSize: 16 }} />
                          <Typography variant="caption">
                            {pdf.file_size_mb} MB
                          </Typography>
                        </Box>
                        <Box
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            gap: 0.5,
                          }}
                        >
                          <DateRange sx={{ fontSize: 16 }} />
                          <Typography variant="caption">
                            {formatDate(pdf.created_at)}
                          </Typography>
                        </Box>
                      </Box>

                      {pdf.author && (
                        <Box
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            gap: 0.5,
                            mb: 1,
                          }}
                        >
                          <Person sx={{ fontSize: 16 }} />
                          <Typography variant="caption">
                            {pdf.author}
                          </Typography>
                        </Box>
                      )}

                      {pdf.processing_error && (
                        <Typography
                          variant="body2"
                          color="error"
                          sx={{ mb: 1 }}
                        >
                          Error: {pdf.processing_error}
                        </Typography>
                      )}
                    </CardContent>

                    <Box
                      sx={{
                        p: 2,
                        pt: 0,
                        display: "flex",
                        justifyContent: "space-between",
                      }}
                    >
                      <Button
                        startIcon={<Visibility />}
                        onClick={() => onViewPDF(pdf)}
                        disabled={pdf.processing_status !== "completed"}
                      >
                        View
                      </Button>
                      <Tooltip title="Delete PDF">
                        <IconButton
                          onClick={() => handleDeletePDF(pdf.id)}
                          disabled={deletePDF.isPending}
                          color="error"
                        >
                          <Delete />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </Card>
                </Grid>
              );
            })}
          </Grid>

          {/* Pagination */}
          {pdfResponse && pdfResponse.pages > 1 && (
            <Box sx={{ display: "flex", justifyContent: "center", mt: 3 }}>
              <Pagination
                count={pdfResponse.pages}
                page={currentPage}
                onChange={handlePageChange}
                color="primary"
                disabled={isLoading}
                showFirstButton
                showLastButton
              />
            </Box>
          )}
        </>
      )}
    </Box>
  );
};

export default PDFList;
