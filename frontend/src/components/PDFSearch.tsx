import React, { useState, useCallback } from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  InputAdornment,
  Chip,
  Paper,
  Pagination,
  Skeleton,
  Button,
} from "@mui/material";
import { Search, PictureAsPdf, Clear } from "@mui/icons-material";
import { useSearchPDFContent } from "../hooks/usePDFs";

const PDFSearch = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [activeQuery, setActiveQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  // Only search when there's an active query
  const { data: searchResults, isLoading } = useSearchPDFContent({
    query: activeQuery,
    pdfId: undefined,
    page: currentPage,
    size: pageSize,
  });

  // Handle search
  const handleSearch = useCallback(() => {
    if (searchQuery.trim()) {
      setActiveQuery(searchQuery.trim());
      setCurrentPage(1);
    }
  }, [searchQuery]);

  // Handle clear search
  const handleClearSearch = useCallback(() => {
    setSearchQuery("");
    setActiveQuery("");
    setCurrentPage(1);
  }, []);

  // Handle page change
  const handlePageChange = useCallback(
    (_event: React.ChangeEvent<unknown>, page: number) => {
      setCurrentPage(page);
    },
    []
  );

  // Handle enter key
  const handleKeyPress = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter") {
        handleSearch();
      }
    },
    [handleSearch]
  );

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Search PDF Content
      </Typography>

      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        Search across all uploaded PDF documents for specific content.
      </Typography>

      {/* Search Input */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: "flex", gap: 2, alignItems: "flex-start" }}>
            <TextField
              fullWidth
              placeholder="Enter search terms..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
                endAdornment: searchQuery && (
                  <InputAdornment position="end">
                    <Button onClick={handleClearSearch} size="small">
                      <Clear />
                    </Button>
                  </InputAdornment>
                ),
              }}
            />
            <Button
              variant="contained"
              data-test="search-button"
              onClick={handleSearch}
              disabled={!searchQuery.trim() || isLoading}
              startIcon={<Search />}
            >
              Search
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Search Results */}
      {activeQuery && (
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
                Search Results{" "}
                {searchResults ? `(${searchResults.total} matches)` : ""}
              </Typography>
              {searchResults && searchResults.pages > 1 && (
                <Typography variant="body2" color="text.secondary">
                  Page {currentPage} of {searchResults.pages}
                </Typography>
              )}
            </Box>

            <Box sx={{ mb: 2 }}>
              <Chip
                label={`"${activeQuery}"`}
                onDelete={handleClearSearch}
                color="primary"
              />
            </Box>

            {isLoading ? (
              <Box>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 2, textAlign: "center" }}
                >
                  Searching...
                </Typography>
                {[...Array(5)].map((_, index) => (
                  <Box key={index} sx={{ mb: 2 }}>
                    <Skeleton variant="text" height={30} sx={{ mb: 1 }} />
                    <Skeleton variant="rectangular" height={100} />
                  </Box>
                ))}
              </Box>
            ) : !searchResults || !searchResults.items?.length ? (
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ textAlign: "center", py: 4 }}
              >
                No matches found for "{activeQuery}"
              </Typography>
            ) : (
              <>
                <Box sx={{ mb: 3 }}>
                  {searchResults.items.map((chunk) => (
                    <Paper
                      key={chunk.id}
                      sx={{
                        p: 2,
                        mb: 2,
                        border: "1px solid",
                        borderColor: "divider",
                      }}
                    >
                      <Box
                        sx={{ display: "flex", alignItems: "center", mb: 1 }}
                      >
                        <PictureAsPdf color="error" sx={{ mr: 1 }} />
                        <Typography variant="subtitle2" sx={{ flex: 1 }}>
                          Chunk {chunk.chunk_number} - Page {chunk.page_number}
                        </Typography>
                        <Chip
                          label={`${chunk.word_count} words`}
                          size="small"
                          variant="outlined"
                        />
                      </Box>

                      <Typography
                        variant="body2"
                        sx={{
                          mb: 1,
                          lineHeight: 1.6,
                          "& mark": {
                            backgroundColor: "warning.light",
                            color: "warning.contrastText",
                            padding: "2px 4px",
                            borderRadius: "2px",
                          },
                        }}
                        dangerouslySetInnerHTML={{
                          __html: chunk.content.replace(
                            new RegExp(`(${activeQuery})`, "gi"),
                            "<mark>$1</mark>"
                          ),
                        }}
                      />

                      <Typography variant="caption" color="text.secondary">
                        {chunk.character_count} characters
                      </Typography>
                    </Paper>
                  ))}
                </Box>

                {searchResults && searchResults.pages > 1 && (
                  <Box
                    sx={{ display: "flex", justifyContent: "center", mt: 3 }}
                  >
                    <Pagination
                      count={searchResults.pages}
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
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default PDFSearch;
