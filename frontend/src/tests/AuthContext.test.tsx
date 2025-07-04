import { render, screen, act } from "@testing-library/react";
import { describe, it, expect, beforeEach, vi } from "vitest";
import { AuthProvider, useAuth } from "../context/AuthContext";

// Mock localStorage
const mockLocalStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};

Object.defineProperty(window, "localStorage", {
  value: mockLocalStorage,
});

// Test component that uses the AuthContext
const TestComponent = () => {
  const { isAuthenticated, token, login, logout } = useAuth();

  return (
    <div>
      <div data-testid="auth-status">
        {isAuthenticated ? "authenticated" : "not authenticated"}
      </div>
      <div data-testid="token">{token || "no token"}</div>
      <button onClick={() => login("test-token")}>Login</button>
      <button onClick={logout}>Logout</button>
    </div>
  );
};

describe("AuthContext", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should provide initial state when no token in localStorage", () => {
    mockLocalStorage.getItem.mockReturnValue(null);

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByTestId("auth-status")).toHaveTextContent(
      "not authenticated"
    );
    expect(screen.getByTestId("token")).toHaveTextContent("no token");
  });

  it("should provide authenticated state when token exists in localStorage", () => {
    mockLocalStorage.getItem.mockReturnValue("existing-token");

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByTestId("auth-status")).toHaveTextContent(
      "authenticated"
    );
    expect(screen.getByTestId("token")).toHaveTextContent("existing-token");
  });

  it("should update state when login is called", () => {
    mockLocalStorage.getItem.mockReturnValue(null);

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    act(() => {
      screen.getByText("Login").click();
    });

    expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
      "token",
      "test-token"
    );
    expect(screen.getByTestId("auth-status")).toHaveTextContent(
      "authenticated"
    );
    expect(screen.getByTestId("token")).toHaveTextContent("test-token");
  });

  it("should update state when logout is called", () => {
    mockLocalStorage.getItem.mockReturnValue("existing-token");

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    act(() => {
      screen.getByText("Logout").click();
    });

    expect(mockLocalStorage.removeItem).toHaveBeenCalledWith("token");
    expect(screen.getByTestId("auth-status")).toHaveTextContent(
      "not authenticated"
    );
    expect(screen.getByTestId("token")).toHaveTextContent("no token");
  });

  it("should throw error when useAuth is used outside AuthProvider", () => {
    const TestComponentWithoutProvider = () => {
      try {
        useAuth();
        return <div>Should not render</div>;
      } catch (error) {
        return <div data-testid="error">{(error as Error).message}</div>;
      }
    };

    render(<TestComponentWithoutProvider />);
    expect(screen.getByTestId("error")).toHaveTextContent(
      "useAuth must be used within an AuthProvider"
    );
  });
});
