/// <reference types="cypress" />

describe("PDF Detail View", () => {
  beforeEach(() => {
    cy.login();
  });

  it("should display PDF details when PDFs exist", () => {
    cy.visit("/documents");

    // Check if PDFs exist and view buttons are available
    cy.get("body").then(($body) => {
      if ($body.text().includes("No PDF documents found")) {
        // No PDFs to view - skip this test
        cy.log("No PDFs available to test detail view");
      } else {
        // PDFs exist - test detail view
        cy.get("button").contains("View").first().click();

        // Verify we're on detail page
        cy.contains("Document Information").should("be.visible");
        cy.contains("Filename:").should("be.visible");

        // Verify basic metadata structure exists
        cy.get("body").should("contain.text", "Pages:");
        cy.get("body").should("contain.text", "Size:");
      }
    });
  });

  it("should navigate back from detail view", () => {
    cy.visit("/documents");

    // Check if PDFs exist before testing navigation
    cy.get("body").then(($body) => {
      if ($body.text().includes("No PDF documents found")) {
        // No PDFs to navigate from - skip this test
        cy.log("No PDFs available to test navigation");
      } else {
        // PDFs exist - test navigation
        cy.get("button").contains("View").first().click();
        cy.wait(2000); // Wait for navigation

        // Click back button (could be arrow back or breadcrumb)
        cy.get(
          'button[aria-label*="Back"], button[aria-label*="back"], .MuiIconButton-root'
        )
          .first()
          .click();

        // Should be back on documents page
        cy.contains("Your PDF Documents").should("be.visible");
      }
    });
  });
});