import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";

// Mock next/navigation
const mockReplace = vi.fn();
const mockPathname = vi.fn(() => "/");

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: mockReplace }),
  usePathname: () => mockPathname(),
}));

// Mock auth
const mockIsAuthenticated = vi.fn();
vi.mock("@/lib/auth", () => ({
  isAuthenticated: () => mockIsAuthenticated(),
}));

import { AuthGuard } from "../auth-guard";

describe("AuthGuard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockPathname.mockReturnValue("/");
  });

  it("shows children when authenticated", () => {
    mockIsAuthenticated.mockReturnValue(true);
    render(
      <AuthGuard>
        <div>Protected content</div>
      </AuthGuard>,
    );
    expect(screen.getByText("Protected content")).toBeDefined();
  });

  it("shows children as guest (no auth required to browse)", () => {
    mockIsAuthenticated.mockReturnValue(false);
    render(
      <AuthGuard>
        <div>Protected content</div>
      </AuthGuard>,
    );
    expect(mockReplace).not.toHaveBeenCalled();
    expect(screen.getByText("Protected content")).toBeDefined();
  });

  it("shows login page without redirect", () => {
    mockIsAuthenticated.mockReturnValue(false);
    mockPathname.mockReturnValue("/login");
    render(
      <AuthGuard>
        <div>Login page</div>
      </AuthGuard>,
    );
    expect(mockReplace).not.toHaveBeenCalled();
    expect(screen.getByText("Login page")).toBeDefined();
  });
});
