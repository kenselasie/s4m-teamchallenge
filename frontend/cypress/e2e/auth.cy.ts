/// <reference types="cypress" />

describe("Authentication Flow", () => {
  beforeEach(() => {
    cy.visit("/login");
  });

  it("should show login form", () => {
    cy.get('input[name="email"]').should("be.visible");
    cy.get('input[name="password"]').should("be.visible");
    cy.contains("button", "Sign In").should("be.visible");
  });

  it("should show error message with invalid credentials", () => {
    cy.get('input[name="email"]').clear().type("wrong@example.com");
    cy.get('input[name="password"]').clear().type("wrongpassword");
    cy.contains("button", "Sign In").click();
    cy.contains("Incorrect username or password").should("be.visible");
  });

  it("should login successfully with correct credentials", () => {
    cy.get('input[name="email"]').clear().type("demo@example.com");
    cy.get('input[name="password"]').clear().type("demo123");
    cy.contains("button", "Sign In").click();
    cy.url().should("eq", Cypress.config().baseUrl + "/dashboard");
    cy.contains("Welcome to the Dashboard").should("be.visible");
  });
});
