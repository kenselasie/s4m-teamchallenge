/// <reference types="cypress" />

describe("PDF List Functionality", () => {
  beforeEach(() => {
    cy.login();
  });

  it("should display list of PDFs", () => {
    cy.visit("/documents");

    // Verify page title
    cy.contains("Your PDF Documents").should("be.visible");

    // If PDFs exist, verify they're displayed with basic structure
    // This will work with whatever PDFs are actually in the backend
    cy.get("body").then(($body) => {
      if ($body.text().includes("No PDF documents found")) {
        // No PDFs in backend - verify empty state
        cy.contains("No PDF documents found").should("be.visible");
        cy.contains("Upload your first PDF to get started").should(
          "be.visible"
        );
      } else {
        // PDFs exist - verify basic card structure
        cy.get('[data-testid="pdf-card"], .MuiCard-root').should("exist");
      }
    });
  });

  it("should show delete functionality when PDFs exist", () => {
    cy.visit("/documents");

    // Check if PDFs exist and delete buttons are available
    cy.get("body").then(($body) => {
      if ($body.text().includes("No PDF documents found")) {
        // No PDFs to delete - just verify empty state
        cy.contains("No PDF documents found").should("be.visible");
      } else {
        // PDFs exist - verify delete buttons are present
        cy.get('button[aria-label*="Delete"], button[title*="Delete"]').should(
          "exist"
        );
      }
    });
  });
});
