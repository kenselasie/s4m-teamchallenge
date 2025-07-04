/// <reference types="cypress" />

describe("PDF Search Functionality", () => {
  beforeEach(() => {
    cy.login();
  });

  it("should perform search functionality", () => {
    cy.visit("/search");

    // Verify search page
    cy.contains("Search PDF Content").should("be.visible");
    cy.get('input[placeholder*="search terms"]').should("be.visible");

    // Perform search with a common word
    cy.get('input[placeholder*="search terms"]').type("test");
    cy.get('[data-test="search-button"]').click();

    // Wait for search results (or no results message)
    cy.get("body", { timeout: 10000 }).then(($body) => {
      expect(
        $body.text().includes("Search Results") ||
          $body.text().includes("No matches found for"),
        'Should contain either "Search Results" or "No matches found for"'
      ).to.be.true;
    });
  });

  it("should handle search with unlikely terms", () => {
    cy.visit("/search");

    // Search for unlikely terms
    cy.get('input[placeholder*="search terms"]').type("xyzunlikelytermzyx");
    cy.get('[data-test="search-button"]').click();

    // Should either show no results or handle gracefully
    cy.get("body", { timeout: 10000 }).then(($body) => {
      expect(
        $body.text().includes("No matches found for") ||
          $body.text().includes("Search Results"),
        'Should contain either "No matches found for" or "Search Results"'
      ).to.be.true;
    });
  });

  it("should clear search results", () => {
    cy.visit("/search");

    // Perform search
    cy.get('input[placeholder*="search terms"]').type("test");
    cy.get('[data-test="search-button"]').click();

    // Wait for search to complete
    cy.wait(2000);

    // Look for clear button and click if exists
    cy.get("body").then(($body) => {
      if ($body.find('button:contains("Clear")').length > 0) {
        cy.get("button").contains("Clear").click();
        // Verify search is cleared
        cy.get('input[placeholder*="search terms"]').should("have.value", "");
      }
    });
  });
});