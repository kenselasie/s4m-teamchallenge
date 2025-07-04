/// <reference types="cypress" />

// Custom command for login without API mocking
Cypress.Commands.add('login', (email: string = 'demo@example.com', password: string = 'demo123') => {
  cy.visit('/login')
  
  // If the form is pre-filled with demo credentials, just click sign in
  // Otherwise, clear and type the provided credentials
  cy.get('input[name="email"]').then(($email) => {
    if ($email.val() !== email) {
      cy.get('input[name="email"]').clear().type(email)
    }
  })
  
  cy.get('input[name="password"]').then(($password) => {
    if ($password.val() !== password) {
      cy.get('input[name="password"]').clear().type(password)
    }
  })
  
  cy.contains('button', 'Sign In').click()
  cy.url().should('eq', Cypress.config().baseUrl + '/dashboard')
})

declare namespace Cypress {
  interface Chainable {
    login(email?: string, password?: string): Chainable<void>
  }
}
