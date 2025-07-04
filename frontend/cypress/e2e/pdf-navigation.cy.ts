/// <reference types="cypress" />

describe("Navigation and User Experience", () => {
  beforeEach(() => {
    cy.login();
  });

  it("should navigate between pages correctly", () => {
    // Start from dashboard
    cy.visit("/dashboard");
    cy.contains("Welcome to the Dashboard").should("be.visible");

    // Navigate to upload using Material-UI tab
    cy.get('[role="tab"]').contains("Upload").click();
    cy.contains("Upload PDF Documents").should("be.visible");

    // Navigate to documents using Material-UI tab
    cy.get('[role="tab"]').contains("Documents").click();
    cy.contains("Your PDF Documents").should("be.visible");

    // Navigate to search using Material-UI tab
    cy.get('[role="tab"]').contains("Search").click();
    cy.contains("Search PDF Content").should("be.visible");
  });

  it("should handle slow network connections", () => {
    // Test that pages load within reasonable time
    cy.visit("/documents", { timeout: 15000 });
    cy.contains("Your PDF Documents", { timeout: 10000 }).should("be.visible");

    cy.visit("/search", { timeout: 15000 });
    cy.contains("Search PDF Content", { timeout: 10000 }).should("be.visible");

    cy.visit("/upload", { timeout: 15000 });
    cy.contains("Upload PDF Documents", { timeout: 10000 }).should("be.visible");
  });
});
