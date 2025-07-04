import { Box, Typography } from "@mui/material";
import Layout from "../components/Layout";
import PDFUpload from "../components/PDFUpload";

const UploadPage = () => {
  return (
    <Layout>
      <Box>
        <Typography variant="h4" gutterBottom>
          Upload PDF Documents
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          Upload PDF files to parse and extract content into searchable chunks.
        </Typography>
        <PDFUpload />
      </Box>
    </Layout>
  );
};

export default UploadPage;
