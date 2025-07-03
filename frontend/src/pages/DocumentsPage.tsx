/**
 * Documents List Page
 */

import React, { useState } from "react";
import { useSearchParams } from "react-router-dom";
import Layout from "../components/Layout";
import PDFList from "../components/PDFList";
import PDFDetail from "../components/PDFDetail";
import { PDF } from "../services/api";

const DocumentsPage = () => {
  const [, setSearchParams] = useSearchParams();
  const [selectedPDF, setSelectedPDF] = useState<PDF | null>(null);

  const handleViewPDF = (pdf: PDF) => {
    setSelectedPDF(pdf);
    setSearchParams({ pdf: pdf.id.toString() });
  };

  const handleBackToList = () => {
    setSelectedPDF(null);
    setSearchParams({});
  };

  return (
    <Layout>
      {selectedPDF ? (
        <PDFDetail pdf={selectedPDF} onBack={handleBackToList} />
      ) : (
        <PDFList onViewPDF={handleViewPDF} />
      )}
    </Layout>
  );
};

export default DocumentsPage;
