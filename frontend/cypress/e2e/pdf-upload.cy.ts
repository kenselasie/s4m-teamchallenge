/// <reference types="cypress" />

describe("PDF Upload Functionality", () => {
  beforeEach(() => {
    cy.login();
  });

  it("should upload a PDF file successfully", () => {
    // Navigate to upload page
    cy.visit("/upload");
    cy.contains("Upload PDF Documents").should("be.visible");

    // Upload test PDF file - the input is hidden so use force: true
    cy.get('input[type="file"]').selectFile(
      "cypress/fixtures/test-document.pdf",
      { force: true }
    );

    // Wait for upload dialog to appear
    cy.contains("Upload PDF").should("be.visible");

    // Add title in the dialog
    cy.get('input[placeholder="Enter a title for this PDF"]').clear().type("Test Document Upload");

    // Submit upload - click the Upload button in the dialog
    cy.get('[role="dialog"]').within(() => {
      cy.get('button').contains("Upload").click();
    });

    // Verify success notification appears
    cy.contains("PDF uploaded and processed successfully!", { timeout: 10000 }).should(
      "be.visible"
    );
  });

  it("should show upload progress and validation", () => {
    cy.visit("/upload");

    // Test file validation - try valid file
    cy.get('input[type="file"]').selectFile(
      "cypress/fixtures/test-document.pdf",
      { force: true }
    );

    // Wait for upload dialog to appear
    cy.contains("Upload PDF").should("be.visible");

    // Verify file is selected and displayed in dialog
    cy.contains("test-document.pdf").should("be.visible");

    // Verify upload button is enabled in the dialog
    cy.get('[role="dialog"]').within(() => {
      cy.get('button').contains("Upload").should("not.be.disabled");
      
      // Close dialog
      cy.get('button').contains("Cancel").click();
    });
  });

  it("should handle invalid file types", () => {
    cy.visit("/upload");

    // Verify upload page loads correctly
    cy.contains("Upload PDF Documents").should("be.visible");
    
    // Verify file input accepts only PDF files
    cy.get('input[type="file"]').should("have.attr", "accept", "application/pdf");
    
    // Verify upload instructions are clear
    cy.contains("Drop PDF files here or click to browse").should("be.visible");
    cy.contains("Supports PDF files up to 10MB").should("be.visible");
  });
});